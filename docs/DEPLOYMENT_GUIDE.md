# DevLens V3 Production Deployment Guide

This guide details the steps to deploy DevLens V3 in a production-ready environment.

---

## 1. System Requirements & Architecture
The DevLens production cluster contains:
- **FastAPI Application Server**: Runs the HTTP endpoints and handles incoming webhooks.
- **Worker Pools**: Daemon tasks that dequeue jobs from Redis queues and execute code audits.
- **Redis Server**: High-throughput queue runner and state storage cache.

---

## 2. Docker Deployment

DevLens includes a `Dockerfile` inside the `backend/` directory.

### Build Production Image
```bash
docker build -t devlens-backend:v3.0.0 -f backend/Dockerfile .
```

### Run API Service
```bash
docker run -d \
  --name devlens-api \
  -p 8000:8000 \
  --env-file .env.prod \
  devlens-backend:v3.0.0 \
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Run Queue Worker
```bash
docker run -d \
  --name devlens-worker \
  --env-file .env.prod \
  devlens-backend:v3.0.0 \
  python app/worker.py
```

---

## 3. Configuration Management
- Set `DEVLENS_ENV=production` to enable strict webhook signature validation and startup checks.
- Keep `socket_timeout` on Redis clients configured to prevent blocking socket hangs.
- Run Nginx as a reverse proxy with SSL certificate termination.
