import unittest
from app.rie.registry import AnalyzerRegistry
from app.rie.orchestrator import AnalysisOrchestrator
from app.rie.analyzers import MetadataAnalyzer, ReadmeAnalyzer

class TestRIE(unittest.TestCase):
    def test_registry_ordering(self):
        reg = AnalyzerRegistry()
        m_analyzer = MetadataAnalyzer()
        r_analyzer = ReadmeAnalyzer()
        
        # Register in reverse priority order
        reg.register(r_analyzer)
        reg.register(m_analyzer)
        
        analyzers = reg.get_analyzers()
        self.assertEqual(analyzers[0].name, "MetadataAnalyzer")
        self.assertEqual(analyzers[1].name, "ReadmeAnalyzer")

    def test_orchestration_and_parsing(self):
        mock_repo_data = {
            "name": "DevLens",
            "stars": 42,
            "last_updated": "2026-07-03T01:30:00Z",
            "readme": "## Getting Started\nTo run the project: make setup && npm install.\n![Visual Screenshot](demo.gif)",
            "files": ["package.json", "Makefile", "LICENSE", "src", "backend", "frontend", ".github", "tests"]
        }
        
        analysis = AnalysisOrchestrator.run_analysis(mock_repo_data)
        
        self.assertEqual(analysis.repo_name, "DevLens")
        
        # Test License Analyzer
        license_res = analysis.results.get("LicenseAnalyzer")
        self.assertTrue(license_res.passed)
        self.assertIn("license", license_res.evidence["detected_license_files"])
        
        # Test README Analyzer
        readme_res = analysis.results.get("ReadmeAnalyzer")
        self.assertTrue(readme_res.passed)
        self.assertTrue(readme_res.evidence["has_setup_instructions"])
        self.assertTrue(readme_res.evidence["has_visual_demos"])
        
        # Test Testing Analyzer
        testing_res = analysis.results.get("TestingAnalyzer")
        self.assertTrue(testing_res.passed)
        
        # Test Developer Experience Analyzer
        dx_res = analysis.results.get("DeveloperExperienceAnalyzer")
        self.assertTrue(dx_res.passed)
        self.assertIn("Makefile", dx_res.evidence["detected_tools"])

if __name__ == "__main__":
    unittest.main()
