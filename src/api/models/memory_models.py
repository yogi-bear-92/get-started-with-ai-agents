"""
Database models for agent memory storage.

This module defines the database models used to store agent memory and user profiles.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    """
    Represents a single memory item from a conversation.
    """
    timestamp: datetime = Field(default_factory=datetime.now)
    thread_id: str
    query: str
    response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserProfile(BaseModel):
    """
    Represents a user profile with preferences and interaction history.
    """
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_interaction: Optional[datetime] = None
    total_interactions: int = 0
    preferences: Dict[str, Any] = Field(default_factory=dict)
    topics_of_interest: List[str] = Field(default_factory=list)


class UserMemory(BaseModel):
    """
    Represents the complete memory for a user, including all memory items.
    """
    user_id: str
    last_updated: datetime = Field(default_factory=datetime.now)
    memories: List[MemoryItem] = Field(default_factory=list)
    profile: UserProfile
