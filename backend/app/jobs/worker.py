import time
import asyncio
from typing import Optional
from app.rie.pipeline import AuditPipeline
from app.jobs.models import AuditJob, JobStatus
from app.jobs.queue import BaseQueue

class Worker:
    def __init__(self, queue: BaseQueue, pipeline: Optional[AuditPipeline] = None):
        self.queue = queue
        self.pipeline = pipeline or AuditPipeline()
        self.running = False
        self.jobs_processed = 0

    async def start(self) -> None:
        self.running = True
        while self.running:
            job = self.queue.dequeue()
            if not job:
                # Idle poll sleep
                await asyncio.sleep(0.5)
                continue
            
            await self.process_job(job)

    def stop(self) -> None:
        self.running = False

    async def process_job(self, job: AuditJob) -> None:
        try:
            # Enforce pipeline execution
            report = await self.pipeline.execute_audit(job.repo_data)
            
            # If AI narrative was failed, and we have retries left, treat as transient failure
            if not report.execution.narrative_completed:
                if job.retries < job.max_retries:
                    job.retries += 1
                    job.status = JobStatus.PENDING
                    self.queue.enqueue(job)
                    return
                else:
                    job.status = JobStatus.FAILED
                    if hasattr(self.queue, "failed_count"):
                        self.queue.failed_count += 1
                    return

            job.status = JobStatus.COMPLETED
            self.jobs_processed += 1
            if hasattr(self.queue, "completed_count"):
                self.queue.completed_count += 1

        except Exception as e:
            if job.retries < job.max_retries:
                job.retries += 1
                job.status = JobStatus.PENDING
                self.queue.enqueue(job)
            else:
                job.status = JobStatus.FAILED
                if hasattr(self.queue, "failed_count"):
                    self.queue.failed_count += 1
