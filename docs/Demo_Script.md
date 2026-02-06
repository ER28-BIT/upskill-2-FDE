# FDE Platform - Demo Script

## Overview
This script guides you through a complete demonstration of the FDE Platform, showcasing all major features and capabilities.

**Duration:** 15-20 minutes
**Audience:** Technical and non-technical stakeholders

---

## Pre-Demo Setup

### Prerequisites
1. Ensure Docker and Docker Compose are installed
2. Clone the repository
3. Have a terminal and web browser ready
4. Port 8501, 8000, 8001, 5432 available

### Setup (5 minutes before demo)
```bash
cd /path/to/upskill-2-FDE
docker compose up --build
```

Wait for all services to become healthy. You'll see:
```
postgres    | database system is ready to accept connections
api         | Uvicorn running on http://0.0.0.0:8000
rag         | Uvicorn running on http://0.0.0.0:8001
ui          | You can now view your Streamlit app in your browser
```

---

## Demo Script

### Part 1: Platform Introduction (2 minutes)

**Say:**
> "Today I'll demonstrate the FDE Platform, a comprehensive data engineering and machine learning system designed for end-to-end data processing, intelligent predictions, and AI-powered question answering."

**Show:**
1. Open terminal showing docker compose output
2. Point out the 5 services running:
   - PostgreSQL database
   - Ingest service
   - API service
   - RAG service
   - UI service

**Say:**
> "The platform is containerized using Docker, making it portable and easy to deploy. Everything runs locally with a single command: 'docker compose up --build'"

---

### Part 2: System Architecture (2 minutes)

**Show:** Open `docs/Architecture.md` or draw on whiteboard

**Explain:**
1. **Data Flow:**
   - CSV/API → Ingest Service → PostgreSQL
   - PostgreSQL → API Service → Predictions
   - Documents → RAG Service → Answers with Sources
   - All services → UI for visualization

2. **Key Design Principles:**
   - Idempotent data ingestion
   - Schema validation with Pydantic
   - Citation discipline in RAG
   - Curated SQL views for dashboard

**Say:**
> "Each service is independently deployable and communicates via REST APIs. The PostgreSQL database serves as the central data store with curated views for efficient querying."

---

### Part 3: Data Ingestion (3 minutes)

**Show:** Terminal with ingest logs

**Say:**
> "Let's start with data ingestion. The ingest service automatically loads CSV files, validates the schema, and writes to PostgreSQL."

**Demo:**
```bash
# Show ingest logs
docker compose logs ingest | tail -20
```

**Point out:**
1. Sample data was automatically created (if no CSV found)
2. 100 records ingested
3. Quality report generated

**Show:** Quality report
```bash
cat data/reports/quality_report_*.json | jq .
```

**Explain the report:**
- Total records processed
- Valid vs invalid counts
- Validation errors (if any)
- Data quality metrics (mean, min, max)

**Say:**
> "Notice the quality report shows 100% completeness. If there were validation errors, the system would block the write and report the issues. This ensures data integrity."

---

### Part 4: Dashboard - KPI Visualization (3 minutes)

**Show:** Open browser to http://localhost:8501

**Say:**
> "Now let's look at the user interface. We have three tabs: Dashboard, Prediction, and Copilot."

**Demo Dashboard Tab:**

1. **Click "Load KPI Data"**
   - Wait for data to load
   - Point out: 100 records loaded

2. **Show Summary Metrics:**
   - Total records
   - Unique metrics (revenue, users)
   - Categories (product_a, product_b, web, mobile)
   - Latest date

3. **Interact with Filters:**
   - Select "revenue" metric
   - Show trend chart updating
   - Select "product_a" category
   - Show filtered data

4. **Explain Visualizations:**
   - Line chart: Average value over time
   - Bar chart: Total value by category
   - Data table: Detailed records

**Say:**
> "The dashboard reads directly from curated SQL views in PostgreSQL. This ensures fast queries and consistent calculations. No ad-hoc Python aggregations means better performance and reliability."

---

### Part 5: Prediction Service (3 minutes)

**Show:** Click on "Prediction" tab

