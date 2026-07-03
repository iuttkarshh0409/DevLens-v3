# GitHub App Architecture

This document specifies the end-to-end architecture of DevLens V3 as a first-class GitHub App integration.

## Integration Diagram
```mermaid
sequenceDiagram
    participant GitHub
    participant DevLens Webhook
    participant DevLens Queue
    participant DevLens Worker
    participant GitHub API

    GitHub->>DevLens Webhook: PR / Check Suite Event (Webhook Payload)
    Note over DevLens Webhook: Validate Signature (HMAC SHA256)
    DevLens Webhook->>GitHub API: POST /statuses/{sha} (pending)
    DevLens Webhook->>GitHub API: POST /check-runs (in_progress)
    DevLens Webhook->>DevLens Queue: Enqueue AuditJob (metadata + check_run_id)
    DevLens Webhook-->>GitHub: 202 OK (Immediate Acknowledgement)
    
    loop Worker Loop
        DevLens Worker->>DevLens Queue: Dequeue Job
        DevLens Worker->>GitHub API: Fetch Repository Tree & .devlens.yml
        Note over DevLens Worker: Run AnalysisOrchestrator
        Note over DevLens Worker: Evaluate Configured Scoring Rules
        Note over DevLens Worker: Generate Multi-Level Annotations
        Note over DevLens Worker: Extract deterministic Repository Insights
        DevLens Worker->>GitHub API: PATCH /check-runs/{id} (complete)
        DevLens Worker->>GitHub API: POST /pulls/{num}/reviews (actionable annotations)
        DevLens Worker->>GitHub API: POST /statuses/{sha} (success/failure status)
    end
```

## Security & Scopes
DevLens operates under a least-privilege permission model:

| Permission | Scope | Rationale |
|---|---|---|
| **Checks** | Read & Write | Required to create check runs, upload annotation marks, and update pass/fail conclusions. |
| **Pull Requests** | Read & Write | Required to analyze code modifications, post inline review comments, and submit reviews. |
| **Commit Statuses** | Read & Write | Required to publish gating build statuses for pull request merge checks. |
| **Contents** | Read-Only | Required to fetch manifests, Dockerfiles, workflow YAMLs, and `.devlens.yml`. |
| **Metadata** | Read-Only | Basic repository identification metadata. |

## Resiliency & State
- All background tasks are stateless.
- Tasks utilize job acknowledgments, automatic Redeliveries, and DLQ routing.
- Worker shutdowns listen to standard operating system signals (`SIGTERM`/`SIGINT`).
