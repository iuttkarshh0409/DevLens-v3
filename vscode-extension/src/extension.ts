import * as vscode from 'vscode';
import { CLIClient, AuditReport } from './client/cli';
import { APIClient } from './client/api';
import { DiagnosticsManager } from './providers/diagnostics';
import { DevLensTreeProvider } from './providers/tree';
import { DevLensStatusBar } from './providers/statusbar';
import { DevLensReportPanel } from './providers/webview';

let lastReport: AuditReport | null = null;
const treeProvider = new DevLensTreeProvider();

export function activate(context: vscode.ExtensionContext) {
  console.log('DevLens VS Code Extension is active!');

  // Bind secret storage to APIClient
  APIClient.secretStorage = context.secrets;

  // Auto-migrate legacy plaintext token configuration to VS Code SecretStorage
  (async () => {
    const config = vscode.workspace.getConfiguration('devlens');
    const legacyToken = config.get<string>('token');
    if (legacyToken) {
      await context.secrets.store('devlens.token', legacyToken);
      await config.update('token', undefined, vscode.ConfigurationTarget.Global);
      console.log('Successfully migrated token to VS Code SecretStorage.');
    }
  })();

  // Initialize UI Widgets
  DevLensStatusBar.initialize();
  vscode.window.registerTreeDataProvider('devlensExplorer', treeProvider);

  // 1. Audit Command (Online / Offline resolver)
  const auditCommand = vscode.commands.registerCommand('devlens.audit', async () => {
    const folders = vscode.workspace.workspaceFolders;
    if (!folders || folders.length === 0) {
      vscode.window.showErrorMessage('No active workspace open. Cannot run audit.');
      return;
    }

    const config = vscode.workspace.getConfiguration('devlens');
    const preferOffline = config.get<boolean>('offlinePreferred', true);
    const workspaceRoot = folders[0].uri.fsPath;

    await vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: "Running DevLens Repository Audit...",
      cancellable: false
    }, async (progress) => {
      try {
        let report: AuditReport;
        if (preferOffline) {
          progress.report({ message: "Running local compliance scans..." });
          report = await CLIClient.executeOfflineAudit(workspaceRoot);
        } else {
          progress.report({ message: "Requesting remote API audit..." });
          // Online audit needs a repo URL - fallback to offline folder if not a remote repo
          const repoUrl = await getGitRemoteUrl(workspaceRoot) || workspaceRoot;
          if (repoUrl.startsWith('http') || repoUrl.includes('github.com')) {
            report = await APIClient.executeOnlineAudit(repoUrl);
          } else {
            progress.report({ message: "No remote git URL. Falling back to offline scanner..." });
            report = await CLIClient.executeOfflineAudit(workspaceRoot);
          }
        }

        // Cache report & update UI
        lastReport = report;
        treeProvider.refresh(report);
        DevLensStatusBar.updateScore(report);
        DiagnosticsManager.updateDiagnostics(report, workspaceRoot);

        vscode.window.showInformationMessage(`DevLens Audit Complete! Compliance Score: ${report.scorecard.overall_score.toFixed(1)}/10.0`);
        
        // Show webview report
        DevLensReportPanel.createOrShow(context.extensionUri, report);
      } catch (error) {
        vscode.window.showErrorMessage(`DevLens Audit Failed: ${(error as Error).message}`);
      }
    });
  });

  // 2. Explicit Offline Audit Command
  const offlineAuditCommand = vscode.commands.registerCommand('devlens.offlineAudit', async () => {
    const folders = vscode.workspace.workspaceFolders;
    if (!folders || folders.length === 0) {
      vscode.window.showErrorMessage('No workspace open to audit.');
      return;
    }
    const workspaceRoot = folders[0].uri.fsPath;

    await vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: "Executing Offline Compliance Scan...",
      cancellable: false
    }, async () => {
      try {
        const report = await CLIClient.executeOfflineAudit(workspaceRoot);
        lastReport = report;
        treeProvider.refresh(report);
        DevLensStatusBar.updateScore(report);
        DiagnosticsManager.updateDiagnostics(report, workspaceRoot);
        vscode.window.showInformationMessage(`Offline Audit Success. Score: ${report.scorecard.overall_score.toFixed(1)}`);
        DevLensReportPanel.createOrShow(context.extensionUri, report);
      } catch (error) {
        vscode.window.showErrorMessage(`Offline Audit Failed: ${(error as Error).message}`);
      }
    });
  });

  // 3. View Analytics Command
  const viewAnalyticsCommand = vscode.commands.registerCommand('devlens.viewAnalytics', async () => {
    const installationId = 12345; // Default fallback
    try {
      const analytics = await APIClient.getAnalyticsOverview(installationId);
      vscode.window.showInformationMessage(`DevLens Analytics: Monitored Repos: ${analytics.total_repositories_monitored}`);
    } catch (e) {
      vscode.window.showErrorMessage(`Failed to fetch analytics: ${(e as Error).message}`);
    }
  });

  // 4. Configure Authentication Token
  const loginCommand = vscode.commands.registerCommand('devlens.login', async () => {
    const token = await vscode.window.showInputBox({
      prompt: 'Enter your DevLens Personal Access Token (PAT)',
      password: true
    });
    if (token) {
      await context.secrets.store('devlens.token', token);
      vscode.window.showInformationMessage('DevLens token updated successfully.');
    }
  });

  // 5. Logout Command
  const logoutCommand = vscode.commands.registerCommand('devlens.logout', async () => {
    await context.secrets.delete('devlens.token');
    vscode.window.showInformationMessage('DevLens credentials cleared.');
  });

  // 6. Open Report Panel
  const openReportCommand = vscode.commands.registerCommand('devlens.openReport', () => {
    if (lastReport) {
      DevLensReportPanel.createOrShow(context.extensionUri, lastReport);
    } else {
      vscode.window.showInformationMessage('No audit report available. Run an audit first.');
    }
  });

  // 7. Refresh Scorecard State
  const refreshCommand = vscode.commands.registerCommand('devlens.refresh', () => {
    vscode.commands.executeCommand('devlens.audit');
  });

  // Register command disposables
  context.subscriptions.push(
    auditCommand,
    offlineAuditCommand,
    viewAnalyticsCommand,
    loginCommand,
    logoutCommand,
    openReportCommand,
    refreshCommand
  );

  // Auto-audit on open (if enabled)
  const config = vscode.workspace.getConfiguration('devlens');
  if (config.get<boolean>('autoAuditOnOpen', false)) {
    vscode.commands.executeCommand('devlens.audit');
  }
}

export function deactivate() {
  DiagnosticsManager.clearDiagnostics();
  DevLensStatusBar.hide();
}

async function getGitRemoteUrl(workspacePath: string): Promise<string | null> {
  return new Promise((resolve) => {
    const cp = require('child_process');
    cp.exec('git config --get remote.origin.url', { cwd: workspacePath }, (err: any, stdout: string) => {
      if (err || !stdout) {
        return resolve(null);
      }
      resolve(stdout.trim());
    });
  });
}