**Say:**
> "The prediction service provides machine learning capabilities via a REST API. Currently using a rules-based model, but it's designed to support trainable sklearn models."

**Demo:**

1. **Set up features:**
   - Keep default 3 features
   - feature1: 2.5
   - feature2: 3.0
   - feature3: 1.5

2. **Click "Make Prediction"**

3. **Show results:**
   - Prediction value: ~2.33 (average of features)
   - Label: "medium" (based on prediction range)
   - Confidence: ~0.95

4. **Explain:**
   > "The model takes feature inputs, makes a prediction, and returns it with a confidence score. The prediction is also saved to the database for tracking and analysis."

5. **Try different values:**
   - Change feature1 to 5.0
   - Show prediction increases to "high"

6. **Show API documentation:**
   - Open new tab: http://localhost:8000/docs
   - Show Swagger UI
   - Point out /health and /predict endpoints
   - Show Pydantic validation schemas

**Say:**
> "The API uses FastAPI with automatic OpenAPI documentation. All inputs and outputs are validated using Pydantic schemas, ensuring type safety and data quality."

---

### Part 6: RAG Copilot (4 minutes)

**Show:** Click on "Copilot" tab

**Say:**
> "The Copilot feature uses Retrieval-Augmented Generation to answer questions about the platform. It searches documentation and always provides sources."

**Demo - Question 1 (Easy):**

1. **Ask:** "How does the ingestion service work?"

2. **Click "Ask"**

3. **Show results:**
   - Answer explains: CSV loading, validation, PostgreSQL writing
   - Confidence: ~0.85 (green)
   - Sources: Shows document names with scores
   - Expand sources to show excerpts

4. **Explain:**
   > "Notice the answer is backed by specific documents. The confidence score is high because the question matches documentation content well."

**Demo - Question 2 (Medium):**

1. **Ask:** "What happens when data validation fails?"

2. **Show results:**
   - Answer explains blocking behavior and quality reports
   - Sources cited
   - Excerpts highlighted

**Demo - Question 3 (Hard/Low Confidence):**

1. **Ask:** "What is the meaning of life?"

2. **Show results:**
   - Answer: "I don't have enough supporting documentation..."
   - Confidence: low (red/orange)
   - Sources: May show irrelevant documents

3. **Explain:**
   > "This demonstrates citation discipline. When the RAG service can't find relevant documentation, it refuses to answer rather than hallucinate. This is crucial for reliability in production systems."

**Show RAG API Docs:**
- Open: http://localhost:8001/docs
- Show /ask endpoint
- Explain parameters: question, top_k, confidence_threshold

**Say:**
> "The RAG service uses TF-IDF for document retrieval, making it fast and reliable without requiring external LLM APIs. We can add LLM providers later for better answer generation while maintaining citation discipline."

---

### Part 7: Behind the Scenes (2 minutes)

**Show:** Database queries

```bash
# Connect to database
docker compose exec postgres psql -U fde_user -d fde_db
```

**Run queries:**

```sql
-- Show raw data
SELECT * FROM raw_data ORDER BY timestamp DESC LIMIT 5;

-- Show predictions
SELECT * FROM predictions ORDER BY created_at DESC LIMIT 3;

-- Show KPI view
SELECT * FROM kpi_daily ORDER BY date DESC LIMIT 5;
```

**Say:**
> "All data is stored in PostgreSQL with proper schema. The kpi_daily view pre-aggregates metrics for dashboard performance."

**Show service health:**
```bash
# Check health endpoints
curl http://localhost:8000/health | jq
curl http://localhost:8001/health | jq
```

**Explain:**
> "Each service has a health endpoint for monitoring. In production, these would be used by load balancers and monitoring systems."

---

### Part 8: Testing & Quality (2 minutes)

**Show:** Run API tests

```bash
# Enter API container
docker compose exec api bash

# Install test dependencies
pip install -q pytest pytest-asyncio httpx

# Run tests
pytest test_api.py -v
```

**Point out:**
- Test coverage for all endpoints
- Validation tests
- Model prediction tests

