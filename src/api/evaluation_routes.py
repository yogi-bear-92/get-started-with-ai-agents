"""
API endpoints for evaluation and monitoring features.
"""

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path to import evals module
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from evals.enhanced_evaluation import store_user_feedback, run_enhanced_evaluation
    EVALUATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import evaluation modules: {e}")
    EVALUATION_AVAILABLE = False
    # Create dummy functions if evaluation modules are not available
    def store_user_feedback(*args, **kwargs):
        return {"status": "evaluation_not_available"}
    
    async def run_enhanced_evaluation(*args, **kwargs):
        return {"status": "evaluation_not_available"}

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


class FeedbackModel(BaseModel):
    """Model for user feedback submission"""
    query: str
    response: str
    rating: int
    comments: Optional[str] = None


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackModel):
    """
    Submit user feedback about an agent response

    This endpoint collects user feedback on agent responses, including:
    - Rating (1-5 scale)
    - Optional comments
    - The query and response being rated
    """
    try:
        feedback_entry = store_user_feedback(
            query=feedback.query,
            response=feedback.response,
            rating=feedback.rating,
            comments=feedback.comments
        )
        return {"status": "success", "feedback_recorded": feedback_entry}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error",
                     "message": f"Failed to store feedback: {str(e)}"}
        )


@router.get("/results")
async def get_evaluation_results(latest: bool = Query(True, description="Get only latest evaluation results")):
    """
    Get agent evaluation results

    Returns evaluation metrics from the most recent evaluation run or all available evaluation runs.
    """
    results_path = Path(__file__).parent.parent / \
        "evals" / "evaluation_results"
    latest_path = results_path / "latest.json"

    try:
        if not results_path.exists():
            return JSONResponse(
                status_code=404,
                content={"status": "error",
                         "message": "No evaluation results available"}
            )

        if latest and latest_path.exists():
            with open(latest_path, 'r') as f:
                return json.load(f)

        # Get all evaluation results if not latest
        if not latest:
            all_results = []
            result_files = list(results_path.glob("eval_results_*.json"))

            for file_path in sorted(result_files, key=lambda x: x.stat().st_mtime, reverse=True):
                with open(file_path, 'r') as f:
                    result = json.load(f)
                    result["filename"] = file_path.name
                    all_results.append(result)

            return {"status": "success", "results": all_results}

        return JSONResponse(
            status_code=404,
            content={"status": "error",
                     "message": "No evaluation results available"}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error",
                     "message": f"Error retrieving evaluation results: {str(e)}"}
        )


@router.post("/run")
async def run_evaluation(agent_id: Optional[str] = None):
    """
    Run agent evaluation

    Trigger an evaluation run for the specified agent or the default agent.
    Results will be stored in the evaluation_results directory.
    """
    try:
        # Run evaluation in a background task
        if EVALUATION_AVAILABLE:
            evaluation_task = asyncio.create_task(
                run_enhanced_evaluation(agent_id))
        else:
            # Return dummy response if evaluation is not available
            return {"status": "success", "message": "Evaluation not available in development mode."}
        return {"status": "success", "message": "Evaluation started. Results will be available soon."}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error",
                     "message": f"Failed to start evaluation: {str(e)}"}
        )


@router.get("/feedback/stats")
async def get_feedback_stats():
    """
    Get aggregated user feedback statistics

    Returns statistics about user feedback, such as average ratings and feedback counts.
    """
    feedback_path = Path(__file__).parent.parent / \
        "evals" / "feedback_data.json"

    try:
        if not feedback_path.exists():
            return {"status": "success", "message": "No feedback data available yet", "stats": {}}

        with open(feedback_path, 'r') as f:
            feedback_data = json.load(f)

        # Calculate aggregate statistics
        stats = {
            "total_feedback_count": 0,
            "average_rating": 0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "top_queries": [],
        }

        all_ratings = []
        query_counts = {}

        for query, feedback_list in feedback_data.get("query_feedback", {}).items():
            query_counts[query] = len(feedback_list)
            stats["total_feedback_count"] += len(feedback_list)

            for item in feedback_list:
                rating = item.get("rating", 0)
                if 1 <= rating <= 5:
                    all_ratings.append(rating)
                    stats["rating_distribution"][rating] += 1

        # Calculate average rating
        if all_ratings:
            stats["average_rating"] = sum(all_ratings) / len(all_ratings)

        # Get top 5 queries by feedback count
        top_queries = sorted(
            query_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        stats["top_queries"] = [
            {"query": query, "feedback_count": count}
            for query, count in top_queries
        ]

        return {"status": "success", "stats": stats}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error",
                     "message": f"Error retrieving feedback stats: {str(e)}"}
        )
