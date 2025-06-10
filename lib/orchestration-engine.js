/**
 * Orchestration Engine Module
 * 
 * This module implements the core orchestration logic for the MCO MCP Server,
 * including workflow state management and progressive revelation.
 */

const { v4: uuidv4 } = require('uuid');
const { SNLPParser } = require('./snlp-parser');
const { ResponseFormats } = require('./mcp-tool-provider');

/**
 * Represents the state of an orchestration workflow
 */
class WorkflowState {
  constructor(workflow, config = {}) {
    this.id = uuidv4();
    this.workflow = workflow;
    this.config = config;
    this.currentStepIndex = 0;
    this.completedSteps = [];
    this.variables = {};
    this.injectionHistory = {
      features: false,
      styles: false
    };
    
    // Extract steps from workflow
    this.steps = this._extractSteps();
  }

  /**
   * Extract steps from the workflow
   * @returns {Array} - Array of workflow steps
   * @private
   */
  _extractSteps() {
    const steps = [];
    
    if (this.workflow.core && 
        this.workflow.core.markers && 
        this.workflow.core.markers.agents) {
      
      // Extract steps from agents section
      const agents = this.workflow.core.markers.agents;
      
      // If agents is an object with agent definitions
      if (typeof agents === 'object' && !Array.isArray(agents)) {
        // For each agent, extract steps
        Object.entries(agents).forEach(([agentName, agentDef]) => {
          if (agentDef && agentDef.steps && Array.isArray(agentDef.steps)) {
            agentDef.steps.forEach((step, index) => {
              steps.push({
                id: `${agentName}_step_${index}`,
                agent: agentName,
                description: typeof step === 'string' ? step : step.description || `Step ${index + 1}`,
                type: this._inferStepType(step),
                index: steps.length
              });
            });
          }
        });
      }
    }
    
    // If no steps were found, create a default step
    if (steps.length === 0) {
      steps.push({
        id: 'default_step_0',
        agent: 'default',
        description: 'Complete the task',
        type: 'implement',
        index: 0
      });
    }
    
    return steps;
  }

  /**
   * Infer the type of a step based on its description
   * @param {string|object} step - Step description or object
   * @returns {string} - Inferred step type
   * @private
   */
  _inferStepType(step) {
    const description = typeof step === 'string' ? step : step.description || '';
    const lowerDesc = description.toLowerCase();
    
    if (lowerDesc.includes('implement') || lowerDesc.includes('develop') || lowerDesc.includes('code') || lowerDesc.includes('build')) {
      return 'implement';
    } else if (lowerDesc.includes('style') || lowerDesc.includes('format') || lowerDesc.includes('design') || lowerDesc.includes('present')) {
      return 'style';
    } else if (lowerDesc.includes('plan') || lowerDesc.includes('architect') || lowerDesc.includes('design')) {
      return 'plan';
    } else if (lowerDesc.includes('test') || lowerDesc.includes('validate') || lowerDesc.includes('verify')) {
      return 'test';
    } else if (lowerDesc.includes('document') || lowerDesc.includes('report')) {
      return 'document';
    } else {
      // Default to implement
      return 'implement';
    }
  }

  /**
   * Get the current step
   * @returns {object|null} - Current step or null if workflow is complete
   */
  getCurrentStep() {
    if (this.currentStepIndex >= this.steps.length) {
      return null; // Workflow is complete
    }
    return this.steps[this.currentStepIndex];
  }

  /**
   * Move to the next step
   * @returns {object|null} - Next step or null if workflow is complete
   */
  moveToNextStep() {
    const currentStep = this.getCurrentStep();
    if (currentStep) {
      this.completedSteps.push(currentStep);
    }
    
    this.currentStepIndex++;
    return this.getCurrentStep();
  }

  /**
   * Get workflow progress
   * @returns {number} - Progress percentage (0-100)
   */
  getProgress() {
    if (this.steps.length === 0) {
      return 100;
    }
    return Math.min(100, Math.round((this.completedSteps.length / this.steps.length) * 100));
  }

