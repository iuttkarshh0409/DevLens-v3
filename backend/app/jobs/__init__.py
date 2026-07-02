from app.jobs.queue import RedisQueue
from app.jobs.models import AuditJob, JobStatus
from app.jobs.worker import Worker

shared_queue = RedisQueue()
