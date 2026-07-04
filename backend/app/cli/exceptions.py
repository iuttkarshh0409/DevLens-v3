class CLIException(Exception):
    """Base exception for all DevLens CLI errors."""
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code

class APIConnectionError(CLIException):
    """Raised when the CLI is unable to reach the API server."""
    def __init__(self, message: str = "Unable to connect to the DevLens API server."):
        super().__init__(message, exit_code=2)

class AuthenticationError(CLIException):
    """Raised when authentication credentials are invalid or missing."""
    def __init__(self, message: str = "Authentication failed. Please login with 'devlens login'."):
        super().__init__(message, exit_code=3)

class ConfigurationError(CLIException):
    """Raised when there is an issue loading or writing config."""
    def __init__(self, message: str):
        super().__init__(message, exit_code=4)

class LocalAuditError(CLIException):
    """Raised when local offline repository analysis fails."""
    def __init__(self, message: str):
        super().__init__(message, exit_code=5)
