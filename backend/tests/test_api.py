import unittest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

class TestAPIIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy", "service": "DevLens Analysis Engine"})

    @patch("app.github.client.GitHubClient.fetch", new_callable=AsyncMock)
    @patch("app.ai.provider.GroqProvider.generate", new_callable=AsyncMock)
    def test_analyze_endpoint_success(self, mock_generate, mock_fetch):
        # 1. Setup mock responses
        mock_fetch.return_value = {
            "name": "DevLens",
            "stars": 42,
            "last_updated": "2026-07-03",
            "readme": "## Getting Started\nmake setup",
            "files": ["package.json", "Makefile", "LICENSE"]
        }
        
        mock_generate.return_value = '{"summary": "Mock summary", "recruiter_verdict": "Mock verdict", "maturity_estimate": "Advanced", "recommendations": [], "priority_checklist": []}'

        # 2. Invoke Endpoint
        response = self.client.post("/analyze", json={"repo_url": "https://github.com/user/DevLens"})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["score"], 6.9) # Calculated score is 6.9, uncapped since < 7.0
        self.assertEqual(data["status"], "INTERVIEW")
        self.assertEqual(data["feedback"], "Mock verdict")
        self.assertIn("timings_ms", data)

    def test_analyze_endpoint_invalid_url(self):
        response = self.client.post("/analyze", json={"repo_url": "not-a-github-url"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid GitHub URL format", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
