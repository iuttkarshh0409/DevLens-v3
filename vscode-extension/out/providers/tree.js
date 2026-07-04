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
exports.DevLensTreeItem = exports.DevLensTreeProvider = void 0;
const vscode = __importStar(require("vscode"));
class DevLensTreeProvider {
    _onDidChangeTreeData = new vscode.EventEmitter();
    onDidChangeTreeData = this._onDidChangeTreeData.event;
    currentReport = null;
    refresh(report) {
        this.currentReport = report;
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
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
            return Promise.resolve(rules.map(r => {
                const icon = r.passed ? '✓' : '✗';
                return new DevLensTreeItem(`${icon} ${r.rule_id}: ${r.description}`, vscode.TreeItemCollapsibleState.None, 'rule-item');
            }));
        }
        return Promise.resolve([]);
    }
}
exports.DevLensTreeProvider = DevLensTreeProvider;
class DevLensTreeItem extends vscode.TreeItem {
    label;
    collapsibleState;
    contextValue;
    constructor(label, collapsibleState, contextValue) {
        super(label, collapsibleState);
        this.label = label;
        this.collapsibleState = collapsibleState;
        this.contextValue = contextValue;
        this.tooltip = this.label;
        // Choose icons dynamically
        if (this.contextValue === 'score') {
            this.iconPath = new vscode.ThemeIcon('dashboard');
        }
        else if (this.contextValue === 'verdict') {
            this.iconPath = new vscode.ThemeIcon('feedback');
        }
        else if (this.contextValue === 'rec-group') {
            this.iconPath = new vscode.ThemeIcon('lightbulb');
        }
        else if (this.contextValue === 'rule-group') {
            this.iconPath = new vscode.ThemeIcon('checklist');
        }
    }
}
exports.DevLensTreeItem = DevLensTreeItem;
//# sourceMappingURL=tree.js.map