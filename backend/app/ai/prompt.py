import os
from typing import Dict, Any

class PromptBuilder:
    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            # Resolve relative to current package directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            prompts_dir = os.path.join(base_dir, "prompts")
        self.prompts_dir = prompts_dir

    def _read_markdown_file(self, filename: str) -> str:
        filepath = os.path.join(self.prompts_dir, filename)
        if not os.path.exists(filepath):
            # Graceful fallback to default system instruction if file missing
            return "System prompt instruction."
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def get_system_prompt(self) -> str:
        return self._read_markdown_file("system.md")

    def get_user_prompt(self, role: str, context_data: Dict[str, Any]) -> str:
        role_instructions = self._read_markdown_file(f"{role}.md")
        import json
        return f"Role: {role}\nInstructions:\n{role_instructions}\nContext Data: {json.dumps(context_data)}"
