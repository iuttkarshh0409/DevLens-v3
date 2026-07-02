import unittest
import asyncio
from app.rie.pipeline import AuditPipeline
from app.benchmark.runner import BenchmarkRunner

class TestBenchmark(unittest.TestCase):
    def test_run_benchmarks_pass(self):
        pipeline = AuditPipeline()
        runner = BenchmarkRunner(pipeline)
        
        # Run all golden benchmarks and assert high pass rate
        report = asyncio.run(runner.run_all())
        
        self.assertEqual(report.total_benchmarks, 3)
        self.assertEqual(report.passed_count, 3)
        self.assertEqual(report.overall_pass_rate, 100.0)
        
        for res in report.results:
            self.assertTrue(res.passed)
            self.assertGreaterEqual(res.actual_score, 3.0)

if __name__ == "__main__":
    unittest.main()
