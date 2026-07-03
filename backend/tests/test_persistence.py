import unittest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.database.models import Base
from app.storage.sql_analytics_store import SQLAnalyticsStore
from app.models.analytics import AuditHistoryRecord, RepositoryHealthRecord, EvidenceSummary
from app.services.analytics_service import AnalyticsService, InMemoryAnalyticsStore
from app.core.config import DEVLENS_ENV

class TestPersistenceAndCaching(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Create an async in-memory SQLite engine for the tests
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.session_factory = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)
        
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        self.store = SQLAnalyticsStore(self.session_factory)
        self.service = AnalyticsService(self.store, retention_days=180, retention_count=5)

    async def asyncTearDown(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await self.engine.dispose()

    async def test_sql_store_audit_save_and_retrieve(self):
        record = AuditHistoryRecord(
            audit_id="audit-123",
            repository_id="repo-999",
            repo_name="owner/repo",
            installation_id=12345,
            score=8.5,
            status="success",
            scoring_version="v1",
            devlens_version="3.0",
            commit_sha="abcdef123456",
            branch="main",
            audit_duration_ms=120,
            trigger_type="push",
            warnings_count=1,
            timestamp=datetime.utcnow(),
            evidence=EvidenceSummary(
                passed_rules=["RULE_1"],
                failed_rules=[],
                frameworks=["FastAPI"],
                languages=["Python"],
                security_findings=0,
                documentation_findings=1,
                testing_findings=0,
                licenses=["MIT"],
                ci=["GitHub Actions"],
                testing=["pytest"],
                deployment=["Docker"],
                architecture="Clean"
            )
        )
        
        await self.store.save_audit_record(record)
        
        # Retrieve
        retrieved = await self.store.get_audit_records(repository_id="repo-999")
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0].audit_id, "audit-123")
        self.assertEqual(retrieved[0].score, 8.5)
        self.assertEqual(retrieved[0].evidence.frameworks, ["FastAPI"])

    async def test_sql_store_retention_and_health(self):
        # Save multiple audits to verify count and time base retention
        for i in range(10):
            record = AuditHistoryRecord(
                audit_id=f"audit-{i}",
                repository_id="repo-999",
                repo_name="owner/repo",
                installation_id=12345,
                score=7.0 + (i * 0.1),
                status="success",
                scoring_version="v1",
                devlens_version="3.0",
                commit_sha="abcdef123456",
                branch="main",
                audit_duration_ms=120,
                trigger_type="push",
                warnings_count=1,
                timestamp=datetime.utcnow() - timedelta(days=200 if i < 2 else 0),
                evidence=EvidenceSummary(
                    passed_rules=["RULE_1"],
                    failed_rules=[],
                    frameworks=["FastAPI"],
                    languages=["Python"],
                    security_findings=0,
                    documentation_findings=1,
                    testing_findings=0,
                    licenses=["MIT"],
                    ci=["GitHub Actions"],
                    testing=["pytest"],
                    deployment=["Docker"],
                    architecture="Clean"
                )
            )
            await self.service.process_audit_completion(record)

        # Retrieve remaining audits
        # We had 10 records. 2 were older than 180 days -> deleted by time cutoff.
        # This leaves 8 records. Count retention limit is 5 -> deletes excess, leaving exactly 5 records.
        records = await self.store.get_audit_records(repository_id="repo-999")
        self.assertEqual(len(records), 5)
        
        # Verify repository health summary got calculated
        healths = await self.store.get_health_records(12345)
        self.assertEqual(len(healths), 1)
        self.assertEqual(healths[0].repository_id, "repo-999")
        self.assertAlmostEqual(healths[0].health_score, 7.9) # latest audit score: 7.0 + 9*0.1 = 7.9

    @patch("redis.Redis.from_url")
    def test_redis_cache_scenarios(self, mock_redis_from_url):
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis_from_url.return_value = mock_redis
        
        # Verify environment routing selector logic
        if DEVLENS_ENV == "production":
            from app.api.analytics import shared_store
            self.assertIsInstance(shared_store, SQLAnalyticsStore)
        else:
            from app.api.analytics import shared_store
            self.assertIsInstance(shared_store, InMemoryAnalyticsStore)
