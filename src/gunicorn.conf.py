# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
# See LICENSE file in the project root for full license information.
from typing import Dict, List

import asyncio
import csv
import json
import logging
import multiprocessing
import os
import sys

from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import (
    Agent,
    AsyncToolSet,
    AzureAISearchTool,
    FilePurpose,
    FileSearchTool,
    Tool,
)
from azure.ai.projects.models import ConnectionType, ApiKeyCredentials
from azure.identity.aio import DefaultAzureCredential
from azure.core.credentials_async import AsyncTokenCredential

from dotenv import load_dotenv

from logging_config import configure_logging
from api.file_parser import FileParser
from api.enhanced_file_search import EnhancedFileSearch

load_dotenv()

logger = configure_logging(os.getenv("APP_LOG_FILE", ""))


agentID = os.environ.get("AZURE_EXISTING_AGENT_ID") if os.environ.get(
    "AZURE_EXISTING_AGENT_ID") else os.environ.get(
        "AZURE_AI_AGENT_ID")

proj_endpoint = os.environ.get("AZURE_EXISTING_AIPROJECT_ENDPOINT")


def list_files_in_files_directory() -> List[str]:
    # Get the absolute path of the 'files' directory
    files_directory = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'files'))

    # List all files in the 'files' directory
    files = [f for f in os.listdir(files_directory) if os.path.isfile(
        os.path.join(files_directory, f))]

    return files


FILES_NAMES = list_files_in_files_directory()


async def create_index_maybe(
        ai_client: AIProjectClient, creds: AsyncTokenCredential) -> None:
    """
    Create the index and upload documents if the index does not exist.

    This code is executed only once, when called on_starting hook is being
    called. This code ensures that the index is being populated only once.
    rag.create_index return True if the index was created, meaning that this
    docker node have started first and must populate index.

    :param ai_client: The project client to be used to create an index.
    :param creds: The credentials, used for the index.
    """
    from api.search_index_manager import SearchIndexManager
    endpoint = os.environ.get('AZURE_AI_SEARCH_ENDPOINT')
    embedding = os.getenv('AZURE_AI_EMBED_DEPLOYMENT_NAME')
    if endpoint and embedding:
        try:
            aoai_connection = await ai_client.connections.get_default(
                connection_type=ConnectionType.AZURE_OPEN_AI, include_credentials=True)
        except ValueError as e:
            logger.error("Error creating index: {e}")
            return

        embed_api_key = None
        if aoai_connection.credentials and isinstance(aoai_connection.credentials, ApiKeyCredentials):
            embed_api_key = aoai_connection.credentials.api_key

        search_mgr = SearchIndexManager(
            endpoint=endpoint,
            credential=creds,
            index_name=os.getenv('AZURE_AI_SEARCH_INDEX_NAME'),
            dimensions=None,
            model=embedding,
            deployment_name=embedding,
            embedding_endpoint=aoai_connection.target,
            embed_api_key=embed_api_key
        )
        # If another application instance already have created the index,
        # do not upload the documents.
        if await search_mgr.create_index(
            vector_index_dimensions=int(
                os.getenv('AZURE_AI_EMBED_DIMENSIONS'))):
            embeddings_path = os.path.join(
                os.path.dirname(__file__), 'data', 'embeddings.csv')

            assert embeddings_path, f'File {embeddings_path} not found.'
            await search_mgr.upload_documents(embeddings_path)
            await search_mgr.close()


def _get_file_path(file_name: str) -> str:
    """
    Get absolute file path.

    :param file_name: The file name.
    """
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     'files',
                     file_name))


