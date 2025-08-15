#!/bin/bash
# Test script for agent personality feature

echo "Testing Agent Personality Feature"
echo "================================="

# Set environment variables for the agent personalities
export AZURE_AI_AGENT_PERSONALITY=default
echo "Set agent personality to: default"

# Run the gunicorn initialization code directly to test agent creation
python -c "
import sys
import os
sys.path.append('/workspaces/get-started-with-ai-agents/src')
os.environ['AZURE_AI_AGENT_PERSONALITY'] = 'customer_service'
print('Creating agent with personality: customer_service')
from gunicorn.conf import initialize_resources
import asyncio
asyncio.run(initialize_resources())
"

# Test each personality
personalities=("default" "customer_service" "technical_support" "sales_assistant" "concierge")

for personality in "${personalities[@]}"; do
    echo ""
    echo "Testing personality: $personality"
    export AZURE_AI_AGENT_PERSONALITY=$personality

    # Run a simple test to check if the personality is being applied correctly
    # This would typically involve creating a test agent and verifying its instructions
    # For this example, we'll just print the personality being used

    echo "AZURE_AI_AGENT_PERSONALITY=$AZURE_AI_AGENT_PERSONALITY"

    # In a real test, we might verify the agent's behavior by sending test queries
    # and checking the responses
done

echo ""
echo "Personality test complete"
