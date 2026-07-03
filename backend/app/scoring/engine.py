from datetime import datetime
from typing import Dict, List
from app.models.analysis import RepositoryAnalysis
from app.scoring.models import ScoreReport, CategoryScore, RuleResult
from app.scoring.rules import registry
from app.scoring.weights import CATEGORY_WEIGHTS
from app.scoring.caps import evaluate_caps
from app.scoring.version import SCORING_VERSION

class ScoringEngine:
    @staticmethod
    def calculate_score(analysis: RepositoryAnalysis) -> ScoreReport:
        # Load policy configurations if present
        from app.core.config_loader import load_repository_policy
        raw_config = None
        if analysis.evidence_graph.raw_response:
            raw_config = analysis.evidence_graph.raw_response.get("devlens_config")
        policy = load_repository_policy(raw_config)

        rule_analyzers = {
            "RULE_001_LICENSE_EXISTS": "LicenseAnalyzer",
            "RULE_002_README_SETUP": "ReadmeAnalyzer",
            "RULE_003_README_DEMO": "ReadmeAnalyzer",
            "RULE_004_CICD_WORKFLOWS": "CICDAnalyzer",
            "RULE_005_TESTING_SUITE": "TestingAnalyzer",
            "RULE_006_CONTAINERIZATION": "DeveloperExperienceAnalyzer",
            "RULE_007_CONTRIBUTING_GUIDE": "CommunityAnalyzer",
            "RULE_008_SECURITY_POLICY": "CommunityAnalyzer",
            "RULE_009_FRAMEWORK_MATURITY": "FrameworkAnalyzer",
            "RULE_010_DEPENDENCY_HEALTH": "DependencyAnalyzer"
        }

        rule_results: List[RuleResult] = []
        
        # 1. Run all rules (or subset filtered by policy)
        for rule in registry.get_rules():
            # If enabledAnalyzers is specified in policy, check if this rule's analyzer is enabled
            rule_analyzer = rule_analyzers.get(rule.id)
            if policy.enabled_analyzers and rule_analyzer not in policy.enabled_analyzers:
                # Rule is disabled, skip it or mark it as passed by default
                continue
                
            result = rule.evaluate(analysis)
            rule_results.append(result)

        # 2. Compute category aggregations
        weights = dict(CATEGORY_WEIGHTS)
        # Apply weight overrides from policy
        for cat, w in policy.weights.items():
            if cat in weights:
                weights[cat] = w

        category_raw: Dict[str, float] = {cat: 0.0 for cat in weights}
        category_max: Dict[str, float] = {cat: 0.0 for cat in weights}
        
        for res in rule_results:
            rule_obj = next((r for r in registry.get_rules() if r.id == res.rule_id), None)
            if rule_obj and rule_obj.category in weights:
                category_raw[rule_obj.category] += res.points_awarded
                category_max[rule_obj.category] += res.max_points

        # 3. Calculate category score structures
        category_scores: Dict[str, CategoryScore] = {}
        weighted_sum = 0.0
        max_possible_weighted = sum(weights.values())

        for cat, weight in weights.items():
            # If no rules exist in category, raw score defaults to 1.0 (perfect)
            raw = 1.0
            if category_max[cat] > 0:
                raw = category_raw[cat] / category_max[cat]
                
            weighted = raw * weight
            weighted_sum += weighted
            category_scores[cat] = CategoryScore(
                category_name=cat,
                raw_score=raw,
                weighted_score=weighted,
                max_contribution=weight
            )

        # 4. Map to base 5.0 to 10.0 scale:
        # Base is 5.0, merit additions scale the remaining 5.0 points based on category completion
        if max_possible_weighted > 0:
            normalized_merit = (weighted_sum / max_possible_weighted) * 5.0
        else:
            normalized_merit = 5.0
        raw_final_score = min(10.0, 5.0 + normalized_merit)

        # 5. Apply hard caps (e.g. 7.0 limit for missing tests/CI)
        final_score = evaluate_caps(rule_results, raw_final_score, policy)

        return ScoreReport(
            overall_score=round(final_score, 1),
            category_scores=category_scores,
            rule_results=rule_results,
            scoring_version=SCORING_VERSION,
            timestamp=datetime.utcnow()
        )

