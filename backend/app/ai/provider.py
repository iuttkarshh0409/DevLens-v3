from abc import ABC, abstractmethod
import json
from app.core.config import get_groq_client, GROQ_API_KEY

class BaseAIProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        pass

class GroqProvider(BaseAIProvider):
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not GROQ_API_KEY or GROQ_API_KEY.lower().startswith("fake"):
            # Return valid mock JSON matching NarrativeSection structure
            return json.dumps({
                "summary": "This is a mock repository intelligence summary.",
                "recruiter_verdict": "Passed basic evaluation checks.",
                "maturity_estimate": "Advanced",
                "recommendations": [
                    {"title": "Enable code analysis", "description": "Configure static checks", "impact": "High"}
                ],
                "priority_checklist": [
                    {"label": "Verify testing coverage", "passed": True, "hiring_impact": "High"}
                ]
            })
            
        client = get_groq_client()
        response = await client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return response.choices[0].message.content


