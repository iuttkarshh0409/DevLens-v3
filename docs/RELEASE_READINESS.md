# DevLens Release Readiness Guide

This document validates the security, operational stability, and marketplace readiness for DevLens V3.0.0 (RC-1).

---

## 1. Security Models & Credentials

### CLI Credential Cache (Fernet)
- Active tokens stored in `~/.devlens/config.toml` are symmetrically encrypted with Fernet.
- Encryption keys are stored separately at `~/.devlens/.key`.
- Encrypted parameters are marked with `enc:` prefix. Legacy plaintext config keys are migrated automatically on load.

### VS Code SecretStorage API
- The extension utilizes `context.secrets` (VS Code Keychain integration) to store Personal Access Tokens (PATs).
- Text configuration values are migrated on activate to prevent exposure in settings.

---

## 2. API Restrictions & Rate Limiting

### Production CORS Rules
- Configured via `ALLOWED_ORIGINS` environment variables.
- Production environments throw exceptions if origins are unset, preventing wildcard openings.

### GitHub API Rate Limiting
- The client inspects rate-limiting headers:
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`
  - `Retry-After`
- Automatically applies exponential backoffs if rate limits are exhausted.

---

## 3. Operations & Lifespans
- Binds lifespan lifecycle events to the FastAPI server.
- Shuts down open SQLAlchemy connections and Redis pipelines, preventing transaction locks.
