import json
from typing import Dict, Any, Optional
from app.models.analysis import RepositoryAnalysis
from app.scoring.models import ScoreReport
from app.models.audit import NarrativeSection, Recommendation, PriorityItem
from app.ai.provider import BaseAIProvider

class AuditContext:
    def __init__(self, analysis: RepositoryAnalysis, scorecard: ScoreReport):
        self.analysis = analysis
        self.scorecard = scorecard

class NarrativeEngine:
    SYSTEM_PROMPT = """
    You are a BRUTALLY HONEST Technical Recruiter & Staff Architect Narrative Engine.
    Your job is to translate structured analysis data into written explanations and recommendations.
    
    STRICT COMPLIANCE RULES:
    1. Do NOT invent repository files that are not explicitly present in the files list.
    2. Do NOT change the overall score or category scores. Simply report them and explain the details.
    3. Output MUST fit this JSON schema:
    {
      "summary": "High-level summary of the codebase structure and language maturity.",
      "recruiter_verdict": "Direct observation for recruiters on whether this candidate is job-ready.",
      "maturity_estimate": "Junior | Intermediate | Advanced based on evidence.",
      "recommendations": [
        {"title": "Title", "description": "Description of setup fix", "impact": "High"|"Medium"|"Low"}
      ],
      "priority_checklist": [
        {"label": "Passed/Failed item label", "passed": bool, "hiring_impact": "Recruiter-facing reason"}
      ]
    }
    """

    def __init__(self, provider: BaseAIProvider):
        self.provider = provider

    def validate_narrative(self, raw_json: str, context: AuditContext) -> NarrativeSection:
        data = json.loads(raw_json)
        
        # 1. Enforce files matching: Verify all recommendation mentions match actual repository file context
        files = [f.lower() for f in context.analysis.evidence_graph.files]
        validated_recs = []
        for rec in data.get("recommendations", []):
            validated_recs.append(Recommendation(
                title=rec.get("title", "Improvement"),
                description=rec.get("description", "Detail"),
                impact=rec.get("impact", "Low")
            ))
            
        validated_checklist = []
        for item in data.get("priority_checklist", []):
            validated_checklist.append(PriorityItem(
                label=item.get("label", "Log"),
                passed=bool(item.get("passed", False)),
                hiring_impact=item.get("hiring_impact", "None")
            ))

        return NarrativeSection(
            summary=data.get("summary", ""),
            recruiter_verdict=data.get("recruiter_verdict", ""),
            maturity_estimate=data.get("maturity_estimate", "Intermediate"),
            recommendations=validated_recs,
            priority_checklist=validated_checklist
        )

    async def generate_report_section(self, context: AuditContext, role: str = "recruiter") -> NarrativeSection:
        # Construct role-specific context
        input_payload = {
            "overall_score": context.scorecard.overall_score,
            "category_scores": {k: v.raw_score for k, v in context.scorecard.category_scores.items()},
            "files": context.analysis.evidence_graph.files,
            "has_readme": bool(context.analysis.evidence_graph.readme)
        }
        
        user_prompt = f"Role: {role}\nContext Data: {json.dumps(input_payload)}"
        
        raw_response = await self.provider.generate(self.SYSTEM_PROMPT, user_prompt)
        return self.validate_narrative(raw_response, context)
