# FDE Platform - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FDE Platform                             │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Data       │
│   Sources    │
│ (CSV/API)    │
└──────┬───────┘
       │
       v
┌─────────────────┐
│     Ingest      │     ┌──────────────┐
│     Service     │────>│  PostgreSQL  │
│  - Validate     │     │              │
│  - Transform    │     │  - raw_data  │
│  - Reports      │     │  - predictions│
└─────────────────┘     │  - kpi_daily │
                        └──────┬───────┘
                               │
       ┌───────────────────────┼───────────────────────┐
       │                       │                       │
       v                       v                       v
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│   API       │        │    RAG      │        │     UI      │
│   Service   │        │   Service   │        │   Service   │
│             │        │             │        │             │
│ - /health   │        │ - /health   │        │ - Dashboard │
│ - /predict  │        │ - /ask      │        │ - Predict   │
│ - Logging   │        │ - Sources   │        │ - Copilot   │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘
       │                      │                       │
       │                      v                       │
       │              ┌──────────────┐                │
       │              │ /data/docs   │                │
       │              │              │                │
       │              │ - platform_  │                │
       │              │   docs.md    │                │
       │              └──────────────┘                │
       │                                              │
       └──────────────────────┬───────────────────────┘
                              │
                              v
                        ┌──────────┐
                        │  Users   │
                        │ (Browser)│
                        └──────────┘
```

## Component Details

### Ingest Service
- **Input:** CSV files, API endpoints
- **Processing:** Pydantic validation, data transformation
- **Output:** PostgreSQL writes, JSON quality reports
- **Idempotency:** ON CONFLICT handling for duplicate prevention

### API Service
- **Framework:** FastAPI (async REST API)
- **Models:** Rules-based (v1), sklearn-ready (v2)
- **Endpoints:**
  - GET /health: Service health status
  - POST /predict: ML predictions
  - GET /: API documentation
- **Database:** Reads/writes predictions table

### RAG Service
- **Framework:** FastAPI
- **Retrieval:** TF-IDF vectorization and cosine similarity
- **Documents:** Loaded from /data/docs directory
- **Endpoints:**
  - GET /health: Service health status
  - POST /ask: Q&A with sources
  - GET /: API documentation
- **Citation:** Always returns sources, refuses low-confidence answers

### UI Service
- **Framework:** Streamlit
- **Tabs:**
  1. **Dashboard:** KPI visualization from SQL views
  2. **Prediction:** Interactive ML prediction interface
  3. **Copilot:** RAG-powered Q&A interface
- **Communication:** HTTP requests to API and RAG services
- **Database:** Direct SQL queries for dashboard data

### PostgreSQL Database
- **Tables:**
  - `raw_data`: Timestamped metrics with categories
  - `predictions`: ML prediction history
- **Views:**
  - `kpi_daily`: Daily aggregated KPIs
  - `recent_predictions`: Latest 100 predictions
- **Indexes:** Optimized for timestamp, metric_name, category queries

## Data Flow Diagrams

### Ingestion Flow
```
CSV File → Read → Validate (Pydantic) → Transform
                      ↓
                   Valid? ───No──→ Quality Report (blocked)
                      ↓
                    Yes
                      ↓
            Write to PostgreSQL (idempotent)
                      ↓
            Generate Quality Report → /data/reports/
```

### Prediction Flow
```
User Input (UI) → API /predict → Model.predict()
                                      ↓
                            Save to predictions table
                                      ↓
                          Return prediction + confidence
                                      ↓
                            Display in UI
```

### RAG Flow
```
Question (UI) → RAG /ask → Load Documents
                               ↓
                    TF-IDF Vectorization
                               ↓
                    Cosine Similarity Search
                               ↓
                    Top-K Document Retrieval
                               ↓
                    Confidence Check
                               ↓
            High? ────No────→ Refuse to Answer
              ↓
            Yes
              ↓
      Generate Answer + Sources
              ↓
        Return to UI with Citations
```

## Technology Stack

### Languages & Frameworks
- Python 3.11
- FastAPI (API/RAG services)
- Streamlit (UI)
- PostgreSQL 15

### Key Libraries
- **Data Processing:** Pandas, NumPy
- **Validation:** Pydantic
- **ML/Retrieval:** scikit-learn
- **Database:** psycopg2
- **Visualization:** Plotly
- **HTTP:** Requests, Uvicorn

### Infrastructure
- Docker & Docker Compose
- PostgreSQL (persistent volume)

## Network Architecture

### Docker Network
All services run in a shared Docker network with the following connectivity:

```
postgres:5432  ←──┬─── ingest
               ├─── api
               └─── ui

api:8000       ←─── ui

rag:8001       ←─── ui

Host:8501      ←─── Browser (UI)
Host:8000      ←─── Browser (API docs)
Host:8001      ←─── Browser (RAG docs)
```

### Health Checks
- **API:** curl http://api:8000/health
- **RAG:** curl http://rag:8001/health
- **PostgreSQL:** pg_isready
- **UI:** Streamlit server running

## Deployment Architecture

### Local Development
```bash
docker compose up --build
```

### Service Dependencies
```
postgres (healthy) → ingest
postgres (healthy) → api
                     api (healthy) → ui
                     rag (healthy) → ui
                     postgres (healthy) → ui
```

### Volume Mounts
- `postgres_data`: PostgreSQL persistent storage
- `./data`: Shared data directory (CSV, reports, docs)
- `./sql`: Database initialization scripts

## Scalability Patterns

### Current (Single Instance)
- One container per service
- Shared PostgreSQL instance
- In-memory caching

### Future (Multi-Instance)
```
                    ┌─── API Pod 1
Load Balancer  ────┼─── API Pod 2
                    └─── API Pod 3
                           ↓
                    Redis Cache
                           ↓
                   PostgreSQL (RDS)
                           ↓
                    Read Replicas
```

## Security Architecture

### Network Security
- Services isolated in Docker network
- Only UI/API ports exposed to host
- Inter-service communication via internal DNS

### Data Security
- Environment variables for credentials
- No hardcoded secrets
- Parameterized SQL queries
- Input validation on all endpoints

### Future Enhancements
- TLS/HTTPS termination
- API authentication (JWT)
- Rate limiting
- Audit logging
