import os
import yaml
from typing import Dict, Any, List, Optional
from app.core.logging import logger

DEFAULT_CONFIG = {
    "apiVersion": "devlens.io/v1",
    "kind": "RepositoryPolicy",
    "spec": {
        "analysis": {
            "enabledAnalyzers": []
        },
        "scoring": {
            "weights": {},
            "caps": {}
        },
        "ignore": {
            "paths": []
        }
    }
}

class RepositoryPolicyConfig:
    def __init__(self, raw_data: Dict[str, Any]):
        self.raw_data = raw_data
        self.api_version = raw_data.get("apiVersion", "devlens.io/v1")
        self.kind = raw_data.get("kind", "RepositoryPolicy")
        self.spec = raw_data.get("spec", {})

    @property
    def enabled_analyzers(self) -> List[str]:
        return self.spec.get("analysis", {}).get("enabledAnalyzers", [])

    @property
    def weights(self) -> Dict[str, float]:
        raw_weights = self.spec.get("scoring", {}).get("weights", {})
        return {k: float(v) for k, v in raw_weights.items()}

    @property
    def caps(self) -> Dict[str, float]:
        raw_caps = self.spec.get("scoring", {}).get("caps", {})
        return {k: float(v) for k, v in raw_caps.items()}

    @property
    def ignored_paths(self) -> List[str]:
        return self.spec.get("ignore", {}).get("paths", [])


def load_repository_policy(content: Optional[str]) -> RepositoryPolicyConfig:
    """Parses and validates the contents of a .devlens.yml file."""
    if not content:
        return RepositoryPolicyConfig(DEFAULT_CONFIG)

    try:
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            logger.warning("Invalid .devlens.yml structure. Using default configuration.")
            return RepositoryPolicyConfig(DEFAULT_CONFIG)

        # Validate basic schema
        api_version = data.get("apiVersion")
        kind = data.get("kind")
        if api_version != "devlens.io/v1" or kind != "RepositoryPolicy":
            logger.warning(f"Unsupported apiVersion ({api_version}) or kind ({kind}). Reverting to defaults.")
            return RepositoryPolicyConfig(DEFAULT_CONFIG)

        return RepositoryPolicyConfig(data)
    except Exception as e:
        logger.error(f"Error loading .devlens.yml: {str(e)}. Reverting to defaults.")
        return RepositoryPolicyConfig(DEFAULT_CONFIG)