async def get_available_tool(
        project_client: AIProjectClient,
        creds: AsyncTokenCredential) -> Tool:
    """
    Get the toolset and tool definition for the agent.

    :param ai_client: The project client to be used to create an index.
    :param creds: The credentials, used for the index.
    :return: The tool set, available based on the environment.
    """
    # File name -> {"id": file_id, "path": file_path}
    file_ids: List[str] = []
    # First try to get an index search.
    conn_id = ""
    if os.environ.get('AZURE_AI_SEARCH_INDEX_NAME'):
        conn_list = project_client.connections.list()
        async for conn in conn_list:
            if conn.type == ConnectionType.AZURE_AI_SEARCH:
                conn_id = conn.id
                break

    toolset = AsyncToolSet()
    if conn_id:
        await create_index_maybe(project_client, creds)

        return AzureAISearchTool(
            index_connection_id=conn_id,
            index_name=os.environ.get('AZURE_AI_SEARCH_INDEX_NAME'))
    else:
        logger.info(
            "agent: index was not initialized, falling back to file search.")

        # Initialize enhanced file search
        enhanced_search = EnhancedFileSearch()
        logger.info(
            f"Scanning files directory for {len(FILES_NAMES)} files with enhanced search")

        # Scan and categorize files
        file_metadata = enhanced_search.scan_files()
        categories = enhanced_search.categorize_files()
        logger.info(
            f"Found {len(categories)} categories: {', '.join(categories.keys())}")

        # Upload files for file search with enhanced metadata
        for file_name in FILES_NAMES:
            file_path = _get_file_path(file_name)

            # Use enhanced file parser to extract metadata
            try:
                content, metadata = FileParser.parse_file(file_path)
                logger.info(
                    f"Processed file {file_name} with metadata: {metadata}")
            except Exception as e:
                logger.warning(f"Error processing file {file_name}: {str(e)}")

            # Upload file to agent
            file = await project_client.agents.files.upload_and_poll(
                file_path=file_path, purpose=FilePurpose.AGENTS)

            # Store file ID
            file_ids.append(file.id)

        # Create the vector store using the file IDs.
        vector_store = await project_client.agents.vector_stores.create_and_poll(
            file_ids=file_ids,
            name="enhanced_file_store"
        )
        logger.info(
            "agent: enhanced file store and vector store created successfully")

        return FileSearchTool(vector_store_ids=[vector_store.id])


async def create_agent(ai_client: AIProjectClient,
                       creds: AsyncTokenCredential) -> Agent:
    logger.info("Creating new agent with resources")
    tool = await get_available_tool(ai_client, creds)
    toolset = AsyncToolSet()
    toolset.add(tool)

    # Define predefined agent personalities
    agent_personalities = {
        "default": {
            "instructions": "Use AI Search always. Avoid to use base knowledge." if isinstance(tool, AzureAISearchTool) else
            "Use File Search always. Avoid to use base knowledge. Always include proper citations for information found in files. " +
            "For each piece of information retrieved from a file, add a citation in the format [Source: Filename, Section X]. " +
            "Organize your responses to clearly distinguish between information from different sources.",
            "temperature": 0.7,
        },
        "customer_service": {
            "instructions": "You are a helpful customer service assistant. Always be polite, patient, and professional. " +
            ("Use AI Search to find accurate information about our products and services. " if isinstance(tool, AzureAISearchTool) else
                "Use File Search to find accurate information about our products and services. " +
                "Always provide citations for specific product information using [Source: Product Name, Brand, ID]. " +
                "When discussing customer information, be sure to reference the source document. " +
                "If information is available from multiple sources, prefer the most recent or most detailed source.") +
            "If you don't know the answer, admit it and offer to connect the customer with a human representative.",
            "temperature": 0.5,
        },
        "technical_support": {
            "instructions": "You are a technical support specialist. Provide clear, concise, and accurate technical information. " +
            ("Use AI Search to find specific technical details. " if isinstance(tool, AzureAISearchTool) else
                "Use File Search to find specific technical details. " +
                "Always cite your sources when providing technical information, using the format [Source: Document Name, Section X]. " +
                "Be precise with citations, including exact section or page numbers when available. " +
                "When providing step-by-step instructions, ensure each step is accurate based on the documentation.") +
            "Use technical language when appropriate but be able to explain concepts in simpler terms when needed.",
            "temperature": 0.3,
        },
        "sales_assistant": {
            "instructions": "You are a sales assistant focused on helping customers find the right products. " +
            ("Use AI Search to provide product information and make appropriate recommendations. " if isinstance(tool, AzureAISearchTool) else
                "Use File Search to provide product information and make appropriate recommendations. " +
                "Always cite product features and specifications with their source documents. " +
                "When comparing products, clearly indicate the source of each comparison point. " +
                "Format citations as [Product Name, Brand, Category] to help customers easily identify product information sources.") +
            "Highlight product benefits and features that match customer needs without being pushy.",
            "temperature": 0.6,
        },
        "concierge": {
            "instructions": "You are a sophisticated and courteous concierge assistant. " +
            ("Use AI Search to provide personalized recommendations and assistance. " if isinstance(tool, AzureAISearchTool) else
                "Use File Search to provide personalized recommendations and assistance. " +
                "When providing information from files, elegantly incorporate citations without disrupting the refined tone. " +
                "Use discreet citation formats such as 'According to [Source]' or footnote-style references at the end of your responses. " +
                "Ensure all recommendations are based on accurate information from the knowledge base.") +
            "Maintain a refined, professional tone while being warm and accommodating. Focus on providing exceptional service and attention to detail.",
            "temperature": 0.7,
        }
    }

    # Get the selected personality from environment variable or use default
    selected_personality = os.environ.get(
        "AZURE_AI_AGENT_PERSONALITY", "default")
    if selected_personality not in agent_personalities:
        logger.warning(
            f"Unknown personality '{selected_personality}', falling back to default")
        selected_personality = "default"

    personality = agent_personalities[selected_personality]
    instructions = personality["instructions"]
    temperature = personality.get("temperature", 0.7)

    logger.info(f"Creating agent with personality: {selected_personality}")

    agent = await ai_client.agents.create_agent(
        model=os.environ["AZURE_AI_AGENT_DEPLOYMENT_NAME"],
        name=os.environ["AZURE_AI_AGENT_NAME"],
        instructions=instructions,
        temperature=temperature,
        toolset=toolset
    )
    return agent


