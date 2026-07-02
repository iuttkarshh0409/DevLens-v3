from app.rie.registry import registry
from app.rie.analyzers import (
    MetadataAnalyzer,
    ReadmeAnalyzer,
    LicenseAnalyzer,
    FrameworkAnalyzer,
    DependencyAnalyzer,
    CICDAnalyzer,
    TestingAnalyzer,
    ArchitectureAnalyzer,
    CommunityAnalyzer,
    DeveloperExperienceAnalyzer
)

# Register default analyzers
registry.register(MetadataAnalyzer())
registry.register(ReadmeAnalyzer())
registry.register(LicenseAnalyzer())
registry.register(FrameworkAnalyzer())
registry.register(DependencyAnalyzer())
registry.register(CICDAnalyzer())
registry.register(TestingAnalyzer())
registry.register(ArchitectureAnalyzer())
registry.register(CommunityAnalyzer())
registry.register(DeveloperExperienceAnalyzer())
