# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Optional, Dict, Any
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Azure imports
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects import AIProjectClient
import azure.ai.agents  # noqa: F401 (ensures agents namespace is loaded if needed)
from azure.ai.agents.models import ListSortOrder

# Red Team (preview) import is optional – provide graceful fallback if package / submodule missing
try:  # pragma: no cover - environment dependent
    from azure.ai.evaluation.red_team import RedTeam, RiskCategory, AttackStrategy  # type: ignore
    _RED_TEAM_AVAILABLE = True
except Exception as _rt_err:  # broad except to surface any packaging mismatch
    RedTeam = None  # type: ignore
    RiskCategory = None  # type: ignore
    AttackStrategy = None  # type: ignore
    _RED_TEAM_AVAILABLE = False
    _RED_TEAM_IMPORT_ERROR = _rt_err  # noqa: N816

async def run_red_team():
    """Run a Red Team scan against an existing agent.

    Requirements:
      - Environment variables:
          AZURE_EXISTING_AIPROJECT_ENDPOINT
          (AZURE_EXISTING_AGENT_ID | AZURE_AI_AGENT_NAME)
          [optional] AZURE_AI_AGENT_DEPLOYMENT_NAME
      - Package providing azure.ai.evaluation.red_team (preview). If unavailable, a clear
        guidance error is raised instead of an ImportError surfacing in editors.
    """
    # Load environment variables from .env file
    current_dir = Path(__file__).parent
    env_path = current_dir / "../src/.env"
    load_dotenv(dotenv_path=env_path)

    if not _RED_TEAM_AVAILABLE:
        raise RuntimeError(
            "Red Team module not available. Ensure the 'azure-ai-evaluation' package version "
            "supports 'azure.ai.evaluation.red_team'. Original import error: "
            f"{_RED_TEAM_IMPORT_ERROR}"
        )

    # Get AI project parameters from environment variables (matching evaluate.py)
    project_endpoint = os.environ.get("AZURE_EXISTING_AIPROJECT_ENDPOINT")
    deployment_name = os.getenv("AZURE_AI_AGENT_DEPLOYMENT_NAME")  # Using getenv for consistency with evaluate.py
    agent_id = os.environ.get("AZURE_EXISTING_AGENT_ID")
    agent_name = os.environ.get("AZURE_AI_AGENT_NAME")
    
    # Validate required environment variables
    if not project_endpoint:
        raise ValueError("Please set the AZURE_EXISTING_AIPROJECT_ENDPOINT environment variable.")
        
    if not agent_id and not agent_name:
        raise ValueError("Please set either AZURE_EXISTING_AGENT_ID or AZURE_AI_AGENT_NAME environment variable.")

    # Initialize Azure credentials (single context for clarity)
    with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:
        with AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client:
            # Look up the agent by name if agent ID is not provided (matching evaluate.py)
            if not agent_id and agent_name:
                for agent in project_client.agents.list_agents():
                    if agent.name == agent_name:
                        agent_id = agent.id
                        break
                        
            if not agent_id:
                raise ValueError("Agent ID not found. Please provide a valid agent ID or name.")
                
            agent = project_client.agents.get_agent(agent_id)
            
            # Use model from agent if not provided - matching evaluate.py
            if not deployment_name:
                deployment_name = agent.model
                
            thread = project_client.agents.threads.create()

            def agent_callback(query: str) -> str:
                message = project_client.agents.messages.create(thread_id=thread.id, role="user", content=query)
                run = project_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)

                # Poll the run as long as run status is queued or in progress
                while run.status in ["queued", "in_progress", "requires_action"]:
                    # Wait for a second
                    time.sleep(1)
                    run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
                    # [END create_run]
                    print(f"Run status: {run.status}")

                if run.status == "failed":
                    print(f"Run error: {run.last_error}")
                    return "Error: Agent run failed."
                messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.DESCENDING)
                for msg in messages:
                    if msg.text_messages:
                        return msg.text_messages[0].text.value
                return "Could not get a response from the agent."
        

            # Print agent details to verify correct targeting
            print(f"Running Red Team evaluation against agent:")
            print(f"  - Agent ID: {agent.id}")
            print(f"  - Agent Name: {agent.name}")
            print(f"  - Using Model: {deployment_name}")
            
            # Configure Red Team scan (type: ignore used because objects are optional at import time)
            assert RedTeam is not None and RiskCategory is not None and AttackStrategy is not None, "Red Team components unexpectedly None after availability check"
            red_team = RedTeam(  # type: ignore[operator]
                azure_ai_project=project_endpoint,
                credential=credential,
                risk_categories=[RiskCategory.Violence],  # type: ignore[attr-defined]
                num_objectives=1,
                output_dir="redteam_outputs/",
            )

            print("Starting Red Team scan...")
            result = await red_team.scan(  # type: ignore[operator]
                target=agent_callback,
                scan_name="Agent-Scan",
                attack_strategies=[AttackStrategy.Flip],  # type: ignore[attr-defined]
            )
            print("Red Team scan complete.")
            return result

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_red_team())