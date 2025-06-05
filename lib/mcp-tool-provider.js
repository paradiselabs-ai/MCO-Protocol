/**
 * MCP Tool Provider Module
 * 
 * This module defines the MCP tool interfaces and response formats for the MCO MCP Server.
 * It implements the Model Context Protocol (MCP) specification for exposing orchestration tools.
 */

const { ParsedWorkflow } = require('./snlp-parser');

/**
 * Represents an MCP tool definition
 */
class MCPTool {
  constructor(name, description, parameters, handler) {
    this.name = name;
    this.description = description;
    this.parameters = parameters;
    this.handler = handler;
  }

  /**
   * Get the tool definition in MCP format
   */
  getDefinition() {
    return {
      name: this.name,
      description: this.description,
      parameters: this.parameters
    };
  }

  /**
   * Execute the tool with the given parameters
   * @param {object} params - Tool parameters
   * @param {object} context - Execution context
   * @returns {Promise<object>} - Tool execution result
   */
  async execute(params, context) {
    return await this.handler(params, context);
  }
}

/**
 * MCP Tool Provider class
 * Manages the registration and execution of MCP tools
 */
class MCPToolProvider {
  constructor(orchestrationEngine) {
    this.tools = {};
    this.orchestrationEngine = orchestrationEngine;
    this._registerTools();
  }

  /**
   * Get all tool definitions
   * @returns {object[]} - Array of tool definitions
   */
  getToolDefinitions() {
    return Object.values(this.tools).map(tool => tool.getDefinition());
  }

  /**
   * Execute a tool by name
   * @param {string} toolName - Name of the tool to execute
   * @param {object} params - Tool parameters
   * @param {object} context - Execution context
   * @returns {Promise<object>} - Tool execution result
   */
  async executeTool(toolName, params, context) {
    const tool = this.tools[toolName];
    if (!tool) {
      throw new Error(`Tool not found: ${toolName}`);
    }
    
    try {
      return await tool.execute(params, context);
    } catch (error) {
      console.error(`Error executing tool ${toolName}:`, error);
      throw error;
    }
  }

  /**
   * Register all MCP tools
   * @private
   */
  _registerTools() {
    // Workflow Management Tools
    this._registerWorkflowTools();
    
    // Success Criteria Tools
    this._registerSuccessCriteriaTools();
    
    // State Management Tools
    this._registerStateManagementTools();
  }

  /**
   * Register workflow management tools
   * @private
   */
  _registerWorkflowTools() {
    // start_orchestration tool
    this.tools['start_orchestration'] = new MCPTool(
      'start_orchestration',
      'Start a new orchestration workflow',
      {
        type: 'object',
        properties: {
          config: {
            type: 'object',
            description: 'Configuration for the orchestration',
            required: false
          }
        }
      },
      async (params, context) => {
        const orchestrationId = await this.orchestrationEngine.startOrchestration(params.config || {});
        return {
          orchestration_id: orchestrationId
        };
      }
    );

    // get_next_directive tool
    this.tools['get_next_directive'] = new MCPTool(
      'get_next_directive',
      'Get the next directive for the current orchestration',
      {
        type: 'object',
        properties: {
          orchestration_id: {
            type: 'string',
            description: 'ID of the orchestration',
            required: false
          }
        }
      },
      async (params, context) => {
        const orchestrationId = params.orchestration_id || context.orchestrationId;
        if (!orchestrationId) {
          throw new Error('Orchestration ID is required');
        }
        
        return await this.orchestrationEngine.getNextDirective(orchestrationId);
      }
    );

    // complete_step tool
    this.tools['complete_step'] = new MCPTool(
      'complete_step',
      'Complete the current step in the orchestration',
      {
        type: 'object',
        properties: {
          orchestration_id: {
            type: 'string',
            description: 'ID of the orchestration',
            required: false
          },
          step_id: {
            type: 'string',
            description: 'ID of the step to complete'
          },
          result: {
            type: 'object',
            description: 'Result of the step execution'
          }
        },
        required: ['step_id', 'result']
      },
      async (params, context) => {
        const orchestrationId = params.orchestration_id || context.orchestrationId;
        if (!orchestrationId) {
          throw new Error('Orchestration ID is required');
        }
        
        return await this.orchestrationEngine.completeStep(
          orchestrationId,
          params.step_id,
          params.result
        );
      }
    );

    // get_workflow_status tool
    this.tools['get_workflow_status'] = new MCPTool(
      'get_workflow_status',
      'Get the current status of the workflow',
      {
        type: 'object',
        properties: {
          orchestration_id: {
            type: 'string',
            description: 'ID of the orchestration',
            required: false
          }
        }
      },
      async (params, context) => {
        const orchestrationId = params.orchestration_id || context.orchestrationId;
        if (!orchestrationId) {
          throw new Error('Orchestration ID is required');
        }
        
        return await this.orchestrationEngine.getWorkflowStatus(orchestrationId);
      }
    );
  }

