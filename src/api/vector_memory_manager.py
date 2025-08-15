"""
Enhanced memory manager with vector-based similarity search.
Improves memory relevance matching using text embeddings.
"""

import os
import json
import hashlib
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class VectorMemoryManager:
    """Enhanced memory manager with vector-based similarity search."""

    def __init__(self,
                 storage_path: Optional[str] = None,
                 max_memory_items: int = 100,
                 memory_retention_days: int = 30,
                 similarity_threshold: float = 0.3):
        """
        Initialize the enhanced memory manager.

        Args:
            storage_path: Path to store memory files.
            max_memory_items: Maximum number of memory items to retain per user.
            memory_retention_days: Number of days to retain memory items.
            similarity_threshold: Minimum similarity score for relevance matching.
        """
        self.storage_path = storage_path or os.path.abspath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'memory'))
        self.max_memory_items = max_memory_items
        self.memory_retention_days = memory_retention_days
        self.similarity_threshold = similarity_threshold

        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )

        # Cache for user memories to avoid repeated file reads
        self._memory_cache = {}
        self._vectorizer_fitted = False

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)

    def _get_user_memory_path(self, user_id: str) -> str:
        """Get the path to the user's memory directory."""
        user_dir = os.path.join(self.storage_path, 'users', user_id)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir

    def _get_user_profile_path(self, user_id: str) -> str:
        """Get the path to the user's profile file."""
        return os.path.join(self._get_user_memory_path(user_id), 'profile.json')

    def _get_conversations_path(self, user_id: str) -> str:
        """Get the path to the user's conversations directory."""
        conversations_dir = os.path.join(
            self._get_user_memory_path(user_id), 'conversations')
        os.makedirs(conversations_dir, exist_ok=True)
        return conversations_dir

    def _load_user_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Load all memories for a specific user."""
        if user_id in self._memory_cache:
            return self._memory_cache[user_id]

        memories = []
        conversations_path = self._get_conversations_path(user_id)

        try:
            for filename in os.listdir(conversations_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(conversations_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        conversation_data = json.load(f)
                        memories.extend(conversation_data.get('memories', []))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Error loading memories for user {user_id}: {e}")

        # Cache the memories
        self._memory_cache[user_id] = memories
        return memories

    def _prepare_text_corpus(self, user_id: str) -> List[str]:
        """Prepare text corpus for vectorization."""
        memories = self._load_user_memories(user_id)
        corpus = []

        for memory in memories:
            # Combine query and response for better context
            text = f"{memory.get('query', '')} {memory.get('response', '')}"
            corpus.append(text.strip())

        return corpus

    def _fit_vectorizer_if_needed(self, user_id: str):
        """Fit the vectorizer with user's memory corpus if not already fitted."""
        if not self._vectorizer_fitted or user_id not in self._memory_cache:
            corpus = self._prepare_text_corpus(user_id)

            if corpus:  # Only fit if we have data
                try:
                    self.vectorizer.fit(corpus)
                    self._vectorizer_fitted = True
                    logger.info(
                        f"Vectorizer fitted with {len(corpus)} documents for user {user_id}")
                except Exception as e:
                    logger.warning(f"Failed to fit vectorizer: {e}")

    def store_conversation_memory(self,
                                  user_id: str,
                                  thread_id: str,
                                  query: str,
                                  response: str) -> bool:
        """
        Store a conversation memory with enhanced metadata.

        Args:
            user_id: Unique identifier for the user.
            thread_id: Thread identifier for grouping related conversations.
            query: User's query/input.
            response: Agent's response.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Create memory item
            memory_item = {
                "id": hashlib.md5(f"{user_id}_{thread_id}_{query}".encode()).hexdigest(),
                "timestamp": datetime.now().isoformat(),
                "thread_id": thread_id,
                "query": query.strip(),
                "response": response.strip(),
                "query_length": len(query),
                "response_length": len(response),
                "topics": self._extract_topics(query, response)
            }

            # Get conversation file path
            conversations_path = self._get_conversations_path(user_id)
            thread_file = os.path.join(conversations_path, f"{thread_id}.json")

            # Load existing conversation or create new
            conversation_data = {"thread_id": thread_id, "memories": []}
            if os.path.exists(thread_file):
                with open(thread_file, 'r', encoding='utf-8') as f:
                    conversation_data = json.load(f)

            # Add new memory
            conversation_data["memories"].append(memory_item)

            # Save conversation
            with open(thread_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)

            # Update user profile
            self._update_user_interaction(user_id, query, response)

            # Clear cache to force reload
            if user_id in self._memory_cache:
                del self._memory_cache[user_id]

            logger.info(
                f"Stored memory for user {user_id}, thread {thread_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False

    def get_relevant_memories(self,
                              user_id: str,
                              query: str,
                              max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories using vector similarity.

        Args:
            user_id: Unique identifier for the user.
            query: Current user query to find relevant memories for.
            max_results: Maximum number of relevant memories to return.

        Returns:
            List of relevant memories ordered by similarity score.
        """
        try:
            # Load user memories
            memories = self._load_user_memories(user_id)

            if not memories or not query.strip():
                return []

            # Prepare corpus for vectorization
            self._fit_vectorizer_if_needed(user_id)

            if not self._vectorizer_fitted:
                # Fallback to keyword-based search
                return self._keyword_based_search(memories, query, max_results)

            # Prepare documents
            documents = []
            for memory in memories:
                doc_text = f"{memory.get('query', '')} {memory.get('response', '')}"
                documents.append(doc_text.strip())

            if not documents:
                return []

            # Vectorize documents and query
            try:
                doc_vectors = self.vectorizer.transform(documents)
                query_vector = self.vectorizer.transform([query])

                # Calculate similarity scores
                similarity_scores = cosine_similarity(
                    query_vector, doc_vectors).flatten()

                # Get relevant memories above threshold
                relevant_indices = []
                for i, score in enumerate(similarity_scores):
                    if score >= self.similarity_threshold:
                        relevant_indices.append((i, score))

                # Sort by similarity score (descending)
                relevant_indices.sort(key=lambda x: x[1], reverse=True)

                # Return top results
                results = []
                for i, score in relevant_indices[:max_results]:
                    memory = memories[i].copy()
                    memory['similarity_score'] = float(score)
                    results.append(memory)

                logger.info(
                    f"Found {len(results)} relevant memories for user {user_id}")
                return results

            except Exception as e:
                logger.warning(
                    f"Vector search failed, falling back to keyword search: {e}")
                return self._keyword_based_search(memories, query, max_results)

        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []

    def _keyword_based_search(self, memories: List[Dict], query: str, max_results: int) -> List[Dict]:
        """Fallback keyword-based search when vector search fails."""
        query_words = set(query.lower().split())
        scored_memories = []

        for memory in memories:
            memory_text = f"{memory.get('query', '')} {memory.get('response', '')}".lower(
            )
            memory_words = set(memory_text.split())

            # Simple keyword overlap score
            overlap = len(query_words.intersection(memory_words))
            if overlap > 0:
                score = overlap / len(query_words.union(memory_words))
                memory_copy = memory.copy()
                memory_copy['similarity_score'] = score
                scored_memories.append(memory_copy)

        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored_memories[:max_results]

    def _extract_topics(self, query: str, response: str) -> List[str]:
        """Extract potential topics from query and response."""
        # Simple topic extraction - could be enhanced with NLP
        text = f"{query} {response}".lower()

        # Common topic keywords
        topic_keywords = {
            'technical': ['api', 'code', 'programming', 'development', 'software'],
            'product': ['features', 'specifications', 'capabilities', 'functions'],
            'support': ['help', 'issue', 'problem', 'error', 'troubleshoot'],
            'information': ['what', 'how', 'when', 'where', 'why', 'explain'],
            'configuration': ['setup', 'config', 'settings', 'install', 'configure']
        }

        topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)

        return topics

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile with interaction history."""
        profile_path = self._get_user_profile_path(user_id)

        default_profile = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_interaction": None,
            "total_interactions": 0,
            "preferences": {},
            "topics_of_interest": [],
            "memory_stats": {
                "total_memories": 0,
                "avg_similarity_threshold": self.similarity_threshold
            }
        }

        try:
            if os.path.exists(profile_path):
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    # Ensure all required fields exist
                    for key, value in default_profile.items():
                        if key not in profile:
                            profile[key] = value
            else:
                profile = default_profile

            # Update memory stats
            memories = self._load_user_memories(user_id)
            profile["memory_stats"]["total_memories"] = len(memories)

            return profile

        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            return default_profile

    def _update_user_interaction(self, user_id: str, query: str, response: str):
        """Update user profile with new interaction data."""
        profile = self.get_user_profile(user_id)

        profile["last_interaction"] = datetime.now().isoformat()
        profile["total_interactions"] += 1

        # Extract and update topics
        topics = self._extract_topics(query, response)
        for topic in topics:
            if topic not in profile["topics_of_interest"]:
                profile["topics_of_interest"].append(topic)

        # Save updated profile
        profile_path = self._get_user_profile_path(user_id)
        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")

    def format_context_for_agent(self, user_id: str, query: str) -> str:
        """Format memory context for agent consumption with enhanced relevance."""
        try:
            relevant_memories = self.get_relevant_memories(
                user_id, query, max_results=3)
            profile = self.get_user_profile(user_id)

            if not relevant_memories and profile["total_interactions"] == 0:
                return ""

            context_parts = ["## User Context Information"]

            # User profile section
            context_parts.append(f"### User Profile")
            context_parts.append(
                f"- Total interactions: {profile['total_interactions']}")
            if profile["topics_of_interest"]:
                context_parts.append(
                    f"- Interests: {', '.join(profile['topics_of_interest'])}")
            if profile["preferences"]:
                context_parts.append("- Preferences:")
                for key, value in profile["preferences"].items():
                    context_parts.append(f"  - {key}: {value}")

            # Relevant memories section
            if relevant_memories:
                context_parts.append(f"\n### Relevant Conversation History")
                for i, memory in enumerate(relevant_memories, 1):
                    timestamp = memory.get('timestamp', 'Unknown')
                    if timestamp != 'Unknown':
                        date = datetime.fromisoformat(
                            timestamp).strftime('%Y-%m-%d')
                    else:
                        date = 'Unknown'

                    similarity = memory.get('similarity_score', 0)
                    context_parts.append(
                        f"Memory {i} ({date}, similarity: {similarity:.2f}):")
                    context_parts.append(f"User asked: {memory['query']}")
                    context_parts.append(
                        f"Agent responded: {memory['response'][:200]}...")

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error formatting context: {e}")
            return ""

    def update_user_profile(self, user_id: str, interaction_data: Dict[str, Any]):
        """Update user profile with additional interaction data."""
        profile = self.get_user_profile(user_id)

        # Update preferences
        if "preferences" in interaction_data:
            profile["preferences"].update(interaction_data["preferences"])

        # Add topics
        if "topic" in interaction_data:
            topic = interaction_data["topic"]
            if topic not in profile["topics_of_interest"]:
                profile["topics_of_interest"].append(topic)

        # Save updated profile
        profile_path = self._get_user_profile_path(user_id)
        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")

    def get_memory_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics about user's memory usage and patterns."""
        memories = self._load_user_memories(user_id)
        profile = self.get_user_profile(user_id)

        if not memories:
            return {"total_memories": 0, "topics": [], "interaction_frequency": 0}

        # Calculate analytics
        topics_count = {}
        total_query_length = 0
        total_response_length = 0

        for memory in memories:
            topics = memory.get('topics', [])
            for topic in topics:
                topics_count[topic] = topics_count.get(topic, 0) + 1

            total_query_length += memory.get('query_length', 0)
            total_response_length += memory.get('response_length', 0)

        # Get date range for frequency calculation
        dates = [datetime.fromisoformat(m['timestamp']) for m in memories]
        if dates:
            date_range = (max(dates) - min(dates)).days or 1
            interaction_frequency = len(memories) / date_range
        else:
            interaction_frequency = 0

        return {
            "total_memories": len(memories),
            "avg_query_length": total_query_length / len(memories) if memories else 0,
            "avg_response_length": total_response_length / len(memories) if memories else 0,
            "top_topics": sorted(topics_count.items(), key=lambda x: x[1], reverse=True)[:5],
            "interaction_frequency": interaction_frequency,
            "memory_span_days": date_range if dates else 0,
            "similarity_threshold": self.similarity_threshold
        }