**Show:** Documentation

```bash
ls docs/
```

**Briefly mention:**
- Design_Doc.md: System architecture and principles
- Architecture.md: Detailed component diagrams
- Runbook.md: Operations guide
- Evaluation_Pack.md: Model and RAG evaluation
- Rollout_Plan.md: Phased deployment strategy

**Say:**
> "We have comprehensive documentation covering design, operations, evaluation, and deployment. This ensures the platform is production-ready."

---

### Part 9: Key Features Recap (1 minute)

**Summarize:**

1. **Idempotent Ingestion**
   - CSV/API support
   - Pydantic validation
   - Quality reporting
   - Blocks bad data

2. **Prediction API**
   - FastAPI with validation
   - Structured logging
   - Extensible to sklearn models
   - Swagger documentation

3. **RAG with Citation Discipline**
   - TF-IDF retrieval
   - Always returns sources
   - Refuses low-confidence answers
   - Configurable thresholds

4. **Interactive Dashboard**
   - Curated SQL views
   - Real-time KPI visualization
   - Interactive filters
   - Plotly charts

5. **Production Ready**
   - Docker Compose deployment
   - Health checks
   - Comprehensive testing
   - Full documentation

---

### Part 10: Future Enhancements (1 minute)

**Mention:**

1. **ML Pipeline:**
   - Trainable sklearn models
   - Model versioning (MLflow)
   - A/B testing

2. **Advanced RAG:**
   - LLM integration (GPT-4, Claude)
   - Vector database (Pinecone)
   - Multi-document reasoning

3. **Enterprise Features:**
   - Authentication (OAuth2)
   - Rate limiting
   - Prometheus monitoring
   - Kubernetes deployment

**Say:**
> "The platform is designed to scale. The modular architecture makes it easy to swap components, add features, and deploy to production environments."

---

## Q&A Preparation

### Common Questions

**Q: How does it scale to larger datasets?**
A: Current implementation is optimized for moderate data volumes. For larger scales, we can:
- Add read replicas for PostgreSQL
- Implement Redis caching
- Use vector databases for RAG
- Horizontal scaling with Kubernetes

**Q: Can we use our own ML models?**
A: Yes! The API service is designed to support any sklearn model. You can train your model, save it with joblib, and load it in the MLModel class.

**Q: How accurate is the RAG?**
A: Accuracy depends on document quality and relevance. We include an evaluation framework with golden Q&A sets to measure and improve retrieval quality.

**Q: What about security?**
A: Current version is for development. For production, we'd add:
- OAuth2 authentication
- API rate limiting
- HTTPS/TLS
- Network policies
- Audit logging

**Q: Can it run in the cloud?**
A: Absolutely! The Docker Compose setup can be translated to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Kubernetes (any cloud)

---

## Demo Tips

### Do's:
- ✅ Test everything before the demo
- ✅ Have backup screenshots if demo fails
- ✅ Prepare for questions
- ✅ Keep energy high and engaging
- ✅ Explain "why" not just "what"

### Don'ts:
- ❌ Rush through sections
- ❌ Ignore errors (explain them!)
- ❌ Use jargon without explanation
- ❌ Skip showing sources in RAG
- ❌ Forget to emphasize key features

### Troubleshooting During Demo:

**If a service is down:**
- Check `docker compose ps`
- Review logs: `docker compose logs [service]`
- Restart: `docker compose restart [service]`
- Have screenshots as backup

**If UI is slow:**
- Refresh the page
- Explain: "This is loading data from PostgreSQL..."
- Use the opportunity to discuss scalability

**If prediction fails:**
- Show the error message
- Explain validation (this is a feature!)
- Use correct format and retry

---

## Post-Demo

### Follow-up Actions:
1. Share repository link
2. Provide access to documentation
3. Schedule follow-up Q&A session
4. Collect feedback
5. Address questions in writing

### Success Metrics:
- Audience understood the architecture
- Key features demonstrated clearly
- Questions answered satisfactorily
- Stakeholders excited about platform
- Next steps identified

---

**End of Demo Script**

*Good luck with your demo! 🚀*