async def initialize_resources():
    try:
        async with DefaultAzureCredential(
                exclude_shared_token_cache_credential=True) as creds:
            async with AIProjectClient(
                credential=creds,
                endpoint=proj_endpoint
            ) as ai_client:
                # If the environment already has AZURE_AI_AGENT_ID or AZURE_EXISTING_AGENT_ID, try
                # fetching that agent
                if agentID is not None:
                    try:
                        agent = await ai_client.agents.get_agent(
                            agentID)
                        logger.info(f"Found agent by ID: {agent.id}")
                        return
                    except Exception as e:
                        logger.warning(
                            "Could not retrieve agent by AZURE_EXISTING_AGENT_ID = "
                            f"{agentID}, error: {e}")

                # Check if an agent with the same name already exists
                agent_list = ai_client.agents.list_agents()
                if agent_list:
                    async for agent_object in agent_list:
                        if agent_object.name == os.environ[
                                "AZURE_AI_AGENT_NAME"]:
                            logger.info(
                                "Found existing agent named "
                                f"'{agent_object.name}'"
                                f", ID: {agent_object.id}")
                            os.environ["AZURE_EXISTING_AGENT_ID"] = agent_object.id
                            return

                # Create a new agent
                agent = await create_agent(ai_client, creds)
                os.environ["AZURE_EXISTING_AGENT_ID"] = agent.id
                logger.info(f"Created agent, agent ID: {agent.id}")

    except Exception as e:
        logger.info("Error creating agent: {e}", exc_info=True)
        raise RuntimeError(f"Failed to create the agent: {e}")


def on_starting(server):
    """This code runs once before the workers will start."""
    asyncio.get_event_loop().run_until_complete(initialize_resources())


max_requests = 1000
max_requests_jitter = 50
log_file = "-"
bind = "0.0.0.0:50505"

if not os.getenv("RUNNING_IN_PRODUCTION"):
    reload = True

# Load application code before the worker processes are forked.
# Needed to execute on_starting.
# Please see the documentation on gunicorn
# https://docs.gunicorn.org/en/stable/settings.html
preload_app = True
num_cpus = multiprocessing.cpu_count()
workers = (num_cpus * 2) + 1
worker_class = "uvicorn.workers.UvicornWorker"

timeout = 120

if __name__ == "__main__":
    print("Running initialize_resources directly...")
    asyncio.run(initialize_resources())
    print("initialize_resources finished.")
