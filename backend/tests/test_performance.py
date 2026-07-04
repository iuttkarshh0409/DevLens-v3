import unittest
import contextvars
from app.observability.metrics import MetricsRegistry
from app.observability.tracing import set_current_context, get_current_context, clear_current_context
from app.core.context import RequestContext
from app.jobs.queue import InMemoryQueue, RedisCircuitBreaker

class TestPerformanceOptimizations(unittest.TestCase):
    def test_metrics_registry(self):
        reg = MetricsRegistry()
        reg.increment("test_counter", {"method": "GET"})
        reg.set_gauge("test_gauge", 4.5, {"node": "A"})
        reg.observe("test_histogram", 0.12, {"action": "parse"})
        
        output = reg.generate_prometheus_output()
        self.assertIn("test_counter{method=\"GET\"} 1", output)
        self.assertIn("test_gauge{node=\"A\"} 4.5", output)
        self.assertIn("test_histogram_count{action=\"parse\"} 1", output)
        self.assertIn("test_histogram_sum{action=\"parse\"} 0.1200", output)

    def test_tracing_context_propagation(self):
        ctx = RequestContext(installation_id=5544)
        token = set_current_context(ctx)
        
        active = get_current_context()
        self.assertIsNotNone(active)
        self.assertEqual(active.installation_id, 5544)
        
        clear_current_context(token)
        self.assertIsNone(get_current_context())

    def test_redis_circuit_breaker(self):
        breaker = RedisCircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
        self.assertTrue(breaker.can_execute())
        
        breaker.record_failure()
        breaker.record_failure()
        breaker.record_failure()
        
        self.assertFalse(breaker.can_execute())

    def test_root_endpoint(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "DevLens API")
        self.assertEqual(data["version"], "3.0.0")
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["docs"], "/docs")
        self.assertEqual(data["openapi"], "/openapi.json")
