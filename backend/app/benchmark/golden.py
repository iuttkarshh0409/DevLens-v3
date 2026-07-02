from app.benchmark.models import ExpectedBenchmark

GOLDEN_BENCHMARKS = [
    ExpectedBenchmark(
        repo_name="ExcellentPortfolio",
        expected_framework="React/NodeJS",
        expected_architecture="Monorepo (Frontend/Backend)",
        min_score=8.5,
        max_score=10.0,
        expected_findings=["RULE_001_LICENSE_EXISTS", "RULE_005_TESTING_SUITE", "RULE_004_CICD_WORKFLOWS"],
        difficulty_level="Hard",
        tags=["portfolio", "full-stack"]
    ),
    ExpectedBenchmark(
        repo_name="TutorialClone",
        expected_framework="React/NodeJS",
        expected_architecture="Standard Code Directory Layout",
        min_score=3.0,
        max_score=7.0,
        expected_findings=["RULE_009_FRAMEWORK_MATURITY"],
        difficulty_level="Medium",
        tags=["clone", "boilerplate"]
    ),
    ExpectedBenchmark(
        repo_name="DockerizedApp",
        expected_framework="Python",
        expected_architecture="Standard Code Directory Layout",
        min_score=7.0,
        max_score=8.5,
        expected_findings=["RULE_006_CONTAINERIZATION"],
        difficulty_level="Medium",
        tags=["docker", "deployment"]
    )
]

MOCK_BENCHMARK_REPOS = {
    "ExcellentPortfolio": {
        "name": "ExcellentPortfolio",
        "stars": 25,
        "last_updated": "2026-07-03",
        "readme": "## Getting Started\nTo run: make build && npm run dev.\n![Visual Screenshot](demo.gif)\nContributions welcome in CONTRIBUTING.md",
        "files": ["package.json", "Makefile", "LICENSE", "backend", "frontend", "conftest.py", ".github", "security.md", "contributing.md"]
    },
    "TutorialClone": {
        "name": "TutorialClone",
        "stars": 0,
        "last_updated": "2026-07-03",
        "readme": "A basic React boilerplate app.",
        "files": ["package.json", "src", "public"]
    },
    "DockerizedApp": {
        "name": "DockerizedApp",
        "stars": 12,
        "last_updated": "2026-07-03",
        "readme": "## Setup Guide\nRun with docker-compose up.",
        "files": ["requirements.txt", "Dockerfile", "docker-compose.yml", "LICENSE", "src"]
    }
}
