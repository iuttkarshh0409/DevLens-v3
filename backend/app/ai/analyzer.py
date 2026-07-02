import json
from typing import Dict, Any
from app.core.config import client_groq
from app.core.logging import logger

class Analyzer:
    SYSTEM_PROMPT = """
    You are a BRUTALLY HONEST Technical Recruiter using a DETERMINISTIC ALGORITHM.
    
    CRITICAL RULE:
    - IF "Automated Tests" AND "CI/CD" are missing from the project files: THE SCORE CANNOT EXCEED 7.0. This is a hard limit.
    
    SCORING CALCULATION (Show math in 'logic_scratchpad'):
    1. BASE: 5.0
    2. MERIT (Apply ONLY if unique/complex):
       - Unique/Innovative Domain (Not a clone): +1.5
       - Professional Architecture (Complex patterns): +1.5
    3. DEDUCTIONS (Must mirror 'readme_audits' booleans exactly):
       - IF License is false: -1.0
       - IF Detailed Setup Guide is false: -1.0
       - IF Visual Demos (Screenshots/GIFs) is false: -1.0
       - IF Generic Tutorial/Clone App: -2.0
    
    DETERMINISM:
    The 'logic_scratchpad' MUST match the 'readme_audits' booleans. If a boolean is False, the deduction MUST be in the scratchpad.
    
    STRICT JSON OUTPUT:
    {
      "logic_scratchpad": "string (5.0 + Merit - Deductions = Score)",
      "score": float (Final score 0.0 to 10.0), 
      "status": "ELITE" (9+) | "STRONG" (7.5-9) | "INTERVIEW" (6-7.5) | "POLISH" (3-6) | "REJECT" (<3), 
      "feedback": "string (Direct, sharp, personalized advice)",
      "wow_insight": {"title": "string", "description": "string"},
      "checklist": [{"title": "string", "impact": "High"|"Medium"|"Low", "hiring_impact": "string"}],
      "readme_audits": [
        {"label": "Project Description", "passed": bool},
        {"label": "Detailed Setup Guide", "passed": bool},
        {"label": "Technology Summary", "passed": bool},
        {"label": "Contribution Guidelines", "passed": bool},
        {"label": "License (MIT/GPL)", "passed": bool},
        {"label": "Architecture Highlights", "passed": bool},
        {"label": "Visual Demos", "passed": bool}
      ]
    }
    """

    @staticmethod
    async def run(repo_data: Dict[str, Any], retries=1) -> Dict[str, Any]:
        for attempt in range(retries + 1):
            try:
                response = await client_groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": Analyzer.SYSTEM_PROMPT},
                        {"role": "user", "content": json.dumps(repo_data)}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.0
                )
                
                content = response.choices[0].message.content
                analysis = json.loads(content)
                
                if "wow_insight" not in analysis:
                    analysis["wow_insight"] = {"title": "Recruiter's Vibe Check", "description": "Analysis is clean, but no specific 'hidden signal' was detected."}

                return analysis

            except Exception as e:
                logger.error(f"Groq LLM Error (Attempt {attempt}): {str(e)}")
                if attempt == retries:
                    return {
                        "score": 0.0, "status": "Audit Failed", "feedback": "Groq analysis engine failed. Please try again.",
                        "wow_insight": {"title": "Failed", "description": "Unable to complete vibe check."},
                        "checklist": [], "readme_audits": []
                    }
