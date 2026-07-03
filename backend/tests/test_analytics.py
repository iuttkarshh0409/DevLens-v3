import unittest
from datetime import datetime, timedelta
import uuid

# App imports
from app.models.analytics import AuditHistoryRecord, EvidenceSummary, RepositoryHealthRecord
from app.services.analytics_service import (
    InMemoryAnalyticsStore,
    AnalyticsService,
    TrendEngine,
    ExportService
)

class TestAnalyticsHistorical(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.store = InMemoryAnalyticsStore()
        self.service = AnalyticsService(self.store, retention_days=30, retention_count=5)
        
    def _create_record(self, repo_id: str, score: float, timestamp: datetime, status: str = "success") -> AuditHistoryRecord:
        return AuditHistoryRecord(
            audit_id=str(uuid.uuid4()),
            repository_id=repo_id,
            repo_name="TestRepo",
            installation_id=12345,
            score=score,
            status=status,
            scoring_version="3.0.0",
            devlens_version="3.0.0",
            commit_sha="abc123sha",
            branch="main",
            audit_duration_ms=450,
            trigger_type="push",
            warnings_count=1,
            timestamp=timestamp,
            evidence=EvidenceSummary(
                passed_rules=["RULE_1"],
                failed_rules=[],
                frameworks=["FastAPI"],
                languages=["Python"],
                security_findings=0,
                documentation_findings=1,
                testing_findings=1
            )
        )

    async def test_processing_and_retention_expiry(self):
        now = datetime.utcnow()
        
        # 1. Old records (beyond 30 days retention cutoff)
        old_record = self._create_record("repo_a", 8.0, now - timedelta(days=32))
        await self.service.process_audit_completion(old_record)
        
        # Verify it got deleted immediately by time-based retention policy
        records = await self.store.get_audit_records(repository_id="repo_a")
        self.assertEqual(len(records), 0)

        # 2. Add multiple records within retention limits to trigger count retention (limit = 5)
        for i in range(7):
            rec = self._create_record("repo_b", 7.0 + (i * 0.1), now - timedelta(minutes=10 - i))
            await self.service.process_audit_completion(rec)

        # Verify only the latest 5 records remain
        records_b = await self.store.get_audit_records(repository_id="repo_b")
        self.assertEqual(len(records_b), 5)
        
        # Ensure they are sorted chronologically and are the latest ones
        self.assertAlmostEqual(records_b[0].score, 7.2)
        self.assertAlmostEqual(records_b[-1].score, 7.6)

    async def test_out_of_order_webhook_delivery_idempotency(self):
        now = datetime.utcnow()
        
        # Simulate webhook payloads arriving backwards
        rec_new = self._create_record("repo_c", 9.0, now)
        rec_old = self._create_record("repo_c", 6.5, now - timedelta(hours=2))
        
        # 1. Process new first
        await self.service.process_audit_completion(rec_new)
        # 2. Process old second (out-of-order payload)
        await self.service.process_audit_completion(rec_old)
        
        # Verify the summary health is built off the latest timestamp (rec_new) despite out-of-order arrives
        healths = await self.store.get_health_records(12345)
        health = [h for h in healths if h.repository_id == "repo_c"][0]
        self.assertEqual(health.health_score, 9.0)
        self.assertEqual(health.last_audit, rec_new.timestamp)

    async def test_nightly_full_rebuild_idempotence(self):
        now = datetime.utcnow()
        rec1 = self._create_record("repo_d", 8.0, now - timedelta(hours=1))
        rec2 = self._create_record("repo_d", 8.5, now)
        
        await self.service.process_audit_completion(rec1)
        await self.service.process_audit_completion(rec2)
        
        # Check current score
        healths = await self.store.get_health_records(12345)
        health_before = [h for h in healths if h.repository_id == "repo_d"][0]
        self.assertEqual(health_before.health_score, 8.5)
        
        # Trigger full rebuild (should remain identical)
        await self.service.execute_nightly_rebuild(12345)
        
        healths_after = await self.store.get_health_records(12345)
        health_after = [h for h in healths_after if h.repository_id == "repo_d"][0]
        self.assertEqual(health_after.health_score, 8.5)

    def test_trend_engine_calculations(self):
        now = datetime.utcnow()
        records = [
            self._create_record("repo_e", 6.0, now - timedelta(days=2), status="failure"),
            self._create_record("repo_e", 8.0, now - timedelta(days=2)),
            self._create_record("repo_e", 9.0, now)
        ]
        
        # Test median calculation
        ts_median = TrendEngine.calculate_trends(records, "daily", "median")
        # For day-2, scores are [6.0, 8.0]. Median is (6.0+8.0)/2 = 7.0
        self.assertEqual(ts_median.points[0].value, 7.0)
        self.assertEqual(ts_median.points[1].value, 9.0)
        
        # Test 90th percentile
        ts_pct = TrendEngine.calculate_trends(records, "daily", "percentile")
        self.assertEqual(ts_pct.points[0].value, 8.0)
        self.assertEqual(ts_pct.points[1].value, 9.0)

        # Test hourly aggregation
        rec_hour1 = self._create_record("repo_e", 7.0, now.replace(minute=15))
        rec_hour2 = self._create_record("repo_e", 9.0, now.replace(minute=45))
        ts_hourly = TrendEngine.calculate_trends([rec_hour1, rec_hour2], "hourly", "average")
        self.assertEqual(len(ts_hourly.points), 1)
        self.assertEqual(ts_hourly.points[0].value, 8.0)

    def test_export_formatting(self):
        now = datetime.utcnow()
        rec = self._create_record("repo_f", 9.5, now)
        
        # Verify JSON envelope structure
        json_out = ExportService.generate_json_export([rec], 12345, "90d")
        self.assertIn("generated_at", json_out)
        self.assertEqual(json_out["installation_id"], 12345)
        self.assertEqual(json_out["record_count"], 1)
        self.assertEqual(json_out["data"][0]["score"], 9.5)
        
        # Verify CSV column formatting
        csv_out = ExportService.generate_csv_export([rec])
        self.assertIn("Audit ID,Repository ID,Repo Name", csv_out)
        self.assertIn("9.5", csv_out)
