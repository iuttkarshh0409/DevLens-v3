import time
import asyncio
import sys
import os

# Set PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.github import RepositorySnapshot
from app.rie.pipeline import AuditPipeline

async def benchmark_pipeline():
    print("Benchmarking Audit Pipeline...")
    snapshot = RepositorySnapshot(
        name="bench-repo",
        readme="# Benchmark README\nSupports automated testing.",
        files=["main.py", "package.json"],
        raw_files_content={
            "main.py": "def hello(): print('bench')",
            "package.json": '{"dependencies": {}}'
        }
    )

    pipeline = AuditPipeline(ai_provider=None)
    
    start_time = time.time()
    iterations = 5
    for i in range(iterations):
        await pipeline.execute_audit(snapshot)
    
    duration = time.time() - start_time
    avg_duration = (duration / iterations) * 1000
    print(f"  Iterations: {iterations}")
    print(f"  Average pipeline execution latency: {avg_duration:.2f} ms")
    print(f"  Throughput: {iterations / duration:.2f} pipelines/sec")

def main():
    asyncio.run(benchmark_pipeline())

if __name__ == "__main__":
    main()
