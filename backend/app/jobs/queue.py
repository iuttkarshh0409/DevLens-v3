import json
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

class RedisQueue(BaseQueue):
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        import os
        is_prod = os.getenv("ENV") == "production"
        try:
            self.client = redis.Redis(host=host, port=port, db=db, socket_timeout=2.0)
            self.client.ping()
            self.active = True
        except Exception as e:
            if is_prod:
                raise RuntimeError(f"Failed to connect to Redis in production: {str(e)}")
            self.active = False
            self.fallback = InMemoryQueue()
            
    def enqueue(self, job: AuditJob) -> None:
        if not self.active:
            return self.fallback.enqueue(job)
        # Store with TTL of 24 hours (86400 seconds)
        self.client.setex(f"job:{job.job_id}", 86400, job.json())
        self.client.rpush("devlens:queue", job.job_id)

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

    def status(self, job_id: str) -> Optional[JobStatus]:
        if not self.active:
            return self.fallback.status(job_id)
        job_data = self.client.get(f"job:{job_id}")
        if not job_data:
            return None
        job = AuditJob.parse_raw(job_data)
        return job.status

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

    def mark_failed_dlq(self, job: AuditJob) -> None:
        if not self.active:
            return self.fallback.mark_failed_dlq(job)
        job.status = JobStatus.FAILED
        self.client.setex(f"job:{job.job_id}", 86400, job.json())
        self.client.rpush("devlens:dlq", job.job_id)
