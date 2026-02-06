# FDE Platform - Runbook

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 5432, 8000, 8001, 8501 available

### Starting the Platform
```bash
cd /path/to/upskill-2-FDE
docker compose up --build
```

Wait for all services to become healthy (usually 1-2 minutes).

### Accessing Services
- **UI:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **RAG Docs:** http://localhost:8001/docs
- **PostgreSQL:** localhost:5432

### Stopping the Platform
```bash
docker compose down
```

To remove all data:
```bash
docker compose down -v
```

## Service Management

### Checking Service Status
```bash
docker compose ps
```

Expected output:
```
NAME                STATUS              PORTS
postgres            Up (healthy)        0.0.0.0:5432->5432/tcp
ingest              Up                  
api                 Up (healthy)        0.0.0.0:8000->8000/tcp
rag                 Up (healthy)        0.0.0.0:8001->8001/tcp
ui                  Up                  0.0.0.0:8501->8501/tcp
```

### Viewing Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f rag
docker compose logs -f ui
docker compose logs -f ingest
docker compose logs -f postgres
```

### Restarting a Service
```bash
docker compose restart api
docker compose restart rag
docker compose restart ui
```

### Rebuilding a Service
```bash
docker compose up --build api
docker compose up --build rag
```

## Common Operations

### Ingesting New Data

1. Place CSV file in the `data/` directory
2. Restart the ingest service:
```bash
docker compose restart ingest
```
3. Check logs:
```bash
docker compose logs ingest
```
4. Verify quality report:
```bash
ls -la data/reports/
cat data/reports/quality_report_*.json
```

### Accessing the Database

```bash
docker compose exec postgres psql -U fde_user -d fde_db
```

Common queries:
```sql
-- View raw data
SELECT * FROM raw_data ORDER BY timestamp DESC LIMIT 10;

-- View KPI aggregates
SELECT * FROM kpi_daily ORDER BY date DESC LIMIT 10;

-- View predictions
SELECT * FROM predictions ORDER BY created_at DESC LIMIT 10;

-- Check row counts
SELECT 'raw_data' as table_name, COUNT(*) FROM raw_data
UNION ALL
SELECT 'predictions', COUNT(*) FROM predictions;
```

### Adding Documentation for RAG

1. Create markdown or text files in `data/docs/`:
```bash
cat > data/docs/my_doc.md << EOF
# My Documentation
Content here...
EOF
```

2. Restart RAG service:
```bash
docker compose restart rag
```

3. Test in UI Copilot tab or via API:
```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What does my documentation say?"}'
```

### Running API Tests

```bash
# Enter API container
docker compose exec api bash

# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest test_api.py -v
```

## Troubleshooting

### Service Won't Start

**Symptom:** Service exits immediately or shows "unhealthy"

**Solutions:**
1. Check logs: `docker compose logs [service]`
2. Verify dependencies: `docker compose ps`
3. Check port conflicts: `netstat -an | grep [port]`
4. Rebuild: `docker compose up --build [service]`

### Database Connection Failures

**Symptom:** Services can't connect to PostgreSQL

**Solutions:**
1. Wait for PostgreSQL to become healthy:
   ```bash
   docker compose ps postgres
   ```
2. Check database is running:
   ```bash
   docker compose exec postgres pg_isready -U fde_user
   ```
3. Verify credentials in docker-compose.yml
4. Restart dependent services:
   ```bash
   docker compose restart api rag ui
   ```

### UI Can't Reach API/RAG

**Symptom:** UI shows connection errors

**Solutions:**
1. Verify API/RAG are healthy:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8001/health
   ```
2. Check from within UI container:
   ```bash
   docker compose exec ui curl http://api:8000/health
   docker compose exec ui curl http://rag:8001/health
   ```
3. Restart UI:
   ```bash
   docker compose restart ui
   ```

### RAG Returns Low Confidence Answers

**Symptom:** RAG refuses to answer most questions

