# DevLens CLI User Guide

This guide introduces you to the installation, configuration, and everyday use cases of the official DevLens Command Line Interface (CLI).

---

## Installation

### With pip
You can install the DevLens CLI directly from the source repository:
```bash
pip install ./backend
```

### With pipx
For isolated CLI environments (recommended):
```bash
pipx install ./backend
```

---

## Authentication

DevLens CLI uses a Personal Access Token (PAT) to interact with remote FastAPI endpoint APIs.

To log in:
```bash
devlens login
```
This command interactively prompts for your Personal Access Token (PAT) and saves it to your local configuration file.

To clear credentials:
```bash
devlens logout
```

To see active session details:
```bash
devlens whoami
```

---

## Repository Audits

You can audit remote GitHub repositories or scan local folders.

### Online Audit (GitHub)
Triggers remote RIE flows:
```bash
devlens audit https://github.com/owner/repo
```

### Offline Audit (Local Folder)
Runs scanning and RIE metrics calculation entirely locally (no server connection needed):
```bash
devlens audit ./my-local-project --offline
```
This is ideal for local pre-commit checks and development pipelines.

### Output Formatting Flags
- `--score-only`: Print ONLY the score float (e.g. `8.5`).
- `--json`: Render output as structured JSON.
- `--markdown`: Render output as a Markdown summary document.
- `--html`: Render HTML formatted reports.
- Default: Colorful interactive terminal styling with scorecard tables.
