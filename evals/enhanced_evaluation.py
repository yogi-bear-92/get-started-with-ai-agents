"""
Enhances the existing evaluation framework with additional metrics and evaluators.

This module extends the standard Azure AI Foundry evaluators with custom metrics that
provide deeper insights into agent performance, including:
- Response quality metrics
- Factual accuracy assessment
- Latency and token efficiency metrics
- User feedback incorporation
- A/B testing between agent configurations
"""

import os
import json
import time
import statistics
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from azure.ai.agents.models import RunStatus, MessageRole
from azure.ai.evaluation import evaluate, AIAgentConverter
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.language.questions import QuestionAnsweringClient
from azure.core.credentials import AzureKeyCredential

# Import standard evaluators
from azure.ai.evaluation import (
    ToolCallAccuracyEvaluator, 
    IntentResolutionEvaluator, 
    TaskAdherenceEvaluator, 
    CodeVulnerabilityEvaluator, 
    ContentSafetyEvaluator, 
    IndirectAttackEvaluator
)

# Constants for configuration
EVALUATION_RESULTS_PATH = Path(__file__).parent / "evaluation_results"
FEEDBACK_DATABASE_PATH = Path(__file__).parent / "feedback_data.json"


class EnhancedOperationalMetricsEvaluator:
    """Expanded operational metrics evaluator with additional performance statistics"""
    
    def __init__(self):
        pass
        
    def __call__(self, *, metrics: dict, **kwargs):
        """Process and enrich operational metrics"""
        enhanced_metrics = metrics.copy()
        
        # Calculate token efficiency (tokens per second)
        if "prompt-tokens" in metrics and "client-run-duration-in-seconds" in metrics:
            if metrics["client-run-duration-in-seconds"] > 0:
                enhanced_metrics["tokens-per-second"] = (
                    metrics["prompt-tokens"] + metrics.get("completion-tokens", 0)
                ) / metrics["client-run-duration-in-seconds"]
        
        # Calculate response size relative to prompt
        if "prompt-tokens" in metrics and "completion-tokens" in metrics:
            if metrics["prompt-tokens"] > 0:
                enhanced_metrics["response-to-prompt-ratio"] = metrics["completion-tokens"] / metrics["prompt-tokens"]
        
        return enhanced_metrics


class ResponseQualityEvaluator:
    """Evaluates the quality of agent responses based on multiple dimensions"""
    
    def __init__(self, model_config: dict):
        self.model_config = model_config
        
    def __call__(self, *, agent_response: str, query: str, **kwargs) -> dict:
        """Evaluate response quality on multiple dimensions
        
        Args:
            agent_response: The agent's response text
            query: The user's original query
            
        Returns:
            Dict with quality metrics
        """
        # Initialize quality scores
        quality_metrics = {
            "response_completeness": 0.0,
            "response_relevance": 0.0,
            "response_conciseness": 0.0,
            "overall_quality_score": 0.0
        }
        
        # Calculate completeness (based on response length relative to query complexity)
        words_in_query = len(query.split())
        words_in_response = len(agent_response.split())
        expected_min_words = min(words_in_query * 1.5, 30)  # Heuristic for minimum expected response length
        
        if words_in_response >= expected_min_words:
            quality_metrics["response_completeness"] = min(1.0, words_in_response / (words_in_query * 3))
        else:
            quality_metrics["response_completeness"] = words_in_response / expected_min_words
            
        # Calculate relevance (simplified implementation)
        # Ideally this would use embeddings and cosine similarity
        common_words = set(query.lower().split()) & set(agent_response.lower().split())
        quality_metrics["response_relevance"] = min(1.0, len(common_words) * 2 / words_in_query)
        
        # Calculate conciseness (penalize extremely verbose responses)
        ideal_max_length = words_in_query * 5  # Heuristic for maximum ideal response length
        if words_in_response <= ideal_max_length:
            quality_metrics["response_conciseness"] = 1.0
        else:
            quality_metrics["response_conciseness"] = ideal_max_length / words_in_response
            
        # Calculate overall quality score (weighted average)
        quality_metrics["overall_quality_score"] = (
            quality_metrics["response_completeness"] * 0.4 +
            quality_metrics["response_relevance"] * 0.4 + 
            quality_metrics["response_conciseness"] * 0.2
        )
        
        return quality_metrics


