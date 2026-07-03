import unittest
import time
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
import redis

# App imports
from app.core.config_loader import load_repository_policy
from app.services.insights_service import RepositoryInsightsService
from app.services.annotation_engine import RepositoryAnnotationEngine
from app.models.analysis import EvidenceGraph, RepositoryMetadata, RepositoryAnalysis, AnalyzerResult
from app.services.github.checks_service import ChecksService
from app.services.github.pr_review_service import PRReviewService
from app.services.github.status_service import StatusService
from app.api.badges import generate_svg_badge
from app.github.client import get_installation_access_token, _token_cache
from app.jobs.queue import RedisQueue, InMemoryQueue, RedisCircuitBreaker, AuditJob, JobStatus
from app.webhooks.router import verify_signature


class TestConfigLoader(unittest.TestCase):
    def test_default_config_fallback(self):
        policy = load_repository_policy(None)
        self.assertEqual(policy.api_version, "devlens.io/v1")
        self.assertEqual(policy.kind, "RepositoryPolicy")
        self.assertEqual(policy.enabled_analyzers, [])
        self.assertEqual(policy.weights, {})
        self.assertEqual(policy.ignored_paths, [])

    def test_valid_yaml_parsing(self):
        yaml_content = """
apiVersion: devlens.io/v1
kind: RepositoryPolicy
spec:
  analysis:
    enabledAnalyzers:
      - LicenseAnalyzer
  scoring:
    weights:
      TESTING: 2.0
    caps:
      MISSING_TESTS_OR_CICD: 8.0
  ignore:
    paths:
      - "**/fixtures/**"
"""
        policy = load_repository_policy(yaml_content)
        self.assertEqual(policy.api_version, "devlens.io/v1")
        self.assertEqual(policy.kind, "RepositoryPolicy")
        self.assertEqual(policy.enabled_analyzers, ["LicenseAnalyzer"])
        self.assertEqual(policy.weights, {"TESTING": 2.0})
        self.assertEqual(policy.caps, {"MISSING_TESTS_OR_CICD": 8.0})
        self.assertEqual(policy.ignored_paths, ["**/fixtures/**"])


class TestInsightsService(unittest.TestCase):
    def test_tech_stack_detection(self):
        meta = RepositoryMetadata(name="TestRepo", stars=10, last_updated="2026-07-03T19:00:00Z")
        graph = EvidenceGraph(
            metadata=meta,
            files=[
                "package.json",
                "package-lock.json",
                "requirements.txt",
                "main.py",
                "Dockerfile",
                ".github/workflows/ci.yml",
                "tests/test_app.py",
                "vercel.json"
            ],
            readme="Contains React and FastAPI setups. Runs pytest."
        )
        insights = RepositoryInsightsService.extract_insights(graph)
        self.assertIn("React", insights["frontend"])
        self.assertIn("FastAPI", insights["backend"])
        self.assertIn("GitHub Actions", insights["ci"])
        self.assertIn("Pytest", insights["testing"])
        self.assertIn("Docker", insights["containerization"])
        self.assertIn("pip", insights["package_managers"])
        self.assertIn("npm", insights["package_managers"])
        self.assertIn("Vercel", insights["deployment"])
        self.assertEqual(insights["architecture"], "Standard")

    def test_expanded_stack_ecosystems(self):
        meta = RepositoryMetadata(name="TestRepo", stars=5, last_updated="2026-07-03T19:00:00Z")
        graph = EvidenceGraph(
            metadata=meta,
            files=[
                "pom.xml",
                "Cargo.toml",
                "go.mod",
                "composer.json",
                "bun.lockb",
                "turbo.json",
                "nx.json",
                "pnpm-workspace.yaml",
                "compose.yaml",
                "devcontainer.json"
            ],
            readme="Rust Cargo project with Go modules and Bun workspaces."
        )
        insights = RepositoryInsightsService.extract_insights(graph)
        # Verify ecosystem detections
        self.assertIn("maven", insights["package_managers"])
        self.assertIn("cargo", insights["package_managers"])
        self.assertIn("go", insights["package_managers"])
        self.assertIn("composer", insights["package_managers"])
        self.assertIn("bun", insights["package_managers"])
        self.assertIn("Spring Boot", insights["backend"])
        self.assertIn("Rust Cargo", insights["backend"])
        self.assertIn("Go Modules", insights["backend"])
        self.assertIn("Docker Compose", insights["containerization"])
        self.assertIn("devcontainer", insights["containerization"])
        self.assertEqual(insights["architecture"], "Monorepo")


