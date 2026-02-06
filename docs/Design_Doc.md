# FDE Platform - Design Document

## Executive Summary
The FDE (Forward Deployed Engineering) Platform is a comprehensive data engineering and machine learning system designed for end-to-end data processing, prediction, and intelligent question-answering capabilities.

## System Architecture

### Core Components

#### 1. Ingest Service
**Purpose:** Load, validate, and store data from multiple sources

**Features:**
- CSV and API data loading support
- Pydantic-based schema validation
- Idempotent writes to PostgreSQL (ON CONFLICT handling)
- JSON quality report generation
- Automatic blocking of writes when required fields are missing

**Technology Stack:** Python, Pandas, Pydantic, PostgreSQL

#### 2. API Service
**Purpose:** Provide prediction capabilities via REST API

**Features:**
- FastAPI-based REST API
- `/health` endpoint for service monitoring
- `/predict` endpoint for ML predictions
- Pydantic validation for all inputs/outputs
- Structured logging
- Rules-based model with sklearn extensibility
- Prediction history stored in database

**Technology Stack:** FastAPI, Pydantic, scikit-learn, PostgreSQL

#### 3. RAG Service
**Purpose:** Retrieval-Augmented Generation for documentation Q&A

**Features:**
- TF-IDF/BM25 document retrieval
- `/ask` endpoint for natural language questions
- Always returns sources with answers
- Citation discipline (refuses low-confidence answers)
- Configurable confidence thresholds
- LLM provider interface (extensible)

**Technology Stack:** FastAPI, scikit-learn (TF-IDF), Python

#### 4. UI Service
**Purpose:** Interactive web interface for all platform capabilities

**Features:**
- **Dashboard Tab:** Real-time KPI visualization from curated SQL views
- **Prediction Tab:** Interactive prediction interface
- **Copilot Tab:** AI-powered Q&A with source citations
- Service health monitoring
- Interactive visualizations with Plotly

**Technology Stack:** Streamlit, Pandas, Plotly, Requests

#### 5. Database (PostgreSQL)
**Purpose:** Centralized data storage and curated views

**Schema:**
- `raw_data`: Stores ingested metrics with metadata
- `predictions`: Stores prediction history
- `kpi_daily`: Curated view for daily KPI aggregations

## Design Principles

### 1. Idempotency
All write operations are idempotent, using ON CONFLICT handling to prevent duplicates.

### 2. Validation First
All data is validated using Pydantic schemas before processing or storage.

### 3. Observability
Structured logging throughout all services for debugging and monitoring.

### 4. Citation Discipline
RAG service always provides sources and refuses to answer when confidence is insufficient.

### 5. Separation of Concerns
Each service has a single, well-defined responsibility.

### 6. Curated Views
Dashboard reads only from pre-aggregated SQL views, not ad-hoc Python aggregations.

## Data Flow

1. **Ingestion Flow:**
   CSV/API → Schema Validation → PostgreSQL → Quality Report

2. **Prediction Flow:**
   UI → API Service → Model → PostgreSQL → UI

3. **RAG Flow:**
   UI → RAG Service → Document Retrieval → Answer Generation → UI

## Deployment

### Docker Compose
All services are containerized and orchestrated via Docker Compose:
```bash
docker compose up --build
```

### Service Ports
- PostgreSQL: 5432
- API: 8000
- RAG: 8001
- UI: 8501

### Health Checks
All services implement health check endpoints for monitoring.

## Scalability Considerations

### Current Implementation
- Single instance per service
- PostgreSQL with connection pooling
- In-memory document indexing

### Future Enhancements
- Horizontal scaling with load balancers
- Redis caching layer
- Vector database for RAG (e.g., Pinecone, Weaviate)
- Model serving with dedicated inference servers
- Message queue for asynchronous processing

## Testing Strategy

### Unit Tests
- API service: pytest with TestClient
- Input validation tests
- Model prediction tests

### Integration Tests
- End-to-end service communication
- Database operations
- Docker Compose smoke tests

### Evaluation
- Model metrics: accuracy, precision, recall
- RAG evaluation: golden Q&A set with retrieval metrics
- Error slice analysis

## Security Considerations

1. **Environment Variables:** Sensitive credentials stored in environment variables
2. **Input Validation:** All inputs validated with Pydantic
3. **SQL Injection Prevention:** Parameterized queries throughout
4. **CORS:** Configurable CORS policies for API services
5. **Network Isolation:** Services communicate via internal Docker network

## Monitoring & Observability

1. **Structured Logging:** JSON-formatted logs with timestamps
2. **Health Endpoints:** `/health` on all services
3. **Quality Reports:** Ingestion quality metrics in JSON
4. **Database Views:** Pre-aggregated KPIs for dashboard

## Known Limitations

1. In-memory document indexing (not suitable for large doc sets)
2. Synchronous request handling (no async workers)
3. Simple rules-based model (placeholder for ML)
4. No authentication/authorization
5. No rate limiting

## Future Roadmap

1. **ML Model Training:** Implement sklearn model training pipeline
2. **Model Registry:** MLflow or similar for model versioning
3. **Advanced RAG:** LLM integration for better answer generation
4. **Authentication:** OAuth2/JWT for secure access
5. **Monitoring:** Prometheus + Grafana dashboards
6. **CI/CD:** Automated testing and deployment pipelines
