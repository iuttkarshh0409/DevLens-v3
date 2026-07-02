from typing import Dict, Any
from app.models.audit import AuditReport

class AuditResponseMapper:
    @staticmethod
    def map_to_legacy_response(report: AuditReport, fetch_time: float, pipeline_time: float) -> Dict[str, Any]:
        score = report.scorecard.overall_score
        
        # Categorize status based on scoring
        if score >= 9.0:
            status = "ELITE"
        elif score >= 7.5:
            status = "STRONG"
        elif score >= 6.0:
            status = "INTERVIEW"
        elif score >= 3.0:
            status = "POLISH"
        else:
            status = "REJECT"

        # Formulate priority checklist
        ui_checklist = []
        if report.narrative:
            for rec in report.narrative.recommendations:
                ui_checklist.append({
                    "title": rec.title,
                    "impact": rec.impact,
                    "hiring_impact": rec.description
                })
        else:
            for res in report.scorecard.rule_results:
                if not res.passed:
                    ui_checklist.append({
                        "title": res.rule_id,
                        "impact": "High" if "LICENSE" in res.rule_id or "TEST" in res.rule_id else "Medium",
                        "hiring_impact": res.failure_reason
                    })

        # Formulate specific checklist evaluations
        ui_audits = []
        rule_label_map = {
            "RULE_001_LICENSE_EXISTS": "License (MIT/GPL)",
            "RULE_002_README_SETUP": "Detailed Setup Guide",
            "RULE_003_README_DEMO": "Visual Demos",
            "RULE_004_CICD_WORKFLOWS": "Architecture Highlights",
            "RULE_005_TESTING_SUITE": "Technology Summary",
            "RULE_007_CONTRIBUTING_GUIDE": "Contribution Guidelines",
            "RULE_009_FRAMEWORK_MATURITY": "Project Description"
        }
        for res in report.scorecard.rule_results:
            label = rule_label_map.get(res.rule_id)
            if label:
                ui_audits.append({
                    "label": label,
                    "passed": res.passed
                })

        return {
            "logic_scratchpad": f"Base: 5.0 | Normal: {score}",
            "score": score,
            "status": status,
            "feedback": report.narrative.recruiter_verdict if report.narrative else "Audit completed.",
            "wow_insight": {
                "title": "Signal Detected",
                "description": report.narrative.summary if report.narrative else "Repository parsing completed successfully."
            },
            "checklist": ui_checklist,
            "readme_audits": ui_audits,
            "timings_ms": {
                "fetch": round(fetch_time, 2),
                "pipeline": round(pipeline_time, 2),
                "total": round(fetch_time + pipeline_time, 2)
            }
        }
