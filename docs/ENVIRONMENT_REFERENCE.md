# DevLens V3 Environment Variables Reference

Catalog of environment configurations used to configure the DevLens API and worker.

---

## 1. Required Variables

| Name | Type | Allowed Values | Target Environment | Rationale |
|---|---|---|---|---|
| **`GROQ_API_KEY`** | Secret | String | All | Auth key for running Groq LLM narrative reviews. |
| **`GITHUB_TOKEN`** | Secret | String | All | API access token for performing repository checks. |
| **`GITHUB_APP_ID`** | Public | Integer | All | GitHub App identification number. |
| **`GITHUB_APP_PRIVATE_KEY`** | Secret | String (PEM block) | All | Key used to generate JWT tokens for GitHub App API exchanges. |
| **`GITHUB_WEBHOOK_SECRET`** | Secret | String | Production (Strict) | Secret key used to sign incoming webhook requests. |

---

## 2. Optional Variables

| Name | Default Value | Target Environment | Rationale |
|---|---|---|---|
| **`DEVLENS_ENV`** | `"development"` | All | Configures security policies (e.g. `"production"` mode enforces strict fail-closed webhook checks). |
| **`REDIS_HOST`** | `"localhost"` | All | IP/Hostname of the Redis service instance. |
| **`REDIS_PORT`** | `6379` | All | Access port for the Redis instance. |
| **`REDIS_DB`** | `0` | All | Database index mapping for Redis. |
