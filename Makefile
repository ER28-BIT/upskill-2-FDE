.PHONY: help setup start stop restart logs test clean docs ingest index

help:
	@echo "FDE MVP - Available Commands"
	@echo "============================"
	@echo "setup      - Run setup script and generate sample data"
	@echo "start      - Start all services with Docker Compose"
	@echo "stop       - Stop all services"
	@echo "restart    - Restart all services"
	@echo "logs       - Show logs from all services"
	@echo "test       - Run tests"
	@echo "clean      - Clean up containers and volumes"
	@echo "ingest     - Ingest sample data into the system"
	@echo "index      - Index documentation for RAG copilot"
	@echo "docs       - Open API documentation in browser"

setup:
	@./setup.sh

start:
	@docker-compose up -d
	@echo "Services started!"
	@echo "API: http://localhost:8000"
	@echo "Dashboard: http://localhost:8501"
	@echo "API Docs: http://localhost:8000/docs"

stop:
	@docker-compose down

restart:
	@docker-compose restart

logs:
	@docker-compose logs -f

test:
	@python -m pytest tests/ -v

clean:
	@docker-compose down -v
	@echo "All containers and volumes removed"

ingest:
	@echo "Ingesting sample data..."
	@curl -X POST http://localhost:8000/ingest \
		-H 'Content-Type: application/json' \
		-d @data/raw/sample_events.json

index:
	@echo "Indexing documentation..."
	@curl -X POST http://localhost:8000/copilot/index

docs:
	@echo "Opening API documentation..."
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || echo "Please open http://localhost:8000/docs in your browser"
