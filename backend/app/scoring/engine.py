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
        rule_results: List[RuleResult] = []
        
        # 1. Run all rules
        for rule in registry.get_rules():
            result = rule.evaluate(analysis)
            rule_results.append(result)

        # 2. Compute category aggregations
        category_raw: Dict[str, float] = {cat: 0.0 for cat in CATEGORY_WEIGHTS}
        category_max: Dict[str, float] = {cat: 0.0 for cat in CATEGORY_WEIGHTS}
        
        for res in rule_results:
            rule_obj = next((r for r in registry.get_rules() if r.id == res.rule_id), None)
            if rule_obj and rule_obj.category in CATEGORY_WEIGHTS:
                category_raw[rule_obj.category] += res.points_awarded
                category_max[rule_obj.category] += res.max_points

        # 3. Calculate category score structures
        category_scores: Dict[str, CategoryScore] = {}
        weighted_sum = 0.0
        max_possible_weighted = sum(CATEGORY_WEIGHTS.values())

        for cat, weight in CATEGORY_WEIGHTS.items():
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
        normalized_merit = (weighted_sum / max_possible_weighted) * 5.0
        raw_final_score = min(10.0, 5.0 + normalized_merit)

        # 5. Apply hard caps (e.g. 7.0 limit for missing tests/CI)
        final_score = evaluate_caps(rule_results, raw_final_score)

        return ScoreReport(
            overall_score=round(final_score, 1),
            category_scores=category_scores,
            rule_results=rule_results,
            scoring_version=SCORING_VERSION,
            timestamp=datetime.utcnow()
        )
