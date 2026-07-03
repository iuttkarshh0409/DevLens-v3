# DevLens Security Policy & Permissions Justification

This document outlines the security architecture and justifies each permission request required by DevLens.

---

## 1. Permissions Justification Matrix

DevLens strictly operates on the principle of least privilege. The following matrix details why each permission scope is requested.

| Scope | Permission Type | Rationale / Usage |
|---|---|---|
| **Checks** | Read & Write | Required to create, update, and complete Check Runs containing audit results and annotations. |
| **Pull Requests** | Read & Write | Required to publish inline review comments and annotations directly on pull requests. |
| **Contents** | Read-Only | Required to fetch manifest configuration files (`package.json`, `.devlens.yml`, etc.) for auditing. |
| **Metadata** | Read-Only | Basic repository information (branch list, commit IDs, tags) required to run webhook actions. |

---

## 2. Token Security & Caching
- **Installation Tokens**: DevLens requests short-lived installation access tokens.
- **Cache TTL Security**: Tokens are stored in a thread-safe and asyncio-safe in-memory cache, and reused only if they have more than 60 seconds of remaining lifetime. 
- **Encryption**: Secrets are loaded into memory from protected environment variables and are never output to system logs.

---

## 3. Vulnerability Reporting
If you discover a security vulnerability in DevLens, please report it via email to `security@devlens.io`. Do not open public GitHub issues for security reports. We respond to all security reports within 24 hours.
