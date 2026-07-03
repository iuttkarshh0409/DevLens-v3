from typing import List, Dict, Any, Optional
from app.models.analysis import EvidenceGraph

class RepositoryInsightsService:
    @staticmethod
    def extract_insights(graph: EvidenceGraph) -> Dict[str, Any]:
        """Deterministically extracts repository tech stack metadata and characteristics."""
        files = graph.files
        readme = graph.readme.lower()
        
        frontend = []
        backend = []
        ci = []
        testing = []
        containerization = []
        license_info = "None"
        package_managers = []
        architecture = "Standard"
        deployment = []

        # Convert files list to lower cases for fast lookup
        files_set = {f.lower() for f in files}

        # 1. Package Managers & Framework Hooks
        has_package_json = False
        has_requirements_txt = False
        has_poetry_lock = False
        
        for f in files_set:
            if "package.json" in f:
                has_package_json = True
            if "requirements.txt" in f:
                has_requirements_txt = True
            if "poetry.lock" in f or ("pyproject.toml" in f and "poetry" in readme):
                has_poetry_lock = True
            
            # Package Manager mapping
            if "package-lock.json" in f and "npm" not in package_managers:
                package_managers.append("npm")
            if "yarn.lock" in f and "yarn" not in package_managers:
                package_managers.append("yarn")
            if "pnpm-lock.yaml" in f and "pnpm" not in package_managers:
                package_managers.append("pnpm")
            if "requirements.txt" in f and "pip" not in package_managers:
                package_managers.append("pip")
            if ("poetry.lock" in f or "pyproject.toml" in f) and "poetry" not in package_managers:
                package_managers.append("poetry")
            if ("pipfile" in f or "pipfile.lock" in f) and "pipenv" not in package_managers:
                package_managers.append("pipenv")
            if "hatch.toml" in f and "hatch" not in package_managers:
                package_managers.append("hatch")
            if "uv.lock" in f and "uv" not in package_managers:
                package_managers.append("uv")
            if "pom.xml" in f and "maven" not in package_managers:
                package_managers.append("maven")
            if ("build.gradle" in f or "build.gradle.kts" in f) and "gradle" not in package_managers:
                package_managers.append("gradle")
            if ("cargo.toml" in f or "cargo.lock" in f) and "cargo" not in package_managers:
                package_managers.append("cargo")
            if ("go.mod" in f or "go.sum" in f) and "go" not in package_managers:
                package_managers.append("go")
            if ("composer.json" in f or "composer.lock" in f) and "composer" not in package_managers:
                package_managers.append("composer")
            if (f.endswith(".csproj") or "packages.config" in f) and "nuget" not in package_managers:
                package_managers.append("nuget")
            if "bun.lockb" in f and "bun" not in package_managers:
                package_managers.append("bun")

        # 2. Frontend / Backend Stack Detection
        # Check files content / naming conventions
        if has_package_json:
            # Check README for clues if files is shallow
            if "react" in readme or any("react" in f for f in files_set):
                frontend.append("React")
            if "vue" in readme or any("vue" in f for f in files_set):
                frontend.append("Vue")
            if "angular" in readme or any("angular" in f for f in files_set):
                frontend.append("Angular")
            if "svelte" in readme or any("svelte" in f for f in files_set):
                frontend.append("Svelte")
            if "tailwind" in readme or any("tailwind" in f for f in files_set):
                frontend.append("Tailwind")
            if "express" in readme or any("express" in f for f in files_set):
                backend.append("Express")

        # Python frameworks
        if has_requirements_txt or has_poetry_lock or any(f.endswith(".py") for f in files_set):
            if "fastapi" in readme or any("main.py" in f or "fastapi" in f for f in files_set):
                backend.append("FastAPI")
            if "django" in readme or any("manage.py" in f for f in files_set):
                backend.append("Django")
            if "flask" in readme or any("app.py" in f or "flask" in f for f in files_set):
                backend.append("Flask")

        # Java & Rust & Go Backend Detection
        if "maven" in package_managers or "gradle" in package_managers:
            backend.append("Spring Boot")
        if "cargo" in package_managers:
            backend.append("Rust Cargo")
        if "go" in package_managers:
            backend.append("Go Modules")

        # 3. CI Pipelines
        if any(".github/workflows" in f for f in files_set):
            ci.append("GitHub Actions")
        if any(".gitlab-ci.yml" in f for f in files_set):
            ci.append("GitLab CI")
        if any(".circleci/config.yml" in f for f in files_set):
            ci.append("CircleCI")

        # 4. Testing Frameworks
        if "pytest" in readme or any("conftest.py" in f or "test_" in f and f.endswith(".py") for f in files_set):
            testing.append("Pytest")
        if "jest" in readme or any("jest.config" in f for f in files_set):
            testing.append("Jest")
        if "vitest" in readme or any("vitest.config" in f for f in files_set):
            testing.append("Vitest")

        # 5. Containerization & Dev Environments
        if any("dockerfile" in f for f in files_set):
            containerization.append("Docker")
        if any("docker-compose" in f or "compose.yaml" in f or "compose.yml" in f for f in files_set):
            containerization.append("Docker Compose")
        if any("devcontainer.json" in f or ".devcontainer" in f for f in files_set):
            containerization.append("devcontainer")

        # 6. License
        license_files = [f for f in files if f.upper() in ["LICENSE", "LICENCE", "COPYING", "LICENSE.TXT", "LICENSE.MD"]]
        if license_files:
            license_info = license_files[0]

        # 7. Architecture (Monorepo detection)
        # If we have multiple package.json or workspace/orchestration config files
        pkg_json_count = sum(1 for f in files_set if "package.json" in f)
        if pkg_json_count > 1 or any(x in files_set for x in ["turbo.json", "nx.json", "lerna.json", "pnpm-workspace.yaml"]):
            architecture = "Monorepo"
        elif sum(1 for f in files_set if "setup.py" in f or "pyproject.toml" in f) > 1:
            architecture = "Monorepo"

        # 8. Deployment Target
        if any("vercel.json" in f for f in files_set):
            deployment.append("Vercel")
        if any("netlify.toml" in f for f in files_set):
            deployment.append("Netlify")
        if any("procfile" in f for f in files_set):
            deployment.append("Heroku")

        return {
            "frontend": frontend,
            "backend": backend,
            "ci": ci,
            "testing": testing,
            "containerization": containerization,
            "license": license_info,
            "package_managers": package_managers,
            "architecture": architecture,
            "deployment": deployment
        }
