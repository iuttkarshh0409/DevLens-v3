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
exports.DevLensStatusBar = void 0;
const vscode = __importStar(require("vscode"));
class DevLensStatusBar {
    static statusBarItem;
    static initialize() {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBarItem.command = 'devlens.openReport';
        this.showPlaceholder();
    }
    static showPlaceholder() {
        const config = vscode.workspace.getConfiguration('devlens');
        if (!config.get('showStatusBar', true)) {
            this.statusBarItem.hide();
            return;
        }
        this.statusBarItem.text = '$(shield) DevLens: Ready';
        this.statusBarItem.tooltip = 'Click to open DevLens Audit Dashboard';
        this.statusBarItem.show();
    }
    static updateScore(report) {
        const config = vscode.workspace.getConfiguration('devlens');
        if (!config.get('showStatusBar', true)) {
            this.statusBarItem.hide();
            return;
        }
        const score = report.scorecard.overall_score;
        let rating = 'Risky';
        if (score >= 8.0) {
            rating = 'Strong';
        }
        else if (score >= 5.0) {
            rating = 'Fair';
        }
        this.statusBarItem.text = `$(shield) DevLens Score: ${score.toFixed(1)} (${rating})`;
        this.statusBarItem.tooltip = `Latest Audit Score: ${score.toFixed(1)}/10.0 | Verdict: ${rating}\nClick to view full dashboard report.`;
        this.statusBarItem.show();
    }
    static hide() {
        this.statusBarItem.hide();
    }
}
exports.DevLensStatusBar = DevLensStatusBar;
//# sourceMappingURL=statusbar.js.map