from abc import ABC, abstractmethod
from app.models.analysis import RepositoryAnalysis
from app.scoring.models import RuleResult

class BaseRule(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def max_points(self) -> float:
        pass

    @abstractmethod
    def evaluate(self, analysis: RepositoryAnalysis) -> RuleResult:
        pass

class RuleRegistry:
    def __init__(self):
        self._rules = []

    def register(self, rule: BaseRule) -> None:
        self._rules.append(rule)

    def get_rules(self) -> list:
        return self._rules

registry = RuleRegistry()

# Concrete Rules
class LicenseRule(BaseRule):
    @property
    def id(self) -> str: return "RULE_001_LICENSE_EXISTS"
    @property
    def category(self) -> str: return "SECURITY"
    @property
    def description(self) -> str: return "Verify the repository contains an open-source license file."
    @property
    def max_points(self) -> float: return 1.0

    def evaluate(self, analysis: RepositoryAnalysis) -> RuleResult:
        res = analysis.results.get("LicenseAnalyzer")
        passed = res.passed if res else False
        return RuleResult(
            rule_id=self.id,
            description=self.description,
            passed=passed,
            points_awarded=1.0 if passed else 0.0,
            max_points=self.max_points,
            failure_reason=None if passed else "No license file (LICENSE/COPYING) detected in root directory."
        )

class ReadmeSetupRule(BaseRule):
    @property
    def id(self) -> str: return "RULE_002_README_SETUP"
    @property
    def category(self) -> str: return "DOCUMENTATION"
    @property
    def description(self) -> str: return "Verify the README contains installation and setup instructions."
    @property
    def max_points(self) -> float: return 1.0

    def evaluate(self, analysis: RepositoryAnalysis) -> RuleResult:
        res = analysis.results.get("ReadmeAnalyzer")
        passed = res.evidence.get("has_setup_instructions", False) if res else False
        return RuleResult(
            rule_id=self.id,
            description=self.description,
            passed=passed,
            points_awarded=1.0 if passed else 0.0,
            max_points=self.max_points,
            failure_reason=None if passed else "README does not contain distinct setup or installation headers."
        )

class ReadmeDemoRule(BaseRule):
    @property
    def id(self) -> str: return "RULE_003_README_DEMO"
    @property
    def category(self) -> str: return "DOCUMENTATION"
    @property
    def description(self) -> str: return "Verify the README includes visual screenshots or demo animations."
    @property
    def max_points(self) -> float: return 1.0

    def evaluate(self, analysis: RepositoryAnalysis) -> RuleResult:
        res = analysis.results.get("ReadmeAnalyzer")
        passed = res.evidence.get("has_visual_demos", False) if res else False
        return RuleResult(
            rule_id=self.id,
            description=self.description,
            passed=passed,
            points_awarded=1.0 if passed else 0.0,
            max_points=self.max_points,
            failure_reason=None if passed else "No screenshots, gifs, or external live demo links detected in README."
        )

class CICDWorkflowRule(BaseRule):
    @property
    def id(self) -> str: return "RULE_004_CICD_WORKFLOWS"
    @property
    def category(self) -> str: return "CICD"
    @property
    def description(self) -> str: return "Verify the repository contains active continuous integration workflows."
    @property
    def max_points(self) -> float: return 1.0

    def evaluate(self, analysis: RepositoryAnalysis) -> RuleResult:
        res = analysis.results.get("CICDAnalyzer")
        passed = res.passed if res else False
        return RuleResult(
            rule_id=self.id,
            description=self.description,
            passed=passed,
            points_awarded=1.0 if passed else 0.0,
            max_points=self.max_points,
            failure_reason=None if passed else "No CI workflow configurations (like GitHub Actions workflows) detected."
        )

class TestingRule(BaseRule):
    @property
    def id(self) -> str: return "RULE_005_TESTING_SUITE"
    @property
    def category(self) -> str: return "TESTING"
    @property
    def description(self) -> str: return "Verify the repository contains an automated unit testing suite."
    @property
    def max_points(self) -> float: return 1.0

    def evaluate(self, analysis: RepositoryAnalysis) -> RuleResult:
        res = analysis.results.get("TestingAnalyzer")
        passed = res.passed if res else False
        return RuleResult(
            rule_id=self.id,
            description=self.description,
            passed=passed,
            points_awarded=1.0 if passed else 0.0,
            max_points=self.max_points,
            failure_reason=None if passed else "No test directories, specs, or test run configurations found."
        )

class ContainerizationRule(BaseRule):
    @property
    def id(self) -> str: return "RULE_006_CONTAINERIZATION"
    @property
    def category(self) -> str: return "DEVELOPER_EXPERIENCE"
    @property
    def description(self) -> str: return "Verify the presence of Docker/container configurations."
    @property
    def max_points(self) -> float: return 1.0

    def evaluate(self, analysis: RepositoryAnalysis) -> RuleResult:
        res = analysis.results.get("DeveloperExperienceAnalyzer")
        passed = False
        if res:
            passed = any("Docker" in tool for tool in res.evidence.get("detected_tools", []))
        return RuleResult(
            rule_id=self.id,
            description=self.description,
            passed=passed,
            points_awarded=1.0 if passed else 0.0,
            max_points=self.max_points,
            failure_reason=None if passed else "No Dockerfile or docker-compose.yml configuration detected."
        )

class ContributingGuideRule(BaseRule):
    @property
    def id(self) -> str: return "RULE_007_CONTRIBUTING_GUIDE"
    @property
    def category(self) -> str: return "COMMUNITY_HEALTH"
    @property
    def description(self) -> str: return "Verify the repository contains contributing instructions."
    @property
    def max_points(self) -> float: return 1.0

    def evaluate(self, analysis: RepositoryAnalysis) -> RuleResult:
        res = analysis.results.get("CommunityAnalyzer")
        passed = False
        if res:
            passed = any("contributing" in f for f in res.evidence.get("detected_community_files", []))
        return RuleResult(
            rule_id=self.id,
            description=self.description,
            passed=passed,
            points_awarded=1.0 if passed else 0.0,
            max_points=self.max_points,
            failure_reason=None if passed else "No CONTRIBUTING.md file detected in the repository."
        )

class SecurityPolicyRule(BaseRule):
    @property
    def id(self) -> str: return "RULE_008_SECURITY_POLICY"
    @property
    def category(self) -> str: return "SECURITY"
    @property
    def description(self) -> str: return "Verify the repository contains a security vulnerabilities policy."
    @property
    def max_points(self) -> float: return 1.0

    def evaluate(self, analysis: RepositoryAnalysis) -> RuleResult:
        res = analysis.results.get("CommunityAnalyzer")
        passed = False
        if res:
            passed = any("security" in f for f in res.evidence.get("detected_community_files", []))
        return RuleResult(
            rule_id=self.id,
            description=self.description,
            passed=passed,
            points_awarded=1.0 if passed else 0.0,
            max_points=self.max_points,
            failure_reason=None if passed else "No SECURITY.md policy file detected."
        )

class FrameworkMaturityRule(BaseRule):
    @property
    def id(self) -> str: return "RULE_009_FRAMEWORK_MATURITY"
    @property
    def category(self) -> str: return "ARCHITECTURE"
    @property
    def description(self) -> str: return "Verify code layout uses standard frameworks or package directories."
    @property
    def max_points(self) -> float: return 1.0

    def evaluate(self, analysis: RepositoryAnalysis) -> RuleResult:
        res = analysis.results.get("FrameworkAnalyzer")
        passed = res.passed if res else False
        return RuleResult(
            rule_id=self.id,
            description=self.description,
            passed=passed,
            points_awarded=1.0 if passed else 0.0,
            max_points=self.max_points,
            failure_reason=None if passed else "No standard package manifests detected to confirm language framework."
        )

class DependencyHealthRule(BaseRule):
    @property
    def id(self) -> str: return "RULE_010_DEPENDENCY_HEALTH"
    @property
    def category(self) -> str: return "DEPENDENCIES"
    @property
    def description(self) -> str: return "Verify the presence of package lock files."
    @property
    def max_points(self) -> float: return 1.0

    def evaluate(self, analysis: RepositoryAnalysis) -> RuleResult:
        res = analysis.results.get("DependencyAnalyzer")
        passed = res.passed if res else False
        return RuleResult(
            rule_id=self.id,
            description=self.description,
            passed=passed,
            points_awarded=1.0 if passed else 0.0,
            max_points=self.max_points,
            failure_reason=None if passed else "No dependency manifests (e.g. package.json, requirements.txt) detected."
        )

# Register default rules
registry.register(LicenseRule())
registry.register(ReadmeSetupRule())
registry.register(ReadmeDemoRule())
registry.register(CICDWorkflowRule())
registry.register(TestingRule())
registry.register(ContainerizationRule())
registry.register(ContributingGuideRule())
registry.register(SecurityPolicyRule())
registry.register(FrameworkMaturityRule())
registry.register(DependencyHealthRule())
