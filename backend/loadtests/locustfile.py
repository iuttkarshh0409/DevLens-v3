from locust import HttpUser, task, between

class DevLensLoadTestUser(HttpUser):
    # Simulated pause between tasks (1 to 3 seconds)
    wait_time = between(1, 3)

    @task(3)
    def test_health(self):
        """Simulate pinging backend service health check."""
        self.client.get("/health")

    @task(2)
    def test_metrics(self):
        """Simulate Prometheus polling the metrics registry."""
        self.client.get("/metrics")

    @task(4)
    def test_analytics_overview(self):
        """Simulate loading the main analytics overview widgets."""
        self.client.get("/api/v1/analytics/overview?installation_id=12345")

    @task(2)
    def test_analytics_trends(self):
        """Simulate loading historical metrics trends."""
        self.client.get("/api/v1/analytics/trends?installation_id=12345&metric=score&period=weekly")

    @task(2)
    def test_analytics_repositories(self):
        """Simulate loading the monitored repositories page list."""
        self.client.get("/api/v1/analytics/repositories?installation_id=12345&page=1&limit=10")

    @task(1)
    def test_analytics_export(self):
        """Simulate downloading telemetry data exports."""
        self.client.get("/api/v1/analytics/export?installation_id=12345&format=json")
