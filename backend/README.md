# DevLens Backend

The `backend/` directory contains the FastAPI application, GitHub App integration, Repository Intelligence Engine, CLI package, persistence layer, worker logic, and backend test suite for DevLens V3.

## Recommended Local Workflow

The recommended way to run the backend is through the repository root Docker Compose stack.

From the repository root:

```bash
docker compose up --build
```

This starts:

- PostgreSQL
- Redis
- DevLens API
- DevLens worker

Default local endpoints:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## Environment Variables

Common backend variables used by the checked-in Compose workflow include:

- `GROQ_API_KEY`
- `GITHUB_TOKEN`
- `GITHUB_APP_ID`
- `GITHUB_APP_PRIVATE_KEY`
- `GITHUB_WEBHOOK_SECRET`
- `DATABASE_URL`
- `REDIS_URL`
- `ALLOWED_ORIGINS`

For the full reference, see [docs/ENVIRONMENT_REFERENCE.md](../docs/ENVIRONMENT_REFERENCE.md).

## Direct Python Setup

If you need to run the backend outside Docker Compose:

1. Create a virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. Install dependencies.
   ```bash
   pip install -r requirements.txt
   ```
3. Export the required environment variables for your target environment, including `GROQ_API_KEY`.
4. Start the API server.
   ```bash
   uvicorn app.main:app --reload
   ```

## Packaging

The packaged CLI and backend metadata are defined in [pyproject.toml](./pyproject.toml).

## Tests

Backend tests are located in `backend/tests/`.
