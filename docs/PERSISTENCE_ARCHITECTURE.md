# DevLens V3 Database & Persistence Architecture Spec

This document details the layout, configuration, and recovery workflows of the DevLens V3 database and caching infrastructure.

---

## 1. Storage Architecture
To prevent tight coupling between core business logic and storage interfaces, DevLens employs a swappable interface layout:
- **`BaseAnalyticsStore`**: Abstract base class declaring async methods for fetching, deleting, and updating audit histories and health indexes.
- **`InMemoryAnalyticsStore`**: Memory storage model loaded during development and unit testing.
- **`SQLAnalyticsStore`**: Production-grade async SQL store configured directly using environment parameters.

---

## 2. SQL Schema
The initial SQL migrations configure two primary tables:

### `audit_history`
Exposes the granular log history of all audit jobs.
- `audit_id`: String (Primary Key)
- `repository_id`: String
- `repo_name`: String
- `installation_id`: Integer
- `score`: Float
- `status`: String
- `warnings_count`: Integer
- `timestamp`: DateTime
- `evidence`: JSON (Pydantic serialized `EvidenceSummary` DTO)

#### Indexes
- `idx_installation_timestamp`: `(installation_id, timestamp)` -> Optimizes organization-wide timeline lookups.
- `idx_repository_timestamp`: `(repository_id, timestamp)` -> Optimizes individual repo trend history.

### `repository_health`
Stores calculated status caches of monitored repositories.
- `repository_id`: String (Primary Key)
- `repo_name`: String
- `health_score`: Float
- `last_audit`: DateTime
- `trend`: String (`"up"`, `"down"`, `"stable"`)
- `risk_level`: String (`"low"`, `"medium"`, `"high"`)
- `critical_findings`: Integer
- `documentation_score`: Float
- `security_score`: Float
- `testing_score`: Float

---

## 3. Cache Lifecycle & Keys Versioning
DevLens utilizes Redis for distributed cache hosting of analytical widgets.
- **Key Version Namespace**: `analytics:v1:{installation_id}`
- **TTL Limit**: Configured by `ANALYTICS_CACHE_TTL` (default 900 seconds / 15 minutes).
- **Invalidation**: Webhook task completions trigger immediate invalidation delete calls on `/overview` caches to enforce freshness.
- **Graceful Fail-Safe Fallback**: Any Redis connection socket timeout or disconnection is caught, causing endpoints to fall back immediately to SQL db queries.

---

## 4. Environment Switching
- **Development / Tests**: Set `DEVLENS_ENV=development` to initialize `InMemoryAnalyticsStore`.
- **Production**: Set `DEVLENS_ENV=production` and supply a `DATABASE_URL` (using `postgresql+asyncpg` driver mapping) to load the persistent `SQLAnalyticsStore`.

---

## 5. Backup & Restore
- **Postgres Database Backup**:
  ```bash
  pg_dump -U postgres -h localhost devlens > devlens_backup_$(date +%F).sql
  ```
- **Redis Cache Backup**: Copy `/var/lib/redis/dump.rdb` daily to backup storage.

---

## 6. Migration Strategy & Schema Versioning
All database changes must run via Alembic.

### Running Upgrades
```bash
python -m alembic upgrade head
```

### Rolling Back
```bash
python -m alembic downgrade -1
```
