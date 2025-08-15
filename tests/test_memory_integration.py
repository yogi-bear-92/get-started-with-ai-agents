#!/usr/bin/env python3
"""
Comprehensive memory integration test for the AI Agent application.
Tests the full memory system functionality including API endpoints.
"""

import requests
import json
import time
import sys
import os

# Server configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "integration_test_user"


def test_server_health():
    """Test that the server is running and responsive."""
    print("🏥 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy and responsive")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server health check failed: {e}")
        return False


def test_memory_user_profile():
    """Test user profile creation and retrieval."""
    print("\n👤 Testing user profile management...")
    try:
        response = requests.get(f"{BASE_URL}/api/memory/user/{TEST_USER_ID}")
        if response.status_code == 200:
            data = response.json()
            profile = data.get('profile', {})
            print(f"✅ User profile retrieved: {profile['user_id']}")
            print(f"   Total interactions: {profile['total_interactions']}")
            print(f"   Topics of interest: {profile['topics_of_interest']}")
            return True
        else:
            print(f"❌ Profile retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Profile test failed: {e}")
        return False


def test_memory_endpoints():
    """Test all memory-related API endpoints."""
    print("\n🧠 Testing memory endpoints...")
    success_count = 0
    total_tests = 2

    # Test 1: User profile endpoint
    if test_memory_user_profile():
        success_count += 1

    # Test 2: Memory clear endpoint
    print("\n🧹 Testing memory clear...")
    try:
        response = requests.post(f"{BASE_URL}/api/memory/clear/{TEST_USER_ID}")
        if response.status_code == 200:
            print("✅ Memory clear endpoint responsive")
            success_count += 1
        else:
            print(f"❌ Memory clear failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Memory clear test failed: {e}")

    return success_count == total_tests


def test_agent_endpoints():
    """Test agent-related endpoints."""
    print("\n🤖 Testing agent endpoints...")

    # Test agents list endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/agents")
        if response.status_code == 200:
            print("✅ Agents endpoint responsive")
            return True
        else:
            print(f"❌ Agents endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Agents test failed: {e}")
        return False


def simulate_memory_storage():
    """Simulate memory storage by directly using the memory manager."""
    print("\n💾 Testing direct memory storage...")
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from api.memory_manager import MemoryManager

        # Initialize memory manager
        memory_manager = MemoryManager()

        # Store some test conversations
        test_conversations = [
            {
                "query": "What are the main features of the AI agent?",
                "response": "The AI agent has memory management, file search capabilities, and contextual responses."
            },
            {
                "query": "How does the memory system work?",
                "response": "The memory system stores conversation history and user preferences to provide contextual responses."
            },
            {
                "query": "Can you tell me about the agent's capabilities?",
                "response": "The agent can process documents, remember conversations, and provide personalized assistance."
            }
        ]

        for i, conv in enumerate(test_conversations):
            memory_manager.store_conversation_memory(
                user_id=TEST_USER_ID,
                thread_id=f"test_thread_{i}",
                query=conv["query"],
                response=conv["response"]
            )

        print(f"✅ Stored {len(test_conversations)} test conversations")

        # Test memory retrieval
        relevant_memories = memory_manager.get_relevant_memories(
            user_id=TEST_USER_ID,
            query="agent features and capabilities"
        )

        print(f"✅ Retrieved {len(relevant_memories)} relevant memories")
        for i, memory in enumerate(relevant_memories):
            print(f"   Memory {i+1}: {memory['query'][:40]}...")

        return len(relevant_memories) > 0

    except Exception as e:
        print(f"❌ Memory storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_context_formatting():
    """Test memory context formatting for agents."""
    print("\n📝 Testing memory context formatting...")
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from api.memory_manager import MemoryManager

        memory_manager = MemoryManager()

        # Format context for agent
        context = memory_manager.format_context_for_agent(
            user_id=TEST_USER_ID,
            query="Tell me more about AI capabilities"
        )

        if context and len(context) > 0:
            print("✅ Context formatted successfully")
            print(f"   Context length: {len(context)} characters")
            print(f"   Context preview: {context[:100]}...")
            return True
        else:
            print("❌ Context formatting returned empty result")
            return False

    except Exception as e:
        print(f"❌ Context formatting test failed: {e}")
        return False


def run_comprehensive_memory_test():
    """Run all memory integration tests."""
    print("🧪 Starting Comprehensive Memory Integration Test")
    print("=" * 55)

    start_time = time.time()
    passed_tests = 0
    total_tests = 6

    # Test 1: Server health
    if test_server_health():
        passed_tests += 1

    # Test 2: Memory endpoints
    if test_memory_endpoints():
        passed_tests += 1

    # Test 3: Agent endpoints
    if test_agent_endpoints():
        passed_tests += 1

    # Test 4: Direct memory storage
    if simulate_memory_storage():
        passed_tests += 1

    # Test 5: Memory context formatting
    if test_memory_context_formatting():
        passed_tests += 1

    # Test 6: Re-test memory endpoints after storage
    print("\n🔄 Re-testing memory endpoints after storage...")
    if test_memory_user_profile():
        passed_tests += 1

    # Summary
    end_time = time.time()
    duration = end_time - start_time

    print("\n" + "=" * 55)
    print(f"📊 Test Results Summary")
    print(f"   Tests passed: {passed_tests}/{total_tests}")
    print(f"   Success rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"   Duration: {duration:.2f} seconds")

    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Memory integration is working correctly.")
        return True
    else:
        print(
            f"\n⚠️  {total_tests - passed_tests} tests failed. Memory integration needs attention.")
        return False


if __name__ == "__main__":
    success = run_comprehensive_memory_test()
    sys.exit(0 if success else 1)
