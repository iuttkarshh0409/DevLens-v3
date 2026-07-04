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
exports.DiagnosticsManager = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
class DiagnosticsManager {
    static collection = vscode.languages.createDiagnosticCollection('devlens');
    static updateDiagnostics(report, workspaceRoot) {
        this.collection.clear();
        const diagnosticsMap = new Map();
        for (const rule of report.scorecard.rule_results) {
            if (!rule.passed && rule.file_path) {
                const targetPath = path.isAbsolute(rule.file_path)
                    ? rule.file_path
                    : path.join(workspaceRoot, rule.file_path);
                const fileUri = vscode.Uri.file(targetPath);
                const line = Math.max(0, (rule.line_number ?? 1) - 1); // 0-indexed line number
                const range = new vscode.Range(line, 0, line, 100);
                const diagnostic = new vscode.Diagnostic(range, `[DevLens] Rule ${rule.rule_id} failed: ${rule.description} (Points: ${rule.points_awarded}/${rule.max_points})`, vscode.DiagnosticSeverity.Warning);
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
    static clearDiagnostics() {
        this.collection.clear();
    }
}
exports.DiagnosticsManager = DiagnosticsManager;
//# sourceMappingURL=diagnostics.js.map