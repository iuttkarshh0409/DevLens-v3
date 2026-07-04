import * as vscode from 'vscode';
import * as path from 'path';
import { AuditReport } from '../client/cli';

export class DiagnosticsManager {
  private static collection = vscode.languages.createDiagnosticCollection('devlens');

  public static updateDiagnostics(report: AuditReport, workspaceRoot: string): void {
    this.collection.clear();
    const diagnosticsMap = new Map<string, vscode.Diagnostic[]>();

    for (const rule of report.scorecard.rule_results) {
      if (!rule.passed && rule.file_path) {
        const targetPath = path.isAbsolute(rule.file_path)
          ? rule.file_path
          : path.join(workspaceRoot, rule.file_path);
          
        const fileUri = vscode.Uri.file(targetPath);
        const line = Math.max(0, (rule.line_number ?? 1) - 1); // 0-indexed line number
        const range = new vscode.Range(line, 0, line, 100);

        const diagnostic = new vscode.Diagnostic(
          range,
          `[DevLens] Rule ${rule.rule_id} failed: ${rule.description} (Points: ${rule.points_awarded}/${rule.max_points})`,
          vscode.DiagnosticSeverity.Warning
        );
        
        diagnostic.code = rule.rule_id;
        diagnostic.source = 'DevLens';

        const list = diagnosticsMap.get(fileUri.toString()) || [];
        list.push(diagnostic);
        diagnosticsMap.set(fileUri.toString(), list);
      }
    }

    for (const [uriStr, diagnostics] of diagnosticsMap.entries()) {
      this.collection.set(vscode.Uri.parse(uriStr), diagnostics);
    }
  }

  public static clearDiagnostics(): void {
    this.collection.clear();
  }
}
