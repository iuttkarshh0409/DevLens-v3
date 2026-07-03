# .devlens.yml Policy Specification

This document defines the schema, version namespaces, and usage details for `.devlens.yml`.

## Format Schema

```yaml
apiVersion: devlens.io/v1
kind: RepositoryPolicy
spec:
  analysis:
    enabledAnalyzers:
      - LicenseAnalyzer
      - ReadmeAnalyzer
      - CICDAnalyzer
      - TestingAnalyzer
      - DependencyAnalyzer
      - FrameworkAnalyzer
      - CommunityAnalyzer
      - DeveloperExperienceAnalyzer
  scoring:
    weights:
      DOCUMENTATION: 2.0
      TESTING: 2.5
    caps:
      MISSING_TESTS_OR_CICD: 7.5
  ignore:
    paths:
      - "**/tests/fixtures/**"
      - "dist/*"
```

## Options Reference

### `apiVersion`
- **Type**: `string`
- **Required**: `true`
- **Value**: Must be exactly `devlens.io/v1`.

### `kind`
- **Type**: `string`
- **Required**: `true`
- **Value**: Must be exactly `RepositoryPolicy`.

### `spec.analysis.enabledAnalyzers`
- **Type**: `array of strings`
- **Default**: `[]` (All analyzers run by default).
- **Description**: Whitelist of analyzers to execute. If empty, all registered analyzers execute.

### `spec.scoring.weights`
- **Type**: `object` (Key-value mapping of category string to numeric weight)
- **Description**: Custom category score multipliers. Overrides default weights.
- **Valid Categories**: `DOCUMENTATION`, `ARCHITECTURE`, `TESTING`, `CICD`, `SECURITY`, `DEPENDENCIES`, `COMMUNITY_HEALTH`, `DEVELOPER_EXPERIENCE`.

### `spec.scoring.caps`
- **Type**: `object` (Key-value mapping of cap name to limit score)
- **Description**: Overrides scoring ceiling caps.
- **Valid Caps**: `MISSING_TESTS_OR_CICD` (Defaults to `7.0`).

### `spec.ignore.paths`
- **Type**: `array of strings`
- **Description**: File glob patterns to ignore during repository index extraction.

---

## JSON Schema Validation
A JSON Schema is published at [devlens.schema.json](file:///d:/Side Projects/utility-projects/DevLens/backend/app/schemas/devlens.schema.json).
Add the following parameter to your workspace settings to map IDE validation:
```json
"json.schemas": [
  {
    "fileMatch": [
      ".devlens.yml",
      ".devlens.yaml"
    ],
    "url": "http://localhost:8000/app/schemas/devlens.schema.json"
  }
]
```
