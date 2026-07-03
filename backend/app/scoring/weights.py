from app.scoring.config import ScoringConfig

config = ScoringConfig()

CATEGORY_WEIGHTS = {
    "DOCUMENTATION": config.get_weight("DOCUMENTATION"),
    "ARCHITECTURE": config.get_weight("ARCHITECTURE"),
    "TESTING": config.get_weight("TESTING"),
    "CICD": config.get_weight("CICD"),
    "SECURITY": config.get_weight("SECURITY"),
    "DEPENDENCIES": config.get_weight("DEPENDENCIES"),
    "COMMUNITY_HEALTH": config.get_weight("COMMUNITY_HEALTH"),
    "DEVELOPER_EXPERIENCE": config.get_weight("DEVELOPER_EXPERIENCE")
}
