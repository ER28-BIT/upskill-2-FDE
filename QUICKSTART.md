# Quick Start Guide

Get up and running with the FDE MVP in under 5 minutes!

## Prerequisites Check

```bash
# Verify Docker is installed
docker --version
docker-compose --version

# Verify ports are available
lsof -i :8000 -i :8501 -i :5432
# Should show no results
```

## 5-Minute Setup

### Step 1: Clone and Setup (30 seconds)
```bash
git clone <YOUR_REPO_URL>
cd upskill-2-FDE
./setup.sh
```

### Step 2: Start Services (1 minute)
```bash
docker-compose up -d
```

Wait for services to be ready (~60 seconds).

### Step 3: Initialize System (30 seconds)
```bash
# Index documentation for RAG
curl -X POST http://localhost:8000/copilot/index

# Ingest sample data
curl -X POST http://localhost:8000/ingest \
  -H 'Content-Type: application/json' \
  -d @data/raw/sample_events.json
```

### Step 4: Access Services (immediate)
- **API**: http://localhost:8000
- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## Quick Test

### Test the API
```bash
# Create an event
curl -X POST http://localhost:8000/events \
  -H 'Content-Type: application/json' \
  -d '{
    "event_type": "transaction",
    "customer_id": "CUST_TEST_001",
    "value": 1500.00,
    "status": "success"
  }'

# Get risk prediction
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": "CUST_TEST_001",
    "event_type": "transaction",
    "value": 5000.00
  }'

# Ask the copilot
curl -X POST http://localhost:8000/copilot \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "What are the supported event types?",
    "max_sources": 3
  }'
```

### View the Dashboard
Open http://localhost:8501 in your browser to see:
- Daily metrics and trends
- Customer activity analysis
- Risk analysis visualizations
- Event summaries
- Data quality monitoring

## Common Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Run tests
python -m pytest tests/ -v

# Use Makefile shortcuts
make start    # Start all services
make stop     # Stop all services
make logs     # View logs
make ingest   # Ingest sample data
make index    # Index documentation
```

## Troubleshooting

### Service won't start
```bash
docker-compose down -v
docker-compose up -d
```

### Port conflicts
Edit `docker-compose.yml` and change port mappings.

### Can't connect to API
```bash
# Check if services are running
docker-compose ps

# Check logs for errors
docker-compose logs api
```

## Next Steps

1. **Explore the Dashboard** - See visualizations at http://localhost:8501
2. **Try the API** - Interactive docs at http://localhost:8000/docs
3. **Read the Docs** - See `docs/` directory for detailed guides
4. **Run Examples** - Try `python examples/api_usage_example.py`

## Need Help?

- 📖 Full Documentation: [README.md](README.md)
- 🚀 Deployment Guide: [docs/deployment_guide.md](docs/deployment_guide.md)
- 🔌 API Guide: [docs/api_guide.md](docs/api_guide.md)
- 📊 System Overview: [docs/system_overview.md](docs/system_overview.md)

Enjoy your FDE MVP! 🎉
