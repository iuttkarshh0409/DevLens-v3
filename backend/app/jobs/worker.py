import time
import signal
import asyncio
from typing import Optional
from app.rie.pipeline import AuditPipeline
from app.jobs.models import AuditJob, JobStatus
from app.jobs.queue import BaseQueue
from app.core.logging import logger

class Worker:
    def __init__(self, queue: BaseQueue, pipeline: Optional[AuditPipeline] = None, job_timeout_sec: float = 30.0):
        from app.ai.provider import GroqProvider
        self.queue = queue
        self.pipeline = pipeline or AuditPipeline(ai_provider=GroqProvider())
        self.running = False
        self.jobs_processed = 0
        self.job_timeout_sec = job_timeout_sec

    def _setup_signal_handlers(self) -> None:
        """Registers handlers for SIGTERM and SIGINT to stop cleanly."""
        try:
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, self.stop)
        except NotImplementedError:
            # add_signal_handler is not fully implemented on Windows asyncio event loops
            # We catch it gracefully here
            pass

    async def start(self) -> None:
        self.running = True
        self._setup_signal_handlers()
        logger.info("Worker process started successfully.")
        
        while self.running:
            job = self.queue.dequeue()
            if not job:
                await asyncio.sleep(0.5)
                continue
            
            await self.process_job(job)

    def stop(self) -> None:
        logger.info("Graceful shutdown signal received. Stopping worker loop...")
        self.running = False

    async def process_job(self, job: AuditJob) -> None:
        from app.github.client import GitHubClient
        from app.services.github.checks_service import ChecksService
        from app.services.github.pr_review_service import PRReviewService
        from app.services.github.status_service import StatusService

        repo_name = job.repo_data.get("name")
        owner = job.repo_data.get("owner")
        installation_id = job.repo_data.get("installation_id")
        pull_number = job.repo_data.get("pull_number")
        head_sha = job.repo_data.get("head_sha")
        check_run_id = job.repo_data.get("check_run_id")

        client = None
        repo_input = job.repo_data

        try:
            if installation_id and owner and repo_name:
                client = GitHubClient(installation_id=installation_id)
                snapshot = await client.fetch(owner, repo_name)
                repo_input = snapshot

            # Enforce execution timeout constraint
            start_time = time.time()
            logger.info(f"STAGE [ANALYZE REPOSITORY - START]: Running audit pipeline for {owner or 'local'}/{repo_name or 'local'} @ {head_sha or 'local'}")
            report = await asyncio.wait_for(
                self.pipeline.execute_audit(repo_input),
                timeout=self.job_timeout_sec
            )
            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"STAGE [ANALYZE REPOSITORY - SUCCESS]: Completed audit pipeline for {owner or 'local'}/{repo_name or 'local'} in {duration_ms}ms")
            
            if not report.execution.narrative_completed:
                if job.retries < job.max_retries:
                    # Exponential Backoff Sleep before retry enqueueing
                    backoff_delay = 2 ** job.retries
                    logger.warning(f"Narrative failed. Backoff sleep for {backoff_delay}s before retry.")
                    await asyncio.sleep(backoff_delay)
                    
                    job.retries += 1
                    job.status = JobStatus.PENDING
                    self.queue.enqueue(job)
                    return
                else:
                    logger.error(f"Job {job.job_id} exceeded maximum retries. Routing to DLQ.")
                    self.queue.mark_failed_dlq(job)
                    return

            score = report.scorecard.overall_score
            
            # Save completed audit details to PostgreSQL & Redis Cache
            from app.api.analytics import shared_analytics
            from app.models.analytics import AuditHistoryRecord, EvidenceSummary
            from datetime import datetime

            passed_rules = [r.rule_id for r in report.scorecard.rule_results if r.passed]
            failed_rules = [r.rule_id for r in report.scorecard.rule_results if not r.passed]
            
            security_findings = len([r for r in failed_rules if r.startswith("SEC")])
            documentation_findings = len([r for r in failed_rules if r.startswith("DOC")])
            testing_findings = len([r for r in failed_rules if r.startswith("TEST")])

            frameworks = getattr(report.analysis, "frameworks", [])
            languages = getattr(report.analysis, "languages", [])
            licenses = getattr(report.analysis, "licenses", [])
            ci = getattr(report.analysis, "ci", [])
            testing = getattr(report.analysis, "testing", [])
            deployment = getattr(report.analysis, "deployment", [])
            architecture = getattr(report.analysis, "architecture", "Standard")

            evidence = EvidenceSummary(
                passed_rules=passed_rules,
                failed_rules=failed_rules,
                frameworks=frameworks,
                languages=languages,
                licenses=licenses,
                ci=ci,
                testing=testing,
                deployment=deployment,
                architecture=architecture,
                security_findings=security_findings,
                documentation_findings=documentation_findings,
                testing_findings=testing_findings
            )

            record = AuditHistoryRecord(
                audit_id=job.job_id,
                repository_id=f"{installation_id or 12345}/{repo_name or 'test-repo'}",
                repo_name=repo_name or "test-repo",
                installation_id=installation_id or 12345,
                score=score,
                status="success",
                scoring_version=report.scorecard.scoring_version,
                devlens_version="3.0",
                commit_sha=head_sha or "unknown",
                branch=job.repo_data.get("branch") or "main",
                audit_duration_ms=duration_ms,
                trigger_type=job.repo_data.get("trigger_type") or "push",
                warnings_count=len(report.scorecard.rule_results) - len(passed_rules),
                timestamp=datetime.utcnow(),
                evidence=evidence
            )
            
            await shared_analytics.process_audit_completion(record)
            
            # Publish Integration statuses
            if client:
                raw_files = getattr(repo_input, "raw_files_content", {}) if not isinstance(repo_input, dict) else {}
                logger.info(f"STAGE [PUBLISH RESULTS - START]: Submitting integration statuses to GitHub for {owner}/{repo_name}")
                
                if check_run_id:
                    checks_svc = ChecksService(client)
                    conclusion = "success" if score >= 7.0 else "failure"
                    logger.info(f"STAGE [UPDATE CHECK RUN - START]: Marking check run {check_run_id} as completed with conclusion: {conclusion}")
                    await checks_svc.complete_check(owner, repo_name, check_run_id, report.analysis, score, raw_files)
                    logger.info(f"STAGE [UPDATE CHECK RUN - SUCCESS]: Successfully patched check run {check_run_id} as completed")
                
                if pull_number:
                    pr_svc = PRReviewService(client)
                    await pr_svc.submit_pr_review(owner, repo_name, pull_number, report.analysis, score, raw_files)
                
                if head_sha:
                    status_svc = StatusService(client)
                    await status_svc.post_completion_status(owner, repo_name, head_sha, score)
                
                logger.info(f"STAGE [PUBLISH RESULTS - SUCCESS]: Finished submitting integration statuses to GitHub for {owner}/{repo_name}")

            job.status = JobStatus.COMPLETED
            self.jobs_processed += 1
            if hasattr(self.queue, "completed_count"):
                self.queue.completed_count += 1

        except Exception as e:
            logger.error(f"Job execution failed with exception: {str(e)}")
            if job.retries < job.max_retries:
                backoff_delay = 2 ** job.retries
                logger.warning(f"Retrying job {job.job_id} in {backoff_delay}s.")
                await asyncio.sleep(backoff_delay)
                
                job.retries += 1
                job.status = JobStatus.PENDING
                self.queue.enqueue(job)
            else:
                logger.error(f"Job {job.job_id} failed permanently. Routing to DLQ.")
                self.queue.mark_failed_dlq(job)

