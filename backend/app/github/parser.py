import re
from typing import Tuple
from fastapi import HTTPException
from app.core.logging import logger

def parse_github_url(url: str) -> Tuple[str, str]:
    """Robustly extracts (owner, repo) from HTTPS, SSH, and path-only GitHub URLs."""
    pattern = r"(?:https?://)?(?:www\.)?github\.com[:/]([^/]+)/([^/\.\s\?#]+)(?:\.git)?(?:/.*)?"
    match = re.search(pattern, url.strip())
    
    if not match:
        logger.warning(f"Failed to parse URL: {url}")
        raise HTTPException(status_code=400, detail="Invalid GitHub URL format.")
    
    return match.group(1), match.group(2)
