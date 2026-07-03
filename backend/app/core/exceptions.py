class DevLensException(Exception):
    """Base exception for all DevLens errors."""
    pass

class GitHubApiException(DevLensException):
    """Raised when upstream GitHub API requests fail, timeout, or return errors."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"GitHub API Error [{status_code}]: {message}")

class ProviderApiException(DevLensException):
    """Raised when third-party AI provider requests fail or timeout."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"AI Provider Error: {message}")

class AnalysisException(DevLensException):
    """Raised during repository intelligence extraction or rule score calculation."""
    pass

class ValidationException(DevLensException):
    """Raised when request payload or signature parsing checks fail."""
    pass