class FactualAccuracyEvaluator:
    """Evaluates the factual accuracy of agent responses against ground truth"""
    
    def __init__(self, credential: DefaultAzureCredential, azure_ai_project: str):
        self.credential = credential
        self.azure_ai_project = azure_ai_project
        
    def __call__(self, *, agent_response: str, metrics: dict, **kwargs) -> dict:
        """Evaluate factual accuracy against ground truth if available
        
        Args:
            agent_response: The agent's response text
            metrics: Metrics dict containing ground truth if available
            
        Returns:
            Dict with accuracy metrics
        """
        accuracy_metrics = {
            "has_ground_truth": False,
            "factual_accuracy_score": None,
            "contains_factual_errors": None
        }
        
        ground_truth = metrics.get("ground-truth", "")
        
        if not ground_truth:
            return accuracy_metrics
            
        accuracy_metrics["has_ground_truth"] = True
        
        # Simple word overlap for factual similarity
        # In production, this would use more sophisticated NLP techniques
        gt_words = set(ground_truth.lower().split())
        response_words = set(agent_response.lower().split())
        
        # Calculate Jaccard similarity as a simple accuracy measure
        intersection = len(gt_words.intersection(response_words))
        union = len(gt_words.union(response_words))
        
        if union > 0:
            accuracy_metrics["factual_accuracy_score"] = intersection / union
            accuracy_metrics["contains_factual_errors"] = accuracy_metrics["factual_accuracy_score"] < 0.6
        
        return accuracy_metrics


class UserFeedbackEvaluator:
    """Incorporates user feedback data into evaluation metrics"""
    
    def __init__(self):
        self.feedback_database_path = FEEDBACK_DATABASE_PATH
        self._load_feedback_data()
        
    def _load_feedback_data(self):
        """Load feedback data from JSON file"""
        if self.feedback_database_path.exists():
            with open(self.feedback_database_path, 'r') as f:
                self.feedback_data = json.load(f)
        else:
            self.feedback_data = {"query_feedback": {}}
            
    def __call__(self, *, query: str, **kwargs) -> dict:
        """Retrieve feedback metrics for similar queries
        
        Args:
            query: The user's query
            
        Returns:
            Dict with feedback metrics
        """
        feedback_metrics = {
            "has_user_feedback": False,
            "average_user_rating": None,
            "feedback_count": 0,
            "positive_feedback_ratio": None
        }
        
        # Simple exact query matching
        # In production, this would use semantic similarity
        if query in self.feedback_data["query_feedback"]:
            feedback = self.feedback_data["query_feedback"][query]
            feedback_metrics["has_user_feedback"] = True
            feedback_metrics["feedback_count"] = len(feedback)
            
            if feedback:
                ratings = [item["rating"] for item in feedback]
                feedback_metrics["average_user_rating"] = sum(ratings) / len(ratings)
                positive_ratings = sum(1 for r in ratings if r >= 4)
                feedback_metrics["positive_feedback_ratio"] = positive_ratings / len(ratings)
        
        return feedback_metrics


def store_user_feedback(query: str, response: str, rating: int, comments: str = None):
    """Store user feedback in the feedback database
    
    Args:
        query: The user's query
        response: The agent's response
        rating: User rating (1-5)
        comments: Optional user comments
    """
    feedback_path = FEEDBACK_DATABASE_PATH
    
    # Load existing feedback
    if feedback_path.exists():
        with open(feedback_path, 'r') as f:
            feedback_data = json.load(f)
    else:
        feedback_data = {"query_feedback": {}}
    
    # Add new feedback
    timestamp = datetime.now().isoformat()
    
    if query not in feedback_data["query_feedback"]:
        feedback_data["query_feedback"][query] = []
        
    feedback_entry = {
        "timestamp": timestamp,
        "rating": rating,
        "comments": comments,
        "response_snippet": response[:100] + "..." if len(response) > 100 else response
    }
    
    feedback_data["query_feedback"][query].append(feedback_entry)
    
    # Write back to file
    feedback_path.parent.mkdir(exist_ok=True)
    with open(feedback_path, 'w') as f:
        json.dump(feedback_data, f, indent=2)
        
    return feedback_entry


