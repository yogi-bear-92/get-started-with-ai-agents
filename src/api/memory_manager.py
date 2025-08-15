"""
Memory Manager for AI Agent

This module provides persistent memory and context management for the AI agent,
allowing it to recall information from previous conversations and maintain
context across sessions.
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from azure.ai.agents.models import ThreadMessage

# Set up logging
logger = logging.getLogger("azureaiapp")


class MemoryManager:
    """
    Manages persistent memory for AI agents, storing and retrieving context
    from past conversations to enhance the agent's responses.
    """

    def __init__(self, storage_path: Optional[str] = None,
                 max_memory_items: int = 50,
                 memory_retention_days: int = 30):
        """
        Initialize the memory manager.

        Args:
            storage_path: Path to store memory files. Defaults to src/data/memory.
            max_memory_items: Maximum number of memory items to retain per user.
            memory_retention_days: Number of days to retain memory items.
        """
        self.storage_path = storage_path or os.path.abspath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'memory'))
        self.max_memory_items = max_memory_items
        self.memory_retention_days = memory_retention_days

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)

    def _get_user_memory_path(self, user_id: str) -> str:
        """
        Get the path to the user's memory file.

        Args:
            user_id: Unique identifier for the user.

        Returns:
            Path to the user's memory file.
        """
        # Convert user_id to a valid filename
        safe_user_id = "".join(c if c.isalnum() else "_" for c in user_id)
        return os.path.join(self.storage_path, f"{safe_user_id}_memory.json")

    def store_conversation_memory(self,
                                  user_id: str,
                                  thread_id: str,
                                  query: str,
                                  response: str,
                                  metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Store a new memory item from the conversation.

        Args:
            user_id: Unique identifier for the user.
            thread_id: ID of the conversation thread.
            query: User's query.
            response: Agent's response.
            metadata: Additional metadata about the interaction.
        """
        memory_path = self._get_user_memory_path(user_id)

        # Load existing memories
        memories = []
        if os.path.exists(memory_path):
            try:
                with open(memory_path, 'r') as f:
                    memories = json.load(f)
            except Exception as e:
                logger.error(f"Error loading memory file: {e}")

        # Add new memory
        memory_item = {
            "timestamp": datetime.now().isoformat(),
            "thread_id": thread_id,
            "query": query,
            "response": response[:1000],  # Limit size of stored response
            "metadata": metadata or {}
        }

        # Add to beginning of list (newest first)
        memories.insert(0, memory_item)

        # Enforce maximum memory size
        if len(memories) > self.max_memory_items:
            memories = memories[:self.max_memory_items]

        # Remove old memories
        cutoff_date = (datetime.now() -
                       timedelta(days=self.memory_retention_days)).isoformat()
        memories = [m for m in memories if m["timestamp"] >= cutoff_date]

        # Save updated memories
        try:
            with open(memory_path, 'w') as f:
                json.dump(memories, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory file: {e}")

    def get_relevant_memories(self,
                              user_id: str,
                              query: str,
                              max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories for the current query.

        Args:
            user_id: Unique identifier for the user.
            query: Current user query to find relevant memories for.
            max_results: Maximum number of relevant memories to return.

        Returns:
            List of relevant memories.
        """
        memory_path = self._get_user_memory_path(user_id)

        if not os.path.exists(memory_path):
            return []

        try:
            with open(memory_path, 'r') as f:
                memories = json.load(f)
        except Exception as e:
            logger.error(f"Error loading memory file: {e}")
            return []

        # Simple keyword matching for relevance
        # In production, use embeddings and vector similarity
        query_keywords = set(query.lower().split())
        scored_memories = []

        for memory in memories:
            memory_keywords = set(memory["query"].lower().split())
            # Calculate overlap between query keywords and memory keywords
            overlap = len(query_keywords.intersection(memory_keywords))
            if overlap > 0:
                scored_memories.append((memory, overlap))

        # Sort by relevance score (descending)
        scored_memories.sort(key=lambda x: x[1], reverse=True)

        # Return top results
        return [memory for memory, score in scored_memories[:max_results]]

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get or create user profile with preferences and history summary.

        Args:
            user_id: Unique identifier for the user.

        Returns:
            User profile dictionary.
        """
        profile_path = os.path.join(
            self.storage_path, f"{user_id}_profile.json")

        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading profile: {e}")

        # Create default profile if none exists
        default_profile = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_interaction": None,
            "total_interactions": 0,
            "preferences": {},
            "topics_of_interest": []
        }

        try:
            with open(profile_path, 'w') as f:
                json.dump(default_profile, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving profile: {e}")

        return default_profile

    def update_user_profile(self,
                            user_id: str,
                            interaction_data: Dict[str, Any]) -> None:
        """
        Update user profile with new interaction data.

        Args:
            user_id: Unique identifier for the user.
            interaction_data: New data from interaction to update profile with.
        """
        profile = self.get_user_profile(user_id)

        # Update profile with new data
        profile["last_interaction"] = datetime.now().isoformat()
        profile["total_interactions"] += 1

        # Update preferences if provided
        if "preferences" in interaction_data:
            for key, value in interaction_data["preferences"].items():
                profile["preferences"][key] = value

        # Update topics if provided
        if "topic" in interaction_data and interaction_data["topic"]:
            if interaction_data["topic"] not in profile["topics_of_interest"]:
                profile["topics_of_interest"].append(interaction_data["topic"])

        # Save updated profile
        profile_path = os.path.join(
            self.storage_path, f"{user_id}_profile.json")
        try:
            with open(profile_path, 'w') as f:
                json.dump(profile, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving profile: {e}")

    def format_context_for_agent(self,
                                 user_id: str,
                                 query: str) -> str:
        """
        Format memory and profile data as context for the agent.

        Args:
            user_id: Unique identifier for the user.
            query: Current user query.

        Returns:
            Formatted context string to add to agent prompt.
        """
        relevant_memories = self.get_relevant_memories(user_id, query)
        profile = self.get_user_profile(user_id)

        context_parts = ["## User Context Information"]

        # Add profile info if available
        if profile.get("total_interactions", 0) > 0:
            context_parts.append("### User Profile")
            context_parts.append(
                f"- Total interactions: {profile['total_interactions']}")

            if profile.get("preferences"):
                context_parts.append("- Preferences:")
                for key, value in profile["preferences"].items():
                    context_parts.append(f"  - {key}: {value}")

            if profile.get("topics_of_interest"):
                # Limit to 5 topics
                topics = ", ".join(profile["topics_of_interest"][:5])
                context_parts.append(f"- Topics of interest: {topics}")

        # Add relevant memories if available
        if relevant_memories:
            context_parts.append("\n### Relevant Conversation History")
            for i, memory in enumerate(relevant_memories):
                timestamp = datetime.fromisoformat(
                    memory["timestamp"]).strftime("%Y-%m-%d")
                context_parts.append(f"Memory {i+1} ({timestamp}):")
                context_parts.append(f"User asked: {memory['query']}")
                # Truncate long responses
                context_parts.append(
                    f"You responded: {memory['response'][:200]}...")
                context_parts.append("")  # Empty line between memories

        return "\n".join(context_parts)
