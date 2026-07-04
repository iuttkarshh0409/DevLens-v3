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
const assert = __importStar(require("assert"));
const vscode = __importStar(require("vscode"));
const diagnostics_1 = require("../../providers/diagnostics");
const statusbar_1 = require("../../providers/statusbar");
suite('DevLens VS Code Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start DevLens VS Code Extension tests.');
    test('Extension should be present and registered', () => {
        assert.ok(vscode.extensions.getExtension('devlens.devlens'));
    });
    test('Registered commands should be present on activation', async () => {
        const commands = await vscode.commands.getCommands(true);
        assert.ok(commands.includes('devlens.audit'));
        assert.ok(commands.includes('devlens.offlineAudit'));
        assert.ok(commands.includes('devlens.viewAnalytics'));
        assert.ok(commands.includes('devlens.login'));
        assert.ok(commands.includes('devlens.logout'));
        assert.ok(commands.includes('devlens.openReport'));
    });
    test('Settings configurations return expected default schemas', () => {
        const config = vscode.workspace.getConfiguration('devlens');
        assert.strictEqual(config.get('endpoint'), 'http://localhost:8000');
        assert.strictEqual(config.get('offlinePreferred'), true);
        assert.strictEqual(config.get('autoAuditOnOpen'), false);
    });
    test('DiagnosticsManager should clear correctly without errors', () => {
        assert.doesNotThrow(() => {
            diagnostics_1.DiagnosticsManager.clearDiagnostics();
        });
    });
    test('StatusBar should toggle status correctly without exceptions', () => {
        assert.doesNotThrow(() => {
            statusbar_1.DevLensStatusBar.initialize();
            statusbar_1.DevLensStatusBar.showPlaceholder();
            statusbar_1.DevLensStatusBar.hide();
        });
    });
});
//# sourceMappingURL=extension.test.js.map