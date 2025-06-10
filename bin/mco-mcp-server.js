#!/usr/bin/env node

/**
 * MCO MCP Server (stdio implementation)
 * 
 * Proper MCP server implementation using stdio transport
 * Implements the Model Context Protocol (MCP) for exposing orchestration tools
 */

const path = require('path');
const fs = require('fs');

// Import MCP SDK with absolute paths
const { Server } = require(path.join(__dirname, '../node_modules/@modelcontextprotocol/sdk/dist/cjs/server/index.js'));
const { StdioServerTransport } = require(path.join(__dirname, '../node_modules/@modelcontextprotocol/sdk/dist/cjs/server/stdio.js'));
const { CallToolRequestSchema, ListToolsRequestSchema } = require(path.join(__dirname, '../node_modules/@modelcontextprotocol/sdk/dist/cjs/types.js'));

// Import MCO components
const { OrchestrationEngine } = require('../lib/orchestration-engine');
const { MCPToolProvider } = require('../lib/mcp-tool-provider');

// Get config directory from environment or current directory
const configDir = process.env.MCO_CONFIG_DIR || process.cwd();

// Redirect all console output to stderr to keep stdout clean for MCP
const originalConsole = { ...console };
console.log = (...args) => originalConsole.error('[MCO]', ...args);
console.info = (...args) => originalConsole.error('[MCO]', ...args);
console.warn = (...args) => originalConsole.error('[MCO]', ...args);
console.error = (...args) => originalConsole.error('[MCO]', ...args);
console.debug = (...args) => originalConsole.error('[MCO]', ...args);

// Initialize components
const orchestrationEngine = new OrchestrationEngine();
const toolProvider = new MCPToolProvider(orchestrationEngine);

// Create MCP server
const server = new Server(
  {
    name: 'mco-orchestration',
    version: '0.2.3',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Register tool handlers
server.setRequestHandler(ListToolsRequestSchema, async () => {
  console.error('[MCO] Listing tools...');
  const tools = toolProvider.getToolDefinitions();
  console.error(`[MCO] Found ${tools.length} tools`);
  
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
  
  console.error(`[MCO] Executing tool: ${name}`);
  console.error(`[MCO] Arguments:`, args);
  
  try {
    // Create a minimal context for tool execution
    const context = {
      clientId: 'mcp-client',
      orchestrationId: args.orchestration_id || null
    };
    
    const result = await toolProvider.executeTool(name, args, context);
    
    console.error(`[MCO] Tool ${name} executed successfully`);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  } catch (error) {
    console.error(`[MCO] Error executing tool ${name}:`, error.message);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error.message,
            tool: name
          }, null, 2)
        }
      ],
      isError: true
    };
  }
});

// Start the server
async function main() {
  console.error(`[MCO] Starting MCO MCP Server...`);
  console.error(`[MCO] Using configuration directory: ${configDir}`);
  
  // Check if config directory exists
  if (!fs.existsSync(configDir)) {
    console.error(`[MCO] Warning: Configuration directory ${configDir} does not exist`);
  }
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('[MCO] MCO MCP Server started and ready for connections');
}

// Handle shutdown gracefully
process.on('SIGINT', () => {
  console.error('[MCO] Shutting down MCO MCP Server...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('[MCO] Shutting down MCO MCP Server...');
  process.exit(0);
});

// Start the server
main().catch((error) => {
  console.error('[MCO] Failed to start server:', error);
  process.exit(1);
});
