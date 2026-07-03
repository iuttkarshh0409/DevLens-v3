# Changelog

All notable changes to the DevLens project will be documented in this file. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2026-07-03

### Added
- **GitHub Apps Core Suite**: Separated Checks, PR review comment generation, and Status gate integrations.
- **Dynamic Config Policy**: Added Kubernetes-style `.devlens.yml` yaml specification (`apiVersion: devlens.io/v1`, `kind: RepositoryPolicy`).
- **Resilient Redis Queue**: Added circuit breakers, exponential jitter backoffs, and fallback in-memory managers.
- **Safe Token Caching**: Added thread-safe and asyncio-safe installation access token caching with < 60s remaining lifetime validation.
- **Ecosystem Detections**: Expanded technology insights (Cargo, Go Modules, composer, bun, Nuget, Poetry).

### Fixed
- Webhook endpoints fail closed when `GITHUB_WEBHOOK_SECRET` is missing in production environment.
- Annotations chunking issues resolved by deterministic batch partitioning of max 50 items.
