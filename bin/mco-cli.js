#!/usr/bin/env node

/**
 * MCO CLI
 * 
 * Command-line interface for the MCO MCP Server and Configuration Tool
 */

const { program } = require('commander');
const fs = require('fs-extra');
const path = require('path');
const { spawn } = require('child_process');
const { SNLPParser } = require('../lib/snlp-parser');

// Set up CLI
program
  .name('mco')
  .description('MCO (Model Configuration Orchestration) MCP Server & Configuration Tool')
  .version('0.1.0');

// Init command - Create new MCO project with config tool
program
  .command('init')
  .description('Create a new MCO project with the configuration tool')
  .argument('[project-name]', 'Name of the project directory', 'mco-project')
  .action(async (projectName) => {
    try {
      // Create project directory
      const projectDir = path.resolve(process.cwd(), projectName);
      await fs.ensureDir(projectDir);
      
      console.log(`Creating new MCO project in ${projectDir}...`);
      
      // Create empty SNLP files
      await fs.writeFile(path.join(projectDir, 'mco.core'), '// MCO Core Configuration\n\n@workflow "New Workflow"\n\n@data\n\n@agents\n');
      await fs.writeFile(path.join(projectDir, 'mco.sc'), '// MCO Success Criteria\n\n@goal\n\n@success_criteria\n');
      await fs.writeFile(path.join(projectDir, 'mco.features'), '// MCO Features\n\n@features\n');
      await fs.writeFile(path.join(projectDir, 'mco.styles'), '// MCO Styles\n\n@styles\n');
      
      console.log('Created empty SNLP files.');
      
      // Open configuration tool
      console.log('Opening configuration tool...');
      const configToolPath = path.resolve(__dirname, '../web/config-tool/index.html');
      const open = (await import('open')).default;
      await open(configToolPath);
      
      console.log(`
MCO project initialized successfully!

To start the MCP server:
  mco serve ${projectName}

To validate your SNLP files:
  mco validate ${projectName}
      `);
    } catch (error) {
      console.error('Error initializing MCO project:', error);
      process.exit(1);
    }
  });

// Validate command - Validate SNLP files
program
  .command('validate')
  .description('Validate SNLP files')
  .argument('[config-dir]', 'Directory containing SNLP files', '.')
  .action(async (configDir) => {
    try {
      const parser = new SNLPParser();
      const resolvedDir = path.resolve(process.cwd(), configDir);
      
      console.log(`Validating SNLP files in ${resolvedDir}...`);
      
      // Check if directory exists
      if (!await fs.pathExists(resolvedDir)) {
        console.error(`Directory ${resolvedDir} does not exist.`);
        process.exit(1);
      }
      
      // Check for required files
      const requiredFiles = ['mco.core', 'mco.sc'];
      const optionalFiles = ['mco.features', 'mco.styles'];
      const missingFiles = [];
      
      for (const file of requiredFiles) {
        if (!await fs.pathExists(path.join(resolvedDir, file))) {
          missingFiles.push(file);
        }
      }
      
      if (missingFiles.length > 0) {
        console.error(`Missing required files: ${missingFiles.join(', ')}`);
        process.exit(1);
      }
      
      // Parse and validate files
      try {
        const workflow = await parser.parseDirectory(resolvedDir);
        console.log('✅ SNLP files are valid!');
        
        // Print workflow summary
        const persistentContext = workflow.getPersistentContext();
        console.log('\nWorkflow Summary:');
        console.log(`- Name: ${persistentContext.workflow_name || 'Unnamed workflow'}`);
        console.log(`- Goal: ${persistentContext.goal || 'No goal specified'}`);
        
        if (persistentContext.criteria && persistentContext.criteria.length > 0) {
          console.log(`- Success Criteria: ${persistentContext.criteria.length} criteria defined`);
        } else {
          console.log('- Success Criteria: None defined');
        }
        
        // Check for optional files
        for (const file of optionalFiles) {
          if (await fs.pathExists(path.join(resolvedDir, file))) {
            console.log(`- ${file}: Present`);
          } else {
            console.log(`- ${file}: Missing (optional)`);
          }
        }
      } catch (error) {
        console.error('❌ SNLP validation failed:', error.message);
        process.exit(1);
      }
    } catch (error) {
      console.error('Error validating SNLP files:', error);
      process.exit(1);
    }
  });

// Serve command - Start MCP server
program
  .command('serve')
  .description('Start MCP server')
  .argument('[config-dir]', 'Directory containing SNLP files', '.')
  .option('-p, --port <port>', 'Port to listen on', '3000')
  .option('-h, --host <host>', 'Host to bind to', 'localhost')
  .action(async (configDir, options) => {
    try {
      const resolvedDir = path.resolve(process.cwd(), configDir);
      
      console.log(`Starting MCO MCP Server with configuration from ${resolvedDir}...`);
      
      // Check if directory exists
      if (!await fs.pathExists(resolvedDir)) {
        console.error(`Directory ${resolvedDir} does not exist.`);
        process.exit(1);
      }
      
      // Set environment variable for config directory
      process.env.MCO_CONFIG_DIR = resolvedDir;
      
      // Start server
      const serverPath = path.resolve(__dirname, 'mco-server.js');
      const server = spawn('node', [serverPath, '--port', options.port, '--host', options.host], {
        stdio: 'inherit',
        env: process.env
      });
      
      // Handle server exit
      server.on('close', (code) => {
        if (code !== 0) {
          console.error(`Server exited with code ${code}`);
          process.exit(code);
        }
      });
    } catch (error) {
      console.error('Error starting MCP server:', error);
      process.exit(1);
    }
  });

// Templates command - List available templates
program
  .command('templates')
  .description('List available templates')
  .action(() => {
    console.log('Available templates:');
    console.log('- Research Assistant: Multi-step research workflows');
    console.log('- Software Development: Code generation workflows');
    console.log('- Content Creation: Writing and editing workflows');
    console.log('- Data Analysis: Data processing workflows');
    console.log('- Custom: Start from scratch');
  });

// Deploy command - Deploy to cloud MCP service
program
  .command('deploy')
  .description('Deploy to cloud MCP service')
  .argument('[config-dir]', 'Directory containing SNLP files', '.')
  .action((configDir) => {
    console.log(`Deploying MCO configuration from ${configDir} to cloud service...`);
    console.log('This feature is not yet implemented.');
  });

// Parse command-line arguments
program.parse(process.argv);

// If no command is provided, show help
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
