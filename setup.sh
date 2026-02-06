#!/bin/bash
# Setup script for FDE MVP

set -e

echo "=================================================="
echo "FDE MVP Setup Script"
echo "=================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your configuration if needed"
fi

# Generate sample data
echo ""
echo "Generating sample data..."
python scripts/generate_sample_data.py

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "To start the system with Docker:"
echo "  docker-compose up -d"
echo ""
echo "To access the services:"
echo "  API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Dashboard: http://localhost:8501"
echo ""
echo "To ingest sample data:"
echo "  curl -X POST http://localhost:8000/ingest \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d @data/raw/sample_events.json"
echo ""
echo "To index documentation for RAG:"
echo "  curl -X POST http://localhost:8000/copilot/index"
echo ""
