# FDE Platform - Evaluation Pack

## Overview
This document describes the evaluation methodology for the FDE Platform, including model metrics, error analysis, and RAG evaluation.

## Model Evaluation

### Metrics

#### Prediction Service Metrics

**Primary Metrics:**
- **Accuracy:** Percentage of correct predictions
- **Precision:** True positives / (True positives + False positives)
- **Recall:** True positives / (True positives + False negatives)
- **F1 Score:** Harmonic mean of precision and recall
- **Confidence Calibration:** How well confidence scores match actual accuracy

**Implementation:**
```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def evaluate_predictions(y_true, y_pred, y_proba):
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted'),
        'recall': recall_score(y_true, y_pred, average='weighted'),
        'f1': f1_score(y_true, y_pred, average='weighted'),
    }
    return metrics
```

**Monitoring:**
```sql
-- Query for model performance over time
SELECT 
    DATE(created_at) as date,
    model_version,
    COUNT(*) as prediction_count,
    AVG(confidence) as avg_confidence,
    MIN(confidence) as min_confidence,
    MAX(confidence) as max_confidence
FROM predictions
GROUP BY DATE(created_at), model_version
ORDER BY date DESC;
```

### Error Analysis

#### Error Slicing Strategy

1. **By Confidence Level:**
   - High confidence errors (>0.8): Systematic issues
   - Medium confidence (0.5-0.8): Model uncertainty
   - Low confidence (<0.5): Expected errors

2. **By Feature Range:**
   - Identify which feature ranges lead to errors
   - Check for data drift or distribution shifts

3. **By Time Period:**
   - Temporal patterns in errors
   - Identify degradation over time

**Example Query:**
```sql
-- Error distribution by confidence bucket
SELECT 
    CASE 
        WHEN confidence >= 0.8 THEN 'high'
        WHEN confidence >= 0.5 THEN 'medium'
        ELSE 'low'
    END as confidence_bucket,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence
FROM predictions
GROUP BY confidence_bucket;
```

### Model Comparison Framework

```python
def compare_models(model_v1, model_v2, test_data):
    """Compare two model versions"""
    results = {}
    
    for model_name, model in [('v1', model_v1), ('v2', model_v2)]:
        predictions = model.predict(test_data)
        results[model_name] = {
            'predictions': predictions,
            'metrics': calculate_metrics(predictions, test_data.labels)
        }
    
    return results
```

## RAG Evaluation

### Golden Q&A Dataset

A curated set of question-answer pairs with expected sources for evaluation.

**Format:**
```json
{
  "qa_pairs": [
    {
      "id": "qa_001",
      "question": "How does the ingestion service work?",
      "expected_answer_keywords": ["CSV", "validate", "Pydantic", "PostgreSQL", "idempotent"],
      "expected_sources": ["platform_docs.md", "Design_Doc.md"],
      "difficulty": "easy"
    },
    {
      "id": "qa_002",
      "question": "What happens when data validation fails?",
      "expected_answer_keywords": ["block", "quality report", "validation errors"],
      "expected_sources": ["platform_docs.md"],
      "difficulty": "medium"
    },
    {
      "id": "qa_003",
      "question": "How are predictions stored in the database?",
      "expected_answer_keywords": ["predictions table", "input_data", "confidence", "model_version"],
      "expected_sources": ["Design_Doc.md", "Architecture.md"],
      "difficulty": "medium"
    },
    {
      "id": "qa_004",
      "question": "What is the purpose of the kpi_daily view?",
      "expected_answer_keywords": ["curated", "aggregated", "KPI", "dashboard"],
      "expected_sources": ["Design_Doc.md"],
      "difficulty": "easy"
    },
    {
      "id": "qa_005",
      "question": "How does the RAG service ensure citation discipline?",
      "expected_answer_keywords": ["sources", "confidence threshold", "refuse", "low confidence"],
      "expected_sources": ["Design_Doc.md", "Architecture.md"],
      "difficulty": "hard"
    }
  ]
}
```

### RAG Metrics

