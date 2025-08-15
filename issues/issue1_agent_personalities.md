# Issue: Add Support for Multiple Agent Personalities [COMPLETED]

## Description

Currently, our AI agent has a single personality defined in the gunicorn.conf.py file with basic instructions:
```python
instructions = "Use AI Search always. Avoid to use base knowledge." if isinstance(tool, AzureAISearchTool) else "Use File Search always.  Avoid to use base knowledge."
```

This is limiting for users who might want different personalities for their agents depending on the use case (e.g., customer service, technical support, sales assistant).

## Implementation Tasks

1. Modify `src/gunicorn.conf.py` to support configurable agent personalities through environment variables.
2. Create a set of predefined personalities that define different behaviors (customer service, technical support, sales, etc.).
3. Update the agent creation process to apply the selected personality.
4. Update the frontend UI in `src/frontend/src/components/agents/AgentPreview.tsx` to allow selecting different personalities.
5. Add documentation in README.md about how to configure and use different personalities.

## Technical Requirements

- Add a new environment variable called `AZURE_AI_AGENT_PERSONALITY` to select from predefined personalities.
- Create a dictionary of personality profiles in `gunicorn.conf.py` that include instructions, temperature, and other relevant parameters.
- Update `azure.yaml` to include the new environment variable.
- Update the frontend to display and allow selection of available personalities.

## Acceptance Criteria

- Users can select from at least 3 predefined personalities when creating an agent.
- Each personality should have different instructions and parameters.
- The frontend allows easy switching between personalities.
- Documentation explains how to create custom personalities.
- All changes maintain backward compatibility with existing deployment methods.
