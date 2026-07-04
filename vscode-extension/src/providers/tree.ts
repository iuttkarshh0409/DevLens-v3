import * as vscode from 'vscode';
import { AuditReport } from '../client/cli';

export class DevLensTreeProvider implements vscode.TreeDataProvider<DevLensTreeItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<DevLensTreeItem | undefined | null | void> = new vscode.EventEmitter<DevLensTreeItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<DevLensTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

  private currentReport: AuditReport | null = null;

  public refresh(report: AuditReport | null): void {
    this.currentReport = report;
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: DevLensTreeItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: DevLensTreeItem): Thenable<DevLensTreeItem[]> {
    if (!this.currentReport) {
      return Promise.resolve([
        new DevLensTreeItem('No audit data. Run audit to begin.', vscode.TreeItemCollapsibleState.None, 'info')
      ]);
    }

    if (!element) {
      // Root level items
      const score = this.currentReport.scorecard.overall_score;
      const verdict = this.currentReport.narrative?.recruiter_verdict || 'Ready for audit';
      
      return Promise.resolve([
        new DevLensTreeItem(`Score: ${score.toFixed(1)}/10.0`, vscode.TreeItemCollapsibleState.None, 'score'),
        new DevLensTreeItem(`Verdict: ${verdict}`, vscode.TreeItemCollapsibleState.None, 'verdict'),
        new DevLensTreeItem('Recommendations', vscode.TreeItemCollapsibleState.Collapsed, 'rec-group'),
        new DevLensTreeItem('Checked Rules', vscode.TreeItemCollapsibleState.Collapsed, 'rule-group')
      ]);
    }

    // Recommendations group children
    if (element.contextValue === 'rec-group') {
      const recs = this.currentReport.narrative?.recommendations || [];
      if (recs.length === 0) {
        return Promise.resolve([new DevLensTreeItem('No recommendations found.', vscode.TreeItemCollapsibleState.None)]);
      }
      return Promise.resolve(recs.map(r => new DevLensTreeItem(`[${r.impact}] ${r.title}: ${r.description}`, vscode.TreeItemCollapsibleState.None, 'rec-item')));
    }

    // Checked Rules group children
    if (element.contextValue === 'rule-group') {
      const rules = this.currentReport.scorecard.rule_results || [];
      return Promise.resolve(
        rules.map(r => {
          const icon = r.passed ? '✓' : '✗';
          return new DevLensTreeItem(`${icon} ${r.rule_id}: ${r.description}`, vscode.TreeItemCollapsibleState.None, 'rule-item');
        })
      );
    }

    return Promise.resolve([]);
  }
}

export class DevLensTreeItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState,
    public readonly contextValue?: string
  ) {
    super(label, collapsibleState);
    this.tooltip = this.label;
    
    // Choose icons dynamically
    if (this.contextValue === 'score') {
      this.iconPath = new vscode.ThemeIcon('dashboard');
    } else if (this.contextValue === 'verdict') {
      this.iconPath = new vscode.ThemeIcon('feedback');
    } else if (this.contextValue === 'rec-group') {
      this.iconPath = new vscode.ThemeIcon('lightbulb');
    } else if (this.contextValue === 'rule-group') {
      this.iconPath = new vscode.ThemeIcon('checklist');
    }
  }
}
