#!/usr/bin/env node

/**
 * MCO MCP Server (Unified: HTTP/WebSocket + Stdio)
 * 
 * Main entry point for the MCO MCP Server. This server can operate in two modes:
 * 1. HTTP/WebSocket (default): For web-based clients and easy integration.
 * 2. Stdio (with --stdio flag): For standard MCP command-line tooling.
 */

const http = require('http');
const express = require('express');
const WebSocket = require('ws');
const { program } = require('commander');
const path = require('path');
const fs = require('fs');

// --- Core MCO Logic ---
const { OrchestrationEngine } = require('./lib/orchestration-engine');
const { MCPToolProvider } = require('./lib/mcp-tool-provider');

// --- Commander Setup ---
program
  .option('--stdio', 'Run in standard I/O mode for MCP compatibility')
  .option('-p, --port <port>', 'Port to listen on (HTTP mode)', '3000')
  .option('-h, --host <host>', 'Host to bind to (HTTP mode)', 'localhost')
  .option('-c, --config-dir <dir>', 'Directory containing SNLP files', process.env.MCO_CONFIG_DIR || '.')
  .option('-v, --verbose', 'Enable verbose logging')
  .parse(process.argv);

const options = program.opts();

// --- Shared Components ---
const logger = {
    debug: (...args) => { if (options.verbose) console.error(`[DEBUG] ${new Date().toISOString()}:`, ...args); },
    info: (...args) => console.error(`[INFO] ${new Date().toISOString()}:`, ...args),
    warn: (...args) => console.error(`[WARN] ${new Date().toISOString()}:`, ...args),
    error: (...args) => console.error(`[ERROR] ${new Date().toISOString()}:`, ...args),
};

const orchestrationEngine = new OrchestrationEngine(options.configDir, logger);
const toolProvider = new MCPToolProvider(orchestrationEngine, logger);

// --- Mode Execution ---
if (options.stdio) {
    runStdioMode();
} else {
    runHttpMode();
}

// --- Stdio Mode Implementation ---
async function runStdioMode() {
    logger.info('Starting MCO MCP Server in Stdio mode...');

    // Redirect stdout to keep it clean for MCP messages
    console.log = (...args) => logger.debug('[STDOUT-CAPTURE]', ...args);

    const { Server } = require('@modelcontextprotocol/sdk/dist/cjs/server');
    const { StdioServerTransport } = require('@modelcontextprotocol/sdk/dist/cjs/server/stdio');
    const { CallToolRequestSchema, ListToolsRequestSchema } = require('@modelcontextprotocol/sdk/dist/cjs/types');

    const server = new Server(
        { name: 'mco-orchestration', version: '0.3.0' },
        { capabilities: { tools: {} } }
    );

    server.setRequestHandler(ListToolsRequestSchema, async () => {
        logger.info('Handling ListTools request...');
        const tools = toolProvider.getToolDefinitions();
        return {
            tools: tools.map(tool => ({
                name: tool.name,
                description: tool.description,
                inputSchema: tool.parameters
            }))
        };
    });

    server.setRequestHandler(CallToolRequestSchema, async (request) => {
        const { name, arguments: args } = request.params;
        logger.info(`Handling CallTool request for: ${name}`);
        logger.debug('Arguments:', args);

        try {
            const context = { clientId: 'mcp-client', orchestrationId: args.orchestration_id || null };
            const result = await toolProvider.executeTool(name, args, context);
            logger.info(`Tool ${name} executed successfully.`);
            return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
        } catch (error) {
            logger.error(`Error executing tool ${name}:`, error.message);
            return { content: [{ type: 'text', text: JSON.stringify({ error: error.message, tool: name }, null, 2) }], isError: true };
        }
    });

    const transport = new StdioServerTransport();
    await server.connect(transport);
    logger.info('MCO MCP Server started and connected via stdio.');

    process.on('SIGINT', () => {
        logger.info('Shutting down...');
        process.exit(0);
    });
    process.on('SIGTERM', () => {
        logger.info('Shutting down...');
        process.exit(0);
    });
}

// --- HTTP/WebSocket Mode Implementation ---
function runHttpMode() {
    logger.info('Starting MCO MCP Server in HTTP/WebSocket mode...');
    const app = express();
    app.use(express.json());
    const server = http.createServer(app);
    const wss = new WebSocket.Server({ server });

    const clients = new Map();

    wss.on('connection', (ws) => {
        const clientId = `ws-${Date.now().toString()}`;
        clients.set(clientId, { ws, orchestrationId: null });
        logger.info(`Client connected: ${clientId}`);

        ws.send(JSON.stringify({
            type: 'welcome',
            clientId,
            message: 'Connected to MCO MCP Server',
            tools: toolProvider.getToolDefinitions()
        }));

        ws.on('message', async (message) => {
            try {
                const data = JSON.parse(message);
                logger.debug(`Received message from client ${clientId}:`, data);

                if (data.type === 'tool_call') {
                    const { tool, params, requestId } = data;
                    const client = clients.get(clientId);
                    const context = { clientId, orchestrationId: client.orchestrationId };

                    try {
                        const result = await toolProvider.executeTool(tool, params, context);
                        if (tool === 'start_orchestration' && result.orchestration_id) {
                            client.orchestrationId = result.orchestration_id;
                            clients.set(clientId, client);
                        }
                        ws.send(JSON.stringify({ type: 'tool_result', requestId, result }));
                    } catch (error) {
                        logger.error(`Error executing tool ${tool}:`, error);
                        ws.send(JSON.stringify({ type: 'error', requestId, error: error.message }));
                    }
                }
            } catch (error) {
                logger.error('Error processing message:', error);
                ws.send(JSON.stringify({ type: 'error', error: 'Invalid message format' }));
            }
        });

        ws.on('close', () => {
            logger.info(`Client disconnected: ${clientId}`);
            clients.delete(clientId);
        });
    });

    app.get('/', (req, res) => {
        res.json({ name: 'MCO MCP Server', version: '0.3.0', status: 'running' });
    });

    app.get('/tools', (req, res) => {
        res.json(toolProvider.getToolDefinitions());
    });

    const port = parseInt(options.port, 10);
    const host = options.host;

    server.listen(port, host, () => {
        logger.info(`MCO MCP Server running at http://${host}:${port}`);
        logger.info(`Using configuration directory: ${options.configDir}`);
        toolProvider.getToolDefinitions().forEach(tool => logger.info(`- Tool: ${tool.name}`))
    });

    process.on('SIGINT', () => {
        logger.info('Shutting down server...');
        wss.close(() => server.close(() => process.exit(0)));
    });
}
