# DevLens VS Code Extension User Guide

The official DevLens extension integrates repository audits, compliance metrics, and health telemetry directly into Visual Studio Code.

---

## Installation

### From VSIX Package
1. Download the compiled `.vsix` file.
2. In VS Code, open the Extensions view (`Ctrl+Shift+X`).
3. Click the `...` menu in the top-right corner of the Extensions view.
4. Select **Install from VSIX...** and choose the downloaded file.

---

## Configuration Settings

You can configure the extension by opening VS Code Settings (`Ctrl+,`) and searching for `DevLens`:

- `devlens.endpoint`: Target API server address (default: `http://localhost:8000`).
- `devlens.offlinePreferred`: Prefer running audits locally via the DevLens CLI over online API requests (default: `false`).
- `devlens.autoAuditOnOpen`: Automatically run an audit when opening a workspace.
- `devlens.showStatusBar`: Display the scorecard overall rating in the status bar.

The default first-run behavior is API-backed. If the configured endpoint is still the default localhost server and that server is not running, the extension shows an actionable message explaining that DevLens Server must be started locally or that `devlens.endpoint` should be changed to a reachable production endpoint.

---

## Command Reference

Access the command palette (`Ctrl+Shift+P`) and type `DevLens:`:

- `DevLens: Audit Workspace (Interactive)`: Runs an API-backed audit by default. If offline mode has been explicitly enabled, the extension uses the local DevLens CLI instead.
- `DevLens: Run Local Offline Audit`: Forces a local directory scan through the DevLens CLI.
- `DevLens: Show Health Telemetry`: Connects to backend REST APIs to fetch overview metrics.
- `DevLens: Configure PAT Authentication Token`: Interactively input your token.
- `DevLens: Logout (Clear Token)`: Clears active configuration tokens.
- `DevLens: Display Webview Audit Dashboard`: Opens the rich HTML scorecard dashboard.
- `DevLens: Refresh Scorecard State`: Re-runs the compliance audit.

## Offline Mode

Offline mode remains available, but it depends on the external `devlens` CLI binary being installed and available on your `PATH`.

- If you explicitly enable `devlens.offlinePreferred`, interactive audits will use the CLI workflow.
- If you run `DevLens: Run Local Offline Audit`, the extension checks whether the CLI is available first.
- If the CLI is missing, the extension shows a clear error explaining that the DevLens CLI must be installed before offline audits can be used.
