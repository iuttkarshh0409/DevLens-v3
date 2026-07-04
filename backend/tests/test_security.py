import unittest
import os
import httpx
from unittest.mock import AsyncMock, MagicMock
from app.cli.security import encrypt_token, decrypt_token
from app.github.client import GitHubClient, GitHubApiException

class TestSecurityRC1(unittest.IsolatedAsyncioTestCase):
    def test_fernet_encryption_and_decryption(self):
        token = "ghp_secure_personal_access_token_12345"
        encrypted = encrypt_token(token)
        self.assertTrue(encrypted.startswith("enc:"))
        
        decrypted = decrypt_token(encrypted)
        self.assertEqual(decrypted, token)
        
        # Test fallback / plaintext compatibility
        self.assertEqual(decrypt_token(token), token)

    def test_production_cors_unconfigured_fails(self):
        # Setting production mode without allowed origins should raise a ValueError
        os.environ["DEVLENS_ENV"] = "production"
        os.environ["ALLOWED_ORIGINS"] = ""
        
        # Verify ValueError is raised upon module load/re-triggering config verification
        with self.assertRaises(ValueError):
            # Reloading configuration settings triggers check
            import importlib
            import app.core.config
            importlib.reload(app.core.config)
            
        # Restore environment settings
        os.environ["DEVLENS_ENV"] = "development"
        importlib.reload(app.core.config)

    async def test_github_rate_limiting_backoff(self):
        client_mock = AsyncMock()
        
        # Create a mock response with rate limit headers exhausted
        res_mock = MagicMock(spec=httpx.Response)
        res_mock.status_code = 403
        res_mock.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "9999999999", # Big epoch time to force exception if sleep exceeds 60s
            "Retry-After": "1" # Force retry using sleep_sec=1
        }
        
        # Next call returns success
        res_success = MagicMock(spec=httpx.Response)
        res_success.status_code = 200
        res_success.headers = {"X-RateLimit-Remaining": "5000"}
        
        client_mock.request.side_effect = [res_mock, res_success]
        
        gh_client = GitHubClient(oauth_token="test_tok")
        # Run request mapping
        response = await gh_client.request_api(client_mock, "GET", "https://api.github.com/user")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client_mock.request.call_count, 2)
