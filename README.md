# DevLens V3

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CLI](https://img.shields.io/badge/CLI-devlens-blue)](./backend/pyproject.toml)
[![VS%20Code](https://img.shields.io/badge/VS%20Code-Extension-007ACC)](./vscode-extension/package.json)

DevLens V3 is a repository auditing platform built around a GitHub App, a Repository Intelligence Engine (RIE), a FastAPI backend, PostgreSQL persistence, Redis-backed job execution, an official CLI, and an official VS Code extension.

The platform analyzes repositories, publishes GitHub feedback, stores audit history, exposes analytics, and supports both API-backed and local offline workflows.

## Highlights

- GitHub App integration for installation, callbacks, webhooks, and repository event processing
- Repository Intelligence Engine (RIE) for deterministic repository inspection, ecosystem detection, scoring, and policy evaluation
- GitHub Checks, PR review comments, annotations, and commit status publishing
- Versioned `.devlens.yml` repository configuration support
- PostgreSQL persistence for audit history and analytics records
- Redis-backed queueing and cache support
- Official `devlens` CLI for configuration, authentication, audits, analytics, and version reporting
- Official VS Code extension for workspace audits, diagnostics, report viewing, and API or CLI-backed execution
- Production hardening, observability, and release-oriented Docker Compose workflows

## Architecture

DevLens V3 is organized as a single repository containing the backend services, frontend, CLI packaging, and the VS Code extension.

- `backend/`: FastAPI application, GitHub App logic, Repository Intelligence Engine, CLI package, persistence, jobs, and tests
- `frontend/`: React and Vite frontend
- `vscode-extension/`: Official VS Code extension source and packaged output
- `docs/`: operational, marketplace, CLI, extension, and release documentation
- `docker-compose.yml`: local and release validation stack for PostgreSQL, Redis, API, and worker services
- `run_e2e_compose.py`: Compose-based end-to-end verification helper

## Project Structure

```text
DevLens/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   ├── dependencies/
│   │   │   ├── middleware/
│   │   │   ├── schemas/
│   │   │   └── __init__.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   ├── exceptions.py
│   │   │   └── constants.py
│   │   │
│   │   ├── database/
│   │   │   ├── models/
│   │   │   ├── repositories/
│   │   │   ├── migrations/
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   │
│   │   ├── integrations/
│   │   │   ├── github/
│   │   │   ├── vscode/
│   │   │   ├── slack/
│   │   │   └── ...
│   │   │
│   │   ├── services/
│   │   │   ├── analysis/
│   │   │   ├── reporting/
│   │   │   ├── indexing/
│   │   │   ├── recommendations/
│   │   │   └── notifications/
│   │   │
│   │   ├── workers/
│   │   │   ├── jobs/
│   │   │   ├── scheduler.py
│   │   │   └── queue.py
│   │   │
│   │   ├── webhooks/
│   │   │   ├── github.py
│   │   │   └── handlers.py
│   │   │
│   │   ├── cli/
│   │   │
│   │   ├── observability/
│   │   │   ├── metrics.py
│   │   │   ├── tracing.py
│   │   │   └── health.py
│   │   │
│   │   ├── utils/
│   │   │
│   │   └── main.py
│   │
│   ├── alembic/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   ├── e2e/
│   │   └── fixtures/
│   │
│   ├── scripts/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── styles/
│   │   ├── types/
│   │   └── utils/
│   │
│   └── package.json
│
├── vscode-extension/
│   ├── src/
│   │   ├── commands/
│   │   ├── providers/
│   │   ├── panels/
│   │   ├── services/
│   │   ├── telemetry/
│   │   └── extension.ts
│   │
│   ├── media/
│   ├── resources/
│   ├── out/
│   └── package.json
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── design/
│   ├── deployment/
│   └── assets/
│
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   ├── monitoring/
│   └── scripts/
│
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
│
├── docker-compose.yml
├── run_e2e_compose.py
├── LICENSE
├── CONTRIBUTING.md
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- Docker and Docker Compose
- A Groq API key for narrative analysis flows
- GitHub App credentials for GitHub-integrated production workflows

### Start the Local Stack

The checked-in Docker Compose configuration is the recommended way to run DevLens V3 locally.

1. Export the backend environment variables required for your workflow.
2. Start the services from the repository root.

```bash
docker compose up --build
```

This starts:

- PostgreSQL on `5432`
- Redis on `6379`
- DevLens API on `8000`
- DevLens worker for background jobs

The API health endpoint is available at `http://localhost:8000/health`.

### Key Environment Variables

Common variables used by the checked-in Compose workflow include:

- `GROQ_API_KEY`
- `GITHUB_TOKEN`
- `GITHUB_APP_ID`
- `GITHUB_APP_PRIVATE_KEY`
- `GITHUB_WEBHOOK_SECRET`

For the full environment reference, see [docs/ENVIRONMENT_REFERENCE.md](./docs/ENVIRONMENT_REFERENCE.md).

## GitHub App

DevLens V3 ships as a GitHub App-oriented platform.

- Installation and callback flows are implemented in the backend
- Webhook handling supports repository event processing and job dispatch
- Installation tokens are used for GitHub API access in App-backed flows
- Checks, pull request reviews, and status updates are published from backend services

Additional setup and operational details are documented in:

- [docs/APP_ONBOARDING_GUIDE.md](./docs/APP_ONBOARDING_GUIDE.md)
- [docs/GITHUB_APP_ARCHITECTURE.md](./docs/GITHUB_APP_ARCHITECTURE.md)
- [docs/GITHUB_INTEGRATION_SPECIFICATION.md](./docs/GITHUB_INTEGRATION_SPECIFICATION.md)

## PostgreSQL and Redis

DevLens V3 uses PostgreSQL and Redis as part of the standard platform runtime.

- PostgreSQL stores audit history, repository health records, and analytics data
- Redis supports queueing, cache coordination, and worker-side resilience flows
- The repository includes Alembic migration setup under `backend/alembic/`

The default Compose stack provisions both services automatically.

## CLI

The official CLI is packaged from `backend/pyproject.toml` and exposed as the `devlens` command.

Primary command areas include:

- `devlens audit`
- `devlens login`
- `devlens logout`
- `devlens whoami`
- `devlens version`
- `devlens config ...`
- `devlens analytics ...`
- `devlens cache ...`

CLI documentation:

- [docs/CLI_GUIDE.md](./docs/CLI_GUIDE.md)
- [docs/CLI_REFERENCE.md](./docs/CLI_REFERENCE.md)
- [docs/CLI_CONFIGURATION.md](./docs/CLI_CONFIGURATION.md)

## VS Code Extension

The official VS Code extension lives in `vscode-extension/` and provides:

- interactive workspace audits
- explicit offline audits through the local `devlens` CLI
- API-backed audit execution
- diagnostics and status bar updates
- report presentation through a webview panel

The default experience is API-first. Offline mode remains available when the DevLens CLI is installed and explicitly enabled or invoked.

Extension documentation:

- [docs/VSCODE_EXTENSION_GUIDE.md](./docs/VSCODE_EXTENSION_GUIDE.md)
- [docs/VSCODE_EXTENSION_ARCHITECTURE.md](./docs/VSCODE_EXTENSION_ARCHITECTURE.md)

## Frontend

The frontend application is located in `frontend/` and can be run independently for UI work:

```bash
cd frontend
npm install
npm run dev
```

The default local frontend URL is `http://localhost:5173`.

## Deployment

DevLens V3 is documented around containerized deployment and the checked-in Compose stack rather than a Vercel-only workflow.

- Use [docker-compose.yml](./docker-compose.yml) for local production-style startup
- Build the backend container from [backend/Dockerfile](./backend/Dockerfile)
- Use Alembic migrations for database initialization and upgrades
- Configure production environment variables before enabling GitHub App callbacks and webhook processing

Deployment and operations references:

- [docs/DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md)
- [docs/RUNBOOK.md](./docs/RUNBOOK.md)
- [docs/PRODUCTION_HARDENING.md](./docs/PRODUCTION_HARDENING.md)
- [docs/OBSERVABILITY_GUIDE.md](./docs/OBSERVABILITY_GUIDE.md)

## Documentation

Additional release and marketplace material is available under `docs/`, including:

- [docs/CHANGELOG.md](./docs/CHANGELOG.md)
- [docs/SECURITY.md](./docs/SECURITY.md)
- [docs/SUPPORT.md](./docs/SUPPORT.md)
- [docs/PRIVACY_POLICY.md](./docs/PRIVACY_POLICY.md)
- [docs/TERMS_OF_SERVICE.md](./docs/TERMS_OF_SERVICE.md)
- [docs/MARKETPLACE_LISTING.md](./docs/MARKETPLACE_LISTING.md)

## Repository

- Maintainer: [@iuttkarshh0409](https://github.com/iuttkarshh0409)
- Repository: [iuttkarshh0409/DevLens-v3](https://github.com/iuttkarshh0409/DevLens-v3)

## License

Distributed under the MIT License. See [LICENSE](./LICENSE).
