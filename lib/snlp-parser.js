/**
 * SNLP Parser Module
 * 
 * This module handles parsing of Syntactic Natural Language Programming (SNLP) files
 * used by the MCO MCP Server for orchestration.
 */

const fs = require('fs-extra');
const path = require('path');
const yaml = require('yaml');

/**
 * Represents a parsed SNLP file
 */
class ParsedSNLP {
  constructor() {
    this.markers = {};
    this.nlpSections = {};
    this.rawContent = '';
    this.fileType = '';
  }
}

/**
 * Represents a complete parsed MCO workflow
 */
class ParsedWorkflow {
  constructor() {
    this.core = null;
    this.sc = null;
    this.features = null;
    this.styles = null;
    this.configDir = '';
  }

  /**
   * Check if the workflow has the minimum required files
   */
  isValid() {
    return this.core !== null && this.sc !== null;
  }

  /**
   * Get persistent context from core and sc files
   */
  getPersistentContext() {
    const context = {
      core: this.core ? this.core.markers : {},
      success_criteria: this.sc ? this.sc.markers : {},
    };

    // Extract specific fields for easier access
    if (this.core && this.core.markers) {
      if (this.core.markers.workflow) {
        context.workflow_name = this.core.markers.workflow;
      }
      if (this.core.markers.data) {
        context.data = this.core.markers.data;
      }
    }

    if (this.sc && this.sc.markers) {
      if (this.sc.markers.success_criteria) {
        context.criteria = this.sc.markers.success_criteria;
      }
      if (this.sc.markers.goal) {
        context.goal = this.sc.markers.goal;
      }
      if (this.sc.markers.target_audience) {
        context.target_audience = this.sc.markers.target_audience;
      }
      if (this.sc.markers.developer_vision) {
        context.developer_vision = this.sc.markers.developer_vision;
      }
    }

    return context;
  }

  /**
   * Get injectable context for a specific step
   * @param {string} stepType - Type of step (e.g., "implement", "develop", "style", "format")
   */
  getInjectableContext(stepType) {
    const context = {};

    // Determine if features should be injected
    if (this.features && 
        (stepType === 'implement' || 
         stepType === 'develop' || 
         stepType === 'code' || 
         stepType === 'build')) {
      context.features = this.features.markers;
    }

    // Determine if styles should be injected
    if (this.styles && 
        (stepType === 'style' || 
         stepType === 'format' || 
         stepType === 'design' || 
         stepType === 'present')) {
      context.styles = this.styles.markers;
    }

    return Object.keys(context).length > 0 ? context : null;
  }
}

/**
 * Main SNLP Parser class
 */
class SNLPParser {
  /**
   * Parse a single SNLP file
   * @param {string} filePath - Path to the SNLP file
   * @returns {ParsedSNLP} - Parsed SNLP object
   */
  async parseFile(filePath) {
    try {
      const content = await fs.readFile(filePath, 'utf8');
      const fileName = path.basename(filePath);
      const fileType = fileName.split('.')[1]; // e.g., "core", "sc", "features", "styles"
      
      const parsed = new ParsedSNLP();
      parsed.rawContent = content;
      parsed.fileType = fileType;
      
      // Parse markers and NLP sections
      this._parseContent(content, parsed);
      
      return parsed;
    } catch (error) {
      console.error(`Error parsing SNLP file ${filePath}:`, error);
      throw error;
    }
  }

