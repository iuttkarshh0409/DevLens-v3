import * as cp from 'child_process';

export interface AuditReport {
  metadata: {
    repo_name: string;
    timestamp: string;
  };
  scorecard: {
    overall_score: number;
    scoring_version: string;
    rule_results: Array<{
      rule_id: string;
      description: string;
      passed: boolean;
      points_awarded: number;
      max_points: number;
      file_path?: string;
      line_number?: number;
    }>;
  };
  narrative?: {
    summary: string;
    recruiter_verdict: string;
    maturity_estimate: string;
    recommendations?: Array<{
      title: string;
      description: string;
      impact: string;
    }>;
  };
  duration_ms: number;
}

export class CLIClient {
  public static async executeOfflineAudit(workspacePath: string): Promise<AuditReport> {
    return new Promise((resolve, reject) => {
      // Execute the local CLI audit command in offline mode
      const cmd = `devlens audit "${workspacePath}" --offline --json`;
      
      cp.exec(cmd, { cwd: workspacePath }, (error, stdout, stderr) => {
        if (error) {
          // If cli tool is missing on system path
          if ((error as any).code === 'ENOENT' || error.message.includes('not found') || error.message.includes('is not recognized')) {
            return reject(new Error('DevLens CLI is not installed or not found on system PATH. Please run "pip install ./backend".'));
          }
          // If execution failed but still returned output
          if (!stdout) {
            return reject(new Error(`CLI Execution failed: ${error.message}\n${stderr}`));
          }
        }
        
        try {
          // Robust bounding search for JSON block
          const startIdx = stdout.indexOf('{');
          const endIdx = stdout.lastIndexOf('}');
          
          if (startIdx === -1 || endIdx === -1) {
            return reject(new Error(`Invalid CLI output format: No JSON payload found. Console log: ${stdout}`));
          }
          
          const jsonStr = stdout.substring(startIdx, endIdx + 1);
          const report: AuditReport = JSON.parse(jsonStr);
          resolve(report);
        } catch (parseError) {
          reject(new Error(`Failed to parse CLI JSON report: ${(parseError as Error).message}\nRaw Output: ${stdout}`));
        }
      });
    });
  }
}