  /**
   * Get workflow status
   * @returns {string} - Workflow status ('in_progress', 'complete')
   */
  getStatus() {
    return this.currentStepIndex >= this.steps.length ? 'complete' : 'in_progress';
  }

  /**
   * Set a workflow variable
   * @param {string} key - Variable key
   * @param {any} value - Variable value
   */
  setVariable(key, value) {
    this.variables[key] = value;
  }

  /**
   * Get a workflow variable
   * @param {string} key - Variable key
   * @returns {any} - Variable value or undefined if not found
   */
  getVariable(key) {
    return this.variables[key];
  }
}

/**
 * Orchestration Engine class
 * Manages workflow state and progressive revelation
 */
class OrchestrationEngine {
  constructor() {
    this.parser = new SNLPParser();
    this.workflows = {};
  }

  /**
   * Start a new orchestration
   * @param {object} config - Orchestration configuration
   * @returns {Promise<string>} - Orchestration ID
   */
  async startOrchestration(config = {}) {
    try {
      // Parse workflow files
      const configDir = config.config_dir || process.env.MCO_CONFIG_DIR;
      if (!configDir) {
        throw new Error('Configuration directory is required');
      }
      
      const workflow = await this.parser.parseDirectory(configDir);
      
      // Create workflow state
      const state = new WorkflowState(workflow, config);
      
      // Store workflow state
      this.workflows[state.id] = state;
      
      return state.id;
    } catch (error) {
      console.error('Error starting orchestration:', error);
      throw error;
    }
  }

  /**
   * Get the next directive for an orchestration
   * @param {string} orchestrationId - Orchestration ID
   * @returns {Promise<object>} - Next directive
   */
  async getNextDirective(orchestrationId) {
    const state = this._getWorkflowState(orchestrationId);
    
    const currentStep = state.getCurrentStep();
    if (!currentStep) {
      // Workflow is complete
      return ResponseFormats.directive(
        'complete',
        'workflow_complete',
        'The workflow is complete.',
        state.workflow.getPersistentContext(),
        null,
        'All steps have been completed successfully.'
      );
    }
    
    // Get persistent context
    const persistentContext = state.workflow.getPersistentContext();
    
    // Determine if context should be injected for this step
    let injectedContext = null;
    
    // Check if we should inject features (if not already injected)
    if (!state.injectionHistory.features && 
        currentStep.type === 'implement' && 
        state.workflow.features) {
      injectedContext = { features: state.workflow.features.markers };
      state.injectionHistory.features = true;
    }
    // Check if we should inject styles (if not already injected)
    else if (!state.injectionHistory.styles && 
             currentStep.type === 'style' && 
             state.workflow.styles) {
      injectedContext = { styles: state.workflow.styles.markers };
      state.injectionHistory.styles = true;
    }
    // Default injection based on workflow progress
    else if (!state.injectionHistory.features && 
             state.getProgress() >= 33 && 
             state.workflow.features) {
      injectedContext = { features: state.workflow.features.markers };
      state.injectionHistory.features = true;
    }
    else if (!state.injectionHistory.styles && 
             state.getProgress() >= 66 && 
             state.workflow.styles) {
      injectedContext = { styles: state.workflow.styles.markers };
      state.injectionHistory.styles = true;
    }
    
    // Create instruction from step description
    const instruction = `${currentStep.description}`;
    
    // Create guidance based on step type
    let guidance = '';
    switch (currentStep.type) {
      case 'plan':
        guidance = 'Focus on planning and architecture. Consider the overall structure and design.';
        break;
      case 'implement':
        guidance = 'Focus on implementation details. Write code and build functionality.';
        break;
      case 'style':
        guidance = 'Focus on styling and presentation. Ensure the output is well-formatted and visually appealing.';
        break;
      case 'test':
        guidance = 'Focus on testing and validation. Ensure the implementation meets requirements.';
        break;
      case 'document':
        guidance = 'Focus on documentation. Explain how the implementation works and how to use it.';
        break;
      default:
        guidance = 'Complete the task according to the requirements.';
    }
    
    return ResponseFormats.directive(
      'execute',
      currentStep.id,
      instruction,
      persistentContext,
      injectedContext,
      guidance
    );
  }

