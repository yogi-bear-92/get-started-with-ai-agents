# Agent Personalities

This feature allows you to configure different personalities for your AI agent, providing more tailored and specialized behavior depending on your use case.

## Available Personalities

The following personalities are available:

1. **Default** - Basic agent behavior with standard knowledge retrieval instructions.
   - Balanced temperature (0.7)
   - Uses knowledge source (AI Search or File Search) for information retrieval

2. **Customer Service** - Optimized for customer support scenarios.
   - More conservative temperature (0.5) for reliable responses
   - Polite, patient, and professional tone
   - Focuses on product and service information
   - Will acknowledge limitations and offer human escalation when appropriate

3. **Technical Support** - Specialized for technical assistance.
   - Low temperature (0.3) for precise technical information
   - Clear and concise technical explanations
   - Ability to simplify complex concepts when needed
   - Focuses on procedural guidance and troubleshooting

4. **Sales Assistant** - Designed for product recommendations and sales.
   - Moderate temperature (0.6) for creativity in recommendations
   - Highlights product benefits and features
   - Makes appropriate product recommendations
   - Focuses on matching products to customer needs

5. **Concierge** - Refined personal assistant providing premium service.
   - Balanced temperature (0.7) for personalized recommendations
   - Sophisticated and courteous communication style
   - Focuses on providing exceptional service and attention to detail
   - Perfect for hospitality and premium services scenarios

## Configuration

You can select a personality by setting the `AZURE_AI_AGENT_PERSONALITY` environment variable to one of the following values:
- `default`
- `customer_service`
- `technical_support`
- `sales_assistant`
- `concierge`

### Local Development

For local development, set the environment variable in your `.env` file:

```
AZURE_AI_AGENT_PERSONALITY=technical_support
```

### Azure Deployment

When deploying to Azure, set the environment variable using Azure Developer CLI:

```bash
azd env set AZURE_AI_AGENT_PERSONALITY customer_service
```

## Creating Custom Personalities

To create a custom personality:

1. Modify the `agent_personalities` dictionary in `src/gunicorn.conf.py`
2. Define a new personality with the following properties:
   - `instructions`: Specific guidance for the agent behavior
   - `temperature`: Controls creativity vs. consistency (0.0-1.0)
   - Other optional parameters as needed

Example of adding a custom personality:

```python
"researcher": {
    "instructions": "You are a research assistant. Provide thorough, accurate, and well-sourced information. " +
                 "Use AI Search to find authoritative information. " +
                 "Always cite sources and acknowledge limitations in available information.",
    "temperature": 0.2,
},
```

**Important**: Remember that changing agent personalities requires recreating the agent. The agent operates in read-only mode after creation, so you'll need to delete the existing agent and create a new one with the updated personality.
