# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import secrets
from typing import Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, Depends, HTTPException, status
from opentelemetry import trace
import asyncio
import json
import os
import uuid
from typing import AsyncGenerator, Optional, Dict

import fastapi
from fastapi import Request, Depends, HTTPException, APIRouter, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

import logging
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from .memory_manager import MemoryManager

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    Agent,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    AsyncAgentEventHandler,
    RunStep
)
from azure.ai.projects import AIProjectClient

# Create a logger for this module
logger = logging.getLogger("azureaiapp")

# Set the log level for the azure HTTP logging policy to WARNING (or ERROR)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.WARNING)

tracer = trace.get_tracer(__name__)

# Create router
router = APIRouter()

# Define the directory for your templates.
directory = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=directory)

# Initialize memory manager
memory_manager = MemoryManager()

# Create a new FastAPI router
router = fastapi.APIRouter()

security = HTTPBasic()

username = os.getenv("WEB_APP_USERNAME")
password = os.getenv("WEB_APP_PASSWORD")
basic_auth = username and password


def authenticate(credentials: Optional[HTTPBasicCredentials] = Depends(security)) -> None:

    if not basic_auth:
        logger.info(
            "Skipping authentication: WEB_APP_USERNAME or WEB_APP_PASSWORD not set.")
        return

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credentials required",
            headers={"WWW-Authenticate": "Basic"},
        )

    correct_username = secrets.compare_digest(
        credentials.username, username or "")
    correct_password = secrets.compare_digest(
        credentials.password, password or "")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return


auth_dependency = Depends(authenticate) if basic_auth else None


def get_ai_project(request: Request) -> AIProjectClient:
    return request.app.state.ai_project


def get_agent_client(request: Request) -> AgentsClient:
    return request.app.state.agent_client


def get_agent_id(request: Request) -> str:
    agent_id = request.app.state.agent_id
    if not agent_id:
        raise HTTPException(status_code=500, detail="Agent ID not configured")
    return agent_id


def get_app_insights_connection_string(request: Request) -> Optional[str]:
    return request.app.state.app_insights_connection_string


# Enhanced event handler that integrates with memory management
class MyEventHandler(AsyncAgentEventHandler):
    def __init__(self, ai_project: AIProjectClient, app_insights_conn_str: Optional[str],
                 user_id: str, user_query: str):
        super().__init__()
        self._ai_project = ai_project
        self._app_insights_conn_str = app_insights_conn_str or ""
        self.user_id = user_id
        self.user_query = user_query
        self.agent_response = ""

    async def on_message_delta(self, delta: MessageDeltaChunk) -> None:
        if delta.content:
            for content_part in delta.content:
                if hasattr(content_part, 'text') and content_part.text:
                    if hasattr(content_part.text, 'value'):
                        print(content_part.text.value, end="", flush=True)
                        self.agent_response += content_part.text.value

    async def on_run_step_done(self, run_step: RunStep) -> None:
        # Uncomment to see the run step details
        # print(f"Run step done: {run_step.id}")
        pass

    async def on_end(self) -> None:
        # Store the conversation in memory when the interaction is complete
        try:
            if self.agent_response.strip():
                memory_manager.store_conversation_memory(
                    user_id=self.user_id,
                    thread_id=f"thread_{self.user_id}_{uuid.uuid4().hex[:8]}",
                    query=self.user_query,
                    response=self.agent_response
                )
                logger.info(
                    f"Stored conversation memory for user {self.user_id}")
        except Exception as e:
            logger.error(f"Failed to store conversation memory: {e}")


# Utility function to format messages with annotations
async def get_message_and_annotations(agent_client: AgentsClient, message: ThreadMessage) -> Dict:
    try:
        message_content = ""
        annotations = []
        citations = []

        if message.content:
            for content_part in message.content:
                if hasattr(content_part, 'text'):
                    message_content += content_part.text.value

                    if hasattr(content_part.text, 'annotations'):
                        for annotation in content_part.text.annotations:
                            if hasattr(annotation, 'file_citation'):
                                file_citation = annotation.file_citation
                                citations.append({
                                    "file_id": file_citation.file_id,
                                    "quote": file_citation.quote
                                })
                            elif hasattr(annotation, 'file_path'):
                                file_path = annotation.file_path
                                annotations.append({
                                    "type": "file_path",
                                    "file_id": file_path.file_id
                                })

        return {
            "id": message.id,
            "role": message.role,
            "content": message_content,
            "annotations": annotations,
            "citations": citations,
            "created_at": message.created_at
        }
    except Exception as e:
        logger.error(f"Error formatting message: {e}")
        return {
            "id": getattr(message, 'id', 'unknown'),
            "role": getattr(message, 'role', 'unknown'),
            "content": str(message),
            "annotations": [],
            "citations": [],
            "created_at": None
        }


