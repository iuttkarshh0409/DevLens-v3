import time
import httpx
import uuid
from typing import Dict, Any, Optional

from app.cli.exceptions import APIConnectionError, AuthenticationError, CLIException
from app.cli.commands.config import get_active_config

class DevLensClient:
    def __init__(
        self,
        endpoint: Optional[str] = None,
        token: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        cfg = get_active_config(cli_endpoint=endpoint, cli_token=token, cli_timeout=timeout)
        self.endpoint = cfg["endpoint"].rstrip("/")
        self.token = cfg["token"]
        self.timeout = cfg["timeout"]
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "DevLens-CLI/1.0.0"
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Execute request with retry loops and translation logic.
        """
        url = f"{self.endpoint}/{path.lstrip('/')}"
        
        # Inject unique request ID
        req_headers = {**self.headers, "X-Request-ID": f"cli-{uuid.uuid4()}"}
        
        last_ex = None
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.request(
                        method=method,
                        url=url,
                        headers=req_headers,
                        json=json_data,
                        params=params
                    )
                    
                # Handle status translations
                if response.status_code in (401, 403):
                    raise AuthenticationError("Active authentication credentials are invalid or expired.")
                elif response.status_code >= 500:
                    # Retry on server error
                    last_ex = CLIException(f"Server error: {response.status_code} | {response.text}", exit_code=6)
                elif response.status_code >= 400:
                    raise CLIException(f"API Error ({response.status_code}): {response.text}", exit_code=7)
                else:
                    return response.json()
                    
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
                last_ex = APIConnectionError(f"Unable to connect to active endpoint '{self.endpoint}': {str(e)}")
            except (AuthenticationError, CLIException) as e:
                # Do not retry on auth/client errors
                raise e
            
            # Backoff before retrying
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                
        # If we reach here, retry loop failed
        if last_ex:
            raise last_ex
        raise CLIException("Request failed permanently.")
