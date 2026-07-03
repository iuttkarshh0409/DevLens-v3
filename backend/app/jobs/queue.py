import json
import time
import random
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import redis
from app.jobs.models import AuditJob, JobStatus


class BaseQueue(ABC):
    @abstractmethod
    def enqueue(self, job: AuditJob) -> None: pass

    @abstractmethod
    def dequeue(self) -> Optional[AuditJob]: pass

    @abstractmethod
    def status(self, job_id: str) -> Optional[JobStatus]: pass

    @abstractmethod
    def cancel(self, job_id: str) -> bool: pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]: pass

    @abstractmethod
    def mark_failed_dlq(self, job: AuditJob) -> None: pass

class InMemoryQueue(BaseQueue):
    def __init__(self):
        self.queue: List[AuditJob] = []
        self.jobs_store: Dict[str, AuditJob] = {}
        self.dlq: List[AuditJob] = []
        self.failed_count = 0
        self.completed_count = 0

    def enqueue(self, job: AuditJob) -> None:
        job.status = JobStatus.PENDING
        self.queue.append(job)
        self.jobs_store[job.job_id] = job

    def dequeue(self) -> Optional[AuditJob]:
        if not self.queue:
            return None
        job = self.queue.pop(0)
        job.status = JobStatus.RUNNING
        return job

    def status(self, job_id: str) -> Optional[JobStatus]:
        job = self.jobs_store.get(job_id)
        return job.status if job else None

    def cancel(self, job_id: str) -> bool:
        job = self.jobs_store.get(job_id)
        if job and job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            job.status = JobStatus.CANCELLED
            if job in self.queue:
                self.queue.remove(job)
            return True
        return False

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "queue_depth": len(self.queue),
            "completed_jobs": self.completed_count,
            "failed_jobs": self.failed_count,
            "dlq_depth": len(self.dlq)
        }

    def mark_failed_dlq(self, job: AuditJob) -> None:
        job.status = JobStatus.FAILED
        self.dlq.append(job)
        self.failed_count += 1

class RedisCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 10.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # "CLOSED", "OPEN", "HALF-OPEN"
        self.last_state_change = time.time()

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_state_change = time.time()

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_state_change > self.recovery_timeout:
                self.state = "HALF-OPEN"
                self.last_state_change = time.time()
                return True
            return False
        return True  # HALF-OPEN


def with_redis_retry(max_retries: int = 3, base_delay: float = 0.5):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not self.circuit_breaker.can_execute():
                # If circuit is open, delegate immediately to fallback method
                if hasattr(self, "fallback") and self.fallback:
                    fallback_method = getattr(self.fallback, func.__name__)
                    return fallback_method(*args, **kwargs)
                raise RuntimeError("Redis circuit breaker is OPEN. Connection suspended.")

            retries = 0
            while True:
                try:
                    if not self.active or not self.client:
                        if self.is_prod:
                            self.reconnect()
                        else:
                            if hasattr(self, "fallback") and self.fallback:
                                fallback_method = getattr(self.fallback, func.__name__)
                                return fallback_method(*args, **kwargs)
                            raise redis.ConnectionError("Redis is inactive in development.")
                    res = func(self, *args, **kwargs)
                    self.circuit_breaker.record_success()
                    return res
                except (redis.ConnectionError, redis.TimeoutError) as e:
                    self.circuit_breaker.record_failure()
                    retries += 1
                    if retries > max_retries:
                        if self.is_prod:
                            raise e
                        if hasattr(self, "fallback") and self.fallback:
                            fallback_method = getattr(self.fallback, func.__name__)
                            return fallback_method(*args, **kwargs)
                        raise e
                    
                    # Exponential backoff delay with randomized jitter
                    temp = min(30.0, base_delay * (2 ** retries))
                    sleep_time = temp / 2 + random.uniform(0, temp / 2)
                    time.sleep(sleep_time)
        return wrapper
    return decorator


class RedisQueue(BaseQueue):
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        import os
        self.host = host
        self.port = port
        self.db = db
        self.is_prod = os.getenv("DEVLENS_ENV", "development").lower() == "production"
        self.circuit_breaker = RedisCircuitBreaker()
        self.client = None
        self.active = False
        self.fallback = InMemoryQueue()
        
        try:
            self.reconnect()
        except Exception as e:
            if self.is_prod:
                raise RuntimeError(f"Failed to connect to Redis in production: {str(e)}")

    def reconnect(self) -> None:
        """Establishes or refreshes connection to Redis."""
        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
            decode_responses=False
        )
        self.client.ping()
        self.active = True

    @with_redis_retry()
    def enqueue(self, job: AuditJob) -> None:
        if not self.active:
            return self.fallback.enqueue(job)
        self.client.setex(f"job:{job.job_id}", 86400, job.json())
        self.client.rpush("devlens:queue", job.job_id)

    @with_redis_retry()
    def dequeue(self) -> Optional[AuditJob]:
        if not self.active:
            return self.fallback.dequeue()
        job_id_bytes = self.client.lpop("devlens:queue")
        if not job_id_bytes:
            return None
        job_id = job_id_bytes.decode("utf-8")
        job_data = self.client.get(f"job:{job_id}")
        if not job_data:
            return None
        job = AuditJob.parse_raw(job_data)
        job.status = JobStatus.RUNNING
        self.client.setex(f"job:{job.job_id}", 86400, job.json())
        return job

    @with_redis_retry()
    def status(self, job_id: str) -> Optional[JobStatus]:
        if not self.active:
            return self.fallback.status(job_id)
        job_data = self.client.get(f"job:{job_id}")
        if not job_data:
            return None
        job = AuditJob.parse_raw(job_data)
        return job.status

    @with_redis_retry()
    def cancel(self, job_id: str) -> bool:
        if not self.active:
            return self.fallback.cancel(job_id)
        job_data = self.client.get(f"job:{job_id}")
        if not job_data:
            return False
        job = AuditJob.parse_raw(job_data)
        if job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            job.status = JobStatus.CANCELLED
            self.client.setex(f"job:{job.job_id}", 86400, job.json())
            self.client.lrem("devlens:queue", 0, job_id)
            return True
        return False

    @with_redis_retry()
    def get_metrics(self) -> Dict[str, Any]:
        if not self.active:
            return self.fallback.get_metrics()
        depth = self.client.llen("devlens:queue")
        dlq_depth = self.client.llen("devlens:dlq")
        return {
            "queue_depth": depth,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "dlq_depth": dlq_depth
        }

    @with_redis_retry()
    def mark_failed_dlq(self, job: AuditJob) -> None:
        if not self.active:
            return self.fallback.mark_failed_dlq(job)
        job.status = JobStatus.FAILED
        self.client.setex(f"job:{job.job_id}", 86400, job.json())
        self.client.rpush("devlens:dlq", job.job_id)
