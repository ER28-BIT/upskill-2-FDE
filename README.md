# FDE MVP: Forward Deployed Engineer MVP System

A 6 week applied AI course designed to help guide SWE careers towards Forward Deployed Eng roles.

## Overview

This is a comprehensive end-to-end system that delivers:

1. **Data Ingestion Pipeline**: Ingests operational/customer event data into PostgreSQL with validation and data quality reporting
2. **KPI Dashboard**: Streamlit dashboard serving curated KPIs via SQL views
3. **Risk Prediction API**: FastAPI endpoint returning risk scores and labels based on customer event analysis
4. **RAG Copilot**: FastAPI RAG (Retrieval-Augmented Generation) copilot that answers questions using local documentation with strict citations and refusal rules

## Architecture

```
┌─────────────────┐     ┌──────────────────┐
│  Data Sources   │────▶│  Data Ingestion  │
└─────────────────┘     │   & Validation   │
                        └──────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   PostgreSQL DB  │
                        │  + SQL Views     │
                        └──────────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
         ┌───────────┐  ┌───────────┐  ┌───────────┐
         │  FastAPI  │  │ Streamlit │  │    RAG    │
         │   Risk    │  │    KPI    │  │  Copilot  │
         │  Predict  │  │ Dashboard │  │           │
         └───────────┘  └───────────┘  └───────────┘
```

## Features

### 1. Data Ingestion & Validation
- Schema validation for all incoming events
- Data quality scoring and reporting
- Support for multiple event types (transaction, login, error, etc.)
- Batch ingestion with detailed error tracking
- CSV and JSON import support

### 2. KPI Dashboard
Five comprehensive analytics views:
- **Daily Metrics**: Event counts, success rates, active customers
- **Customer Activity**: Engagement patterns and behavior analysis
- **Risk Analysis**: High-risk customer identification
- **Event Summary**: Event type distribution and trends
- **Data Quality**: Validation metrics and quality scores

### 3. Risk Prediction
Machine learning-based risk scoring considering:
- Event type risk profiles
- Historical failure rates
- Transaction value anomalies
- Activity frequency patterns

Risk labels: `low`, `medium`, `high`

### 4. RAG Copilot
Intelligent document Q&A system featuring:
- Semantic search over local documentation
- Source citation for every answer
- Confidence scoring
- Automatic refusal when sources are insufficient
- ChromaDB vector storage

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL (if not using Docker)

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/ER28-BIT/upskill-2-FDE.git
cd upskill-2-FDE
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the services**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501

### Local Development

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up PostgreSQL**
```bash
# Install and start PostgreSQL
# Create database: fde_mvp
```

3. **Configure environment**
```bash
cp .env.example .env
# Update DATABASE_URL in .env
```

4. **Run the API**
```bash
python -m uvicorn src.api.main:app --reload
```

5. **Run the Dashboard** (in a new terminal)
```bash
streamlit run src/dashboard/app.py
```

## Usage

### Generate Sample Data

```bash
python scripts/generate_sample_data.py
```

### Ingest Sample Data

```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d @data/raw/sample_events.json
```

### Index Documentation for RAG Copilot

```bash
curl -X POST "http://localhost:8000/copilot/index"
```

### Query the API

**Create an Event:**
```bash
curl -X POST "http://localhost:8000/events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "transaction",
    "customer_id": "CUST_0001",
    "value": 1500.50,
    "status": "success"
  }'
```

**Get Risk Prediction:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_0001",
    "event_type": "transaction",
    "value": 5000.00
  }'
```

**Ask the Copilot:**
```bash
curl -X POST "http://localhost:8000/copilot" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the supported event types?",
    "max_sources": 3
  }'
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

See [docs/api_guide.md](docs/api_guide.md) for detailed API usage examples.

## Project Structure

```
upskill-2-FDE/
├── src/
│   ├── api/              # FastAPI application
│   │   ├── main.py       # Main API application
│   │   └── rag_copilot.py # RAG copilot implementation
│   ├── dashboard/        # Streamlit dashboard
│   │   └── app.py
│   ├── database/         # Database configuration
│   │   ├── connection.py
│   │   └── views.py      # SQL views for KPIs
│   ├── ingestion/        # Data ingestion pipeline
│   │   └── data_pipeline.py
│   └── models/           # Data models
│       ├── api_models.py      # Pydantic models
│       ├── database_models.py # SQLAlchemy models
│       └── risk_model.py      # Risk prediction model
├── docs/                 # Documentation
├── data/                 # Data storage
│   ├── raw/             # Raw data files
│   └── processed/       # Processed data
├── scripts/             # Utility scripts
├── tests/               # Test files
├── docker-compose.yml   # Docker composition
├── Dockerfile          # Docker image definition
└── requirements.txt    # Python dependencies
```

## Technologies

- **FastAPI**: High-performance API framework
- **Streamlit**: Interactive dashboard
- **PostgreSQL**: Relational database
- **SQLAlchemy**: ORM and database toolkit
- **ChromaDB**: Vector database for RAG
- **Sentence Transformers**: Embedding model
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualizations
- **Docker**: Containerization

## Development

### Running Tests
```bash
pytest tests/
```

### Adding Documentation
1. Add markdown files to `docs/` directory
2. Re-index the copilot: `curl -X POST "http://localhost:8000/copilot/index"`

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Deployment

### Production Considerations

1. **Security**
   - Add authentication/authorization
   - Use secure password for PostgreSQL
   - Enable HTTPS/TLS
   - Implement rate limiting

2. **Scalability**
   - Use connection pooling
   - Add caching layer (Redis)
   - Consider read replicas for analytics

3. **Monitoring**
   - Add logging and metrics
   - Set up alerts for failures
   - Monitor API performance

4. **Backup**
   - Regular database backups
   - Document backup/restore procedures

## Documentation

- [System Overview](docs/system_overview.md)
- [API Guide](docs/api_guide.md)

## License

See [LICENSE](LICENSE) file for details.

## Support

For questions or issues, please open an issue on GitHub.
