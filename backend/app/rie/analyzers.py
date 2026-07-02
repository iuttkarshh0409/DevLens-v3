import re
from typing import List
from app.rie.base import BaseAnalyzer, AnalyzerContext
from app.models.analysis import AnalyzerResult

class MetadataAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "MetadataAnalyzer"

    @property
    def priority(self) -> int:
        return 1

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        meta = context.evidence_graph.metadata
        return AnalyzerResult(
            analyzer_name=self.name,
            passed=bool(meta.name),
            evidence={
                "stars": meta.stars,
                "last_updated": meta.last_updated,
                "name": meta.name
            }
        )

class ReadmeAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "ReadmeAnalyzer"

    @property
    def priority(self) -> int:
        return 2

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        readme = context.evidence_graph.readme
        has_readme = len(readme.strip()) > 50
        has_setup = bool(re.search(r"(setup|install|getting started|requirements)", readme, re.I))
        has_demo = bool(re.search(r"(!\[.*\]\(.*\)|screenshot|gif|demo|live)", readme, re.I))
        
        return AnalyzerResult(
            analyzer_name=self.name,
            passed=has_readme and has_setup,
            evidence={
                "has_readme": has_readme,
                "has_setup_instructions": has_setup,
                "has_visual_demos": has_demo,
                "readme_length": len(readme)
            }
        )

class LicenseAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "LicenseAnalyzer"

    @property
    def priority(self) -> int:
        return 3

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        files = [f.lower() for f in context.evidence_graph.files]
        license_files = [f for f in files if "license" in f or "copying" in f]
        passed = len(license_files) > 0
        return AnalyzerResult(
            analyzer_name=self.name,
            passed=passed,
            evidence={
                "detected_license_files": license_files,
                "has_license": passed
            }
        )

class FrameworkAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "FrameworkAnalyzer"

    @property
    def priority(self) -> int:
        return 4

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        files = [f.lower() for f in context.evidence_graph.files]
        detected = []
        if "package.json" in files:
            detected.append("React/NodeJS")
        if "requirements.txt" in files or "pipfile" in files:
            detected.append("Python")
        if "cargo.toml" in files:
            detected.append("Rust")
        
        return AnalyzerResult(
            analyzer_name=self.name,
            passed=len(detected) > 0,
            evidence={
                "detected_frameworks": detected
            }
        )

class DependencyAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "DependencyAnalyzer"

    @property
    def priority(self) -> int:
        return 5

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        files = [f.lower() for f in context.evidence_graph.files]
        manifests = [f for f in files if f in ["package.json", "requirements.txt", "cargo.toml", "go.mod", "pom.xml"]]
        
        return AnalyzerResult(
            analyzer_name=self.name,
            passed=len(manifests) > 0,
            evidence={
                "has_manifests": len(manifests) > 0,
                "detected_manifests": manifests
            }
        )

class CICDAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "CICDAnalyzer"

    @property
    def priority(self) -> int:
        return 6

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        files = [f.lower() for f in context.evidence_graph.files]
        has_ci = False
        detected = []
        
        # Check for GitHub workflows
        for f in files:
            if ".github" in f or "workflows" in f or "actions" in f:
                has_ci = True
                detected.append("GitHub Actions")
            if "vercel.json" in f:
                has_ci = True
                detected.append("Vercel Deploy")
                
        return AnalyzerResult(
            analyzer_name=self.name,
            passed=has_ci,
            evidence={
                "has_ci_cd": has_ci,
                "detected_workflows": detected
            }
        )

class TestingAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "TestingAnalyzer"

    @property
    def priority(self) -> int:
        return 7

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        files = [f.lower() for f in context.evidence_graph.files]
        test_indicators = [f for f in files if "test" in f or "spec" in f]
        passed = len(test_indicators) > 0
        
        return AnalyzerResult(
            analyzer_name=self.name,
            passed=passed,
            evidence={
                "has_tests": passed,
                "test_files": test_indicators
            }
        )

class ArchitectureAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "ArchitectureAnalyzer"

    @property
    def priority(self) -> int:
        return 8

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        files = [f.lower() for f in context.evidence_graph.files]
        patterns = []
        
        # Look for monorepo patterns
        if "backend" in files and "frontend" in files:
            patterns.append("Monorepo (Frontend/Backend)")
        
        # Look for src-based patterns
        if "src" in files or "app" in files:
            patterns.append("Standard Code Directory Layout")
            
        return AnalyzerResult(
            analyzer_name=self.name,
            passed=len(patterns) > 0,
            evidence={
                "has_identifiable_architecture": len(patterns) > 0,
                "detected_patterns": patterns
            }
        )

class CommunityAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "CommunityAnalyzer"

    @property
    def priority(self) -> int:
        return 9

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        files = [f.lower() for f in context.evidence_graph.files]
        community_files = [f for f in files if "contributing" in f or "code_of_conduct" in f or "security.md" in f]
        
        return AnalyzerResult(
            analyzer_name=self.name,
            passed=len(community_files) > 0,
            evidence={
                "has_community_files": len(community_files) > 0,
                "detected_community_files": community_files
            }
        )

class DeveloperExperienceAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "DeveloperExperienceAnalyzer"

    @property
    def priority(self) -> int:
        return 10

    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        files = [f.lower() for f in context.evidence_graph.files]
        dx_tools = []
        if "makefile" in files:
            dx_tools.append("Makefile")
        if "dockerfile" in files or "docker-compose.yml" in files:
            dx_tools.append("Docker Containerization")
            
        return AnalyzerResult(
            analyzer_name=self.name,
            passed=len(dx_tools) > 0,
            evidence={
                "has_dx_tools": len(dx_tools) > 0,
                "detected_tools": dx_tools
            }
        )
