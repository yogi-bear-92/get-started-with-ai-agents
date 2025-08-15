# AI Agent Guidelines for get-started-with-ai-agents

## Project Overview
This is a sample application that demonstrates how to build and deploy AI agents using Azure AI Foundry. The solution creates a web-based chat interface that leverages Azure AI Agent service and uses file search for knowledge retrieval from uploaded files, enabling responses with citations.

## Guidelines for Copilot Coding Agent

When working with this codebase as a Copilot coding agent:

1. **Focus on Azure Integration**: When modifying code, always maintain proper Azure service integration patterns - especially with Azure AI Foundry, AI Agents, and identity management.

2. **Configuration Priority**: Prioritize environment variables over hardcoded values. All configurations should be handled via the `azure.yaml` and environment files.

3. **File Operation Timing**: Be extremely careful when suggesting file operations for AI agents. Remember files must be in place BEFORE agent creation, not after.

4. **Development Tasks**: For local development tasks, suggest deployment with `azd up` first, then local testing with the FastAPI server using `uvicorn`.

5. **Evaluation Testing**: When implementing new features or fixing issues, recommend running both evaluation (`evals/evaluate.py`) and red teaming (`airedteaming/ai_redteaming.py`) tests.

## Architecture

The application consists of these main components:
- **Web Frontend**: React UI for chat interaction (`src/frontend/`)
- **Backend API**: FastAPI service for handling agent communication (`src/api/`)
- **AI Agent**: Built using Azure AI Foundry project and services
- **Evaluations**: Tools for agent quality evaluation (`evals/`)
- **Red Teaming**: Security testing capabilities (`airedteaming/`)

## Key Development Workflows

### 1. Deployment

Deploy the full solution to Azure:
```bash
azd up
```

This provisions all necessary Azure resources and deploys the application.

### 2. Local Development

After deploying to Azure once, run locally:
```bash
# In src directory
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\scripts\activate
python -m pip install -r requirements.txt

# For frontend development
cd src/frontend
pnpm run setup

# Start server
cd src
python -m uvicorn "api.main:create_app" --factory --reload
```

### 3. Agent Customization

- **Agent instructions** and **tools** are defined in `src/gunicorn.conf.py`
- **IMPORTANT**: Agent files must be added to `src/files/` BEFORE agent creation
- Modifying an existing agent requires recreating it or using the Azure AI Foundry UI

### 4. Key Integration Points

- **Agent Communication**: `src/api/routes.py` handles API endpoints for agent interaction
- **AI Project Client**: `src/api/main.py` initializes the AI project and agent client
- **Frontend-Backend Communication**: `src/frontend/src/components/agents/AgentPreview.tsx` manages requests to backend

### 5. Evaluation and Testing

- Evaluate agent performance: `python evals/evaluate.py`
- Run security testing: `python airedteaming/ai_redteaming.py`

## Configuration

- Most settings are controlled via environment variables (see `azure.yaml` for the list)
- Customizations can be made by setting variables with `azd env set KEY VALUE`
- Important configuration settings:
  - Agent model: `AZURE_AI_AGENT_MODEL_NAME` (default: gpt-4o-mini)
  - Agent model format: `AZURE_AI_AGENT_MODEL_FORMAT` (default: Microsoft)
  - Enable/disable resources: `USE_AZURE_AI_SEARCH_SERVICE`, `USE_APPLICATION_INSIGHTS`

## Project Conventions

- All Python code follows standard practices with module imports at the top
- API routes in FastAPI follow REST principles
- React components are function-based with TypeScript
- Files for agent knowledge must be placed in `src/files/` before agent creation

## Important Note on File Updates

After an agent is created, it operates in **read-only mode** for file operations. If you need to update files:
1. Delete the existing agent in Azure AI Foundry
2. Update files in `src/files/` or `src/data/embeddings.csv`
3. Restart the server or redeploy with `azd deploy`

## Common Tasks for Copilot Agent

### Adding New Agent Features
1. Modify `src/gunicorn.conf.py` to adjust agent instructions or add new tools
2. Add any new knowledge files to `src/files/` directory
3. Update environment variables if needed with `azd env set`
4. Deploy changes with `azd deploy` or restart local server

### Customizing the UI
1. Edit React components in `src/frontend/src/components/`
2. Focus on `AgentPreview.tsx` for message handling and API communication
3. Run `pnpm build` in the frontend directory after changes
4. Restart the local development server to see changes

### Debugging Issues
1. Check application logs in Azure Portal (if deployed) or local server output
2. Verify environment variables are correctly set in `.env` or via `azd env`
3. For agent-specific issues, examine API responses in `src/api/routes.py`
4. Run evaluation tests to verify agent behavior with `python evals/evaluate.py`

### Extending the Application
1. Add new API endpoints in `src/api/routes.py` following existing patterns
2. Ensure proper error handling and async patterns for FastAPI
3. Update frontend components to utilize new endpoints
4. Document any new environment variables in project documentation
