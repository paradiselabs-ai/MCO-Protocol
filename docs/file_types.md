# MCO Server Documentation

## File Types and Progressive Structure

The MCO Server implements the original Percertain DSL structure with a multi-file approach that supports progressive revelation and a clear separation of concerns. This document explains each file type, its purpose, and how they work together in the orchestration process.

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

The MCO Server implements a sophisticated orchestration mechanism that leverages these file types in a way that gives the agent(s) persistent context 
of core features and the developers defined criteria for success, while strategically injecting the less vital features and styling, into the system prompt and agent roles and by acting as a new prompt being given, and starts repeatedly looping through them at strategic times.
Because of the structure of the SNLP syntax, using "progressive revelation", each MCO file starts at the top with the most foundational and basic core functionality or whatever it is you are orchestrating the agents to develop, and as the file is read, each new section builds on top of the one previous, meaning ideally, a @definition that is 4th from the top should only be understood as a task or instruction because it continues from the 3rd above it, and continue through referential and iterative development. 
Each new @data value gives the agent more insight and context into the user's application or project that is being developed. This progressive iteration of information, with the repetative prompt injection the MCO server implements, allows the agents to develop *not* by giving the entire specs of the project to the agents through a long, well structured prompt, or a .agentrules type of file used by many different coding agnets in many IDE's (i.e. Cline (Claude Dev) using a .clinerules file in the root directory), but allowing the agent to loop through the specs, structured so that it builds iteratively from the bottom up, ensuring that nothing gets forgotten, or overlooked, reducing hallucinations, not having to remember a single, long, multi-faceted prompt that lays out the entire project. 

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

## TL;DR - A quick analogy to help you understand what MCO is doing

Imagine two people that are the exact same. Two versions of the same person, (A/B diff views of a person). This person is an artist, a painter with a large canvas, thumb gripping a palette with many different colors, ready to paint a masterpiece. Each version has been hired to paint a specific image of intricate detailed bustling city scene with many different people, cars, shops, buildings, birds, a specific number of windows each building has, street signs, clouds, even the specific clothes people are wearing. 

### Version 1 - Instructed by prompted/vibe coding (Non-MCO)

1. The painter recieves from the person who hired him a very long, extremely detailed, extremely descriptive, very specific set of instructions for the painting. The painter reads it, then starts to paint. 
2. Continuing to paint from memory of the instructions, the painter paints everything that he remembers, until he has to read the instructions again.
3. Upon re-reading the instructions the painter realizes that he has painted several different sections that nearly follow the instructions, but some of the color choices and other little details are not correct. What's more is the painter notices that the scene has some background elements that really should have been painted first, then paint the parts that have already been painted over those background elements.
4. The painter must fix several things, with no clear plan or standard process of refactoring the painting to fix the parts that are wrong, sometimes attempting to paint the background elements *carefully* around the objects in the foreground elements, sometimes painting over the foreground elements entirely and then repainting them (sometimes inaccurately). 
5. Repeat steps 3 - 4 as many times as needed, until either finally is finished, or the buyer who hired the painter asks for his money back.  


### Version 2 - Using the MCO Protocol

1. The painter looks at the instructions. Before there was any instructions there was a request at the top: "Paint each part step by step in the order that I gave you: First, paint a landscape that we will fit things into later, where a river is the middle, getting smaller and fading in perspective. Next paint a small boat about 2/3rds of the way, just cruising down the river, then paint a blue stripe across the part of the boat not in the water. After this, in the upper left side-ish of the page, (not too far up or too the right though) paint a flock of birds, but make a flew of the typical V shape when birds fly together, make one side of the V seem a little off by putting an extra space between the second and third birds, as if the bird was invisible. Now, between the boat and the birds, paint a bird that had left the formation, and was now almost aggressively flying towards the boat." No doubt, the painter would need to keep going back to the instructions in order to follow them the best way, and this is how MCO works. The instructions "Paint each part step by step in the order that I gave you: First, paint a landscape that we will fit things into later, where a river is the middle, getting smaller and fading in perspective." would be the persistent part that stays in its persistent context. The rest would be stregically placed in the agent loop so as they loop they read more and understand  more of your instructions, without having to backtrack, or return to a different section, it can build more as each time it loops its forgotten what comes next after a certain numer of tasks. And this is who MCO allows for better control over the agents. 


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
