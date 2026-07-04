import * as vscode from 'vscode';
import { AuditReport } from '../client/cli';

export class DevLensStatusBar {
  private static statusBarItem: vscode.StatusBarItem;

  public static initialize(): void {
    this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    this.statusBarItem.command = 'devlens.openReport';
    this.showPlaceholder();
  }

  public static showPlaceholder(): void {
    const config = vscode.workspace.getConfiguration('devlens');
    if (!config.get<boolean>('showStatusBar', true)) {
      this.statusBarItem.hide();
      return;
    }
    this.statusBarItem.text = '$(shield) DevLens: Ready';
    this.statusBarItem.tooltip = 'Click to open DevLens Audit Dashboard';
    this.statusBarItem.show();
  }

  public static updateScore(report: AuditReport): void {
    const config = vscode.workspace.getConfiguration('devlens');
    if (!config.get<boolean>('showStatusBar', true)) {
      this.statusBarItem.hide();
      return;
    }

    const score = report.scorecard.overall_score;
    let rating = 'Risky';
    if (score >= 8.0) {
      rating = 'Strong';
    } else if (score >= 5.0) {
      rating = 'Fair';
    }

    this.statusBarItem.text = `$(shield) DevLens Score: ${score.toFixed(1)} (${rating})`;
    this.statusBarItem.tooltip = `Latest Audit Score: ${score.toFixed(1)}/10.0 | Verdict: ${rating}\nClick to view full dashboard report.`;
    this.statusBarItem.show();
  }

  public static hide(): void {
    this.statusBarItem.hide();
  }
}