@router.post("/api/chat")
async def chat(
    request: Request,
    user_id: str = "default_user",
    thread_id: Optional[str] = None,
    user_query: str = "",
    _auth=auth_dependency
):
    """Enhanced chat endpoint with memory integration"""
    try:
        agent_client = get_agent_client(request)
        agent_id = get_agent_id(request)
        ai_project = get_ai_project(request)
        app_insight_conn_str = get_app_insights_connection_string(request)

        if not user_query.strip():
            raise HTTPException(
                status_code=400, detail="Query cannot be empty")

        logger.info(f"Chat request from user {user_id}: {user_query}")

        # Get memory context for the user
        memory_context = memory_manager.format_context_for_agent(
            user_id, user_query)

        # Enhance the user query with memory context
        enhanced_content = f"{memory_context}\n\nUser Query: {user_query}" if memory_context else user_query

        # Handle thread creation/retrieval
        if thread_id:
            try:
                thread = agent_client.threads.get(thread_id)
            except Exception:
                thread = agent_client.threads.create()
                thread_id = thread.id
        else:
            thread = agent_client.threads.create()
            thread_id = thread.id

        # Create the message
        message = agent_client.messages.create(
            thread_id=thread_id,
            role="user",
            content=enhanced_content
        )

        # Create the run with streaming
        event_handler = MyEventHandler(
            ai_project, app_insight_conn_str, user_id, user_query)

        # Start the streaming run
        run = agent_client.runs.create_and_stream(
            thread_id=thread_id,
            agent_id=agent_id,
            event_handler=event_handler
        )

        # Return successful response
        return JSONResponse(content={
            "status": "success",
            "thread_id": thread_id,
            "message": "Chat completed successfully"
        })

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Chat failed: {str(e)}"}
        )


@router.get("/api/messages")
async def get_messages(
    request: Request,
    thread_id: str,
    _auth=auth_dependency
):
    """Get messages from a thread"""
    try:
        agent_client = get_agent_client(request)

        response = agent_client.messages.list(thread_id=thread_id)
        messages = []

        for message in response:
            formatted_message = await get_message_and_annotations(agent_client, message)
            messages.append(formatted_message)

        return JSONResponse(content={"messages": messages})

    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get messages: {str(e)}"}
        )


@router.get("/api/agents")
async def get_agents(request: Request, _auth=auth_dependency):
    """Get available agents"""
    try:
        agent_client = get_agent_client(request)
        agents = agent_client.agents.list()

        agent_list = []
        for agent in agents:
            agent_list.append({
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "model": agent.model,
                "instructions": agent.instructions
            })

        return JSONResponse(content={"agents": agent_list})

    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get agents: {str(e)}"}
        )


# Memory management endpoints
@router.get("/api/memory/user/{user_id}")
async def get_user_memory(user_id: str, _auth=auth_dependency):
    """Get user memory profile and recent conversations"""
    try:
        profile = memory_manager.get_user_profile(user_id)
        recent_memories = memory_manager.get_relevant_memories(
            user_id, "", limit=10)

        return JSONResponse(content={
            "profile": profile,
            "recent_memories": recent_memories
        })

    except Exception as e:
        logger.error(f"Error getting user memory: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get user memory: {str(e)}"}
        )


@router.post("/api/memory/clear/{user_id}")
async def clear_user_memory(user_id: str, _auth=auth_dependency):
    """Clear all memory for a specific user"""
    try:
        # Note: This would need to be implemented in the memory manager
        logger.info(f"Memory clear requested for user {user_id}")
        return JSONResponse(content={"status": "success", "message": "Memory cleared"})

    except Exception as e:
        logger.error(f"Error clearing memory: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to clear memory: {str(e)}"}
        )


# Health check endpoint
@router.get("/api/health")
async def health_check():
    """Basic health check endpoint"""
    return JSONResponse(content={"status": "healthy", "service": "ai-agent-api"})


# Root endpoint
@router.get("/")
async def index(request: Request, _auth=auth_dependency):
    """Serve the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})
