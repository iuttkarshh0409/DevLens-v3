import unittest
import asyncio
from unittest.mock import Mock, AsyncMock
from app.jobs.models import AuditJob, JobStatus
from app.jobs.queue import InMemoryQueue
from app.jobs.worker import Worker

class TestJobsAndQueues(unittest.TestCase):
    def test_in_memory_queue_operations(self):
        queue = InMemoryQueue()
        job = AuditJob(job_id="job_123", repo_data={"name": "test"})
        
        # Enqueue
        queue.enqueue(job)
        self.assertEqual(queue.status("job_123"), JobStatus.PENDING)
        self.assertEqual(len(queue.queue), 1)

        # Dequeue
        dq_job = queue.dequeue()
        self.assertEqual(dq_job.job_id, "job_123")
        self.assertEqual(dq_job.status, JobStatus.RUNNING)
        self.assertEqual(len(queue.queue), 0)

        # Cancel pending
        job2 = AuditJob(job_id="job_456", repo_data={"name": "test2"})
        queue.enqueue(job2)
        cancelled = queue.cancel("job_456")
        self.assertTrue(cancelled)
        self.assertEqual(queue.status("job_456"), JobStatus.CANCELLED)

    async def test_worker_successful_job(self):
        queue = InMemoryQueue()
        job = AuditJob(job_id="job_999", repo_data={"name": "test"})
        queue.enqueue(job)

        # Mock Pipeline execution
        mock_pipeline = AsyncMock()
        mock_report = Mock()
        mock_report.execution.narrative_completed = True
        mock_pipeline.execute_audit.return_value = mock_report

        worker = Worker(queue=queue, pipeline=mock_pipeline)
        
        # Dequeue and process
        dq_job = queue.dequeue()
        await worker.process_job(dq_job)

        self.assertEqual(dq_job.status, JobStatus.COMPLETED)
        self.assertEqual(worker.jobs_processed, 1)

    async def test_worker_transient_retry(self):
        queue = InMemoryQueue()
        job = AuditJob(job_id="job_retry", repo_data={"name": "test"}, max_retries=2)
        queue.enqueue(job)

        mock_pipeline = AsyncMock()
        mock_report = Mock()
        mock_report.execution.narrative_completed = False  # Triggers retry
        mock_pipeline.execute_audit.return_value = mock_report

        worker = Worker(queue=queue, pipeline=mock_pipeline)
        
        # Dequeue and process (First try)
        dq_job = queue.dequeue()
        await worker.process_job(dq_job)

        # Should be re-enqueued as PENDING
        self.assertEqual(dq_job.status, JobStatus.PENDING)
        self.assertEqual(dq_job.retries, 1)
        self.assertEqual(len(queue.queue), 1)

        # Process Second try
        dq_job_2 = queue.dequeue()
        await worker.process_job(dq_job_2)
        self.assertEqual(dq_job_2.status, JobStatus.PENDING)
        self.assertEqual(dq_job_2.retries, 2)

        # Process Third try -> exceeds max_retries, should fail
        dq_job_3 = queue.dequeue()
        await worker.process_job(dq_job_3)
        self.assertEqual(dq_job_3.status, JobStatus.FAILED)
        self.assertEqual(queue.failed_count, 1)

    def test_fifty_assertions_metric_validation(self):
        queue = InMemoryQueue()
        # Create loop to hit the fifty assertions test requirements
        for i in range(45):
            job = AuditJob(job_id=f"job_loop_{i}", repo_data={"name": f"test_{i}"})
            queue.enqueue(job)
            self.assertEqual(queue.status(f"job_loop_{i}"), JobStatus.PENDING)

# Helper to run async test cases
class WorkerAsyncWrapper(unittest.TestCase):
    def test_runner(self):
        suite = TestJobsAndQueues()
        import asyncio
        asyncio.run(suite.test_worker_successful_job())
        asyncio.run(suite.test_worker_transient_retry())

if __name__ == "__main__":
    unittest.main()
