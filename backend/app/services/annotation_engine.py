from typing import List, Dict, Any, Optional
from app.models.analysis import RepositoryAnalysis
from app.scoring.rules import registry as rules_registry

class RepositoryAnnotation:
    def __init__(
        self,
        rule_id: str,
        level: str,  # 'repository', 'file', 'line'
        path: str,
        message: str,
        suggestion: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ):
        self.rule_id = rule_id
        self.level = level
        self.path = path
        self.message = message
        self.suggestion = suggestion
        self.start_line = start_line
        self.end_line = end_line

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "rule_id": self.rule_id,
            "level": self.level,
            "path": self.path,
            "message": self.message,
            "suggestion": self.suggestion
        }
        if self.start_line is not None:
            result["start_line"] = self.start_line
        if self.end_line is not None:
            result["end_line"] = self.end_line
        return result


class RepositoryAnnotationEngine:
    @staticmethod
    def generate_annotations(analysis: RepositoryAnalysis, raw_files_content: Optional[Dict[str, str]] = None) -> List[RepositoryAnnotation]:
        """Translates repository evaluation failures and code smells into multi-level annotations."""
        annotations = []
        raw_files = raw_files_content or {}

        # 1. Map failed scoring rules
        # Evaluate all registered rules against the RepositoryAnalysis
        for rule in rules_registry.get_rules():
            rule_res = rule.evaluate(analysis)
            if not rule_res.passed:
                rule_id = rule.id
                
                if rule_id == "RULE_001_LICENSE_EXISTS":
                    annotations.append(RepositoryAnnotation(
                        rule_id=rule_id,
                        level="repository",
                        path="",
                        message="Missing Open-Source License.",
                        suggestion="Create a LICENSE or COPYING file in the root directory to specify code permissions."
                    ))
                elif rule_id == "RULE_002_README_SETUP":
                    annotations.append(RepositoryAnnotation(
                        rule_id=rule_id,
                        level="file",
                        path="README.md",
                        message="README missing installation or setup instructions.",
                        suggestion="Add a distinct '# Setup' or '# Installation' header in your README.md with clear start steps."
                    ))
                elif rule_id == "RULE_003_README_DEMO":
                    annotations.append(RepositoryAnnotation(
                        rule_id=rule_id,
                        level="file",
                        path="README.md",
                        message="README lacks visual showcase or demo.",
                        suggestion="Add a GIF, screenshot, or deployment link to show reviewers what the project does."
                    ))
                elif rule_id == "RULE_004_CICD_WORKFLOWS":
                    annotations.append(RepositoryAnnotation(
                        rule_id=rule_id,
                        level="repository",
                        path="",
                        message="No Continuous Integration (CI) configuration detected.",
                        suggestion="Create a workflow file under .github/workflows/ci.yml to automate build verification."
                    ))
                elif rule_id == "RULE_005_TESTING_SUITE":
                    annotations.append(RepositoryAnnotation(
                        rule_id=rule_id,
                        level="repository",
                        path="",
                        message="Missing automated testing setup.",
                        suggestion="Establish a tests/ directory containing unit/integration tests (e.g. pytest or jest)."
                    ))
                elif rule_id == "RULE_006_CONTAINERIZATION":
                    annotations.append(RepositoryAnnotation(
                        rule_id=rule_id,
                        level="repository",
                        path="",
                        message="Missing container configurations.",
                        suggestion="Add a Dockerfile in your root directory to enable containerized deployments."
                    ))
                elif rule_id == "RULE_007_CONTRIBUTING_GUIDE":
                    annotations.append(RepositoryAnnotation(
                        rule_id=rule_id,
                        level="repository",
                        path="",
                        message="Missing contributing guide.",
                        suggestion="Create a CONTRIBUTING.md file in the root to help contributors onboard."
                    ))
                elif rule_id == "RULE_008_SECURITY_POLICY":
                    annotations.append(RepositoryAnnotation(
                        rule_id=rule_id,
                        level="repository",
                        path="",
                        message="Missing security reporting policy.",
                        suggestion="Create a SECURITY.md file detailing how security issues should be reported."
                    ))
                elif rule_id == "RULE_009_FRAMEWORK_MATURITY":
                    annotations.append(RepositoryAnnotation(
                        rule_id=rule_id,
                        level="repository",
                        path="",
                        message="Project layout doesn't follow framework standards.",
                        suggestion="Add manifest files (e.g., package.json, setup.py, go.mod) corresponding to your languages."
                    ))
                elif rule_id == "RULE_010_DEPENDENCY_HEALTH":
                    annotations.append(RepositoryAnnotation(
                        rule_id=rule_id,
                        level="repository",
                        path="",
                        message="Missing lockfiles / dependencies health verification.",
                        suggestion="Commit standard lockfiles (package-lock.json, poetry.lock, yarn.lock) to ensure reproducible builds."
                    ))

        # 2. Check for deterministic Line-level code smells (e.g. latest tags in Dockerfiles)
        for filepath, content in raw_files.items():
            if "dockerfile" in filepath.lower():
                lines = content.splitlines()
                for idx, line in enumerate(lines):
                    # Check for FROM with latest tag or missing tag
                    if line.strip().startswith("FROM "):
                        base_image = line.replace("FROM ", "").strip()
                        if ":latest" in base_image:
                            annotations.append(RepositoryAnnotation(
                                rule_id="LINE_RULE_DOCKER_LATEST",
                                level="line",
                                path=filepath,
                                message="Docker base image uses ':latest' tag.",
                                suggestion="Pin your Docker image to a specific version (e.g. python:3.11-slim) to avoid breaking changes.",
                                start_line=idx + 1,
                                end_line=idx + 1
                            ))
                        elif ":" not in base_image and "/" not in base_image and "@sha" not in base_image:
                            annotations.append(RepositoryAnnotation(
                                rule_id="LINE_RULE_DOCKER_NO_TAG",
                                level="line",
                                path=filepath,
                                message="Docker base image lacks version pin.",
                                suggestion="Always specify a version tag for base images to prevent non-reproducible environments.",
                                start_line=idx + 1,
                                end_line=idx + 1
                            ))

            # Check for package.json dependencies with wildcards
            if filepath.lower().endswith("package.json"):
                import json
                try:
                    pkg_data = json.loads(content)
                    deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                    for dep_name, dep_val in deps.items():
                        if dep_val == "*" or dep_val == "latest":
                            # Attempt to find which line it is on
                            lines = content.splitlines()
                            line_no = None
                            for idx, line in enumerate(lines):
                                if f'"{dep_name}"' in line and ("*" in line or "latest" in line):
                                    line_no = idx + 1
                                    break
                            
                            annotations.append(RepositoryAnnotation(
                                rule_id="LINE_RULE_PACKAGE_WILDCARD",
                                level="line" if line_no else "file",
                                path=filepath,
                                message=f"Dependency '{dep_name}' uses wildcard version '{dep_val}'.",
                                suggestion="Pin dependencies to strict versions to safeguard production builds.",
                                start_line=line_no,
                                end_line=line_no
                            ))
                except Exception:
                    pass

        return annotations
