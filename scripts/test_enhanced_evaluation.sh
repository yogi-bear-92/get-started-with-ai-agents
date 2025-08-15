#!/bin/bash
# Test script for the enhanced evaluation framework

echo "Testing Enhanced Evaluation Framework"
echo "===================================="

# Ensure we're in the correct directory
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  echo "Activating virtual environment..."
  if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
  elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
  else
    echo "Failed to find activate script in .venv"
    exit 1
  fi
fi

# Install required packages
echo "Installing evaluation requirements..."
pip install -r evals/requirements-evaluation.txt

# Run the enhanced evaluation
echo "Running enhanced evaluation..."
python -m evals.enhanced_evaluation

# Check if the evaluation results file exists
if [ -d "evals/evaluation_results" ] && [ "$(ls -A evals/evaluation_results)" ]; then
  echo "Evaluation completed successfully!"
  echo "Results saved in evals/evaluation_results/"

  # Show the latest results file
  latest_file=$(ls -t evals/evaluation_results | head -1)
  echo "Latest results file: $latest_file"
else
  echo "No evaluation results found. Something may have gone wrong."
  exit 1
fi

echo
echo "Testing API endpoints..."
echo "======================="

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null; then
  echo "Server doesn't appear to be running. Please start the server first."
  echo "Run: cd src && python -m uvicorn api.main:create_app --factory --reload"
  exit 1
fi

# Test evaluation API endpoints
echo "Testing /evaluation/results endpoint..."
curl -s http://localhost:8000/evaluation/results | jq . || echo "Failed to get evaluation results"

echo
echo "Testing /evaluation/feedback/stats endpoint..."
curl -s http://localhost:8000/evaluation/feedback/stats | jq . || echo "Failed to get feedback stats"

echo
echo "Testing /evaluation/run endpoint..."
curl -s -X POST http://localhost:8000/evaluation/run | jq . || echo "Failed to start evaluation"

echo
echo "Done!"