#### 1. Retrieval Metrics

**Precision@K:**
```python
def precision_at_k(retrieved_docs, relevant_docs, k):
    """
    Calculate precision at k for retrieval
    """
    top_k = retrieved_docs[:k]
    relevant_retrieved = len(set(top_k) & set(relevant_docs))
    return relevant_retrieved / k if k > 0 else 0
```

**Recall@K:**
```python
def recall_at_k(retrieved_docs, relevant_docs, k):
    """
    Calculate recall at k for retrieval
    """
    top_k = retrieved_docs[:k]
    relevant_retrieved = len(set(top_k) & set(relevant_docs))
    return relevant_retrieved / len(relevant_docs) if len(relevant_docs) > 0 else 0
```

**Mean Reciprocal Rank (MRR):**
```python
def mean_reciprocal_rank(retrieved_docs_list, relevant_docs_list):
    """
    Calculate MRR across multiple queries
    """
    reciprocal_ranks = []
    for retrieved, relevant in zip(retrieved_docs_list, relevant_docs_list):
        for i, doc in enumerate(retrieved, 1):
            if doc in relevant:
                reciprocal_ranks.append(1.0 / i)
                break
        else:
            reciprocal_ranks.append(0.0)
    
    return sum(reciprocal_ranks) / len(reciprocal_ranks)
```

#### 2. Answer Quality Metrics

**Keyword Overlap:**
```python
def keyword_overlap(answer, expected_keywords):
    """
    Check if expected keywords appear in answer
    """
    answer_lower = answer.lower()
    found_keywords = [kw for kw in expected_keywords if kw.lower() in answer_lower]
    return len(found_keywords) / len(expected_keywords)
```

**Source Attribution:**
```python
def check_source_attribution(returned_sources, expected_sources):
    """
    Verify correct sources are returned
    """
    returned_names = [s['document'] for s in returned_sources]
    overlap = len(set(returned_names) & set(expected_sources))
    return overlap / len(expected_sources) if expected_sources else 0
```

**Confidence Calibration:**
```python
def confidence_calibration(predictions, ground_truth, num_bins=10):
    """
    Measure how well confidence scores match actual accuracy
    """
    bins = np.linspace(0, 1, num_bins + 1)
    bin_accuracies = []
    bin_confidences = []
    
    for i in range(num_bins):
        mask = (predictions['confidence'] >= bins[i]) & (predictions['confidence'] < bins[i+1])
        if mask.sum() > 0:
            bin_acc = (predictions[mask]['correct'] == ground_truth[mask]).mean()
            bin_conf = predictions[mask]['confidence'].mean()
            bin_accuracies.append(bin_acc)
            bin_confidences.append(bin_conf)
    
    return bin_accuracies, bin_confidences
```

### RAG Evaluation Script

```python
import json
import requests

def evaluate_rag(qa_dataset_path, rag_url="http://localhost:8001"):
    """
    Evaluate RAG system against golden Q&A dataset
    """
    with open(qa_dataset_path) as f:
        qa_data = json.load(f)
    
    results = []
    
    for qa in qa_data['qa_pairs']:
        # Get answer from RAG
        response = requests.post(
            f"{rag_url}/ask",
            json={"question": qa['question'], "top_k": 3}
        )
        
        if response.status_code == 200:
            rag_response = response.json()
            
            # Evaluate
            eval_result = {
                'id': qa['id'],
                'question': qa['question'],
                'difficulty': qa['difficulty'],
                'confidence': rag_response['confidence'],
                'keyword_overlap': keyword_overlap(
                    rag_response['answer'],
                    qa['expected_answer_keywords']
                ),
                'source_attribution': check_source_attribution(
                    rag_response['sources'],
                    qa['expected_sources']
                ),
                'returned_sources': [s['document'] for s in rag_response['sources']]
            }
            
            results.append(eval_result)
    
    # Aggregate metrics
    metrics = {
        'avg_confidence': sum(r['confidence'] for r in results) / len(results),
        'avg_keyword_overlap': sum(r['keyword_overlap'] for r in results) / len(results),
        'avg_source_attribution': sum(r['source_attribution'] for r in results) / len(results),
        'by_difficulty': {}
    }
    
    # Breakdown by difficulty
    for difficulty in ['easy', 'medium', 'hard']:
        difficulty_results = [r for r in results if r['difficulty'] == difficulty]
        if difficulty_results:
            metrics['by_difficulty'][difficulty] = {
                'count': len(difficulty_results),
                'avg_keyword_overlap': sum(r['keyword_overlap'] for r in difficulty_results) / len(difficulty_results),
                'avg_source_attribution': sum(r['source_attribution'] for r in difficulty_results) / len(difficulty_results)
            }
    
    return results, metrics

# Usage
results, metrics = evaluate_rag('data/rag_golden_qa.json')
print(json.dumps(metrics, indent=2))
```

