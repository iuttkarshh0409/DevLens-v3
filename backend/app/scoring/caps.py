from typing import List
from app.scoring.models import RuleResult

def evaluate_caps(rule_results: List[RuleResult], current_score: float) -> float:
    # 7.0 Ceiling: If automated tests or CI/CD workflows are missing, cap at 7.0
    has_tests = False
    has_cicd = False
    for res in rule_results:
        if res.rule_id == "RULE_005_TESTING_SUITE" and res.passed:
            has_tests = True
        if res.rule_id == "RULE_004_CICD_WORKFLOWS" and res.passed:
            has_cicd = True
            
    if not has_tests or not has_cicd:
        return min(current_score, 7.0)
    return current_score
