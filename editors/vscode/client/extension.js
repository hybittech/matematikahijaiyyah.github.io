// Launches `hc lsp` and speaks LSP to it over stdio.
//
// Written against vscode's own API rather than vscode-languageclient, so the
// extension has no npm dependencies and can be loaded straight from disk. The
// protocol surface used here is small: framed JSON-RPC in, diagnostics out.
//
// Syntax highlighting works without any of this — the TextMate grammar is
// declarative. The server only adds live parse errors, hover and completion,
// and the extension degrades to highlighting alone if `hc` is not installed.

const vscode = require('vscode');
const { spawn } = require('child_process');

let child = null;
let diagnostics = null;
let nextId = 1;
const pending = new Map();
let buffer = Buffer.alloc(0);

function send(message) {
    if (!child) return;
    const body = Buffer.from(JSON.stringify(message), 'utf8');
    child.stdin.write(`Content-Length: ${body.length}\r\n\r\n`);
    child.stdin.write(body);
}

function request(method, params) {
    const id = nextId++;
    send({ jsonrpc: '2.0', id, method, params });
    return new Promise((resolve) => pending.set(id, resolve));
}

function notify(method, params) {
    send({ jsonrpc: '2.0', method, params });
}

function onMessage(message) {
    if (message.id !== undefined && pending.has(message.id)) {
        pending.get(message.id)(message.result);
        pending.delete(message.id);
        return;
    }
    if (message.method === 'textDocument/publishDiagnostics') {
        const { uri, diagnostics: items } = message.params;
        diagnostics.set(
            vscode.Uri.parse(uri),
            items.map((d) => {
                const { start, end } = d.range;
                return new vscode.Diagnostic(
                    new vscode.Range(start.line, start.character, end.line, end.character),
                    d.message,
                    vscode.DiagnosticSeverity.Error
                );
            })
        );
    }
}

// Frames arrive split across chunks, so decode from a running buffer.
function onData(chunk) {
    buffer = Buffer.concat([buffer, chunk]);
    for (;;) {
        const headerEnd = buffer.indexOf('\r\n\r\n');
        if (headerEnd === -1) return;
        const header = buffer.slice(0, headerEnd).toString('utf8');
        const match = /content-length:\s*(\d+)/i.exec(header);
        if (!match) return;
        const length = parseInt(match[1], 10);
        const bodyStart = headerEnd + 4;
        if (buffer.length < bodyStart + length) return;
        const body = buffer.slice(bodyStart, bodyStart + length).toString('utf8');
        buffer = buffer.slice(bodyStart + length);
        try {
            onMessage(JSON.parse(body));
        } catch (err) {
            console.error('hc: malformed message from server', err);
        }
    }
}

function documentIsHc(document) {
    return document.languageId === 'hc';
}

function activate(context) {
    diagnostics = vscode.languages.createDiagnosticCollection('hc');
    context.subscriptions.push(diagnostics);

    const config = vscode.workspace.getConfiguration('hc');
    if (!config.get('languageServer.enabled', true)) return;

    const command = config.get('languageServer.command', 'hc');
    try {
        child = spawn(command, ['lsp'], { stdio: ['pipe', 'pipe', 'pipe'] });
    } catch (err) {
        vscode.window.showWarningMessage(
            `HC: could not start "${command} lsp" — highlighting still works. ${err.message}`
        );
        return;
    }

    child.on('error', (err) => {
        vscode.window.showWarningMessage(
            `HC: language server unavailable (${err.message}). Highlighting still works.`
        );
        child = null;
    });
    child.stdout.on('data', onData);
    child.stderr.on('data', (d) => console.error(`hc-lsp: ${d}`));

    request('initialize', { processId: process.pid, rootUri: null, capabilities: {} })
        .then(() => notify('initialized', {}));

    const open = (document) => {
        if (!documentIsHc(document)) return;
        notify('textDocument/didOpen', {
            textDocument: {
                uri: document.uri.toString(),
                languageId: 'hc',
                version: document.version,
                text: document.getText(),
            },
        });
    };

    vscode.workspace.textDocuments.forEach(open);
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(open),
        vscode.workspace.onDidChangeTextDocument((event) => {
            if (!documentIsHc(event.document)) return;
            notify('textDocument/didChange', {
                textDocument: {
                    uri: event.document.uri.toString(),
                    version: event.document.version,
                },
                contentChanges: [{ text: event.document.getText() }],
            });
        }),
        vscode.workspace.onDidCloseTextDocument((document) => {
            if (!documentIsHc(document)) return;
            notify('textDocument/didClose', {
                textDocument: { uri: document.uri.toString() },
            });
            diagnostics.delete(document.uri);
        })
    );
}

function deactivate() {
    if (child) {
        notify('shutdown', {});
        notify('exit', {});
        child.kill();
        child = null;
    }
}

module.exports = { activate, deactivate };
