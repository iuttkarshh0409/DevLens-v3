# DevLens Support & Troubleshooting Guide

This guide assists in diagnosing, resolving, and reporting issues encountered when running the DevLens GitHub integration.

---

## 1. Troubleshooting Common Problems

### Symptom: DevLens Check Run hangs or shows "In Progress" indefinitely
- **Cause**: Redis queue failure or worker container crash.
- **Resolution**: 
  1. Verify the status of background worker queues using the `/api/health` diagnostics.
  2. If the Redis circuit breaker opened, DevLens will degrade to in-memory queues. Restart Redis to close the circuit and resume normal worker queues.

### Symptom: API returns "401 Webhook signature validation failed"
- **Cause**: The `GITHUB_WEBHOOK_SECRET` environment variable is either missing or mismatched between GitHub App settings and your server config.
- **Resolution**: Ensure your `GITHUB_WEBHOOK_SECRET` environment variable matches the secret defined in your App settings. If running in production mode, signature validation is strict and cannot be bypassed.

### Symptom: Missing code annotations or incomplete stack insights
- **Cause**: Deprecated configuration specs in your `.devlens.yml` file.
- **Resolution**: Ensure your configuration conforms to the `.devlens.yml` schema (`apiVersion: devlens.io/v1`, `kind: RepositoryPolicy`).

---

## 2. Escalation & Contact
If troubleshooting does not resolve the issue:
- **Email Support**: `support@devlens.io` (average response time < 2 hours)
- **Status Page**: `status.devlens.io`
- **GitHub Issues**: Open a ticket in the [DevLens community support repository](https://github.com/devlens/support).
