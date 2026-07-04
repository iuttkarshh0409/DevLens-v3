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
- `devlens.token`: Personal Access Token (PAT) for authenticated API operations.
- `devlens.offlinePreferred`: Prefer running audits locally via the DevLens CLI over online API requests (default: `true`).
- `devlens.autoAuditOnOpen`: Automatically run an audit when opening a workspace.
- `devlens.showStatusBar`: Display the scorecard overall rating in the status bar.

---

## Command Reference

Access the command palette (`Ctrl+Shift+P`) and type `DevLens:`:

- `DevLens: Audit Workspace (Interactive)`: Runs compliance scans on the current open folder (offline by default, or online fallback).
- `DevLens: Run Local Offline Audit`: Forces a local directory scan bypassing remote API servers.
- `DevLens: Show Health Telemetry`: Connects to backend REST APIs to fetch overview metrics.
- `DevLens: Configure PAT Authentication Token`: Interactively input your token.
- `DevLens: Logout (Clear Token)`: Clears active configuration tokens.
- `DevLens: Display Webview Audit Dashboard`: Opens the rich HTML scorecard dashboard.
- `DevLens: Refresh Scorecard State`: Re-runs the compliance audit.