class ABTestingEvaluator:
    """Compares performance between different agent configurations"""
    
    def __init__(self, config_a_id: str, config_b_id: str, credential: DefaultAzureCredential, project_endpoint: str):
        """Initialize with two agent configurations to compare
        
        Args:
            config_a_id: Agent A ID (baseline)
            config_b_id: Agent B ID (variant)
            credential: Azure credential
            project_endpoint: AI project endpoint
        """
        self.config_a_id = config_a_id
        self.config_b_id = config_b_id
        self.credential = credential
        self.project_endpoint = project_endpoint
        self.results_path = EVALUATION_RESULTS_PATH
        self.results_path.mkdir(exist_ok=True)
        
    async def run_comparison(self, test_queries: List[dict]) -> dict:
        """Run A/B testing comparing two agent configurations
        
        Args:
            test_queries: List of test queries to run against both agents
            
        Returns:
            Dict with comparison results
        """
        # Initialize AI project client
        ai_project = AIProjectClient(
            credential=self.credential,
            endpoint=self.project_endpoint,
            api_version="2025-05-15-preview"
        )
        
        # Get the agent objects
        agent_a = await ai_project.agents.get_agent(self.config_a_id)
        agent_b = await ai_project.agents.get_agent(self.config_b_id)
        
        # Store results for each agent
        results_a = []
        results_b = []
        
        # Run each test query against both agents
        for row in test_queries:
            query = row.get("query")
            
            # Run against agent A
            thread_a = await ai_project.agents.threads.create()
            await ai_project.agents.messages.create(
                thread_a.id, role=MessageRole.USER, content=query
            )
            start_time_a = time.time()
            run_a = await ai_project.agents.runs.create_and_process(
                thread_id=thread_a.id, agent_id=agent_a.id
            )
            end_time_a = time.time()
            
            # Run against agent B
            thread_b = await ai_project.agents.threads.create()
            await ai_project.agents.messages.create(
                thread_b.id, role=MessageRole.USER, content=query
            )
            start_time_b = time.time()
            run_b = await ai_project.agents.runs.create_and_process(
                thread_id=thread_b.id, agent_id=agent_b.id
            )
            end_time_b = time.time()
            
            # Get messages from both threads
            messages_a = [msg async for msg in ai_project.agents.messages.list(thread_a.id)]
            messages_b = [msg async for msg in ai_project.agents.messages.list(thread_b.id)]
            
            # Get the agent responses
            response_a = next((m.content[0].text for m in messages_a if m.role == MessageRole.ASSISTANT), "")
            response_b = next((m.content[0].text for m in messages_b if m.role == MessageRole.ASSISTANT), "")
            
            # Record metrics
            result_a = {
                "query": query,
                "response": response_a,
                "latency": end_time_a - start_time_a,
                "token_usage": run_a.usage.prompt_tokens + run_a.usage.completion_tokens
            }
            
            result_b = {
                "query": query,
                "response": response_b,
                "latency": end_time_b - start_time_b,
                "token_usage": run_b.usage.prompt_tokens + run_b.usage.completion_tokens
            }
            
            results_a.append(result_a)
            results_b.append(result_b)
            
        # Calculate aggregate metrics
        comparison_results = {
            "timestamp": datetime.now().isoformat(),
            "config_a": {
                "agent_id": self.config_a_id,
                "agent_name": agent_a.name,
                "avg_latency": statistics.mean(r["latency"] for r in results_a),
                "avg_tokens": statistics.mean(r["token_usage"] for r in results_a),
                "responses": results_a
            },
            "config_b": {
                "agent_id": self.config_b_id,
                "agent_name": agent_b.name,
                "avg_latency": statistics.mean(r["latency"] for r in results_b),
                "avg_tokens": statistics.mean(r["token_usage"] for r in results_b),
                "responses": results_b
            },
            "comparisons": []
        }
        
        # Compare individual responses
        for i, (res_a, res_b) in enumerate(zip(results_a, results_b)):
            comparison = {
                "query": res_a["query"],
                "latency_diff": res_a["latency"] - res_b["latency"],
                "token_diff": res_a["token_usage"] - res_b["token_usage"],
                "latency_winner": "A" if res_a["latency"] < res_b["latency"] else "B",
                "tokens_winner": "A" if res_a["token_usage"] < res_b["token_usage"] else "B"
            }
            comparison_results["comparisons"].append(comparison)
            
        # Calculate overall winners
        comparison_results["overall_latency_winner"] = (
            "A" if comparison_results["config_a"]["avg_latency"] < comparison_results["config_b"]["avg_latency"] else "B"
        )
        comparison_results["overall_tokens_winner"] = (
            "A" if comparison_results["config_a"]["avg_tokens"] < comparison_results["config_b"]["avg_tokens"] else "B"
        )
        
        # Save results to file
        results_filename = f"abtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(self.results_path / results_filename, 'w') as f:
            json.dump(comparison_results, f, indent=2)
            
        return comparison_results


