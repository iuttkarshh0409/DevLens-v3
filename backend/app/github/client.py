import time
import base64
import asyncio
import httpx
import jwt
import datetime
import calendar
import threading
from typing import Dict, Any, Optional
from app.core.config import GITHUB_TOKEN, GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY
from app.core.logging import logger
from app.core.exceptions import GitHubApiException
from app.core.context import RequestContext
from app.models.github import RepositorySnapshot

# Thread-safe and asyncio-safe Installation Access Token Cache
_token_cache = {}  # {installation_id: {"token": token, "expires_at": expires_epoch}}
_cache_lock = asyncio.Lock()
_thread_lock = threading.Lock()

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
    
    key_pem = GITHUB_APP_PRIVATE_KEY.replace("\\n", "\n")
    return jwt.encode(payload, key_pem, algorithm="RS256")

async def get_installation_access_token(installation_id: int) -> str:
    """Exchanges a signed App JWT for an Installation Access Token, utilizing an in-memory cache."""
    now_epoch = int(time.time())
    
    # 1. Thread-safe read fast path
    with _thread_lock:
        cached = _token_cache.get(installation_id)
        if cached:
            # Reuse cached token if remaining lifetime is >= 60 seconds
            if cached["expires_at"] - now_epoch >= 60:
                return cached["token"]

    # 2. Asyncio-safe lock check path
    async with _cache_lock:
        with _thread_lock:
            cached = _token_cache.get(installation_id)
            if cached and cached["expires_at"] - int(time.time()) >= 60:
                return cached["token"]

        # Fetch new token
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
                raise GitHubApiException(status_code=response.status_code, message="Invalid installation access token request.")
            
            res_data = response.json()
            token = res_data.get("token")
            expires_at_str = res_data.get("expires_at")
            expires_epoch = now_epoch + 3600  # 1 hour fallback
            
            if expires_at_str:
                try:
                    # Parse expires_at ISO string (e.g. 2026-07-03T21:09:41Z)
                    expires_dt = datetime.datetime.strptime(expires_at_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
                    expires_epoch = calendar.timegm(expires_dt.utctimetuple())
                except Exception:
                    pass

            with _thread_lock:
                _token_cache[installation_id] = {
                    "token": token,
                    "expires_at": expires_epoch
                }
            return token


class GitHubClient:
    def __init__(self, installation_id: Optional[int] = None, oauth_token: Optional[str] = None, context: Optional[RequestContext] = None):
        self.installation_id = installation_id
        self.oauth_token = oauth_token
        self.context = context or RequestContext()

    async def get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-Request-ID": self.context.request_id
        }
        
        # Determine authentication strategy automatically
        if self.oauth_token:
            headers["Authorization"] = f"Bearer {self.oauth_token}"
        elif self.installation_id:
            token = await get_installation_access_token(self.installation_id)
            headers["Authorization"] = f"token {token}"
        elif GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
            
        return headers

    async def fetch(self, owner: str, repo: str, context: Optional[RequestContext] = None) -> RepositorySnapshot:
        if context:
            self.context = context
            
        headers = await self.get_headers()
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # 1. Fetch main repo metadata to find default branch
                meta_url = f"https://api.github.com/repos/{owner}/{repo}"
                meta_res = await client.get(meta_url, headers=headers)
                
                if meta_res.status_code == 404:
                    raise GitHubApiException(status_code=404, message="Repository not found or private.")
                if meta_res.status_code == 403:
                    raise GitHubApiException(status_code=403, message="Rate limit exceeded or permission failure on GitHub.")
                if meta_res.status_code != 200:
                    raise GitHubApiException(status_code=meta_res.status_code, message="Failed to fetch repository metadata.")
                
                meta = meta_res.json()
                default_branch = meta.get("default_branch", "main")
                
                # 2. Fetch README and Recursive Git Tree in parallel
                readme_url = f"{meta_url}/readme"
                tree_url = f"{meta_url}/git/trees/{default_branch}?recursive=1"
                
                tasks = [
                    client.get(readme_url, headers=headers),
                    client.get(tree_url, headers=headers)
                ]
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Decode Readme
                readme = ""
                readme_res = responses[0]
                if not isinstance(readme_res, Exception) and readme_res.status_code == 200:
                    try:
                        readme = base64.b64decode(readme_res.json().get('content', '')).decode('utf-8', errors='ignore')
                    except Exception:
                        readme = "Error decoding README."

                # Parse Recursive Git Tree files
                files = []
                tree_res = responses[1]
                if not isinstance(tree_res, Exception) and tree_res.status_code == 200:
                    tree_data = tree_res.json()
                    # Filter items that are files (type 'blob') and append their full paths
                    items = tree_data.get("tree", [])
                    files = [item["path"] for item in items if item.get("type") == "blob"]
                else:
                    # Fallback to flat contents if trees API failed or was empty
                    contents_url = f"{meta_url}/contents"
                    cont_res = await client.get(contents_url, headers=headers)
                    if cont_res.status_code == 200:
                        data = cont_res.json()
                        files = [f['name'] for f in data] if isinstance(data, list) else []

                devlens_config = None
                raw_files_content = {}
                
                # Fetch config
                config_path = next((f for f in files if f.lower() in [".devlens.yml", ".devlens.yaml"]), None)
                if config_path:
                    try:
                        devlens_config = await self.fetch_file_content(owner, repo, config_path, ref=default_branch)
                    except Exception:
                        pass

                # Fetch key files for annotations
                for path in files:
                    if "dockerfile" in path.lower() or path.endswith("package.json") or ".github/workflows" in path.lower():
                        if len(raw_files_content) < 5:
                            try:
                                content = await self.fetch_file_content(owner, repo, path, ref=default_branch)
                                raw_files_content[path] = content
                            except Exception:
                                pass

                return RepositorySnapshot(
                    name=meta.get("name", "Unknown"),
                    stars=meta.get("stargazers_count", 0),
                    last_updated=meta.get("updated_at", ""),
                    readme=readme[:3500],
                    files=files,
                    devlens_config=devlens_config,
                    raw_files_content=raw_files_content
                )
            except httpx.HTTPError as he:
                raise GitHubApiException(status_code=502, message=f"Upstream network failure: {str(he)}")

    async def create_check_run(self, owner: str, repo: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a check run on the target repository."""
        headers = await self.get_headers()
        url = f"https://api.github.com/repos/{owner}/{repo}/check-runs"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 201:
                logger.error(f"Failed to create check run: {response.text}")
                raise GitHubApiException(status_code=response.status_code, message="Check run creation failure.")
            return response.json()

    async def update_check_run(self, owner: str, repo: str, check_run_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing check run."""
        headers = await self.get_headers()
        url = f"https://api.github.com/repos/{owner}/{repo}/check-runs/{check_run_id}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.patch(url, headers=headers, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to update check run: {response.text}")
                raise GitHubApiException(status_code=response.status_code, message="Check run update failure.")
            return response.json()

    async def create_pr_review(self, owner: str, repo: str, pull_number: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a pull request review with annotations/comments."""
        headers = await self.get_headers()
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to submit PR review: {response.text}")
                raise GitHubApiException(status_code=response.status_code, message="PR review creation failure.")
            return response.json()

    async def post_commit_status(self, owner: str, repo: str, sha: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a commit status mapping to a target SHA."""
        headers = await self.get_headers()
        url = f"https://api.github.com/repos/{owner}/{repo}/statuses/{sha}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 201:
                logger.error(f"Failed to post commit status: {response.text}")
                raise GitHubApiException(status_code=response.status_code, message="Commit status creation failure.")
            return response.json()

    async def fetch_file_content(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> str:
        """Fetches the raw text content of a file from a repository at a specific ref."""
        headers = await self.get_headers()
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        if ref:
            url += f"?ref={ref}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise GitHubApiException(status_code=response.status_code, message=f"Failed to fetch file content for {path}.")
            
            try:
                data = response.json()
                content_b64 = data.get("content", "")
                return base64.b64decode(content_b64).decode("utf-8", errors="ignore")
            except Exception:
                return ""

