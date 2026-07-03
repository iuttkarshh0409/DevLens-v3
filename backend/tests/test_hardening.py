import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch

from app.ai.prompt import PromptBuilder
from app.scoring.config import ScoringConfig
from app.core.context import RequestContext
from app.core.exceptions import DevLensException, GitHubApiException, ProviderApiException, AnalysisException, ValidationException
from app.rie.orchestrator import AnalysisOrchestrator
from app.rie.base import BaseAnalyzer, AnalyzerContext
from app.rie.registry import registry
from app.models.analysis import AnalyzerResult, EvidenceGraph, RepositoryMetadata, RepositoryAnalysis
from app.models.github import RepositorySnapshot


class TestPromptBuilder(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_prompt_builder_loads_markdown(self):
        # Create system.md and recruiter.md
        with open(os.path.join(self.test_dir, "system.md"), "w", encoding="utf-8") as f:
            f.write("# System Prompt\nRun analysis rules.")
        with open(os.path.join(self.test_dir, "recruiter.md"), "w", encoding="utf-8") as f:
            f.write("# Recruiter Prompt\nGenerate recruiting insights.")

        builder = PromptBuilder(prompts_dir=self.test_dir)
        self.assertEqual(builder.get_system_prompt(), "# System Prompt\nRun analysis rules.")
        
        user_prompt = builder.get_user_prompt("recruiter", {"repo": "test"})
        self.assertIn("# Recruiter Prompt\nGenerate recruiting insights.", user_prompt)
        self.assertIn("recruiter", user_prompt)

    def test_prompt_builder_missing_fallback(self):
        builder = PromptBuilder(prompts_dir=self.test_dir)
        self.assertEqual(builder.get_system_prompt(), "System prompt instruction.")
        user_prompt = builder.get_user_prompt("unknown_role", {})
        self.assertIn("System prompt instruction.", user_prompt)


class TestScoringConfig(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.profile_path = os.path.join(self.test_dir, "profile.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_scoring_config_loads_json(self):
        config_data = {
            "version": "4.0.0",
            "base_score": 3.0,
            "max_score": 12.0,
            "weights": {
                "TESTING": 3.0,
                "CICD": 2.5
            },
            "caps": {
                "CUSTOM_CAP": 6.5
            }
        }
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        config = ScoringConfig(profile_path=self.profile_path)
        self.assertEqual(config.version, "4.0.0")
        self.assertEqual(config.base_score, 3.0)
        self.assertEqual(config.max_score, 12.0)
        self.assertEqual(config.get_weight("TESTING"), 3.0)
        self.assertEqual(config.get_weight("SECURITY"), 1.0)  # Default fallback weight
        self.assertEqual(config.get_cap("CUSTOM_CAP"), 6.5)
        self.assertEqual(config.get_cap("MISSING_TESTS_OR_CICD"), 7.0)  # Default fallback cap

    def test_scoring_config_fallback_when_missing(self):
        config = ScoringConfig(profile_path="/nonexistent/path.json")
        self.assertEqual(config.version, "V3.0")
        self.assertEqual(config.base_score, 5.0)
        self.assertEqual(config.get_weight("DOCUMENTATION"), 1.5)
        self.assertEqual(config.get_cap("MISSING_TESTS_OR_CICD"), 7.0)


class TestRequestContext(unittest.TestCase):
    def test_request_context_defaults(self):
        ctx = RequestContext()
        self.assertIsNotNone(ctx.request_id)
        self.assertIsNotNone(ctx.audit_id)
        self.assertIsNone(ctx.installation_id)
        self.assertIsNone(ctx.user_id)
        self.assertIsNone(ctx.github_delivery_id)
        self.assertGreater(ctx.start_time, 0.0)
        self.assertEqual(ctx.trace_metadata, {})

    def test_request_context_propagation(self):
        ctx = RequestContext(
            request_id="req_123",
            audit_id="aud_456",
            installation_id=9876,
            user_id="user_abc",
            github_delivery_id="delivery_xyz",
            trace_metadata={"env": "test"}
        )
        self.assertEqual(ctx.request_id, "req_123")
        self.assertEqual(ctx.audit_id, "aud_456")
        self.assertEqual(ctx.installation_id, 9876)
        self.assertEqual(ctx.user_id, "user_abc")
        self.assertEqual(ctx.github_delivery_id, "delivery_xyz")
        self.assertEqual(ctx.trace_metadata, {"env": "test"})


class TestExceptions(unittest.TestCase):
    def test_exceptions_inheritance(self):
        self.assertTrue(issubclass(GitHubApiException, DevLensException))
        self.assertTrue(issubclass(ProviderApiException, DevLensException))
        self.assertTrue(issubclass(AnalysisException, DevLensException))
        self.assertTrue(issubclass(ValidationException, DevLensException))

        gh_ex = GitHubApiException(status_code=403, message="Rate limit exceeded")
        self.assertEqual(gh_ex.status_code, 403)
        self.assertEqual(gh_ex.message, "Rate limit exceeded")
        self.assertIn("GitHub API Error [403]: Rate limit exceeded", str(gh_ex))

        prov_ex = ProviderApiException(message="Timeout calling OpenAI")
        self.assertEqual(prov_ex.message, "Timeout calling OpenAI")
        self.assertIn("AI Provider Error: Timeout calling OpenAI", str(prov_ex))


class BadAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "BadAnalyzer"

    @property
    def priority(self) -> int:
        return 100

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        raise ValueError("Simulated analyzer exception")


class GoodAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "GoodAnalyzer"

    @property
    def priority(self) -> int:
        return 10

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        return AnalyzerResult(analyzer_name=self.name, passed=True, evidence={"status": "ok"})


class TestOrchestratorSandboxing(unittest.TestCase):
    def test_sandboxed_orchestrator_execution(self):
        # We temporarily mock registry.get_analyzers to return both a Good and Bad Analyzer
        good = GoodAnalyzer()
        bad = BadAnalyzer()
        
        with patch.object(registry, "get_analyzers", return_value=[good, bad]):
            repo_snapshot = RepositorySnapshot(
                name="test-repo",
                stars=42,
                last_updated="2026-07-03T19:00:00Z",
                readme="Hello World",
                files=["README.md"]
            )
            
            ctx = RequestContext(request_id="test_sandbox_req")
            analysis: RepositoryAnalysis = AnalysisOrchestrator.run_analysis(repo_snapshot, request_context=ctx)
            
            self.assertEqual(analysis.repo_name, "test-repo")
            self.assertEqual(len(analysis.results), 2)
            self.assertTrue(analysis.results["GoodAnalyzer"].passed)
            self.assertFalse(analysis.results["BadAnalyzer"].passed)
            self.assertEqual(len(analysis.warnings), 1)
            self.assertIn("Analyzer BadAnalyzer failed: Simulated analyzer exception", analysis.warnings[0])


if __name__ == "__main__":
    unittest.main()
