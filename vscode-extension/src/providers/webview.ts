import * as vscode from 'vscode';
import { AuditReport } from '../client/cli';

export class DevLensReportPanel {
  public static currentPanel: DevLensReportPanel | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];

  public static createOrShow(extensionUri: vscode.Uri, report: AuditReport): void {
    const column = vscode.window.activeTextEditor ? vscode.window.activeTextEditor.viewColumn : undefined;

    if (DevLensReportPanel.currentPanel) {
      DevLensReportPanel.currentPanel.update(report);
      DevLensReportPanel.currentPanel._panel.reveal(column);
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      'devlensReport',
      'DevLens Audit Report',
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        localResourceRoots: [extensionUri]
      }
    );

    DevLensReportPanel.currentPanel = new DevLensReportPanel(panel, report);
  }

  private constructor(panel: vscode.WebviewPanel, report: AuditReport) {
    this._panel = panel;
    this.update(report);

    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
  }

  public update(report: AuditReport): void {
    this._panel.webview.html = this._getHtmlForWebview(report);
  }

  public dispose(): void {
    DevLensReportPanel.currentPanel = undefined;
    this._panel.dispose();
    while (this._disposables.length) {
      const x = this._disposables.pop();
      if (x) {
        x.dispose();
      }
    }
  }

  private _getHtmlForWebview(report: AuditReport): string {
    const score = report.scorecard.overall_score;
    const ratingColor = score >= 8.0 ? '#4caf50' : (score >= 5.0 ? '#ffeb3b' : '#f44336');
    const ratingText = score >= 8.0 ? 'EXCELLENT' : (score >= 5.0 ? 'FAIR' : 'RISKY');
    
    const rulesList = report.scorecard.rule_results.map(r => `
      <div class="rule-item" style="border-left: 4px solid ${r.passed ? '#4caf50' : '#f44336'}">
        <div class="rule-header">
          <strong>${r.rule_id}</strong> - ${r.description}
          <span class="badge" style="background-color: ${r.passed ? '#4caf50' : '#f44336'}">${r.passed ? 'PASSED' : 'FAILED'}</span>
        </div>
        <div class="rule-details">Points: ${r.points_awarded}/${r.max_points}</div>
      </div>
    `).join('');

    const recs = report.narrative?.recommendations || [];
    const recsList = recs.map(r => `
      <div class="rec-item">
        <strong>[${r.impact}] ${r.title}</strong>
        <p>${r.description}</p>
      </div>
    `).join('');

    return `<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>DevLens Audit Report</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          padding: 20px;
          color: var(--vscode-editor-foreground);
          background-color: var(--vscode-editor-background);
        }
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 2px solid var(--vscode-panel-border);
          padding-bottom: 15px;
          margin-bottom: 20px;
        }
        .scorecard {
          padding: 15px;
          border-radius: 8px;
          background-color: var(--vscode-welcomePage-buttonBackground);
          color: var(--vscode-welcomePage-buttonHoverBackground);
          text-align: center;
          max-width: 250px;
        }
        .score-val {
          font-size: 3em;
          font-weight: bold;
        }
        .verdict {
          font-size: 1.2em;
          font-weight: bold;
          margin: 10px 0;
        }
        .section-title {
          font-size: 1.4em;
          border-bottom: 1px solid var(--vscode-panel-border);
          padding-bottom: 5px;
          margin-top: 30px;
        }
        .rule-item {
          padding: 10px;
          margin: 10px 0;
          background-color: var(--vscode-editor-lineHighlightBackground);
          border-radius: 4px;
        }
        .rule-header {
          display: flex;
          justify-content: space-between;
        }
        .badge {
          padding: 2px 6px;
          border-radius: 3px;
          color: white;
          font-size: 0.8em;
          font-weight: bold;
        }
        .rec-item {
          background-color: var(--vscode-keybindingTable-rowsBackground);
          padding: 12px;
          margin: 8px 0;
          border-radius: 4px;
        }
      </style>
    </head>
    <body>
      <div class="header">
        <div>
          <h1>DevLens Audit Report</h1>
          <p>Repository: <strong>${report.metadata.repo_name}</strong></p>
          <p>Analyzed on: ${new Date(report.metadata.timestamp).toLocaleString()}</p>
        </div>
        <div class="scorecard" style="background-color: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 2px solid ${ratingColor}">
          <div class="score-val" style="color: ${ratingColor}">${score.toFixed(1)}</div>
          <div class="verdict" style="color: ${ratingColor}">${ratingText}</div>
          <div>Maturity: ${report.narrative?.maturity_estimate || 'Unknown'}</div>
        </div>
      </div>

      ${report.narrative ? `
      <div class="section-title">AI Narrative Summary</div>
      <p>${report.narrative.summary}</p>
      <p><strong>Recruiter Verdict:</strong> ${report.narrative.recruiter_verdict}</p>
      ` : ''}

      ${recs.length > 0 ? `
      <div class="section-title">Recommendations</div>
      <div>${recsList}</div>
      ` : ''}

      <div class="section-title">Rule Evaluations</div>
      <div>${rulesList}</div>
    </body>
    </html>`;
  }
}