  /**
   * Complete a step in the orchestration
   * @param {string} orchestrationId - Orchestration ID
   * @param {string} stepId - Step ID
   * @param {object} result - Step result
   * @returns {Promise<object>} - Step completion result
   */
  async completeStep(orchestrationId, stepId, result) {
    const state = this._getWorkflowState(orchestrationId);
    
    const currentStep = state.getCurrentStep();
    if (!currentStep) {
      throw new Error('No current step to complete');
    }
    
    if (currentStep.id !== stepId) {
      throw new Error(`Step ID mismatch: expected ${currentStep.id}, got ${stepId}`);
    }
    
    // Move to next step
    const nextStep = state.moveToNextStep();
    
    // Evaluate result against success criteria
    const evaluation = await this.evaluateAgainstCriteria(orchestrationId, result);
    
    return ResponseFormats.stepCompletion(
      'success',
      nextStep ? nextStep.id : null,
      evaluation
    );
  }

  /**
   * Get workflow status
   * @param {string} orchestrationId - Orchestration ID
   * @returns {Promise<object>} - Workflow status
   */
  async getWorkflowStatus(orchestrationId) {
    const state = this._getWorkflowState(orchestrationId);
    
    const currentStep = state.getCurrentStep();
    
    return ResponseFormats.workflowStatus(
      state.getStatus(),
      state.getProgress(),
      currentStep,
      state.completedSteps,
      currentStep ? state.steps.slice(state.currentStepIndex) : []
    );
  }

  /**
   * Evaluate a result against success criteria
   * @param {string} orchestrationId - Orchestration ID
   * @param {object} result - Result to evaluate
   * @returns {Promise<object>} - Evaluation result
   */
  async evaluateAgainstCriteria(orchestrationId, result) {
    const state = this._getWorkflowState(orchestrationId);
    
    // Get success criteria
    const persistentContext = state.workflow.getPersistentContext();
    const criteria = persistentContext.criteria || [];
    
    // Simple evaluation - just check if result exists
    const success = !!result;
    
    // In a real implementation, this would do more sophisticated evaluation
    const criteriaResults = Array.isArray(criteria) ? criteria.map(criterion => {
      return {
        criterion,
        satisfied: true, // Simplified evaluation
        feedback: 'Criterion satisfied'
      };
    }) : [];
    
    return ResponseFormats.evaluation(
      success,
      criteriaResults,
      'Evaluation complete'
    );
  }

  /**
   * Get persistent context for an orchestration
   * @param {string} orchestrationId - Orchestration ID
   * @returns {Promise<object>} - Persistent context
   */
  async getPersistentContext(orchestrationId) {
    const state = this._getWorkflowState(orchestrationId);
    return state.workflow.getPersistentContext();
  }

  /**
   * Set a workflow variable
   * @param {string} orchestrationId - Orchestration ID
   * @param {string} key - Variable key
   * @param {any} value - Variable value
   * @returns {Promise<boolean>} - Success indicator
   */
  async setWorkflowVariable(orchestrationId, key, value) {
    const state = this._getWorkflowState(orchestrationId);
    state.setVariable(key, value);
    return true;
  }

  /**
   * Get a workflow variable
   * @param {string} orchestrationId - Orchestration ID
   * @param {string} key - Variable key
   * @returns {Promise<any>} - Variable value
   */
  async getWorkflowVariable(orchestrationId, key) {
    const state = this._getWorkflowState(orchestrationId);
    return {
      key,
      value: state.getVariable(key)
    };
  }

  /**
   * Get workflow state by ID
   * @param {string} orchestrationId - Orchestration ID
   * @returns {WorkflowState} - Workflow state
   * @throws {Error} - If workflow state not found
   * @private
   */
  _getWorkflowState(orchestrationId) {
    const state = this.workflows[orchestrationId];
    if (!state) {
      throw new Error(`Workflow not found: ${orchestrationId}`);
    }
    return state;
  }
}

module.exports = {
  OrchestrationEngine,
  WorkflowState
};
