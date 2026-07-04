# DevLens CLI Reference Guide

Detailed command hierarchy, flags, configuration options, and exit status codes.

---

## Command Hierarchy

- `devlens [GLOBAL FLAGS]`
  - `login`
  - `logout`
  - `whoami`
  - `audit <repo_or_path> [AUDIT FLAGS]`
  - `version`
  - `config`
    - `init`
    - `show`
    - `set <key> <value>`
  - `analytics`
    - `overview`
    - `trends`
    - `repositories`
    - `export`
  - `cache`
    - `invalidate`

---

## Command Reference

### `devlens audit`
```text
Arguments:
  repo_or_path        GitHub Repository URL or Local Directory Path.

Options:
  -o, --offline       Inspect local repository offline using built-in engine.
  --json              Print audit results as raw JSON.
  --markdown          Print audit results in Markdown format.
  --html              Print audit results in HTML format.
  --score-only        Print ONLY the final overall score float.
```

---

## Exit Status Codes

The CLI maps failures to the following exit codes:

- `0`: Execution succeeded.
- `1`: Unexpected execution error.
- `2`: Network API server connection failure.
- `3`: Active credentials invalid or unauthorized.
- `4`: Configuration TOML reading or writing failure.
- `5`: Offline scanner error.
- `6`: Server error (HTTP 5xx).
- `7`: Client parameter or bad request error (HTTP 4xx).
