# FDE MVP System Overview

## Introduction

The Forward Deployed Engineer MVP is an end-to-end system designed for operational data analysis, risk prediction, and intelligent documentation assistance.

## System Components

### 1. Data Ingestion Pipeline

The data ingestion pipeline processes operational and customer event data with the following features:

- **Validation**: All incoming events are validated against a schema
- **Data Quality Reporting**: Each ingestion batch generates a quality report
- **Error Tracking**: Invalid records are logged with specific error messages
- **Metrics**: Track total records, valid records, invalid records, and quality scores

#### Supported Event Types
- `transaction`: Financial transactions
- `login`: User login events
- `logout`: User logout events
- `error`: System errors
- `warning`: Warning messages
- `info`: Informational events

#### Event Status Values
- `success`: Event completed successfully
- `failed`: Event failed
- `pending`: Event is pending
- `cancelled`: Event was cancelled

### 2. KPI Dashboard

The Streamlit dashboard provides real-time visualization of key performance indicators:

#### Available KPI Views
1. **Daily Metrics**: Track daily event counts, success rates, and active customers
2. **Customer Activity**: Analyze customer engagement and behavior patterns
3. **Risk Analysis**: Monitor high-risk customers and risk score distributions
4. **Event Summary**: View event type distributions and trends
5. **Data Quality**: Monitor data quality scores and validation metrics

### 3. Risk Prediction API

The risk prediction endpoint calculates risk scores based on multiple factors:

#### Risk Factors
- **Event Type Risk**: Different event types have different inherent risk levels
- **Failure Rate**: Historical failure rate for the customer
- **Value Anomaly**: Deviation from customer's typical transaction values
- **Activity Frequency**: Recent activity patterns

#### Risk Labels
- `low`: Risk score < 0.3
- `medium`: Risk score 0.3 - 0.7
- `high`: Risk score > 0.7

### 4. RAG Copilot

The Retrieval-Augmented Generation copilot answers questions using local documentation:

#### Features
- **Document Indexing**: Automatically indexes markdown files from the docs directory
- **Semantic Search**: Uses sentence transformers for intelligent document retrieval
- **Citation**: Provides source citations for all answers
- **Confidence Scoring**: Includes confidence scores for answers
- **Refusal Rule**: Returns "insufficient information" message when confidence is low

#### Usage Guidelines
- Ask specific questions about the system or processes
- The copilot will search indexed documentation
- Always check the provided sources for verification
- If confidence is low, consult full documentation or experts

## API Endpoints

### Event Management
- `POST /events`: Create a new event
- `GET /events`: List events with optional filtering
- `GET /events/{id}`: Get specific event details

### Data Ingestion
- `POST /ingest`: Ingest batch of events with validation
- `GET /data-quality/reports`: Get data quality reports

### Risk Prediction
- `POST /predict`: Predict risk score for a customer event

### RAG Copilot
- `POST /copilot`: Query the copilot with a question
- `POST /copilot/index`: Index documentation files
- `POST /copilot/reset`: Reset the document collection

## Best Practices

### Data Ingestion
1. Always validate data before ingestion
2. Review data quality reports regularly
3. Address validation errors promptly
4. Monitor quality score trends

### Risk Management
1. Review high-risk customers daily
2. Investigate sudden risk score changes
3. Combine risk scores with other metrics
4. Set up alerts for high-risk events

### Dashboard Usage
1. Refresh data regularly during active periods
2. Monitor success rates and failure trends
3. Track customer activity patterns
4. Use visualizations to identify anomalies

### Copilot Usage
1. Keep documentation up to date
2. Re-index after documentation changes
3. Ask specific, focused questions
4. Verify answers with source citations
5. Don't rely solely on copilot for critical decisions
