# MCO Server Documentation

## File Types and Progressive Structure

The MCO Server implements a multi-file approach that supports progressive revelation and a clear separation of concerns. This document explains each file type, its purpose, and how they work together in the orchestration process.

## Core File Types

### 1. mco.core

The `mco.core` file contains the essential, ordered definitions that form the foundation of the orchestration. This file is always loaded into persistent memory and is available throughout the entire orchestration process.

**Structure:**
```
// --- mco.core --- 

// Metadata Section
@workflow "Workflow Name"
@description "Description of the workflow"
@version "1.0"

// Data Section (Core Data Structures & Initial State)
@data:
  key1: value1
  key2: value2
  // ... other core data variables

// Agents Section
@agents:
  agent1:
    model: "model_name"
    description: "Agent description"
    tools: ["tool1", "tool2"]
  
  agent2:
    model: "model_name"
    description: "Agent description"
    tools: ["tool1", "tool2"]

// Workflow Section
@workflow_steps:
  step1:
    agent: "agent1"
    task: "Task description with {variable} placeholders"
    output: "output_variable"
    
  step2:
    agent: "agent2"
    task: "Task description"
    input: "{input_variable}"
    output: "output_variable"

// Error Handling
@error_handling:
  error_condition1:
    condition: "Condition expression"
    action: "Action to take"
```

**Purpose:**
- Defines the core workflow structure and components
- Establishes the data model and initial state
- Specifies the agents involved and their capabilities
- Outlines the workflow steps and their relationships
- Provides error handling mechanisms

**Progressive Revelation:**
The `mco.core` file follows a progressive structure where each section builds on the previous ones:
1. Metadata provides the high-level context
2. Data defines the variables that will be used
3. Agents specify who will perform the tasks
4. Workflow steps define what will be done and in what order
5. Error handling addresses what happens when things go wrong

### 2. mco.sc (Success Criteria)

The `mco.sc` file defines the overall goal, success criteria, target audience, and developer vision. Like `mco.core`, this file is loaded into persistent memory and is available throughout the orchestration.

**Structure:**
```
// --- mco.sc --- 

@goal
  "Detailed description of the overall goal of the workflow."

@success_criteria
  - "Criterion 1"
  - "Criterion 2"
  - "Criterion 3"
  // ... additional criteria

@target_audience
  "Description of the intended audience for the workflow outputs."

@developer_vision
  "The developer's vision for how this workflow should function and what value it should provide."
```

**Purpose:**
- Defines what success looks like for the workflow
- Establishes the target audience to guide output formatting and complexity
- Captures the developer's vision to align the execution with intentions
- Provides a reference point for evaluation throughout the workflow

**Progressive Revelation:**
The `mco.sc` file builds on the `mco.core` file by adding:
1. The goal that the workflow is trying to achieve
2. Specific criteria that must be met for success
3. The audience that will consume the output
4. The developer's vision for the workflow's value

### 3. mco.features

The `mco.features` file contains optional features and brainstorming ideas. Unlike `mco.core` and `mco.sc`, this file is not loaded into persistent memory but is instead injected at strategic points in the workflow, typically during implementation or development steps.

**Structure:**
```
// --- mco.features --- 

@optional
  feature1:
    description: "Description of optional feature"
    > "Additional natural language context about the feature"
  
  feature2:
    description: "Description of optional feature"
    > "Additional natural language context about the feature"

@brainstorm
  - "Idea 1"
  - "Idea 2"
  - "Idea 3"
  // ... additional ideas
```

**Purpose:**
- Provides optional features that can be implemented if time and resources allow
- Offers creative ideas and possibilities for exploration
- Allows for flexibility and innovation beyond the core requirements
- Supports the "progressive revelation" approach by introducing new ideas at appropriate times

**Strategic Injection:**
The `mco.features` file is injected at strategic points in the workflow, typically:
- During implementation or development steps
- When creative solutions are needed
- At approximately 1/3 of the way through the workflow (if no specific injection points are identified)

### 4. mco.styles

The `mco.styles` file defines styling preferences and guidelines. Like `mco.features`, this file is not loaded into persistent memory but is injected at strategic points, typically during styling, formatting, or presentation steps.

**Structure:**
```
// --- mco.styles --- 

@style_guide
  category1:
    attribute1: "Value"
    attribute2: "Value"
  
  category2:
    attribute1: "Value"
    attribute2: "Value"
  
  > "Additional natural language context about styling preferences"
```

**Purpose:**
- Defines the visual and stylistic aspects of the workflow output
- Provides guidelines for formatting, language style, and presentation
- Ensures consistency and quality in the final deliverables
- Supports the "progressive revelation" approach by introducing styling concerns at appropriate times

**Strategic Injection:**
The `mco.styles` file is injected at strategic points in the workflow, typically:
- During styling or formatting steps
- When preparing final presentations or outputs
- At approximately 2/3 of the way through the workflow (if no specific injection points are identified)

## How They Work Together

The MCO Server implements a sophisticated orchestration mechanism that leverages these file types in a way that allows for effective AI Agent orchestration:

1. **Persistent Memory:**
   - `mco.core` and `mco.sc` are loaded into persistent memory at the start of orchestration
   - They are always available to the agents throughout the entire workflow
   - They provide the foundational structure and success criteria

2. **Strategic Injection:**
   - `mco.features` is injected during implementation/development steps
   - `mco.styles` is injected during styling/formatting steps
   - Injection points are determined by analyzing the workflow steps or using default positions

3. **Progressive Revelation:**
   - The structure follows a natural progression from core definitions to success criteria to features to styling
   - Each file builds on the previous ones, adding new layers of information
   - This approach prevents overwhelming agents with too much information at once

4. **Syntax-NLP Flow:**
   - The files combine structured syntax (`@sections`) with natural language processing (NLP) context (`> "text"`)
   - This creates an effective flow between structured data and flexible guidance
   - The NLP sections allow for nuance and creativity within the structured framework

## Implementation Details

The MCO Server implements this approach through several key components:

1. **ConfigManager:**
   - Loads and parses all file types
   - Preserves the exact syntax and structure
   - Maintains the separation between different file types

2. **PersistentMemoryManager:**
   - Manages what goes into persistent memory vs. what gets injected
   - Determines appropriate injection points based on workflow analysis
   - Ensures the right information is available at the right time

3. **Orchestrator:**
   - Coordinates the workflow execution
   - Implements the progressive revelation structure
   - Handles the flow between different steps

4. **Adapters:**
   - Framework-specific implementations that connect to different agent frameworks
   - Translate the MCO protocol into framework-specific instructions
   - Preserve the persistent vs. injected distinction

## Example Usage

Here's how a typical workflow might progress:

1. **Initial Setup:**
   - Load `mco.core` and `mco.sc` into persistent memory
   - Analyze workflow to determine injection points for `mco.features` and `mco.styles`

2. **Early Steps:**
   - Agents work with just the core structure and success criteria
   - Focus is on understanding the problem and planning

3. **Implementation Steps:**
   - Inject `mco.features` to guide development
   - Agents now have access to optional features and creative ideas

4. **Styling Steps:**
   - Inject `mco.styles` to guide presentation
   - Agents now have access to styling guidelines and preferences

5. **Evaluation:**
   - Throughout the process, evaluate progress against success criteria
   - Ensure the workflow is aligned with the goal and developer vision

This progressive approach ensures that agents are not overwhelmed with information and can focus on the appropriate aspects at each stage of the workflow.
