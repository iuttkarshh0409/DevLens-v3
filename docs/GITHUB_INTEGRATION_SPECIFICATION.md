# GitHub Integration Specification

This document details the payload mapping, API endpoints, and webhook integration schemas for DevLens V3.

## 1. Webhook Handlers
DevLens listens to standard payload requests securely signed with a webhook secret.

### `pull_request` Webhook
- **Actions**: `opened`, `synchronize`, `reopened`.
- **Payload Extraction**:
  - `owner`: `repository.owner.login`
  - `repo`: `repository.name`
  - `pull_number`: `number`
  - `head_sha`: `pull_request.head.sha`
  - `installation_id`: `installation.id`

### `check_suite` Webhook
- **Actions**: `requested`, `rerequested`.
- **Payload Extraction**:
  - `owner`: `repository.owner.login`
  - `repo`: `repository.name`
  - `head_sha`: `check_suite.head_sha`
  - `installation_id`: `installation.id`

---

## 2. API Endpoints
All integration endpoints communicate with GitHub via the REST v3 API:

### Checks API
- **Create**: `POST /repos/{owner}/{repo}/check-runs`
  ```json
  {
    "name": "DevLens Code Audit",
    "head_sha": "{head_sha}",
    "status": "in_progress",
    "started_at": "{timestamp}"
  }
  ```
- **Update**: `PATCH /repos/{owner}/{repo}/check-runs/{check_run_id}`
  ```json
  {
    "status": "completed",
    "completed_at": "{timestamp}",
    "conclusion": "success",
    "output": {
      "title": "DevLens Audit Score: 8.5/10.0",
      "summary": "### DevLens Audit Score: **8.5/10.0**...",
      "annotations": [
        {
          "path": "README.md",
          "start_line": 1,
          "end_line": 1,
          "annotation_level": "warning",
          "title": "README missing installation or setup instructions.",
          "message": "Add a distinct '# Setup' or '# Installation' header in your README.md."
        }
      ]
    }
  }
  ```

### Pull Request Reviews API
- **Create**: `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews`
  ```json
  {
    "body": "### DevLens PR Code Audit: **8.5/10.0**...",
    "event": "APPROVE",
    "comments": [
      {
        "path": "Dockerfile",
        "line": 5,
        "body": "**[Docker base image uses ':latest' tag.]**\nPin your Docker image to a specific version."
      }
    ]
  }
  ```

### Commit Statuses API
- **Create**: `POST /repos/{owner}/{repo}/statuses/{sha}`
  ```json
  {
    "state": "success",
    "target_url": "https://dev-lens-lime.vercel.app",
    "description": "DevLens audit score: 8.5/10.0 (PASSED)",
    "context": "devlens/audit"
  }
  ```
