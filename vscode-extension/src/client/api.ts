import * as vscode from 'vscode';
import * as http from 'http';
import * as https from 'https';
import { URL } from 'url';
import { AuditReport } from './cli';

export class APIClient {
  private static getConfiguration() {
    const config = vscode.workspace.getConfiguration('devlens');
    const endpoint = config.get<string>('endpoint', 'http://localhost:8000');
    const token = config.get<string>('token', '');
    return { endpoint, token };
  }

  private static request(method: string, path: string, body?: any): Promise<any> {
    const { endpoint, token } = this.getConfiguration();
    const targetUrl = new URL(path, endpoint);
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': 'DevLens-VSCode/1.0.0'
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
      method,
      headers,
      timeout: 30000
    };

    const protocol = targetUrl.protocol === 'https:' ? https : http;

    return new Promise((resolve, reject) => {
      const req = protocol.request(targetUrl.href, options, (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          if (res.statusCode && res.statusCode >= 400) {
            return reject(new Error(`API Error (${res.statusCode}): ${data}`));
          }
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error(`Invalid JSON response: ${data}`));
          }
        });
      });

      req.on('error', (e) => {
        reject(new Error(`API Connection Failed: ${e.message}`));
      });

      if (body) {
        req.write(JSON.stringify(body));
      }
      req.end();
    });
  }

  public static async executeOnlineAudit(repoUrl: string): Promise<AuditReport> {
    return this.request('POST', '/analyze', { repo_url: repoUrl });
  }

  public static async getAnalyticsOverview(installationId: number): Promise<any> {
    return this.request('GET', `/api/v1/analytics/overview?installation_id=${installationId}`);
  }

  public static async getAnalyticsTrends(installationId: number, metric: string, period: string): Promise<any> {
    return this.request('GET', `/api/v1/analytics/trends?installation_id=${installationId}&metric=${metric}&period=${period}`);
  }

  public static async getAnalyticsRepositories(installationId: number, page = 1, limit = 10): Promise<any> {
    return this.request('GET', `/api/v1/analytics/repositories?installation_id=${installationId}&page=${page}&limit=${limit}`);
  }
}
