# DevLens Observability Guide

This document describes how to monitor DevLens services using metrics registries and Prometheus.

---

## 1. Prometheus Telemetry Endpoint
DevLens exposes live service metrics at:
```text
GET /metrics
```

### Metrics Schema

| Metric Identifier | Type | Labels | Description |
| :--- | :--- | :--- | :--- |
| `devlens_http_requests_total` | Counter | `method`, `path` | Number of HTTP API hits |
| `devlens_queue_depth` | Gauge | None | Number of active pending tasks |
| `devlens_audit_duration_seconds`| Histogram | None | Latency of the compliance engine |

---

## 2. Scraping Configurations
Add the following target details to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'devlens'
    scrape_interval: 10s
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:8000']
```
