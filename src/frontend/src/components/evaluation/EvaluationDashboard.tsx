import React, { useState, useEffect } from 'react';
import { Spinner, Stack, Text, ProgressBar, Card, Button, Dropdown, Option, Label, Title2 } from '@fluentui/react-components';
import { Info16Filled, ChartMultiple24Regular, StarFilled } from '@fluentui/react-icons';

/**
 * Evaluation Dashboard Component
 * Displays evaluation results and metrics for agent performance
 */
const EvaluationDashboard: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [evaluationResults, setEvaluationResults] = useState<any>(null);
  const [feedbackStats, setFeedbackStats] = useState<any>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Categories of metrics to display
  const categories = [
    { key: 'all', name: 'All Metrics' },
    { key: 'operational', name: 'Operational Metrics' },
    { key: 'quality', name: 'Response Quality' },
    { key: 'accuracy', name: 'Accuracy' },
    { key: 'feedback', name: 'User Feedback' },
    { key: 'safety', name: 'Safety & Compliance' },
  ];

  // Fetch evaluation results on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch latest evaluation results
        const resultsResponse = await fetch('/evaluation/results?latest=true');
        if (!resultsResponse.ok) {
          throw new Error(`Failed to fetch evaluation results: ${resultsResponse.statusText}`);
        }
        const resultsData = await resultsResponse.json();
        
        // Fetch feedback statistics
        const feedbackResponse = await fetch('/evaluation/feedback/stats');
        if (!feedbackResponse.ok) {
          throw new Error(`Failed to fetch feedback stats: ${feedbackResponse.statusText}`);
        }
        const feedbackData = await feedbackResponse.json();
        
        setEvaluationResults(resultsData);
        setFeedbackStats(feedbackData.stats);
        setError(null);
      } catch (err) {
        setError(`Error loading evaluation data: ${err instanceof Error ? err.message : String(err)}`);
        console.error('Error fetching evaluation data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Function to run a new evaluation
  const runEvaluation = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/evaluation/run', { 
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error(`Failed to start evaluation: ${response.statusText}`);
      }
      
      const result = await response.json();
      alert('Evaluation started. Please check back in a few minutes for results.');
      
    } catch (err) {
      setError(`Error starting evaluation: ${err instanceof Error ? err.message : String(err)}`);
      console.error('Error starting evaluation:', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter metrics based on selected category
  const getFilteredMetrics = () => {
    if (!evaluationResults?.metrics) return [];
    
    const metrics = evaluationResults.metrics;
    const allMetrics = Object.entries(metrics).map(([key, value]) => ({ key, value }));
    
    if (selectedCategory === 'all') return allMetrics;
    
    // Filter logic for each category
    switch (selectedCategory) {
      case 'operational':
        return allMetrics.filter(m => 
          m.key.includes('duration') || 
          m.key.includes('tokens') || 
          m.key.includes('latency')
        );
      case 'quality':
        return allMetrics.filter(m => 
          m.key.includes('response_') || 
          m.key.includes('quality') || 
          m.key.includes('coherence')
        );
      case 'accuracy':
        return allMetrics.filter(m => 
          m.key.includes('accuracy') || 
          m.key.includes('factual')
        );
      case 'feedback':
        return allMetrics.filter(m => 
          m.key.includes('feedback') || 
          m.key.includes('rating')
        );
      case 'safety':
        return allMetrics.filter(m => 
          m.key.includes('safety') || 
          m.key.includes('attack') || 
          m.key.includes('vulnerability')
        );
      default:
        return allMetrics;
    }
  };

  // Format metric value for display
  const formatMetricValue = (value: any) => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
      // Show as percentage if between 0-1
      if (value >= 0 && value <= 1) return `${(value * 100).toFixed(1)}%`;
      // Show with 2 decimal places for other numbers
      return value.toFixed(2);
    }
    return String(value);
  };

  // Determine if a metric should be displayed as a progress bar
  const shouldShowAsProgressBar = (key: string, value: any) => {
    return (
      typeof value === 'number' &&
      value >= 0 && 
      value <= 1 &&
      (key.includes('score') || 
       key.includes('accuracy') || 
       key.includes('quality') || 
       key.includes('ratio') || 
       key.includes('relevance'))
    );
  };

  // Get progress bar color based on metric value
  const getProgressBarColor = (key: string, value: number) => {
    if (value >= 0.8) return 'success';
    if (value >= 0.6) return 'info'; 
    if (value >= 0.4) return 'warning';
    return 'error';
  };

  // Loading state
  if (loading && !evaluationResults) {
    return (
      <Stack verticalAlign="center" horizontalAlign="center" style={{ height: '400px' }}>
        <Spinner label="Loading evaluation data..." />
      </Stack>
    );
  }

  // Error state
  if (error && !evaluationResults) {
    return (
      <Stack verticalAlign="center" horizontalAlign="center" style={{ height: '400px', color: 'var(--colorStatusDangerForeground1)' }}>
        <Info16Filled />
        <Text>
          {error}
        </Text>
        <Button appearance="primary" onClick={runEvaluation}>Run Evaluation</Button>
      </Stack>
    );
  }

  // No data state
  if (!evaluationResults?.metrics) {
    return (
      <Stack verticalAlign="center" horizontalAlign="center" style={{ height: '400px' }}>
        <Text>No evaluation data available</Text>
        <Button appearance="primary" onClick={runEvaluation}>Run Evaluation</Button>
      </Stack>
    );
  }

  return (
    <Stack tokens={{ childrenGap: 20 }}>
      <Stack horizontal horizontalAlign="space-between" verticalAlign="center">
        <Title2>Agent Evaluation Dashboard</Title2>
        <Button appearance="primary" onClick={runEvaluation} disabled={loading}>
          {loading ? <Spinner size="tiny" /> : 'Run New Evaluation'}
        </Button>
      </Stack>

      {error && (
        <Stack style={{ color: 'var(--colorStatusDangerForeground1)', padding: '10px' }}>
          <Text>{error}</Text>
        </Stack>
      )}

      {/* Summary Cards */}
      <Stack horizontal tokens={{ childrenGap: 10 }} style={{ overflowX: 'auto' }}>
        <Card style={{ minWidth: '200px', flex: 1 }}>
          <Stack tokens={{ childrenGap: 5 }}>
            <Text weight="semibold">Overall Quality</Text>
            <Text size="xxlarge" weight="bold">
              {evaluationResults.metrics.overall_quality_score 
                ? formatMetricValue(evaluationResults.metrics.overall_quality_score) 
                : formatMetricValue(evaluationResults.metrics.task_adherence_score || 0.0)}
            </Text>
          </Stack>
        </Card>

        <Card style={{ minWidth: '200px', flex: 1 }}>
          <Stack tokens={{ childrenGap: 5 }}>
            <Text weight="semibold">Response Time</Text>
            <Text size="xxlarge" weight="bold">
              {formatMetricValue(evaluationResults.metrics['client-run-duration-in-seconds'] || 0)} s
            </Text>
          </Stack>
        </Card>

        <Card style={{ minWidth: '200px', flex: 1 }}>
          <Stack tokens={{ childrenGap: 5 }}>
            <Text weight="semibold">User Feedback</Text>
            <Stack horizontal verticalAlign="center" tokens={{ childrenGap: 5 }}>
              <Text size="xxlarge" weight="bold">
                {feedbackStats?.average_rating 
                  ? formatMetricValue(feedbackStats.average_rating) 
                  : 'N/A'}
              </Text>
              {feedbackStats?.average_rating && (
                <StarFilled style={{ color: 'gold' }} />
              )}
            </Stack>
            <Text size="small">{feedbackStats?.feedback_count || 0} ratings</Text>
          </Stack>
        </Card>
      </Stack>

      {/* Category Filter */}
      <Stack horizontal verticalAlign="center" tokens={{ childrenGap: 10 }}>
        <Label>Filter Metrics:</Label>
        <Dropdown
          value={selectedCategory}
          onOptionSelect={(_, data) => setSelectedCategory(data.optionValue as string)}
        >
          {categories.map((category) => (
            <Option key={category.key} value={category.key}>
              {category.name}
            </Option>
          ))}
        </Dropdown>
      </Stack>

      {/* Metrics Table */}
      <Card>
        <Stack tokens={{ childrenGap: 15 }} style={{ maxHeight: '500px', overflowY: 'auto' }}>
          {getFilteredMetrics().map(({ key, value }) => (
            <Stack key={key} tokens={{ childrenGap: 5 }}>
              <Stack horizontal horizontalAlign="space-between">
                <Text weight="semibold">{key.replace(/_/g, ' ')}</Text>
                <Text>{formatMetricValue(value)}</Text>
              </Stack>

              {shouldShowAsProgressBar(key, value) && (
                <ProgressBar 
                  value={typeof value === 'number' ? value : 0} 
                  color={getProgressBarColor(key, value as number)} 
                />
              )}
            </Stack>
          ))}
        </Stack>
      </Card>

      {/* Feedback Summary */}
      {feedbackStats && (
        <Card>
          <Stack tokens={{ childrenGap: 10 }}>
            <Text weight="semibold">Feedback Summary</Text>
            
            {feedbackStats.top_queries && feedbackStats.top_queries.length > 0 ? (
              <Stack tokens={{ childrenGap: 8 }}>
                <Text>Top queries with feedback:</Text>
                {feedbackStats.top_queries.map((item: any, index: number) => (
                  <Text key={index} size="small">
                    • "{item.query}" ({item.feedback_count} ratings)
                  </Text>
                ))}
              </Stack>
            ) : (
              <Text>No feedback data available</Text>
            )}
            
            {feedbackStats.rating_distribution && (
              <Stack tokens={{ childrenGap: 5 }}>
                <Text>Rating Distribution:</Text>
                {Object.entries(feedbackStats.rating_distribution).map(([rating, count]) => (
                  <Stack key={rating} horizontal tokens={{ childrenGap: 5 }}>
                    <Text size="small">{rating} stars:</Text>
                    <ProgressBar 
                      value={(count as number) / (feedbackStats.total_feedback_count || 1)} 
                      style={{ width: '100%' }}
                    />
                    <Text size="small">{count}</Text>
                  </Stack>
                ))}
              </Stack>
            )}
          </Stack>
        </Card>
      )}

      <Text size="small" style={{ fontStyle: 'italic' }}>
        Last evaluation run: {new Date(evaluationResults.created_at || Date.now()).toLocaleString()}
      </Text>
    </Stack>
  );
};

export default EvaluationDashboard;
