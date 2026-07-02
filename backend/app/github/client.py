import time
import base64
import asyncio
import httpx
import jwt
from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.core.config import GITHUB_TOKEN, GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY
from app.core.logging import logger

def generate_app_jwt() -> str:
    """Generates a signed JWT for authenticating as the GitHub App."""
    if not GITHUB_APP_ID or not GITHUB_APP_PRIVATE_KEY:
        raise ValueError("GitHub App configuration is missing GITHUB_APP_ID or GITHUB_APP_PRIVATE_KEY.")

    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),  # 10 minutes expiry
        "iss": int(GITHUB_APP_ID)
    }
    
    # Clean the private key structure if formatted with escaped newlines
    key_pem = GITHUB_APP_PRIVATE_KEY.replace("\\n", "\n")
    return jwt.encode(payload, key_pem, algorithm="RS256")

async def get_installation_access_token(installation_id: int) -> str:
    """Exchanges a signed App JWT for an Installation Access Token."""
    app_jwt = generate_app_jwt()
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers)
        if response.status_code != 201:
            logger.error(f"Failed to generate installation token: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Invalid GitHub App installation token configuration.")
        return response.json().get("token")

class GitHubClient:
    def __init__(self, installation_id: Optional[int] = None, oauth_token: Optional[str] = None):
        self.installation_id = installation_id
        self.oauth_token = oauth_token

    async def get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        # Determine authentication strategy automatically
        if self.oauth_token:
            headers["Authorization"] = f"Bearer {self.oauth_token}"
        elif self.installation_id:
            token = await get_installation_access_token(self.installation_id)
            headers["Authorization"] = f"token {token}"
        elif GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
            
        return headers

    async def fetch(self, owner: str, repo: str) -> Dict[str, Any]:
        headers = await self.get_headers()
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                meta_url = f"https://api.github.com/repos/{owner}/{repo}"
                readme_url = f"{meta_url}/readme"
                contents_url = f"{meta_url}/contents"

                tasks = [
                    client.get(meta_url, headers=headers),
                    client.get(readme_url, headers=headers),
                    client.get(contents_url, headers=headers)
                ]
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Check Metadata
                meta_res = responses[0]
                if isinstance(meta_res, Exception) or meta_res.status_code == 404:
                    raise HTTPException(status_code=404, detail="Repository not found or private.")
                if meta_res.status_code == 403:
                    raise HTTPException(status_code=403, detail="Rate limit exceeded or permission failure on GitHub.")
                
                meta = meta_res.json()
                
                # Safe Readme Fetching
                readme = ""
                readme_res = responses[1]
                if not isinstance(readme_res, Exception) and readme_res.status_code == 200:
                    try:
                        readme = base64.b64decode(readme_res.json().get('content', '')).decode('utf-8', errors='ignore')
                    except Exception:
                        readme = "Error decoding README."

                # Safe Structure Fetching
                files = []
                cont_res = responses[2]
                if not isinstance(cont_res, Exception) and cont_res.status_code == 200:
                    data = cont_res.json()
                    files = [f['name'] for f in data] if isinstance(data, list) else []

                return {
                    "name": meta.get("name"),
                    "stars": meta.get("stargazers_count", 0),
                    "last_updated": meta.get("updated_at", ""),
                    "readme": readme[:3500],
                    "files": files[:20]
                }
            except httpx.HTTPError:
                raise HTTPException(status_code=502, detail="Upstream GitHub API failure.")
