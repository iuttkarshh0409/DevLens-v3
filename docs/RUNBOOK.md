# DevLens V3 Incident Response Runbook

Operational procedures for diagnosing and mitigating production service incidents.

---

## Incident 1: Redis Queue Outages / High Latency
**Symptoms**: Job scheduling fails, `/api/health` indicates Redis disconnection, or worker logs show repeated connection retries.

### Mitigation Steps
1. **Verify Circuit Breaker State**: Check logs to see if the circuit state is `OPEN`. If open, check that traffic is routing to `InMemoryQueue` fallback.
2. **Check Redis Service**:
   ```bash
   systemctl status redis-server
   ```
3. **Inspect Connection Pool Limits**: Check if Redis is hitting client limits. Increase `maxclients` in `/etc/redis/redis.conf` if necessary.
4. **Trigger Health Check Probe**: Execute a `ping` manually to verify connectivity:
   ```bash
   redis-cli ping
   ```

---

## Incident 2: GitHub API Rate Limiting (403 Forbidden)
**Symptoms**: Check Run generation fails, worker logs indicate GitHub rate limits are exhausted.

### Mitigation Steps
1. **Identify the Cause**: Check the response headers for `X-RateLimit-Remaining` and `X-RateLimit-Reset`.
2. **Examine Caching**: Verify that the installation token cache is operating correctly (reusing cached tokens until they have <60 seconds remaining).
3. **Verify Scopes**: Check if a repository triggers massive trees API downloads. Configure `.devlens.yml` to ignore heavy paths.

---

## Incident 3: Webhook Verification Validation Failures (HTTP 401)
**Symptoms**: GitHub App logs show webhook deliveries failing with `401 Unauthorized`.

### Mitigation Steps
1. **Check Secrets**: Ensure `GITHUB_WEBHOOK_SECRET` environment variable matches exactly with the GitHub App configuration secret.
2. **Rollover Webhook Secrets**:
   - Generate a new secret key in GitHub App Settings.
   - Update `GITHUB_WEBHOOK_SECRET` environment variables across FastAPI servers.
   - Redeploy FastAPI server without code changes.