**Solutions:**
1. Check documents are loaded:
   ```bash
   curl http://localhost:8001/health
   ```
   Verify `documents_loaded > 0`

2. Add more relevant documentation to `data/docs/`

3. Lower confidence threshold in UI or API call

4. Verify document content is relevant:
   ```bash
   ls -la data/docs/
   cat data/docs/*.md
   ```

### Ingest Service Not Processing Files

**Symptom:** CSV files in data/ directory not being ingested

**Solutions:**
1. Check ingest logs:
   ```bash
   docker compose logs ingest
   ```
2. Verify CSV format matches schema:
   - Required columns: timestamp, metric_name, metric_value
   - Optional columns: category, metadata

3. Check quality report for validation errors:
   ```bash
   cat data/reports/quality_report_*.json | jq .
   ```

4. Re-run ingest:
   ```bash
   docker compose restart ingest
   ```

### High Memory Usage

**Symptom:** System running slow, high memory consumption

**Solutions:**
1. Check container resource usage:
   ```bash
   docker stats
   ```
2. Reduce data volume in data/ directory
3. Clear old quality reports:
   ```bash
   rm data/reports/quality_report_*.json
   ```
4. Restart services:
   ```bash
   docker compose restart
   ```

### Port Already in Use

**Symptom:** "port is already allocated" error

**Solutions:**
1. Check what's using the port:
   ```bash
   lsof -i :8501  # UI
   lsof -i :8000  # API
   lsof -i :8001  # RAG
   lsof -i :5432  # PostgreSQL
   ```
2. Stop conflicting service or change port in docker-compose.yml
3. Restart:
   ```bash
   docker compose up
   ```

## Maintenance

### Backup Database

```bash
docker compose exec postgres pg_dump -U fde_user fde_db > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
cat backup_20240101.sql | docker compose exec -T postgres psql -U fde_user fde_db
```

### Clean Up Old Data

```bash
# Remove old quality reports (keep last 10)
ls -t data/reports/quality_report_*.json | tail -n +11 | xargs rm

# Clean old predictions (in PostgreSQL)
docker compose exec postgres psql -U fde_user -d fde_db -c "
DELETE FROM predictions WHERE created_at < NOW() - INTERVAL '30 days';
"
```

### Update Dependencies

1. Update requirements.txt in service directory
2. Rebuild service:
   ```bash
   docker compose up --build [service]
   ```

### View Resource Usage

```bash
# Real-time stats
docker stats

# Disk usage
docker system df
```

## Monitoring

### Health Check Endpoints

- API: `curl http://localhost:8000/health`
- RAG: `curl http://localhost:8001/health`

### Key Metrics to Monitor

1. **Service availability:** All services "healthy"
2. **Database connections:** All services can connect
3. **Ingestion quality:** Check quality_report completeness
4. **Prediction accuracy:** Monitor predictions table
5. **RAG confidence:** Track average confidence in answers
6. **Response times:** Monitor API endpoint latency

### Log Locations

All logs are available via Docker:
```bash
docker compose logs [service]
```

For persistent logging, configure volume mounts:
```yaml
volumes:
  - ./logs:/app/logs
```

## Emergency Procedures

### Complete Reset

```bash
# Stop all services
docker compose down -v

# Remove all data
rm -rf data/reports/*.json

# Start fresh
docker compose up --build
```

### Service Crash Recovery

```bash
# Identify crashed service
docker compose ps

# Check logs
docker compose logs [crashed-service]

# Restart
docker compose restart [crashed-service]

# If persistent, rebuild
docker compose up --build [crashed-service]
```

## Performance Tuning

### PostgreSQL
Edit docker-compose.yml to add:
```yaml
environment:
  POSTGRES_SHARED_BUFFERS: 256MB
  POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
```

### API Workers
Edit services/api/Dockerfile CMD:
```dockerfile
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### RAG Document Limit
For large document sets, consider pagination or external vector DB.

## Contact & Support

For issues, check:
1. This runbook
2. Service logs
3. GitHub repository issues
4. API documentation at /docs endpoints
