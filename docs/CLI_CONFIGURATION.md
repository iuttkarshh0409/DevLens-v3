# DevLens CLI Configuration Guide

DevLens CLI supports environment variables, file-based configuration, and CI scripting modes.

---

## Configuration Precedence

1. CLI Command-line arguments & flags (highest priority)
2. Environment variables
3. TOML configuration file at `~/.devlens/config.toml` (or custom path via `DEVLENS_CONFIG` variable)
4. System-level built-in defaults (lowest priority)

---

## Configuration Parameters

The following parameters are supported in `config.toml` and environment variables:

| Key | Description | Environment Variable | Default Value |
| :--- | :--- | :--- | :--- |
| `endpoint` | The target API backend URL | `DEVLENS_ENDPOINT` | `http://localhost:8000` |
| `token` | Personal Access Token (PAT) | `DEVLENS_TOKEN` | `""` |
| `format` | Output style (`rich`, `json`) | `DEVLENS_FORMAT` | `rich` |
| `timeout` | Connection timeout in seconds | `DEVLENS_TIMEOUT` | `30` |
| `organization`| Default target GitHub organization | `DEVLENS_ORGANIZATION`| `""` |
| `installation_id`| Default installation ID | `DEVLENS_INSTALLATION_ID`| `0` |

---

## CI/CD Pipeline Automation

In automated pipelines (such as GitHub Actions, GitLab CI, or Jenkins), you should bypass interactive prompts.

### Example: GitHub Actions Workflow
```yaml
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install DevLens CLI
        run: pip install ./backend
      - name: Run Code Audit Compliance Check
        env:
          DEVLENS_ENDPOINT: https://api.devlens.dev
          DEVLENS_TOKEN: ${{ secrets.DEVLENS_TOKEN }}
        run: |
          SCORE=$(devlens audit ./ --offline --score-only)
          echo "Repository compliance score: $SCORE"
          # Fail step if score drops below fair quality threshold
          if (( $(echo "$SCORE < 5.0" | bc -l) )); then
            echo "Error: Score is below fairness threshold!"
            exit 1
          fi
```
This is fully automated and non-interactive. Colors and Rich tables are disabled automatically when output redirection is detected.
