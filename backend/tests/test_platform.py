import unittest
from unittest.mock import Mock, AsyncMock, patch
from app.core.config_loader import load_repository_policy, RepositoryPolicyConfig
from app.services.insights_service import RepositoryInsightsService
from app.services.annotation_engine import RepositoryAnnotationEngine, RepositoryAnnotation
from app.models.analysis import EvidenceGraph, RepositoryMetadata, RepositoryAnalysis, AnalyzerResult
from app.services.github.checks_service import ChecksService
from app.services.github.pr_review_service import PRReviewService
from app.services.github.status_service import StatusService
from app.api.badges import generate_svg_badge


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

    def test_invalid_version_ignored(self):
        yaml_content = """
apiVersion: invalid/v1
kind: RepositoryPolicy
spec:
  scoring:
    weights:
      TESTING: 3.0
"""
        policy = load_repository_policy(yaml_content)
        self.assertEqual(policy.weights, {})  # Fallback to default empty config


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


class TestAnnotationEngine(unittest.TestCase):
    def test_annotations_mapping(self):
        # Mock a failed repo analysis
        meta = RepositoryMetadata(name="TestRepo", stars=10, last_updated="2026-07-03T19:00:00Z")
        graph = EvidenceGraph(metadata=meta, files=["README.md"], readme="minimal readme")
        
        # Missing license, testing, CI, docker
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
        
        # Verify repository-level annotations
        repo_levels = [a for a in annotations if a.level == "repository"]
        self.assertTrue(any(a.rule_id == "RULE_001_LICENSE_EXISTS" for a in repo_levels))
        self.assertTrue(any(a.rule_id == "RULE_004_CICD_WORKFLOWS" for a in repo_levels))

        # Verify line-level annotations
        line_levels = [a for a in annotations if a.level == "line"]
        
        # Latest tag check
        latest_anno = next((a for a in line_levels if a.rule_id == "LINE_RULE_DOCKER_LATEST"), None)
        self.assertIsNotNone(latest_anno)
        self.assertEqual(latest_anno.start_line, 1)
        self.assertEqual(latest_anno.path, "Dockerfile")

        # Wildcard dependency check
        wildcard_anno = next((a for a in line_levels if a.rule_id == "LINE_RULE_PACKAGE_WILDCARD"), None)
        self.assertIsNotNone(wildcard_anno)
        self.assertEqual(wildcard_anno.start_line, 3)
        self.assertEqual(wildcard_anno.path, "package.json")


class TestIntegrationServices(unittest.IsolatedAsyncioTestCase):
    async def test_checks_service_publishing(self):
        client = AsyncMock()
        client.create_check_run.return_value = {"id": 12345}
        client.update_check_run.return_value = {"status": "completed"}

        checks_svc = ChecksService(client)
        run_id = await checks_svc.create_initial_check("owner", "repo", "sha123")
        self.assertEqual(run_id, 12345)

        # Mock complete check run
        meta = RepositoryMetadata(name="TestRepo", stars=10, last_updated="2026-07-03T19:00:00Z")
        graph = EvidenceGraph(metadata=meta, files=["README.md"], readme="setup instructions")
        analysis = RepositoryAnalysis(
            repo_name="TestRepo",
            evidence_graph=graph,
            results={
                "LicenseAnalyzer": AnalyzerResult(analyzer_name="LicenseAnalyzer", passed=True, evidence={})
            }
        )

        await checks_svc.complete_check("owner", "repo", 12345, analysis, 8.5)
        
        # Verify PATCH payload parameters
        args, kwargs = client.update_check_run.call_args
        payload = kwargs.get("payload") or args[3]
        self.assertEqual(payload["conclusion"], "success")
        self.assertIn("Score: 8.5/10.0", payload["output"]["title"])

    async def test_pr_review_publishing(self):
        client = AsyncMock()
        client.create_pr_review.return_value = {"status": "submitted"}

        pr_svc = PRReviewService(client)
        meta = RepositoryMetadata(name="TestRepo", stars=10, last_updated="2026-07-03T19:00:00Z")
        graph = EvidenceGraph(metadata=meta, files=["README.md"], readme="setup instructions")
        analysis = RepositoryAnalysis(
            repo_name="TestRepo",
            evidence_graph=graph,
            results={
                "LicenseAnalyzer": AnalyzerResult(analyzer_name="LicenseAnalyzer", passed=False, evidence={})
            }
        )

        await pr_svc.submit_pr_review("owner", "repo", 42, analysis, 6.0)
        
        # Verify PR Review payload parameters
        args, kwargs = client.create_pr_review.call_args
        payload = kwargs.get("payload") or args[3]
        self.assertEqual(payload["event"], "REQUEST_CHANGES")
        self.assertIn("DevLens PR Code Audit: **6.0/10.0**", payload["body"])

    async def test_status_service_publishing(self):
        client = AsyncMock()
        client.post_commit_status.return_value = {"state": "success"}

        status_svc = StatusService(client)
        await status_svc.post_pending_status("owner", "repo", "sha123")
        
        args, kwargs = client.post_commit_status.call_args
        payload = kwargs.get("payload") or args[3]
        self.assertEqual(payload["state"], "pending")

        await status_svc.post_completion_status("owner", "repo", "sha123", 7.5)
        args, kwargs = client.post_commit_status.call_args
        payload = kwargs.get("payload") or args[3]
        self.assertEqual(payload["state"], "success")
        self.assertIn("score: 7.5/10.0", payload["description"])


class TestBadges(unittest.TestCase):
    def test_badge_svg_generation(self):
        svg = generate_svg_badge("devlens", "passed", "#4c1", "flat")
        self.assertIn("<svg", svg)
        self.assertIn("devlens", svg)
        self.assertIn("passed", svg)
        self.assertIn("fill=\"#4c1\"", svg)


if __name__ == "__main__":
    unittest.main()
