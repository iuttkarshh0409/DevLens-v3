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
exports.CLIClient = void 0;
const cp = __importStar(require("child_process"));
class CLIClient {
    static async isAvailable() {
        return new Promise((resolve) => {
            cp.exec('devlens --version', (error) => {
                if (error) {
                    if (error.code === 'ENOENT' || error.message.includes('not found') || error.message.includes('is not recognized')) {
                        resolve(false);
                        return;
                    }
                }
                resolve(true);
            });
        });
    }
    static async executeOfflineAudit(workspacePath) {
        return new Promise((resolve, reject) => {
            // Execute the local CLI audit command in offline mode
            const cmd = `devlens audit "${workspacePath}" --offline --json`;
            cp.exec(cmd, { cwd: workspacePath }, (error, stdout, stderr) => {
                if (error) {
                    // If cli tool is missing on system path
                    if (error.code === 'ENOENT' || error.message.includes('not found') || error.message.includes('is not recognized')) {
                        return reject(new Error('Offline audits require the DevLens CLI to be installed and available on your PATH. Install it first, then retry offline mode.'));
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
                    const report = JSON.parse(jsonStr);
                    resolve(report);
                }
                catch (parseError) {
                    reject(new Error(`Failed to parse CLI JSON report: ${parseError.message}\nRaw Output: ${stdout}`));
                }
            });
        });
    }
}
exports.CLIClient = CLIClient;
//# sourceMappingURL=cli.js.map