## SNLP Syntax Guide

Syntactical Natural Language Programming (SNLP) is the core syntax used in MCO files. It combines structured markers with natural language to create a hybrid approach that is both machine-parsable and human-readable.

### Basic Syntax

```
@marker Identifier
>NLP Natural language content that provides context, instructions, or details.
```

- **@marker**: Defines the type of content that follows
- **Identifier**: Names or categorizes the content (optional for some markers)
- **>NLP**: Indicates natural language content follows

### Example SNLP Syntax

```
@data Research capability
>NLP The agent should be able to search for information on a given topic using available tools.

@data Analysis capability
>NLP The agent should analyze and synthesize information from multiple sources, identifying patterns and insights.
```

### Common Markers

| Marker | Purpose | Example |
|--------|---------|---------|
| `@data` | Defines a data point or capability | `@data Search capability` |
| `@workflow` | Defines workflow metadata | `@workflow "Research Assistant"` |
| `@goal` | Defines the overall goal | `@goal "Create a comprehensive research report"` |
| `@success_criteria` | Defines evaluation criteria | `@success_criteria "Contains at least 3 sources"` |
| `@optional` | Defines optional features | `@optional Advanced visualization` |
| `@style` | Defines styling preferences | `@style "Academic writing style"` |

### Progressive Structure

SNLP follows a progressive structure where each new element builds on previous ones:

```
@data Foundation
>NLP First, establish the basic structure.

@data Building blocks
>NLP Next, add the core components that build on the foundation.

@data Advanced features
>NLP Finally, incorporate advanced features that enhance the core components.
```

This progressive approach mirrors how software development naturally occurs - starting with foundations and building up in layers.

## File Types
