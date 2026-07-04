import * as assert from 'assert';
import * as vscode from 'vscode';
import { DiagnosticsManager } from '../../providers/diagnostics';
import { DevLensStatusBar } from '../../providers/statusbar';

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
    assert.strictEqual(config.get<string>('endpoint'), 'http://localhost:8000');
    assert.strictEqual(config.get<boolean>('offlinePreferred'), false);
    assert.strictEqual(config.get<boolean>('autoAuditOnOpen'), false);
  });

  test('DiagnosticsManager should clear correctly without errors', () => {
    assert.doesNotThrow(() => {
      DiagnosticsManager.clearDiagnostics();
    });
  });

  test('StatusBar should toggle status correctly without exceptions', () => {
    assert.doesNotThrow(() => {
      DevLensStatusBar.initialize();
      DevLensStatusBar.showPlaceholder();
      DevLensStatusBar.hide();
    });
  });

  test('APIClient secretStorage property is registered', () => {
    const { APIClient } = require('../../client/api');
    assert.ok(Object.prototype.hasOwnProperty.call(APIClient, 'secretStorage'));
  });
});
