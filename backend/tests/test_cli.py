import os
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch, Mock, AsyncMock
from typer.testing import CliRunner

from app.cli.main import app
from app.cli.exceptions import CLIException, APIConnectionError, AuthenticationError
from app.cli.commands.config import DEFAULT_DEFS, dict_to_toml
from app.cli.client import DevLensClient

runner = CliRunner()

class TestDevLensCLI(unittest.TestCase):
    def setUp(self):
        # Set up a temporary config file path for testing environment isolation
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "config.toml")
        os.environ["DEVLENS_CONFIG"] = self.config_path
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        if "DEVLENS_CONFIG" in os.environ:
            del os.environ["DEVLENS_CONFIG"]

    def test_dict_to_toml(self):
        d = {"a": "hello", "b": 12, "c": True, "d": None}
        toml_str = dict_to_toml(d)
        self.assertIn('a = "hello"', toml_str)
        self.assertIn("b = 12", toml_str)
        self.assertIn("c = true", toml_str)
        self.assertIn('d = ""', toml_str)

    def test_config_init(self):
        result = runner.invoke(app, ["config", "init"])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(self.config_path))
        
        # Verify content
        with open(self.config_path, "r") as f:
            content = f.read()
        self.assertIn("endpoint", content)
        self.assertIn("format = \"rich\"", content)

    def test_config_set_and_show(self):
        # Initialize first
        runner.invoke(app, ["config", "init"])
        
        # Set a key
        result = runner.invoke(app, ["config", "set", "endpoint", "https://api.testlens.com"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Updated configuration parameter 'endpoint' successfully.", result.output)
        
        # Set an integer key
        result_timeout = runner.invoke(app, ["config", "set", "timeout", "45"])
        self.assertEqual(result_timeout.exit_code, 0)
        
        # Show configuration
        show_result = runner.invoke(app, ["config", "show"])
        self.assertEqual(show_result.exit_code, 0)
        self.assertIn("https://api.testlens.com", show_result.output)
        self.assertIn("timeout: 45", show_result.output)

    def test_config_precedence(self):
        runner.invoke(app, ["config", "init"])
        
        # 1. Base Default Endpoint: http://localhost:8000
        # 2. File Config Override: https://api.file.com
        runner.invoke(app, ["config", "set", "endpoint", "https://api.file.com"])
        
        # Validate File config is active
        from app.cli.commands.config import get_active_config
        self.assertEqual(get_active_config()["endpoint"], "https://api.file.com")
        
        # 3. Environment Variable Override
        os.environ["DEVLENS_ENDPOINT"] = "https://api.env.com"
        self.assertEqual(get_active_config()["endpoint"], "https://api.env.com")
        
        # 4. CLI Argument Override (Passed explicitly to active lookup)
        cfg_explicit = get_active_config(cli_endpoint="https://api.cli.com")
        self.assertEqual(cfg_explicit["endpoint"], "https://api.cli.com")
        
        # Cleanup
        del os.environ["DEVLENS_ENDPOINT"]

    @patch("app.cli.client.httpx.Client")
    def test_client_retry_and_exceptions(self, mock_httpx):
        # Mock connection failure exceptions
        import httpx
        mock_client = Mock()
        mock_client.request.side_effect = httpx.ConnectError("Connection refused")
        mock_httpx.return_value.__enter__.return_value = mock_client
        
        client = DevLensClient(endpoint="http://localhost:8000")
        
        # Verify client raises connection error after retries
        with self.assertRaises(APIConnectionError):
            client.request("GET", "health")

        # Mock authentication failure (HTTP 401)
        mock_response = Mock()
        mock_response.status_code = 401
        mock_client.request.side_effect = None
        mock_client.request.return_value = mock_response
        
        with self.assertRaises(AuthenticationError):
            client.request("GET", "health")

    def test_login_and_logout(self):
        # Run login with token
        result = runner.invoke(app, ["login", "--token", "test-pat-token"])
        self.assertEqual(result.exit_code, 0)
        
        # Verify token gets encrypted in raw storage config
        from app.cli.commands.config import load_file_config, get_active_config
        raw_token = load_file_config().get("token")
        self.assertTrue(raw_token.startswith("enc:"))
        
        # Verify configuration resolution decrypts it transparently
        self.assertEqual(get_active_config()["token"], "test-pat-token")
        
        # Check whoami outputs correctly
        whoami_res = runner.invoke(app, ["whoami"])
        self.assertEqual(whoami_res.exit_code, 0)
        self.assertIn("Token:    PAT (configured)", whoami_res.output)
        
        # Run logout
        logout_res = runner.invoke(app, ["logout"])
        self.assertEqual(logout_res.exit_code, 0)
        self.assertEqual(load_file_config().get("token"), "")

    def test_offline_audit_scan(self):
        # Set up a temporary project folder to audit locally
        proj_dir = tempfile.mkdtemp()
        try:
            # Create a mock README
            with open(os.path.join(proj_dir, "README.md"), "w") as f:
                f.write("# Mock Project README\nThis is a mock project configuration.")
            # Create a mock Python file
            with open(os.path.join(proj_dir, "main.py"), "w") as f:
                f.write("import math\ndef add(a, b): return a + b")
                
            # Run offline audit
            result = runner.invoke(app, ["audit", proj_dir, "--offline", "--json"])
            self.assertEqual(result.exit_code, 0)
            
            # Find and load the JSON block cleanly
            start_idx = result.output.find("{")
            end_idx = result.output.rfind("}")
            if start_idx == -1 or end_idx == -1:
                raise ValueError(f"No JSON found in output: {result.output}")
            json_str = result.output[start_idx:end_idx+1]
            
            # Inspect output format
            data = json.loads(json_str)
            self.assertIn("metadata", data)
            self.assertIn("scorecard", data)
            score = data["scorecard"]["overall_score"]
            self.assertTrue(isinstance(score, float))
            
            # Test score-only mode
            score_res = runner.invoke(app, ["audit", proj_dir, "--offline", "--score-only"])
            self.assertEqual(score_res.exit_code, 0)
            self.assertIn(f"{score:.1f}", score_res.output)
            
        finally:
            shutil.rmtree(proj_dir)

    @patch("app.cli.commands.audit.DevLensClient")
    def test_online_audit_command(self, mock_client_class):
        mock_client = Mock()
        # Mock analyze return payload
        mock_client.request.return_value = {
            "metadata": {"repo_name": "test-repo"},
            "scorecard": {
                "overall_score": 8.5,
                "scoring_version": "3.0",
                "rule_results": [{"rule_id": "SEC_1", "description": "SSL Check", "passed": True, "points_awarded": 1.0, "max_points": 1.0}]
            },
            "execution": {"rie_completed": True, "scoring_completed": True, "narrative_completed": True},
            "duration_ms": 120
        }
        mock_client_class.return_value = mock_client
        
        result = runner.invoke(app, ["audit", "https://github.com/owner/test-repo", "--json"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("test-repo", result.output)
        self.assertIn("8.5", result.output)

    @patch("app.cli.commands.analytics.DevLensClient")
    def test_analytics_subcommands(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # 1. Overview command
        mock_client.request.return_value = {
            "total_repositories_monitored": 5,
            "score_distribution": {"high_quality": 2, "medium_quality": 2, "low_quality": 1}
        }
        res_overview = runner.invoke(app, ["analytics", "overview"])
        self.assertEqual(res_overview.exit_code, 0)
        self.assertIn("Total Repositories: 5", res_overview.output)
        
        # 2. Trends command
        mock_client.request.return_value = {
            "trends": [{"period_start": "2026-06-01", "value": 7.8, "audit_count": 3}]
        }
        res_trends = runner.invoke(app, ["analytics", "trends"])
        self.assertEqual(res_trends.exit_code, 0)
        self.assertIn("7.80", res_trends.output)
        
        # 3. Repositories command
        mock_client.request.return_value = {
            "total_count": 1,
            "data": [{"repository_id": "123/repo", "repo_name": "repo", "health_score": 8.0, "last_audit": "2026-06-01T12:00:00", "risk_level": "low"}]
        }
        res_repos = runner.invoke(app, ["analytics", "repositories"])
        self.assertEqual(res_repos.exit_code, 0)
        self.assertIn("123/repo", res_repos.output)

    @patch("app.cli.commands.version.DevLensClient")
    def test_version_output_format(self, mock_client_class):
        mock_client = Mock()
        mock_client.request.return_value = {"status": "healthy", "service": "DevLens Backend"}
        mock_client_class.return_value = mock_client
        
        result = runner.invoke(app, ["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("DevLens CLI 3.0.0", result.output)
        self.assertIn("Server:", result.output)
        self.assertIn("DevLens Backend 3.0.0", result.output)
        self.assertIn("API:\nv1", result.output)
