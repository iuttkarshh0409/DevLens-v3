# DevLens V3 Production Hardening & Operational Spec

This document details the operational mechanisms, security limits, recovery semantics, and deployment assumptions of the DevLens V3 platform.

---

## 1. Webhook Security Model
DevLens V3 enforces signature verification to prevent payload spoofing.

- **Signature Check**: All payloads are validated using the `X-Hub-Signature-256` header containing an HMAC hex digest matching `sha256` hash computed with `GITHUB_WEBHOOK_SECRET`.
- **Fail-Closed Policy**: If `DEVLENS_ENV` is set to `"production"`, signature verification is strict. If `GITHUB_WEBHOOK_SECRET` is missing in config, the application throws a validation startup error.
- **Local Dev Bypass**: Local development mode (`DEVLENS_ENV=development`) permits bypass only if `GITHUB_WEBHOOK_SECRET` is undefined, assisting quick local test iterations.

---

## 2. Redis Recovery & Circuit Breaker
To prevent connection storms and excessive load overhead during outages:

- **Circuit Breaker State Machine**:
  - **CLOSED**: Requests map to Redis. Consecutive connection/timeout errors increments failure count.
  - **OPEN**: After 5 consecutive failures, the circuit opens, routing queue metadata transactions instantly to the local `InMemoryQueue` fallback.
  - **HALF-OPEN**: After a 10-second cooldown period, the circuit moves to half-open, executing a connection probe. If successful, it returns to CLOSED; if it fails, it re-opens.
- **Jittered Backoff**: Exponential retry reconnect delays include randomized jitter factors (using `random.uniform`), avoiding stampeding reconnections.

---

## 3. Token Cache Lifecycle
GitHub Installation Tokens have an expiration lifetime (normally 1 hour).

- **Cache TTL**: Tokens are cached in-memory and mapped to installation IDs.
- **Remaining Lifetime Gating**: Cached tokens are reused until they have **less than 60 seconds** of remaining lifetime, after which a transparent thread-safe (`threading.Lock`) and asyncio-safe (`asyncio.Lock`) token refresh JWT exchange runs.

---

## 4. Annotation Batching & Chunking
GitHub Check Runs payloads restrict inline code annotations to a maximum of 50 items per API request payload.

- **Batch Chunking**: Array slice partitions annotations in blocks of 50.
- **Order Guarantees**: Annotations sort deterministically based on file path, start line, and title matching, ensuring stable check run outputs.
- **Graceful Fault Tolerance**: Subsequent batches patch in sequence. If a specific batch fails, the failure is caught, logged, and remaining batches continue patching.

---

## 5. Production Deployment Assumptions
- **State Management**: The API is fully stateless. User state and pipeline contexts route to Redis queue states.
- **Dockerization**: The container setup pins base image versions strictly instead of relying on mutable `:latest` tags.
- **Scaling Limits**: Background tasks scale horizontally. Each worker instance runs independent event analysis pipelines, routing jobs through the shared Redis queue.
