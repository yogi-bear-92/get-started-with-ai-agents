# Monitoring and Evaluation Framework

This document describes the enhanced monitoring and evaluation framework for AI agents in the project. The framework provides comprehensive insights into agent performance, allows for comparison between different agent configurations, and collects user feedback to continuously improve the agent.

## Features

### 1. Enhanced Evaluation Metrics

The evaluation framework now includes several categories of metrics:

- **Operational Metrics**: Response time, token usage, efficiency
- **Response Quality**: Completeness, relevance, conciseness
- **Factual Accuracy**: Comparing responses against ground truth
- **User Feedback**: Ratings and comments from users
- **Safety & Compliance**: Content safety, vulnerability detection

### 2. User Feedback Collection

Users can provide feedback on agent responses through a built-in rating system:

- Star ratings (1-5)
- Optional comments
- Feedback is stored and aggregated for analysis

### 3. Visual Dashboard

The evaluation dashboard provides visual insights into agent performance:

- Summary cards for key metrics
- Detailed metric tables with filtering capabilities
- Feedback statistics and top queries
- Progress indicators for quality metrics

### 4. A/B Testing

Compare performance between different agent configurations:

- Compare response time, token usage, and quality metrics
- Identify the better-performing configuration
- Track performance changes over time

## Using the Evaluation Framework

### Running Evaluations

Evaluations can be triggered in several ways:

1. From the command line:
   ```bash
   python evals/enhanced_evaluation.py
   ```

2. Through the web interface:
   - Navigate to the Evaluation Dashboard
   - Click "Run New Evaluation"

3. Via the API endpoint:
   ```bash
   curl -X POST http://localhost:8000/evaluation/run
   ```

### Viewing Results

Access evaluation results through:

1. The web dashboard at `/evaluation/dashboard`
2. API endpoints:
   - `/evaluation/results?latest=true` for latest results
   - `/evaluation/results` for all historical results
3. JSON files in the `evals/evaluation_results` directory

### Submitting Feedback

Users can submit feedback on agent responses by:

1. Clicking the "Rate this response" button on any agent message
2. Selecting a star rating (1-5)
3. Optionally providing comments

### Using A/B Testing

To run A/B testing between agent configurations:

1. Ensure you have two agent configurations created in Azure AI Foundry
2. Run the test using the ABTestingEvaluator:

```python
from evals.enhanced_evaluation import ABTestingEvaluator

# Initialize the evaluator
ab_tester = ABTestingEvaluator(
    config_a_id="agent-id-1",  # Baseline agent
    config_b_id="agent-id-2",  # Variant agent
    credential=credential,
    project_endpoint="your-project-endpoint"
)

# Run the comparison with test queries
results = await ab_tester.run_comparison(test_queries)
```

## Interpreting Results

### Quality Metrics

- **Response Completeness**: How thoroughly the agent addresses the query (0-1)
- **Response Relevance**: How relevant the response is to the query (0-1)
- **Response Conciseness**: How concisely the response is presented (0-1)
- **Overall Quality**: Weighted average of completeness, relevance, and conciseness

### User Satisfaction

- **Average Rating**: Mean rating across all feedback (1-5)
- **Rating Distribution**: Distribution of ratings across 1-5 stars
- **Positive Feedback Ratio**: Proportion of 4-5 star ratings

### Performance Metrics

- **Tokens Per Second**: Throughput measure of token processing
- **Response Time**: Total time to generate a response
- **Token Usage**: Total tokens consumed (prompt + completion)

## Best Practices

1. **Regular Evaluation**: Run evaluations regularly to track performance over time
2. **Diverse Test Queries**: Use a diverse set of test queries to thoroughly evaluate agent capabilities
3. **User Feedback Collection**: Encourage users to provide feedback for continuous improvement
4. **A/B Testing**: Test major changes using A/B testing before full deployment
5. **Ground Truth Maintenance**: Keep ground truth data updated for accurate factual evaluations

## Technical Details

The evaluation framework is implemented in:

- `evals/enhanced_evaluation.py`: Core evaluation functionality
- `src/api/evaluation_routes.py`: API endpoints for evaluation and feedback
- `src/frontend/src/components/evaluation/`: Frontend components for the dashboard

Data is stored in:
- `evals/evaluation_results/`: JSON files with evaluation results
- `evals/feedback_data.json`: User feedback database