class TestAnnotationEngine(unittest.TestCase):
    def test_annotations_mapping(self):
        meta = RepositoryMetadata(name="TestRepo", stars=10, last_updated="2026-07-03T19:00:00Z")
        graph = EvidenceGraph(metadata=meta, files=["README.md"], readme="minimal readme")
        analysis = RepositoryAnalysis(
            repo_name="TestRepo",
            evidence_graph=graph,
            results={
                "LicenseAnalyzer": AnalyzerResult(analyzer_name="LicenseAnalyzer", passed=False, evidence={}),
                "ReadmeAnalyzer": AnalyzerResult(analyzer_name="ReadmeAnalyzer", passed=True, evidence={"has_setup_instructions": False, "has_visual_demos": False}),
                "CICDAnalyzer": AnalyzerResult(analyzer_name="CICDAnalyzer", passed=False, evidence={}),
                "TestingAnalyzer": AnalyzerResult(analyzer_name="TestingAnalyzer", passed=False, evidence={})
            }
        )
        raw_files = {
            "Dockerfile": "FROM python:latest\nCOPY . .\nCMD python main.py",
            "package.json": '{\n  "dependencies": {\n    "express": "*"\n  }\n}'
        }
        annotations = RepositoryAnnotationEngine.generate_annotations(analysis, raw_files)
        repo_levels = [a for a in annotations if a.level == "repository"]
        self.assertTrue(any(a.rule_id == "RULE_001_LICENSE_EXISTS" for a in repo_levels))
        
        line_levels = [a for a in annotations if a.level == "line"]
        latest_anno = next((a for a in line_levels if a.rule_id == "LINE_RULE_DOCKER_LATEST"), None)
        self.assertIsNotNone(latest_anno)
        self.assertEqual(latest_anno.start_line, 1)


class TestWebhookSecurityHardening(unittest.TestCase):
    @patch("app.webhooks.router.GITHUB_WEBHOOK_SECRET", None)
    @patch("app.webhooks.router.DEVLENS_ENV", "production")
    def test_fail_closed_missing_secret_in_production(self):
        with self.assertRaises(HTTPException) as cm:
            verify_signature(b"payload_body", "sha256=signature")
        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn("Webhook secret is missing", cm.exception.detail)

    @patch("app.webhooks.router.GITHUB_WEBHOOK_SECRET", None)
    @patch("app.webhooks.router.DEVLENS_ENV", "development")
    def test_bypass_missing_secret_in_development(self):
        # Should execute successfully and return None (no exception raised)
        res = verify_signature(b"payload_body", None)
        self.assertIsNone(res)


class TestRedisResilience(unittest.TestCase):
    def test_circuit_breaker_transition(self):
        cb = RedisCircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
        self.assertTrue(cb.can_execute())
        
        # Record failures
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.state, "CLOSED")
        
        cb.record_failure()
        self.assertEqual(cb.state, "OPEN")
        self.assertFalse(cb.can_execute())
        
        # Wait for recovery timeout
        time.sleep(0.12)
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.state, "HALF-OPEN")
        
        # Test success closes the circuit
        cb.record_success()
        self.assertEqual(cb.state, "CLOSED")

    @patch("redis.Redis")
    def test_redis_failure_fallback_degradation(self, mock_redis_cls):
        # Configure mock to throw ConnectionError on ping
        mock_redis = Mock()
        mock_redis.ping.side_effect = redis.ConnectionError("Outage")
        mock_redis_cls.return_value = mock_redis
        
        # Initialize queue (in development mode, should active=False, fallback=InMemoryQueue)
        queue = RedisQueue(host="localhost", port=6379)
        self.assertFalse(queue.active)
        self.assertIsNotNone(queue.fallback)
        
        # Verify fallback works gracefully
        job = AuditJob(job_id="job_resilient", repo_data={"name": "test"})
        queue.enqueue(job)
        self.assertEqual(queue.status("job_resilient"), JobStatus.PENDING)


