import os
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_APP_PRIVATE_KEY = os.getenv("GITHUB_APP_PRIVATE_KEY")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
DEVLENS_ENV = os.getenv("DEVLENS_ENV", "development")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./devlens.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ANALYTICS_CACHE_TTL = int(os.getenv("ANALYTICS_CACHE_TTL", "900"))
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "180"))
SQL_POOL_SIZE = int(os.getenv("SQL_POOL_SIZE", "5"))
SQL_MAX_OVERFLOW = int(os.getenv("SQL_MAX_OVERFLOW", "10"))

# Production validations at startup
if DEVLENS_ENV.lower() == "production":
    if not GITHUB_WEBHOOK_SECRET:
        raise ValueError("CRITICAL CONFIGURATION ERROR: GITHUB_WEBHOOK_SECRET must be set in production mode.")
    if not GITHUB_APP_ID or not GITHUB_APP_PRIVATE_KEY:
        raise ValueError("CRITICAL CONFIGURATION ERROR: GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY must be set in production mode.")
    if "sqlite" in DATABASE_URL.lower():
        # Warn or restrict sqlite in production environment
        pass

_client_groq = None

def get_groq_client() -> AsyncGroq:
    global _client_groq
    if _client_groq is None:
        _client_groq = AsyncGroq(api_key=GROQ_API_KEY)
    return _client_groq


