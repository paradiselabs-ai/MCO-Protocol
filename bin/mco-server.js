#!/usr/bin/env node

/**
 * MCO MCP Server
 * 
 * Main entry point for the MCO MCP Server
 * Implements the Model Context Protocol (MCP) for exposing orchestration tools
 */

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const { program } = require('commander');
const { SNLPParser } = require('../lib/snlp-parser');
const { OrchestrationEngine } = require('../lib/orchestration-engine');
const { MCPToolProvider } = require('../lib/mcp-tool-provider');

// Parse command-line arguments
program
  .option('-p, --port <port>', 'Port to listen on', '3000')
  .option('-h, --host <host>', 'Host to bind to', 'localhost')
  .option('-c, --config-dir <dir>', 'Directory containing SNLP files', process.env.MCO_CONFIG_DIR || '.')
  .option('-v, --verbose', 'Enable verbose logging')
  .parse(process.argv);

const options = program.opts();

// Set up logging
const logLevel = options.verbose ? 'debug' : 'info';
const logger = {
  debug: (...args) => {
    if (logLevel === 'debug') {
      console.debug(`[DEBUG] ${new Date().toISOString()}:`, ...args);
    }
  },
  info: (...args) => console.info(`[INFO] ${new Date().toISOString()}:`, ...args),
  warn: (...args) => console.warn(`[WARN] ${new Date().toISOString()}:`, ...args),
  error: (...args) => console.error(`[ERROR] ${new Date().toISOString()}:`, ...args)
};

// Initialize components
const orchestrationEngine = new OrchestrationEngine();
const toolProvider = new MCPToolProvider(orchestrationEngine);

// Create Express app
const app = express();
app.use(express.json());

// Set up HTTP server
const server = http.createServer(app);

// Set up WebSocket server
const wss = new WebSocket.Server({ server });

// Client connections
const clients = new Map();

// Handle WebSocket connections
wss.on('connection', (ws) => {
  const clientId = Date.now().toString();
  clients.set(clientId, { ws, orchestrationId: null });
  
  logger.info(`Client connected: ${clientId}`);
  
  // Send welcome message
  ws.send(JSON.stringify({
    type: 'welcome',
    clientId,
    message: 'Connected to MCO MCP Server',
    tools: toolProvider.getToolDefinitions()
  }));
  
  // Handle messages
  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message);
      logger.debug(`Received message from client ${clientId}:`, data);
      
      // Handle tool calls
      if (data.type === 'tool_call') {
        const { tool, params } = data;
        
        // Get client context
        const client = clients.get(clientId);
        const context = {
          clientId,
          orchestrationId: client.orchestrationId
        };
        
        try {
          // Execute tool
          const result = await toolProvider.executeTool(tool, params, context);
          
          // Update client orchestration ID if this was a start_orchestration call
          if (tool === 'start_orchestration' && result.orchestration_id) {
            client.orchestrationId = result.orchestration_id;
            clients.set(clientId, client);
          }
          
          // Send result
          ws.send(JSON.stringify({
            type: 'tool_result',
            tool,
            result
          }));
        } catch (error) {
          logger.error(`Error executing tool ${tool}:`, error);
          
          // Send error
          ws.send(JSON.stringify({
            type: 'error',
            tool,
            error: error.message
          }));
        }
      }
    } catch (error) {
      logger.error('Error processing message:', error);
      
      // Send error
      ws.send(JSON.stringify({
        type: 'error',
        error: 'Invalid message format'
      }));
    }
  });
  
  // Handle disconnections
  ws.on('close', () => {
    logger.info(`Client disconnected: ${clientId}`);
    clients.delete(clientId);
  });
});

// HTTP routes
app.get('/', (req, res) => {
  res.json({
    name: 'MCO MCP Server',
    version: '0.1.0',
    description: 'Model Configuration Orchestration MCP Server',
    status: 'running'
  });
});

// Get available tools
app.get('/tools', (req, res) => {
  res.json(toolProvider.getToolDefinitions());
});

// Start server
const port = parseInt(options.port, 10);
const host = options.host;

server.listen(port, host, () => {
  logger.info(`MCO MCP Server running at http://${host}:${port}`);
  logger.info(`Using configuration directory: ${options.configDir}`);
  logger.info('WebSocket endpoint available at ws://${host}:${port}');
  logger.info('Available tools:');
  toolProvider.getToolDefinitions().forEach(tool => {
    logger.info(`- ${tool.name}: ${tool.description}`);
  });
});

// Handle server shutdown
process.on('SIGINT', () => {
  logger.info('Shutting down MCO MCP Server...');
  
  // Close all client connections
  clients.forEach((client) => {
    client.ws.close();
  });
  
  // Close server
  server.close(() => {
    logger.info('Server stopped');
    process.exit(0);
  });
});