async def run_enhanced_evaluation(agent_id: str = None, test_queries_path: str = None, output_path: str = None):
    """Run enhanced evaluation with multiple metrics
    
    Args:
        agent_id: Optional agent ID (defaults to environment variable)
        test_queries_path: Path to test queries JSON file (defaults to evals/eval-queries.json)
        output_path: Path to write evaluation results (defaults to evals/evaluation_results/latest.json)
    
    Returns:
        Evaluation results object
    """
    current_dir = Path(__file__).parent
    test_queries_path = Path(test_queries_path) if test_queries_path else current_dir / "eval-queries.json"
    output_dir = EVALUATION_RESULTS_PATH
    output_dir.mkdir(exist_ok=True)
    
    output_path = Path(output_path) if output_path else output_dir / f"eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    latest_output_path = output_dir / "latest.json"
    
    # Get AI project parameters from environment variables
    env_path = current_dir.parent / "src" / ".env"
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)
    
    project_endpoint = os.environ.get("AZURE_EXISTING_AIPROJECT_ENDPOINT")
    deployment_name = os.getenv("AZURE_AI_AGENT_DEPLOYMENT_NAME")
    agent_name = os.environ.get("AZURE_AI_AGENT_NAME")
    agent_id = agent_id or os.environ.get("AZURE_EXISTING_AGENT_ID")
    
    # Validate required environment variables
    if not project_endpoint:
        raise ValueError("Please set the AZURE_EXISTING_AIPROJECT_ENDPOINT environment variable.")
    
    if not agent_id and not agent_name:
        raise ValueError("Please set either AZURE_EXISTING_AGENT_ID or AZURE_AI_AGENT_NAME environment variable.")
    
    # Initialize AIProjectClient
    from azure.core.pipeline.policies import AsyncRetryPolicy
    credential = DefaultAzureCredential()
    ai_project = AIProjectClient(
        credential=credential,
        endpoint=project_endpoint,
        api_version="2025-05-15-preview"  # Using preview for evaluation support
    )
    
    # Look up the agent by name if agent Id is not provided
    if not agent_id and agent_name:
        async for agent in ai_project.agents.list_agents():
            if agent.name == agent_name:
                agent_id = agent.id
                break
    
    if not agent_id:
        raise ValueError("Agent ID not found. Please provide a valid agent ID or name.")
    
    agent = await ai_project.agents.get_agent(agent_id)
    
    # Use model from agent if not provided
    if not deployment_name:
        deployment_name = agent.model
    
    # Setup required evaluation config
    from urllib.parse import urlparse
    parsed_endpoint = urlparse(project_endpoint)
    model_endpoint = f"{parsed_endpoint.scheme}://{parsed_endpoint.netloc}"
    
    model_config = {
        "azure_deployment": deployment_name,
        "azure_endpoint": model_endpoint,
        "api_version": "",
    }
    thread_data_converter = AIAgentConverter(ai_project)
    
    # Read test queries from input file
    with open(test_queries_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    
    # Create evaluation input file path
    eval_input_path = current_dir / "eval-input.jsonl"
    
    # Execute the test queries against the agent and prepare the evaluation input
    with open(eval_input_path, "w", encoding="utf-8") as f:
        for row in test_data:
            # Create a new thread for each query to isolate conversations
            thread = await ai_project.agents.threads.create()
            
            # Create the user query
            await ai_project.agents.messages.create(
                thread.id, role=MessageRole.USER, content=row.get("query")
            )
            
            # Run agent on thread and measure performance
            start_time = time.time()
            run = await ai_project.agents.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id
            )
            end_time = time.time()
            
            if run.status != RunStatus.COMPLETED:
                raise ValueError(run.last_error or "Run failed to complete")
            
            # Get the response
            messages = [msg async for msg in ai_project.agents.messages.list(thread.id)]
            agent_response = next((m.content[0].text for m in messages if m.role == MessageRole.ASSISTANT), "")
            
            operational_metrics = {
                "server-run-duration-in-seconds": (
                    run.completed_at - run.created_at
                ).total_seconds(),
                "client-run-duration-in-seconds": end_time - start_time,
                "completion-tokens": run.usage.completion_tokens,
                "prompt-tokens": run.usage.prompt_tokens,
                "ground-truth": row.get("ground-truth", ''),
                "agent_response": agent_response,
                "query": row.get("query")
            }
            
            # Add thread data + operational metrics to the evaluation input
            evaluation_data = await thread_data_converter.prepare_evaluation_data(thread_ids=thread.id)
            eval_item = evaluation_data[0]
            eval_item["metrics"] = operational_metrics
            f.write(json.dumps(eval_item) + "\n")
    
    # Now, run an enhanced set of evaluators
    results = await evaluate(
        evaluation_name=f"enhanced-evaluation-{datetime.now().strftime('%Y%m%d')}",
        data=eval_input_path,
        evaluators={
            "operational_metrics": EnhancedOperationalMetricsEvaluator(),
            "response_quality": ResponseQualityEvaluator(model_config=model_config),
            "factual_accuracy": FactualAccuracyEvaluator(credential=credential, azure_ai_project=project_endpoint),
            "user_feedback": UserFeedbackEvaluator(),
            "tool_call_accuracy": ToolCallAccuracyEvaluator(model_config=model_config),
            "intent_resolution": IntentResolutionEvaluator(model_config=model_config),
            "task_adherence": TaskAdherenceEvaluator(model_config=model_config),
            "code_vulnerability": CodeVulnerabilityEvaluator(credential=credential, azure_ai_project=project_endpoint),
            "content_safety": ContentSafetyEvaluator(credential=credential, azure_ai_project=project_endpoint),
            "indirect_attack": IndirectAttackEvaluator(credential=credential, azure_ai_project=project_endpoint)
        },
        output_path=output_path,
        azure_ai_project=project_endpoint,
    )
    
    # Save a copy as latest.json
    with open(output_path, 'r') as source:
        with open(latest_output_path, 'w') as dest:
            dest.write(source.read())
    
    # Format and print the evaluation results
    print_eval_results(results, eval_input_path, output_path)
    
    return results


