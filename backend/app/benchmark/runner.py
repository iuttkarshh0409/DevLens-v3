import time
from datetime import datetime
from typing import List
from app.rie.pipeline import AuditPipeline
from app.benchmark.golden import GOLDEN_BENCHMARKS, MOCK_BENCHMARK_REPOS
from app.benchmark.models import BenchmarkReport, BenchmarkResult

class BenchmarkRunner:
    def __init__(self, pipeline: AuditPipeline):
        self.pipeline = pipeline

    async def run_all(self) -> BenchmarkReport:
        results: List[BenchmarkResult] = []
        passed_count = 0
        failed_count = 0

        for expected in GOLDEN_BENCHMARKS:
            repo_data = MOCK_BENCHMARK_REPOS.get(expected.repo_name)
            if not repo_data:
                continue

            start_time = time.time()
            report = await self.pipeline.execute_audit(repo_data)
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000.0

            # Assess expected framework & architecture
            detected_frameworks = report.analysis.results.get("FrameworkAnalyzer").evidence.get("detected_frameworks", [])
            framework_matches = expected.expected_framework in detected_frameworks or any(expected.expected_framework in f for f in detected_frameworks)
            
            detected_arch = report.analysis.results.get("ArchitectureAnalyzer").evidence.get("detected_patterns", [])
            arch_matches = expected.expected_architecture in detected_arch

            # Assess expected score ranges
            score = report.scorecard.overall_score
            score_matches = expected.min_score <= score <= expected.max_score

            # Assess expected rule checks
            passed_rules = [r.rule_id for r in report.scorecard.rule_results if r.passed]
            mismatched_rules = []
            for rule_id in expected.expected_findings:
                if rule_id not in passed_rules:
                    mismatched_rules.append(rule_id)

            passed = score_matches and len(mismatched_rules) == 0

            if passed:
                passed_count += 1
            else:
                failed_count += 1

            results.append(BenchmarkResult(
                repo_name=expected.repo_name,
                passed=passed,
                actual_score=score,
                score_difference=round(score - expected.min_score, 2),
                mismatched_rules=mismatched_rules,
                mismatched_findings=[],
                execution_time_ms=execution_time_ms
            ))

        total = passed_count + failed_count
        pass_rate = (passed_count / total) * 100.0 if total > 0 else 0.0

        return BenchmarkReport(
            overall_pass_rate=pass_rate,
            total_benchmarks=total,
            passed_count=passed_count,
            failed_count=failed_count,
            results=results,
            timestamp=datetime.utcnow()
        )
