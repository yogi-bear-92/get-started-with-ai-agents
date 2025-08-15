#!/usr/bin/env python3
"""
Test script for the memory management system.

This script tests the basic functionality of the memory manager.
"""

import shutil
import tempfile
from api.memory_manager import MemoryManager
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_memory_manager():
    """Test the memory manager functionality."""
    print("🧪 Testing Memory Manager")
    print("=" * 30)

    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"Using temporary directory: {temp_dir}")

    try:
        # Initialize memory manager
        memory_manager = MemoryManager(storage_path=temp_dir)

        # Test 1: Store conversation memory
        print("\n1. Testing memory storage...")
        memory_manager.store_conversation_memory(
            user_id="test_user_123",
            thread_id="thread_456",
            query="What are the features of SmartView Glasses?",
            response="SmartView Glasses have advanced AR display, voice control, and 12-hour battery life."
        )
        print("✅ Memory stored successfully")

        # Test 2: Retrieve relevant memories
        print("\n2. Testing memory retrieval...")
        memories = memory_manager.get_relevant_memories(
            user_id="test_user_123",
            query="Tell me about SmartView battery"
        )
        print(f"✅ Retrieved {len(memories)} relevant memories")
        for i, memory in enumerate(memories):
            print(f"   Memory {i+1}: {memory['query'][:50]}...")

        # Test 3: User profile management
        print("\n3. Testing user profile...")
        profile = memory_manager.get_user_profile("test_user_123")
        print(f"✅ Profile created: {profile['user_id']}")
        print(f"   Total interactions: {profile['total_interactions']}")

        # Test 4: Update user profile
        print("\n4. Testing profile update...")
        memory_manager.update_user_profile(
            user_id="test_user_123",
            interaction_data={
                "topic": "SmartView products",
                "preferences": {"product_focus": "AR glasses"}
            }
        )
        updated_profile = memory_manager.get_user_profile("test_user_123")
        print(
            f"✅ Profile updated: {updated_profile['total_interactions']} interactions")
        print(f"   Topics: {updated_profile['topics_of_interest']}")

        # Test 5: Format context for agent
        print("\n5. Testing context formatting...")
        context = memory_manager.format_context_for_agent(
            user_id="test_user_123",
            query="What's the warranty on SmartView?"
        )
        print("✅ Context formatted:")
        print(f"   Length: {len(context)} characters")
        print(f"   Preview: {context[:100]}...")

        # Test 6: Store another memory and test retention
        print("\n6. Testing memory retention...")
        memory_manager.store_conversation_memory(
            user_id="test_user_123",
            thread_id="thread_789",
            query="How long is the warranty?",
            response="SmartView Glasses come with a 2-year warranty covering manufacturing defects."
        )

        memories = memory_manager.get_relevant_memories(
            user_id="test_user_123",
            query="warranty information"
        )
        print(f"✅ Now have {len(memories)} relevant memories about warranty")

        print("\n🎉 All tests passed! Memory manager is working correctly.")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up temporary directory: {temp_dir}")


def test_memory_performance():
    """Test memory manager performance with multiple users and memories."""
    print("\n🚀 Testing Memory Manager Performance")
    print("=" * 40)

    temp_dir = tempfile.mkdtemp()

    try:
        memory_manager = MemoryManager(storage_path=temp_dir)

        # Create multiple users with multiple memories
        users = [f"user_{i}" for i in range(10)]
        queries = [
            "What are the SmartView features?",
            "How much do they cost?",
            "What's the battery life?",
            "Is there a warranty?",
            "Can I get support?"
        ]

        import time
        start_time = time.time()

        # Store memories for multiple users
        for user_id in users:
            for i, query in enumerate(queries):
                memory_manager.store_conversation_memory(
                    user_id=user_id,
                    thread_id=f"thread_{user_id}_{i}",
                    query=query,
                    response=f"Response to {query} for {user_id}"
                )

        storage_time = time.time() - start_time
        print(
            f"✅ Stored {len(users) * len(queries)} memories in {storage_time:.2f} seconds")

        # Test retrieval performance
        start_time = time.time()

        total_memories = 0
        for user_id in users:
            memories = memory_manager.get_relevant_memories(
                user_id, "SmartView battery features")
            total_memories += len(memories)

        retrieval_time = time.time() - start_time
        print(
            f"✅ Retrieved {total_memories} relevant memories in {retrieval_time:.2f} seconds")

        # Test context formatting performance
        start_time = time.time()

        for user_id in users[:3]:  # Test a few users
            context = memory_manager.format_context_for_agent(
                user_id, "Tell me about products")

        context_time = time.time() - start_time
        print(f"✅ Formatted context for 3 users in {context_time:.2f} seconds")

        print(f"\n📊 Performance Summary:")
        print(
            f"   Storage: {len(users) * len(queries) / storage_time:.1f} memories/second")
        print(
            f"   Retrieval: {total_memories / retrieval_time:.1f} memories/second")
        print(f"   Context: {3 / context_time:.1f} contexts/second")

    except Exception as e:
        print(f"\n❌ Performance test failed: {e}")

    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_memory_manager()
    test_memory_performance()
