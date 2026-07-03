from typing import List, Any
from app.scoring.models import RuleResult
from app.scoring.config import ScoringConfig

config = ScoringConfig()

def evaluate_caps(rule_results: List[RuleResult], current_score: float, policy: Any = None) -> float:
    # Dynamic Ceiling: If automated tests or CI/CD workflows are missing, apply cap
    has_tests = False
    has_cicd = False
    for res in rule_results:
        if res.rule_id == "RULE_005_TESTING_SUITE" and res.passed:
            has_tests = True
        if res.rule_id == "RULE_004_CICD_WORKFLOWS" and res.passed:
            has_cicd = True
            
    if not has_tests or not has_cicd:
        cap_val = config.get_cap("MISSING_TESTS_OR_CICD")
        if policy and "MISSING_TESTS_OR_CICD" in policy.caps:
            cap_val = policy.caps["MISSING_TESTS_OR_CICD"]
        return min(current_score, cap_val)
    return current_score

