import os
import json
from typing import Dict, Any

class ScoringConfig:
    def __init__(self, profile_path: str = None):
        if profile_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            profile_path = os.path.join(base_dir, "profile.json")
        
        self.profile_path = profile_path
        self.config_data = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        if not os.path.exists(self.profile_path):
            # Safe hardcoded fallback if config deleted
            return {
                "version": "V3.0",
                "base_score": 5.0,
                "max_score": 10.0,
                "weights": {
                    "DOCUMENTATION": 1.5, "ARCHITECTURE": 1.5, "TESTING": 1.5, "CICD": 1.5,
                    "SECURITY": 1.0, "DEPENDENCIES": 1.0, "COMMUNITY_HEALTH": 1.0, "DEVELOPER_EXPERIENCE": 1.0
                },
                "caps": {"MISSING_TESTS_OR_CICD": 7.0}
            }
        with open(self.profile_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def version(self) -> str:
        return self.config_data.get("version", "V3.0")

    @property
    def base_score(self) -> float:
        return float(self.config_data.get("base_score", 5.0))

    @property
    def max_score(self) -> float:
        return float(self.config_data.get("max_score", 10.0))

    def get_weight(self, category: str) -> float:
        return float(self.config_data.get("weights", {}).get(category, 1.0))

    def get_cap(self, cap_name: str) -> float:
        return float(self.config_data.get("caps", {}).get(cap_name, 7.0))
