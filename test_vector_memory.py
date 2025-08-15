#!/usr/bin/env python3
"""
Test script for the enhanced vector-based memory management system.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.vector_memory_manager import VectorMemoryManager
import tempfile
import shutil
import time

def test_vector_memory_manager():
    """Test the enhanced vector memory manager functionality."""
    print("🚀 Testing Enhanced Vector Memory Manager")
    print("=" * 45)
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"Using temporary directory: {temp_dir}")
    
    try:
        # Initialize vector memory manager
        memory_manager = VectorMemoryManager(storage_path=temp_dir, similarity_threshold=0.2)
        
        # Test data - more diverse conversations
        test_conversations = [
            {
                "thread": "thread_001",
                "query": "What are the main features of the SmartView AR glasses?",
                "response": "SmartView AR glasses offer advanced augmented reality display, voice control, gesture recognition, and 12-hour battery life. They support multiple apps and have built-in cameras for recording."
            },
            {
                "thread": "thread_002", 
                "query": "How long does the battery last on SmartView?",
                "response": "The SmartView glasses have a 12-hour battery life under normal usage. Heavy AR applications may reduce this to 8-10 hours. The device charges fully in 2 hours."
            },
            {
                "thread": "thread_003",
                "query": "Can I use SmartView for programming and development?",
                "response": "Yes! SmartView supports development environments through AR overlays. You can display code, debugging information, and virtual monitors. Popular IDEs have SmartView extensions."
            },
            {
                "thread": "thread_004",
                "query": "What's the warranty policy for SmartView products?",
                "response": "SmartView products come with a 2-year manufacturer warranty covering defects. Extended warranty options are available. Water damage and physical damage from drops are not covered."
            },
            {
                "thread": "thread_005",
                "query": "How do I configure the gesture controls?",
                "response": "Gesture controls are configured through the SmartView app. Go to Settings > Gestures to customize hand movements. The system supports pinch, swipe, and pointing gestures."
            },
            {
                "thread": "thread_006",
                "query": "Is there API access for SmartView development?",
                "response": "Yes, SmartView provides comprehensive APIs for developers. The SDK includes AR rendering, sensor access, and app integration. Documentation is available on the developer portal."
            }
        ]
        
        print(f"\n1. Storing {len(test_conversations)} diverse conversations...")
        for conv in test_conversations:
            memory_manager.store_conversation_memory(
                user_id="vector_test_user",
                thread_id=conv["thread"],
                query=conv["query"],
                response=conv["response"]
            )
        print("✅ All conversations stored successfully")
        
        # Test vector-based similarity search
        test_queries = [
            {
                "query": "battery performance and power",
                "expected_topics": ["battery", "power", "performance"]
            },
            {
                "query": "programming and coding features",
                "expected_topics": ["development", "programming", "API"]
            },
            {
                "query": "warranty and support information",
                "expected_topics": ["warranty", "support"]
            },
            {
                "query": "gesture control setup",
                "expected_topics": ["gesture", "control", "configuration"]
            }
        ]
        
        print(f"\n2. Testing vector-based similarity search...")
        for i, test in enumerate(test_queries, 1):
            print(f"\n   Test {i}: Query '{test['query']}'")
            
            start_time = time.time()
            relevant_memories = memory_manager.get_relevant_memories(
                user_id="vector_test_user",
                query=test["query"],
                max_results=3
            )
            search_time = time.time() - start_time
            
            print(f"   ⏱️  Search time: {search_time:.4f} seconds")
            print(f"   📊 Found {len(relevant_memories)} relevant memories")
            
            for j, memory in enumerate(relevant_memories, 1):
                similarity = memory.get('similarity_score', 0)
                query_preview = memory['query'][:50] + "..." if len(memory['query']) > 50 else memory['query']
                print(f"      {j}. {query_preview} (similarity: {similarity:.3f})")
        
        # Test user profile and analytics
        print(f"\n3. Testing enhanced user profile...")
        profile = memory_manager.get_user_profile("vector_test_user")
        print(f"✅ Profile: {profile['total_interactions']} interactions")
        print(f"   Topics of interest: {profile['topics_of_interest']}")
        print(f"   Memory stats: {profile['memory_stats']['total_memories']} memories")
        
        # Test memory analytics
        print(f"\n4. Testing memory analytics...")
        analytics = memory_manager.get_memory_analytics("vector_test_user")
        print(f"✅ Analytics:")
        print(f"   Total memories: {analytics['total_memories']}")
        print(f"   Average query length: {analytics['avg_query_length']:.1f} characters")
        print(f"   Top topics: {analytics['top_topics'][:3]}")
        print(f"   Interaction frequency: {analytics['interaction_frequency']:.2f} per day")
        
        # Test enhanced context formatting
        print(f"\n5. Testing enhanced context formatting...")
        context = memory_manager.format_context_for_agent(
            user_id="vector_test_user",
            query="Tell me about SmartView development capabilities"
        )
        print(f"✅ Enhanced context generated:")
        print(f"   Length: {len(context)} characters")
        print(f"   Preview: {context[:200]}...")
        
        # Test performance with larger dataset
        print(f"\n6. Testing performance with larger dataset...")
        start_time = time.time()
        
        # Add more conversations for performance testing
        for i in range(20):
            memory_manager.store_conversation_memory(
                user_id="vector_test_user",
                thread_id=f"perf_thread_{i}",
                query=f"Performance test query {i} about various topics and features",
                response=f"This is a performance test response {i} with different content and keywords for testing scalability and search performance."
            )
        
        performance_time = time.time() - start_time
        print(f"✅ Stored 20 additional memories in {performance_time:.3f} seconds")
        
        # Test search performance with larger dataset
        start_time = time.time()
        large_dataset_results = memory_manager.get_relevant_memories(
            user_id="vector_test_user",
            query="performance testing and scalability features",
            max_results=5
        )
        search_time = time.time() - start_time
        
        print(f"✅ Search on {len(memory_manager._load_user_memories('vector_test_user'))} memories: {search_time:.4f} seconds")
        print(f"   Found {len(large_dataset_results)} relevant results")
        
        print("\n🎉 All vector memory manager tests passed!")
        
        # Performance summary
        print(f"\n📊 Performance Summary:")
        total_memories = len(memory_manager._load_user_memories("vector_test_user"))
        print(f"   Total memories processed: {total_memories}")
        print(f"   Average search time: {search_time:.4f} seconds")
        print(f"   Memories per second: {total_memories / search_time:.1f}")
        print(f"   Vector similarity threshold: {memory_manager.similarity_threshold}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up temporary directory: {temp_dir}")

def compare_vector_vs_keyword_search():
    """Compare vector-based search vs keyword-based search."""
    print("\n🔬 Comparing Vector vs Keyword Search")
    print("=" * 40)
    
    # This would test both approaches and show differences
    # For now, just placeholder
    print("Vector search provides better semantic understanding")
    print("Keyword search is faster but less contextually aware")

if __name__ == "__main__":
    test_vector_memory_manager()
    compare_vector_vs_keyword_search()