  /**
   * Parse all SNLP files in a directory
   * @param {string} dirPath - Path to the directory containing SNLP files
   * @returns {ParsedWorkflow} - Parsed workflow object
   */
  async parseDirectory(dirPath) {
    try {
      const workflow = new ParsedWorkflow();
      workflow.configDir = dirPath;
      
      // Check if directory exists
      const dirExists = await fs.pathExists(dirPath);
      if (!dirExists) {
        throw new Error(`Directory ${dirPath} does not exist`);
      }
      
      // Read all files in directory
      const files = await fs.readdir(dirPath);
      
      // Parse each MCO file
      for (const file of files) {
        if (file.startsWith('mco.')) {
          const filePath = path.join(dirPath, file);
          const parsed = await this.parseFile(filePath);
          
          // Assign to appropriate property in workflow
          if (file === 'mco.core') {
            workflow.core = parsed;
          } else if (file === 'mco.sc') {
            workflow.sc = parsed;
          } else if (file === 'mco.features') {
            workflow.features = parsed;
          } else if (file === 'mco.styles') {
            workflow.styles = parsed;
          }
        }
      }
      
      // Validate workflow
      if (!workflow.isValid()) {
        throw new Error(`Invalid workflow: missing required files (mco.core and/or mco.sc)`);
      }
      
      return workflow;
    } catch (error) {
      console.error(`Error parsing SNLP directory ${dirPath}:`, error);
      throw error;
    }
  }

  /**
   * Validate SNLP content
   * @param {string} content - SNLP content to validate
   * @returns {object} - Validation result
   */
  validateSNLP(content) {
    try {
      const parsed = new ParsedSNLP();
      this._parseContent(content, parsed);
      
      return {
        valid: true,
        markers: Object.keys(parsed.markers),
        nlpSections: Object.keys(parsed.nlpSections)
      };
    } catch (error) {
      return {
        valid: false,
        error: error.message
      };
    }
  }

  /**
   * Parse SNLP content and extract markers and NLP sections
   * @param {string} content - SNLP content to parse
   * @param {ParsedSNLP} parsed - ParsedSNLP object to populate
   * @private
   */
  _parseContent(content, parsed) {
    // Split content into lines
    const lines = content.split('\n');
    
    let currentMarker = null;
    let currentNLP = null;
    let currentContent = [];
    let inNLPSection = false;
    
    // Process each line
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Skip empty lines and comments
      if (line === '' || line.startsWith('//')) {
        continue;
      }
      
      // Check for marker
      if (line.startsWith('@')) {
        // Save previous marker if exists
        if (currentMarker) {
          if (currentContent.length > 0) {
            try {
              // Try to parse as YAML
              const yamlContent = currentContent.join('\n');
              parsed.markers[currentMarker] = yaml.parse(yamlContent);
            } catch (error) {
              // If not valid YAML, store as string
              parsed.markers[currentMarker] = currentContent.join('\n');
            }
            currentContent = [];
          }
        }
        
        // Extract new marker
        const markerMatch = line.match(/@([a-zA-Z_]+)(?:\s+"([^"]+)")?/);
        if (markerMatch) {
          currentMarker = markerMatch[1];
          if (markerMatch[2]) {
            // If marker has a value in quotes, store it directly
            parsed.markers[currentMarker] = markerMatch[2];
            currentMarker = null; // Reset current marker
          }
        }
      }
      // Check for NLP section
      else if (line.startsWith('>')) {
        inNLPSection = true;
        currentNLP = currentMarker || 'default';
        parsed.nlpSections[currentNLP] = parsed.nlpSections[currentNLP] || [];
        
        // Extract NLP content (remove the '>' prefix)
        const nlpContent = line.substring(1).trim();
        if (nlpContent) {
          parsed.nlpSections[currentNLP].push(nlpContent);
        }
      }
      // Content line
      else {
        if (inNLPSection) {
          // Add to NLP section
          parsed.nlpSections[currentNLP].push(line);
        } else if (currentMarker) {
          // Add to current marker content
          currentContent.push(line);
        }
      }
    }
    
    // Save last marker if exists
    if (currentMarker && currentContent.length > 0) {
      try {
        // Try to parse as YAML
        const yamlContent = currentContent.join('\n');
        parsed.markers[currentMarker] = yaml.parse(yamlContent);
      } catch (error) {
        // If not valid YAML, store as string
        parsed.markers[currentMarker] = currentContent.join('\n');
      }
    }
  }
}

module.exports = {
  SNLPParser,
  ParsedSNLP,
  ParsedWorkflow
};