  /**
   * Register success criteria tools
   * @private
   */
  _registerSuccessCriteriaTools() {
    // evaluate_against_criteria tool
    this.tools['evaluate_against_criteria'] = new MCPTool(
      'evaluate_against_criteria',
      'Evaluate a result against the defined success criteria',
      {
        type: 'object',
        properties: {
          orchestration_id: {
            type: 'string',
            description: 'ID of the orchestration',
            required: false
          },
          result: {
            type: 'object',
            description: 'Result to evaluate'
          }
        },
        required: ['result']
      },
      async (params, context) => {
        const orchestrationId = params.orchestration_id || context.orchestrationId;
        if (!orchestrationId) {
          throw new Error('Orchestration ID is required');
        }
        
        return await this.orchestrationEngine.evaluateAgainstCriteria(
          orchestrationId,
          params.result
        );
      }
    );
  }

  /**
   * Register state management tools
   * @private
   */
  _registerStateManagementTools() {
    // get_persistent_context tool
    this.tools['get_persistent_context'] = new MCPTool(
      'get_persistent_context',
      'Get the persistent context for the current orchestration',
      {
        type: 'object',
        properties: {
          orchestration_id: {
            type: 'string',
            description: 'ID of the orchestration',
            required: false
          }
        }
      },
      async (params, context) => {
        const orchestrationId = params.orchestration_id || context.orchestrationId;
        if (!orchestrationId) {
          throw new Error('Orchestration ID is required');
        }
        
        return await this.orchestrationEngine.getPersistentContext(orchestrationId);
      }
    );

    // set_workflow_variable tool
    this.tools['set_workflow_variable'] = new MCPTool(
      'set_workflow_variable',
      'Set a workflow variable',
      {
        type: 'object',
        properties: {
          orchestration_id: {
            type: 'string',
            description: 'ID of the orchestration',
            required: false
          },
          key: {
            type: 'string',
            description: 'Variable key'
          },
          value: {
            description: 'Variable value'
          }
        },
        required: ['key', 'value']
      },
      async (params, context) => {
        const orchestrationId = params.orchestration_id || context.orchestrationId;
        if (!orchestrationId) {
          throw new Error('Orchestration ID is required');
        }
        
        return await this.orchestrationEngine.setWorkflowVariable(
          orchestrationId,
          params.key,
          params.value
        );
      }
    );

    // get_workflow_variable tool
    this.tools['get_workflow_variable'] = new MCPTool(
      'get_workflow_variable',
      'Get a workflow variable',
      {
        type: 'object',
        properties: {
          orchestration_id: {
            type: 'string',
            description: 'ID of the orchestration',
            required: false
          },
          key: {
            type: 'string',
            description: 'Variable key'
          }
        },
        required: ['key']
      },
      async (params, context) => {
        const orchestrationId = params.orchestration_id || context.orchestrationId;
        if (!orchestrationId) {
          throw new Error('Orchestration ID is required');
        }
        
        return await this.orchestrationEngine.getWorkflowVariable(
          orchestrationId,
          params.key
        );
      }
    );
  }
}

/**
 * Standard response formats for MCP tools
 */
const ResponseFormats = {
  /**
   * Format for directive responses
   * @param {string} type - Directive type
   * @param {string} stepId - Step ID
   * @param {string} instruction - Instruction text
   * @param {object} persistentContext - Persistent context
   * @param {object} injectedContext - Injected context
   * @param {string} guidance - Guidance text
   * @returns {object} - Formatted directive response
   */
  directive: (type, stepId, instruction, persistentContext, injectedContext, guidance) => {
    return {
      type,
      step_id: stepId,
      instruction,
      persistent_context: persistentContext,
      ...(injectedContext ? { injected_context: injectedContext } : {}),
      guidance
    };
  },

  /**
   * Format for step completion responses
   * @param {string} status - Completion status
   * @param {string} nextStepId - Next step ID
   * @param {object} evaluation - Evaluation results
   * @returns {object} - Formatted step completion response
   */
  stepCompletion: (status, nextStepId, evaluation) => {
    return {
      status,
      next_step_id: nextStepId,
      evaluation
    };
  },

  /**
   * Format for workflow status responses
   * @param {string} status - Workflow status
   * @param {number} progress - Progress percentage
   * @param {object} currentStep - Current step information
   * @param {object[]} completedSteps - Completed steps
   * @param {object[]} remainingSteps - Remaining steps
   * @returns {object} - Formatted workflow status response
   */
  workflowStatus: (status, progress, currentStep, completedSteps, remainingSteps) => {
    return {
      status,
      progress,
      current_step: currentStep,
      completed_steps: completedSteps,
      remaining_steps: remainingSteps
    };
  },

  /**
   * Format for evaluation responses
   * @param {boolean} success - Overall success
   * @param {object[]} criteria - Individual criteria evaluations
   * @param {string} feedback - Feedback text
   * @returns {object} - Formatted evaluation response
   */
  evaluation: (success, criteria, feedback) => {
    return {
      success,
      criteria,
      feedback
    };
  },

  /**
   * Format for error responses
   * @param {string} error - Error message
   * @param {string} code - Error code
   * @returns {object} - Formatted error response
   */
  error: (error, code) => {
    return {
      error,
      code
    };
  }
};

module.exports = {
  MCPTool,
  MCPToolProvider,
  ResponseFormats
};
