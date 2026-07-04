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
exports.APIClient = void 0;
const vscode = __importStar(require("vscode"));
const http = __importStar(require("http"));
const https = __importStar(require("https"));
const url_1 = require("url");
class APIClient {
    static secretStorage;
    static async getConfiguration() {
        const config = vscode.workspace.getConfiguration('devlens');
        const endpoint = config.get('endpoint', 'http://localhost:8000');
        let token = '';
        if (APIClient.secretStorage) {
            token = await APIClient.secretStorage.get('devlens.token') || '';
        }
        if (!token) {
            token = config.get('token', '');
        }
        return { endpoint, token };
    }
    static async request(method, path, body) {
        const { endpoint, token } = await this.getConfiguration();
        const targetUrl = new url_1.URL(path, endpoint);
        const headers = {
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
                    }
                    catch (e) {
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
    static async executeOnlineAudit(repoUrl) {
        return this.request('POST', '/analyze', { repo_url: repoUrl });
    }
    static async getAnalyticsOverview(installationId) {
        return this.request('GET', `/api/v1/analytics/overview?installation_id=${installationId}`);
    }
    static async getAnalyticsTrends(installationId, metric, period) {
        return this.request('GET', `/api/v1/analytics/trends?installation_id=${installationId}&metric=${metric}&period=${period}`);
    }
    static async getAnalyticsRepositories(installationId, page = 1, limit = 10) {
        return this.request('GET', `/api/v1/analytics/repositories?installation_id=${installationId}&page=${page}&limit=${limit}`);
    }
}
exports.APIClient = APIClient;
//# sourceMappingURL=api.js.map