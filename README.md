# FDE Platform - Full-Stack Data Engineering & ML System

A comprehensive data engineering and machine learning platform designed for end-to-end data processing, predictions, and intelligent question-answering.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 5432, 8000, 8001, 8501 available

### Running the Platform

```bash
# Clone the repository
git clone <repository-url>
cd upskill-2-FDE

# Start all services
docker compose up --build
```

Wait for all services to become healthy (1-2 minutes), then access:
- **UI Dashboard:** http://localhost:8501
- **API Documentation:** http://localhost:8000/docs
- **RAG Documentation:** http://localhost:8001/docs

## 🏗️ Architecture

The platform consists of 5 main services:

### 1. **Ingest Service**
- Loads CSV/API data
- Validates schema with Pydantic
- Writes to PostgreSQL (idempotent)
- Generates JSON quality reports

### 2. **API Service** (FastAPI)
- `/health` - Health check endpoint
- `/predict` - ML prediction endpoint
- Pydantic validation
- Structured logging
- Basic test coverage

### 3. **RAG Service** (Retrieval-Augmented Generation)
- `/ask` - Q&A endpoint with sources
- TF-IDF document retrieval
- Citation discipline (refuses low-confidence answers)
- Always returns sources

### 4. **UI Service** (Streamlit)
- **Dashboard Tab:** KPI visualization from curated SQL views
- **Prediction Tab:** Interactive ML predictions
- **Copilot Tab:** AI-powered Q&A with sources

### 5. **PostgreSQL Database**
- `raw_data` table: Ingested metrics
- `predictions` table: Prediction history
- `kpi_daily` view: Curated daily KPIs

## 📊 Key Features

✅ **Idempotent Ingestion** - No duplicate data, ON CONFLICT handling
✅ **Schema Validation** - Pydantic models throughout
✅ **Quality Reports** - JSON reports for every ingestion
✅ **Citation Discipline** - RAG always provides sources
✅ **Curated Views** - Dashboard reads from SQL views, not ad-hoc aggregations
✅ **Structured Logging** - Observability across all services
✅ **Health Checks** - All services have /health endpoints
✅ **Docker Compose** - Single command deployment

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Design_Doc.md](docs/Design_Doc.md)** - System architecture and design principles (1-2 pages)
- **[Architecture.md](docs/Architecture.md)** - Detailed component diagrams and data flows
- **[Runbook.md](docs/Runbook.md)** - Operations guide and troubleshooting
- **[Evaluation_Pack.md](docs/Evaluation_Pack.md)** - Model metrics and RAG evaluation
- **[Rollout_Plan.md](docs/Rollout_Plan.md)** - Phased deployment strategy
- **[Demo_Script.md](docs/Demo_Script.md)** - Step-by-step demo guide

## 🔧 Usage Examples

### Ingesting Data

Place CSV files in the `data/` directory with the following schema:
```csv
timestamp,metric_name,metric_value,category
2024-01-01 00:00:00,revenue,1000,product_a
2024-01-01 01:00:00,users,50,web
```

Restart the ingest service:
```bash
docker compose restart ingest
```

Quality reports are generated in `data/reports/`.

### Making Predictions

**Via UI:**
1. Navigate to http://localhost:8501
2. Click "Prediction" tab
3. Enter feature values
4. Click "Make Prediction"

**Via API:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"feature1": 1.5, "feature2": 2.3, "feature3": 0.8}}'
```

### Asking Questions (RAG)

**Via UI:**
1. Navigate to http://localhost:8501
2. Click "Copilot" tab
3. Enter your question
4. View answer with sources

**Via API:**
```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How does the ingestion service work?", "top_k": 3}'
```

## 🧪 Testing

### Running API Tests

```bash
# Enter API container
docker compose exec api bash

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest test_api.py -v
```

### Evaluation Framework

The platform includes evaluation tools for:
- **Model metrics:** Accuracy, precision, recall, F1
- **RAG evaluation:** Golden Q&A set with retrieval metrics
- **Error analysis:** Confidence slicing, feature range analysis

See [Evaluation_Pack.md](docs/Evaluation_Pack.md) for details.

## 🗄️ Database Access

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U fde_user -d fde_db

# Example queries
SELECT * FROM raw_data LIMIT 10;
SELECT * FROM kpi_daily ORDER BY date DESC LIMIT 10;
SELECT * FROM predictions ORDER BY created_at DESC LIMIT 10;
```

## 📈 Monitoring

### Service Health

```bash
# Check all services
docker compose ps

# API health
curl http://localhost:8000/health

# RAG health
curl http://localhost:8001/health
```

### Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f rag
docker compose logs -f ingest
```

## 🔮 Future Enhancements

### Planned Features
- Trainable sklearn model pipeline with MLflow
- LLM integration for RAG (GPT-4, Claude)
- Vector database for better retrieval (Pinecone, Weaviate)
- Authentication and authorization (OAuth2/JWT)
- Kubernetes deployment
- Prometheus + Grafana monitoring
- CI/CD pipeline

## 🛠️ Technology Stack

- **Languages:** Python 3.11
- **Web Frameworks:** FastAPI, Streamlit
- **Database:** PostgreSQL 15
- **ML/Retrieval:** scikit-learn (TF-IDF, models)
- **Validation:** Pydantic
- **Visualization:** Plotly
- **Containerization:** Docker, Docker Compose

## 📝 Requirements Met

✅ **"docker compose up --build" runs locally**
✅ **Ingestion is idempotent** (ON CONFLICT handling)
✅ **Blocks writes when required fields are missing** (Pydantic validation)
✅ **KPI dashboard reads from curated SQL views** (kpi_daily view)
✅ **API uses Pydantic validation** (all endpoints)
✅ **Structured logging** (all services)
✅ **Basic tests** (API service)
✅ **RAG always returns sources** (citation discipline)
✅ **RAG refuses low confidence** ("I don't have enough supporting documentation...")
✅ **Evaluation harness** (model metrics + RAG golden Q&A)
✅ **Complete documentation** (Design Doc, Architecture, Runbook, Rollout, Demo)

## 🤝 Contributing

This is a reference implementation for the Forward Deployed Engineering upskill course. See the individual service directories for code structure.

## 📄 License

See [LICENSE](LICENSE) file for details.

---

**Built as part of the 6-week applied AI course for Forward Deployed Engineering roles.** 