## Data Quality Metrics

### Ingestion Quality

Automatically generated in quality reports:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "source": "data.csv",
  "total_records": 1000,
  "valid_records": 980,
  "invalid_records": 20,
  "data_quality_metrics": {
    "completeness": 0.98,
    "valid_percentage": 98.0,
    "mean_value": 1500.5,
    "min_value": 100.0,
    "max_value": 5000.0
  },
  "validation_errors": [
    {
      "row": 42,
      "error": "metric_name cannot be empty",
      "data": {"timestamp": "2024-01-01", "metric_name": "", "metric_value": "100"}
    }
  ]
}
```

### Dashboard KPI Metrics

```sql
-- Data freshness
SELECT 
    MAX(timestamp) as latest_timestamp,
    EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) / 3600 as hours_since_latest
FROM raw_data;

-- Data coverage
SELECT 
    metric_name,
    category,
    COUNT(DISTINCT DATE(timestamp)) as days_with_data,
    MIN(timestamp) as first_seen,
    MAX(timestamp) as last_seen
FROM raw_data
GROUP BY metric_name, category;

-- Data quality over time
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as record_count,
    COUNT(DISTINCT metric_name) as unique_metrics,
    AVG(metric_value) as avg_value,
    STDDEV(metric_value) as stddev_value
FROM raw_data
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

## Continuous Evaluation

### Automated Testing Schedule

1. **Daily:**
   - Run RAG evaluation on golden Q&A set
   - Check prediction service health
   - Monitor data quality metrics

2. **Weekly:**
   - Full model evaluation on test set
   - Error slice analysis
   - Performance degradation check

3. **Monthly:**
   - Update golden Q&A set
   - Review and update evaluation metrics
   - Generate comprehensive evaluation report

### Alerting Thresholds

```yaml
alerts:
  model_accuracy:
    warning: 0.85
    critical: 0.80
  
  rag_confidence:
    warning: 0.60
    critical: 0.50
  
  data_freshness_hours:
    warning: 24
    critical: 48
  
  ingestion_quality:
    warning: 0.90
    critical: 0.85
```

## Reporting

### Weekly Evaluation Report Template

```markdown
# FDE Platform Evaluation Report - Week of [DATE]

## Model Performance
- Accuracy: X.XX%
- Precision: X.XX%
- Recall: X.XX%
- F1 Score: X.XX%
- Total Predictions: XXXX

## RAG Performance
- Average Confidence: X.XX
- Keyword Overlap: XX%
- Source Attribution: XX%
- Total Questions: XXX

## Data Quality
- Ingestion Success Rate: XX%
- Data Freshness: X hours
- Records Ingested: XXXX

## Issues & Actions
1. [Issue description] - [Action taken]
2. [Issue description] - [Action taken]

## Trends
- [Observation about trends]
- [Recommendation]
```

## Future Enhancements

1. **A/B Testing Framework:** Compare model versions in production
2. **Human Feedback Loop:** Collect user ratings on predictions/answers
3. **Drift Detection:** Automated detection of data/concept drift
4. **Explainability:** SHAP/LIME for model interpretability
5. **Real-time Monitoring:** Prometheus + Grafana dashboards
