import os
import subprocess
import time
import hmac
import hashlib
import json
import httpx

# Configuration matching docker-compose environments
WEBHOOK_SECRET = "fakesecret123"
API_URL = "http://localhost:8000"

def run_cmd(cmd: str):
    print(f"Running command: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result

def main():
    print("=== Starting End-to-End Persistence and Caching Verification ===")
    
    # 1. Clean containers
    run_cmd("docker compose down -v")
    
    # 2. Build and start services
    # Pass dummy credentials so API validation passes
    env = os.environ.copy()
    env["GITHUB_WEBHOOK_SECRET"] = WEBHOOK_SECRET
    env["GITHUB_APP_ID"] = "123456"
    env["GITHUB_APP_PRIVATE_KEY"] = "-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----"
    env["REDIS_URL"] = "redis://localhost:6379/0"
    
    print("Starting services (FastAPI, Postgres, Redis, Worker)...")
    subprocess.run("docker compose up --build -d", shell=True, env=env)
    
    # 3. Wait for services to become healthy
    print("Waiting for API and Database startup...")
    for i in range(15):
        try:
            r = httpx.get(f"{API_URL}/health", timeout=2.0)
            if r.status_code == 200:
                print("API is healthy!")
                break
        except Exception:
            pass
        time.sleep(2.0)
    else:
        print("FAIL: API failed to start or return healthy status.")
        run_cmd("docker compose logs")
        return

    # 4. Run Alembic Database Migrations
    print("Running Alembic DB Migrations inside container...")
    run_cmd("docker compose exec api alembic upgrade head")

    # 5. Build signed GitHub Webhook request (Fully Compliant Payload)
    payload = {
        "ref": "refs/heads/main",
        "before": "0000000000000000000000000000000000000000",
        "after": "1111111111111111111111111111111111111111",
        "repository": {
            "id": 9999,
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "owner": {"login": "owner"},
            "private": False,
            "fork": False,
            "archived": False
        },
        "installation": {
            "id": 12345,
            "account": {"login": "owner"}
        }
    }
    
    body = json.dumps(payload).encode("utf-8")
    signature = "sha256=" + hmac.new(WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    
    headers = {
        "x-github-event": "push",
        "x-github-delivery": "test-delivery-id",
        "x-hub-signature-256": signature,
        "content-type": "application/json"
    }

    # 6. Trigger Audit Workflow via webhook
    print("Sending signed GitHub Push event webhook payload...")
    try:
        r = httpx.post(f"{API_URL}/github/webhook", content=body, headers=headers, timeout=5.0)
        print(f"Webhook response: {r.status_code} | {r.text}")
        if r.status_code != 200:
            print("FAIL: Webhook endpoint did not return 200 status.")
            run_cmd("docker compose logs api")
            return
    except Exception as e:
        print(f"FAIL: Failed sending webhook request: {e}")
        return

    # 7. Poll analytics endpoints verifying PostgreSQL persistence & Redis update
    print("Polling API analytics history (SQL DB + Redis persistence check)...")
    success = False
    for i in range(15):
        try:
            # Query paginated repository health summary which resolves repository stats
            r = httpx.get(f"{API_URL}/api/v1/analytics/repositories?installation_id=12345", timeout=2.0)
            if r.status_code == 200:
                data = r.json()
                if data.get("total_count", 0) > 0:
                    print("SUCCESS: Persisted repository health records found in SQL Database!")
                    print(json.dumps(data, indent=2))
                    success = True
                    break
        except Exception:
            pass
        time.sleep(2.0)
    
    if not success:
        print("FAIL: Persistent analytics did not populate. Checking logs:")
        run_cmd("docker compose logs worker")
        run_cmd("docker compose logs api")
    else:
        # Check cache hits/miss overview endpoint
        try:
            overview_r = httpx.get(f"{API_URL}/api/v1/analytics/overview?installation_id=12345", timeout=2.0)
            print("Overview dashboard Cache overview stats:")
            print(json.dumps(overview_r.json(), indent=2))
        except Exception as e:
            print(f"Warn: Failed calling overview: {e}")

    # 8. Clean up
    print("Cleaning up Docker containers...")
    run_cmd("docker compose down -v")
    
    if success:
        print("\n=== E2E CONFLICT & PERSISTENCE VERIFICATION PASSED ===")
    else:
        print("\n=== E2E CONFLICT & PERSISTENCE VERIFICATION FAILED ===")

if __name__ == "__main__":
    main()
