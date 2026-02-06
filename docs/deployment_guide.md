# Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- 2GB+ RAM available
- Ports 8000, 8501, and 5432 available

## Quick Start Deployment

### 1. Clone and Setup

```bash
git clone https://github.com/ER28-BIT/upskill-2-FDE.git
cd upskill-2-FDE
./setup.sh
```

### 2. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- FastAPI application (port 8000)
- Streamlit dashboard (port 8501)

### 3. Verify Services

Check service health:
```bash
docker-compose ps
```

All services should show "Up" status.

### 4. Initialize System

**Index documentation for RAG copilot:**
```bash
curl -X POST http://localhost:8000/copilot/index
```

**Ingest sample data:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H 'Content-Type: application/json' \
  -d @data/raw/sample_events.json
```

### 5. Access Services

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501

## Local Development

### Without Docker

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start PostgreSQL** (using system package manager or Docker):
```bash
docker run -d \
  --name fde_postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=fde_mvp \
  -p 5432:5432 \
  postgres:15
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your DATABASE_URL
```

4. **Run API:**
```bash
uvicorn src.api.main:app --reload
```

5. **Run Dashboard** (in another terminal):
```bash
streamlit run src/dashboard/app.py
```

## Production Deployment

### Environment Configuration

Create a production `.env` file:

```bash
# PostgreSQL Configuration
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=fde_mvp_prod

# Database URL
DATABASE_URL=postgresql://prod_user:<strong-password>@postgres:5432/fde_mvp_prod
```

### Security Hardening

1. **Change default passwords** in `.env`
2. **Enable HTTPS/TLS** using a reverse proxy (nginx, traefik)
3. **Add authentication** to FastAPI endpoints
4. **Restrict database access** to internal network only
5. **Enable firewall rules** for production environment

### Scaling Considerations

1. **Database:**
   - Use managed PostgreSQL service (AWS RDS, Azure Database, etc.)
   - Enable connection pooling (pgbouncer)
   - Set up read replicas for analytics queries

2. **API:**
   - Scale horizontally using container orchestration (Kubernetes, ECS)
   - Add load balancer in front of API instances
   - Implement rate limiting

3. **Dashboard:**
   - Cache database queries
   - Use connection pooling
   - Consider pre-computing metrics

### Monitoring

Add monitoring with:
- **Logs**: Use Docker logging driver or external service (ELK, Splunk)
- **Metrics**: Prometheus + Grafana
- **Alerts**: Set up alerts for:
  - API error rates
  - Database connection issues
  - High risk events
  - Data quality score drops

### Backup Strategy

1. **Database backups:**
```bash
# Daily backup
docker exec fde_postgres pg_dump -U user fde_mvp > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i fde_postgres psql -U user fde_mvp < backup_20240115.sql
```

2. **Document backups:**
   - Back up `docs/` directory regularly
   - Version control documentation changes

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs api
docker-compose logs dashboard
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker exec fde_postgres psql -U user -d fde_mvp -c "SELECT 1;"
```

### Port Conflicts

If ports are already in use, edit `docker-compose.yml`:

```yaml
services:
  api:
    ports:
      - "8080:8000"  # Changed from 8000:8000
  dashboard:
    ports:
      - "8502:8501"  # Changed from 8501:8501
```

### Reset System

To completely reset:

```bash
docker-compose down -v
docker-compose up -d
# Re-run setup
./setup.sh
```

## Performance Tuning

### Database

Adjust PostgreSQL settings in `docker-compose.yml`:

```yaml
postgres:
  environment:
    POSTGRES_SHARED_BUFFERS: 256MB
    POSTGRES_MAX_CONNECTIONS: 100
    POSTGRES_WORK_MEM: 4MB
```

### API

Set workers in `docker-compose.yml`:

```yaml
api:
  command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Dashboard

Enable caching in Streamlit by ensuring `@st.cache_resource` decorators are used.

## Maintenance

### Update System

```bash
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

### Clean Up Old Data

```sql
-- Delete events older than 90 days
DELETE FROM events WHERE timestamp < NOW() - INTERVAL '90 days';

-- Vacuum database
VACUUM ANALYZE;
```

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review documentation in `docs/`
- Open GitHub issue