class TestInstallationTokenCaching(unittest.IsolatedAsyncioTestCase):
    async def test_token_caching_and_refresh(self):
        # Pre-populate token cache with an active token
        now = int(time.time())
        _token_cache[9999] = {
            "token": "cached_active_token",
            "expires_at": now + 600  # 10 minutes remaining
        }
        
        token = await get_installation_access_token(9999)
        self.assertEqual(token, "cached_active_token")

    @patch("app.github.client.generate_app_jwt")
    @patch("httpx.AsyncClient.post")
    async def test_token_refresh_under_60_seconds(self, mock_post, mock_jwt):
        # Cached token with 30 seconds left (under 60 seconds threshold)
        now = int(time.time())
        _token_cache[8888] = {
            "token": "nearly_expired_token",
            "expires_at": now + 30
        }
        
        # Mock HTTP success for new token
        mock_jwt.return_value = "mock_jwt"
        mock_res = Mock()
        mock_res.status_code = 201
        mock_res.json.return_value = {
            "token": "refreshed_token",
            "expires_at": "2026-07-03T21:00:00Z"
        }
        mock_post.return_value = mock_res
        
        token = await get_installation_access_token(8888)
        self.assertEqual(token, "refreshed_token")
        self.assertEqual(_token_cache[8888]["token"], "refreshed_token")


class TestAnnotationChunking(unittest.IsolatedAsyncioTestCase):
    async def test_checks_service_payload_chunking(self):
        client = AsyncMock()
        client.create_check_run.return_value = {"id": 1234}
        client.update_check_run.return_value = {"status": "completed"}
        
        checks_svc = ChecksService(client)
        
        # Mock RepositoryAnalysis with 55 annotations
        meta = RepositoryMetadata(name="TestRepo", stars=1, last_updated="2026-07-03T19:00:00Z")
        graph = EvidenceGraph(metadata=meta, files=["README.md"], readme="setup info")
        analysis = RepositoryAnalysis(
            repo_name="TestRepo",
            evidence_graph=graph,
            results={
                "ReadmeAnalyzer": AnalyzerResult(
                    analyzer_name="ReadmeAnalyzer", 
                    passed=True, 
                    # Ensure failures triggers many annotations
                    evidence={"has_setup_instructions": False, "has_visual_demos": False}
                )
            }
        )
        
        # Prepare large annotations list to trigger multi-batch (Create mock annotations)
        annotations = [
            AnalyzerResult(analyzer_name="ReadmeAnalyzer", passed=True, evidence={"has_setup_instructions": False, "has_visual_demos": False})
        ]
        
        # We call complete_check with a mock raw files listing that contains many wildcard dependencies
        raw_files = {
            "package.json": '{\n  "dependencies": {\n' + ",\n".join(f'    "dep_{i}": "*"' for i in range(53)) + "\n  }\n}"
        }
        
        await checks_svc.complete_check("owner", "repo", 1234, analysis, 8.0, raw_files)
        
        # Verify it updated the check run twice (1 main, 1 subsequent patch batch)
        self.assertEqual(client.update_check_run.call_count, 2)
        
        # Verify first batch had max 50 annotations
        args1, kwargs1 = client.update_check_run.call_args_list[0]
        payload1 = kwargs1.get("payload") or args1[3]
        self.assertEqual(len(payload1["output"]["annotations"]), 50)
        
        # Verify second batch has 5 annotations (53 dependencies + README failures - 50 = remaining)
        args2, kwargs2 = client.update_check_run.call_args_list[1]
        payload2 = kwargs2.get("payload") or args2[3]
        self.assertLessEqual(len(payload2["output"]["annotations"]), 5)


if __name__ == "__main__":
    unittest.main()
