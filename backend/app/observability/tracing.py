import contextvars
from typing import Optional
from app.core.context import RequestContext

# ContextVar storing the current request context across coroutines
_current_request_context = contextvars.ContextVar("current_request_context", default=None)

def get_current_context() -> Optional[RequestContext]:
    """Retrieve the current coroutine's active context."""
    return _current_request_context.get()

def set_current_context(ctx: RequestContext) -> contextvars.Token:
    """Set the active context for the current coroutine."""
    return _current_request_context.set(ctx)

def clear_current_context(token: contextvars.Token):
    """Restore the previous active context using the token."""
    _current_request_context.reset(token)
