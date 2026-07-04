"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const cli_1 = require("./client/cli");
const api_1 = require("./client/api");
const diagnostics_1 = require("./providers/diagnostics");
const tree_1 = require("./providers/tree");
const statusbar_1 = require("./providers/statusbar");
const webview_1 = require("./providers/webview");
let lastReport = null;
const treeProvider = new tree_1.DevLensTreeProvider();
function activate(context) {
    console.log('DevLens VS Code Extension is active!');
    // Initialize UI Widgets
    statusbar_1.DevLensStatusBar.initialize();
    vscode.window.registerTreeDataProvider('devlensExplorer', treeProvider);
    // 1. Audit Command (Online / Offline resolver)
    const auditCommand = vscode.commands.registerCommand('devlens.audit', async () => {
        const folders = vscode.workspace.workspaceFolders;
        if (!folders || folders.length === 0) {
            vscode.window.showErrorMessage('No active workspace open. Cannot run audit.');
            return;
        }
        const config = vscode.workspace.getConfiguration('devlens');
        const preferOffline = config.get('offlinePreferred', true);
        const workspaceRoot = folders[0].uri.fsPath;
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Running DevLens Repository Audit...",
            cancellable: false
        }, async (progress) => {
            try {
                let report;
                if (preferOffline) {
                    progress.report({ message: "Running local compliance scans..." });
                    report = await cli_1.CLIClient.executeOfflineAudit(workspaceRoot);
                }
                else {
                    progress.report({ message: "Requesting remote API audit..." });
                    // Online audit needs a repo URL - fallback to offline folder if not a remote repo
                    const repoUrl = await getGitRemoteUrl(workspaceRoot) || workspaceRoot;
                    if (repoUrl.startsWith('http') || repoUrl.includes('github.com')) {
                        report = await api_1.APIClient.executeOnlineAudit(repoUrl);
                    }
                    else {
                        progress.report({ message: "No remote git URL. Falling back to offline scanner..." });
                        report = await cli_1.CLIClient.executeOfflineAudit(workspaceRoot);
                    }
                }
                // Cache report & update UI
                lastReport = report;
                treeProvider.refresh(report);
                statusbar_1.DevLensStatusBar.updateScore(report);
                diagnostics_1.DiagnosticsManager.updateDiagnostics(report, workspaceRoot);
                vscode.window.showInformationMessage(`DevLens Audit Complete! Compliance Score: ${report.scorecard.overall_score.toFixed(1)}/10.0`);
                // Show webview report
                webview_1.DevLensReportPanel.createOrShow(context.extensionUri, report);
            }
            catch (error) {
                vscode.window.showErrorMessage(`DevLens Audit Failed: ${error.message}`);
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
                const report = await cli_1.CLIClient.executeOfflineAudit(workspaceRoot);
                lastReport = report;
                treeProvider.refresh(report);
                statusbar_1.DevLensStatusBar.updateScore(report);
                diagnostics_1.DiagnosticsManager.updateDiagnostics(report, workspaceRoot);
                vscode.window.showInformationMessage(`Offline Audit Success. Score: ${report.scorecard.overall_score.toFixed(1)}`);
                webview_1.DevLensReportPanel.createOrShow(context.extensionUri, report);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Offline Audit Failed: ${error.message}`);
            }
        });
    });
    // 3. View Analytics Command
    const viewAnalyticsCommand = vscode.commands.registerCommand('devlens.viewAnalytics', async () => {
        const installationId = 12345; // Default fallback
        try {
            const analytics = await api_1.APIClient.getAnalyticsOverview(installationId);
            vscode.window.showInformationMessage(`DevLens Analytics: Monitored Repos: ${analytics.total_repositories_monitored}`);
        }
        catch (e) {
            vscode.window.showErrorMessage(`Failed to fetch analytics: ${e.message}`);
        }
    });
    // 4. Configure Authentication Token
    const loginCommand = vscode.commands.registerCommand('devlens.login', async () => {
        const token = await vscode.window.showInputBox({
            prompt: 'Enter your DevLens Personal Access Token (PAT)',
            password: true
        });
        if (token) {
            await vscode.workspace.getConfiguration('devlens').update('token', token, vscode.ConfigurationTarget.Global);
            vscode.window.showInformationMessage('DevLens token updated successfully.');
        }
    });
    // 5. Logout Command
    const logoutCommand = vscode.commands.registerCommand('devlens.logout', async () => {
        await vscode.workspace.getConfiguration('devlens').update('token', '', vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage('DevLens credentials cleared.');
    });
    // 6. Open Report Panel
    const openReportCommand = vscode.commands.registerCommand('devlens.openReport', () => {
        if (lastReport) {
            webview_1.DevLensReportPanel.createOrShow(context.extensionUri, lastReport);
        }
        else {
            vscode.window.showInformationMessage('No audit report available. Run an audit first.');
        }
    });
    // 7. Refresh Scorecard State
    const refreshCommand = vscode.commands.registerCommand('devlens.refresh', () => {
        vscode.commands.executeCommand('devlens.audit');
    });
    // Register command disposables
    context.subscriptions.push(auditCommand, offlineAuditCommand, viewAnalyticsCommand, loginCommand, logoutCommand, openReportCommand, refreshCommand);
    // Auto-audit on open (if enabled)
    const config = vscode.workspace.getConfiguration('devlens');
    if (config.get('autoAuditOnOpen', false)) {
        vscode.commands.executeCommand('devlens.audit');
    }
}
function deactivate() {
    diagnostics_1.DiagnosticsManager.clearDiagnostics();
    statusbar_1.DevLensStatusBar.hide();
}
async function getGitRemoteUrl(workspacePath) {
    return new Promise((resolve) => {
        const cp = require('child_process');
        cp.exec('git config --get remote.origin.url', { cwd: workspacePath }, (err, stdout) => {
            if (err || !stdout) {
                return resolve(null);
            }
            resolve(stdout.trim());
        });
    });
}
//# sourceMappingURL=extension.js.map