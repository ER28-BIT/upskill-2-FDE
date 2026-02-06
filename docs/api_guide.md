# API Usage Guide

## Authentication

Currently, the API does not require authentication. In production, implement proper authentication and authorization.

## Creating Events

### Single Event Creation

```bash
curl -X POST "http://localhost:8000/events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "transaction",
    "customer_id": "CUST_0001",
    "value": 1500.50,
    "status": "success",
    "metadata": {"source": "web", "session_id": "abc123"}
  }'
```

### Batch Event Ingestion

```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "event_type": "login",
      "customer_id": "CUST_0001",
      "status": "success"
    },
    {
      "event_type": "transaction",
      "customer_id": "CUST_0001",
      "value": 250.00,
      "status": "success"
    }
  ]'
```

## Risk Prediction

### Predict Risk Score

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_0001",
    "event_type": "transaction",
    "value": 5000.00,
    "metadata": {"urgent": true}
  }'
```

Response:
```json
{
  "customer_id": "CUST_0001",
  "risk_score": 0.456,
  "risk_label": "medium",
  "factors": {
    "event_type_risk": 0.1,
    "failure_rate": 0.15,
    "value_anomaly": 0.18,
    "activity_frequency": 0.026
  }
}
```

## RAG Copilot

### Query the Copilot

```bash
curl -X POST "http://localhost:8000/copilot" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the supported event types?",
    "max_sources": 3
  }'
```

Response:
```json
{
  "answer": "Based on the available documentation:\n\nThe supported event types are...",
  "sources": [
    {
      "filename": "system_overview.md",
      "excerpt": "Supported Event Types include transaction, login, logout...",
      "confidence": 0.856
    }
  ],
  "confidence": 0.856,
  "has_sufficient_sources": true
}
```

### Index Documentation

```bash
curl -X POST "http://localhost:8000/copilot/index"
```

## Data Quality Reports

### Get Recent Reports

```bash
curl -X GET "http://localhost:8000/data-quality/reports?limit=5"
```

Response:
```json
[
  {
    "id": 1,
    "timestamp": "2024-01-15T10:30:00Z",
    "total_records": 100,
    "valid_records": 95,
    "invalid_records": 5,
    "quality_score": 0.95,
    "errors": ["Record 5: Missing required field: status"]
  }
]
```

## Filtering and Pagination

### Get Customer Events

```bash
curl -X GET "http://localhost:8000/events?customer_id=CUST_0001&limit=50"
```

### Get Paginated Events

```bash
curl -X GET "http://localhost:8000/events?skip=0&limit=100"
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message describing the issue"
}
```
