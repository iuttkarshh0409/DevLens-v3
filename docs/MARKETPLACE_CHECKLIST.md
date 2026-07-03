# GitHub Marketplace Submission Checklist

Checklist for evaluating and verifying that DevLens V3 satisfies all GitHub Marketplace guidelines.

---

## 1. GitHub App Configuration
- [ ] **Manifest & Permissions Justification**: All requested permissions (`checks`, `pull_requests`, `contents`, `metadata`) are fully documented in `SECURITY.md`.
- [ ] **Webhook Deliveries**: Webhook endpoints return `HTTP 200` statuses for unknown event notifications.
- [ ] **Fail-Closed Verification**: production webhook requests fail closed if signature headers or secrets are missing.

---

## 2. Onboarding & User Experience
- [ ] **Installation Flow**: Clean redirection to `/app/callback` after App installation.
- [ ] **Configuration support**: Default policy is automatically created if `.devlens.yml` is missing.
- [ ] **Documentation**: Public guides explain `.devlens.yml` structure and usage.

---

## 3. Operational Requirements
- [ ] **Health Check Endpoints**: Running status is queried via the `/api/health` endpoint.
- [ ] **Resilience**: Redis outages degrade gracefully using the in-memory fallback.
- [ ] **Token Limits**: API limits are respected; cache updates tokens only when remaining lifetime is < 60 seconds.