def print_eval_results(results, input_path, output_path):
    """Print the evaluation results in a formatted table"""
    metrics = results.get("metrics", {})
    
    # Get the maximum length for formatting
    key_len = max(len(key) for key in metrics.keys()) + 5
    value_len = 20
    full_len = key_len + value_len + 5
    
    # Format the header
    print("\n" + "=" * full_len)
    print("Enhanced Evaluation Results".center(full_len))
    print("=" * full_len)
    
    # Group metrics by category
    categories = {
        "Operational Metrics": [k for k in metrics.keys() if "duration" in k or "tokens" in k],
        "Response Quality": [k for k in metrics.keys() if "response_" in k or "quality" in k],
        "Accuracy": [k for k in metrics.keys() if "accuracy" in k or "factual" in k],
        "User Feedback": [k for k in metrics.keys() if "feedback" in k or "rating" in k],
        "Safety & Compliance": [k for k in metrics.keys() if "safety" in k or "attack" in k or "vulnerability" in k],
        "Other": []
    }
    
    # Assign remaining metrics to Other category
    for key in metrics.keys():
        assigned = False
        for category, keys in categories.items():
            if key in keys:
                assigned = True
                break
        if not assigned:
            categories["Other"].append(key)
    
    # Print metrics by category
    for category, keys in categories.items():
        if keys:
            print(f"\n{category}:")
            print("-" * len(category))
            for key in sorted(keys):
                if key in metrics:
                    value = metrics[key]
                    if isinstance(value, float):
                        formatted_value = f"{value:.2f}"
                    else:
                        formatted_value = str(value)
                    
                    print(f"{key:<{key_len}} | {formatted_value}")
    
    print("\n" + "=" * full_len + "\n")
    
    # Print additional information
    print(f"Evaluation input: {input_path}")
    print(f"Evaluation output: {output_path}")
    print(f"Dashboard: http://localhost:8000/evaluation/dashboard")  # Will be implemented
    if results.get("studio_url") is not None:
        print(f"AI Foundry URL: {results['studio_url']}")
    
    print("\n" + "=" * full_len + "\n")


async def main():
    """Run the enhanced evaluation framework"""
    try:
        await run_enhanced_evaluation()
    except Exception as e:
        print(f"Error during enhanced evaluation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
