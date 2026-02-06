
# FDE Platform Documentation

## Overview
The FDE Platform is a comprehensive data engineering and machine learning system.

## Components

### Ingest Service
The ingest service loads data from CSV files or APIs, validates the schema using Pydantic,
writes to PostgreSQL database, and generates JSON quality reports.

Key features:
- Idempotent writes using ON CONFLICT
- Schema validation with Pydantic
- Quality report generation
- Blocks writes when required fields are missing

### API Service
The API service provides prediction endpoints using FastAPI.

Endpoints:
- /health: Health check endpoint
- /predict: Prediction endpoint with Pydantic validation

The service uses structured logging and includes basic tests.

### RAG Service
The RAG service provides retrieval-augmented generation using TF-IDF.
It always returns sources and refuses to answer when confidence is low.

### UI Service
The UI service is built with Streamlit and provides three tabs:
- Dashboard: Shows KPIs from curated SQL views
- Prediction: Calls the API /predict endpoint
- Copilot: Calls the RAG /ask endpoint and displays sources

## Database Schema
The system uses PostgreSQL with the following tables:
- raw_data: Stores ingested metrics
- predictions: Stores prediction results
- kpi_daily: Curated view for daily KPIs

## Running the Platform
Use Docker Compose to run the entire platform:
```
docker compose up --build
```

This will start all services: PostgreSQL, Ingest, API, RAG, and UI.
