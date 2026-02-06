"""FastAPI application for FDE MVP."""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os

from src.database.connection import get_db, init_db, engine
from src.database.views import create_kpi_views
from src.models.api_models import (
    EventCreate, EventResponse, RiskPredictionRequest, 
    RiskPredictionResponse, RAGQuery, RAGResponse
)
from src.models.database_models import Event
from src.ingestion.data_pipeline import DataIngestion
from src.models.risk_model import RiskPredictor
from src.api.rag_copilot import RAGCopilot

# Initialize FastAPI app
app = FastAPI(
    title="FDE MVP API",
    description="Forward Deployed Engineer MVP with data ingestion, KPIs, risk prediction, and RAG copilot",
    version="1.0.0"
)

# Initialize RAG copilot
rag_copilot = RAGCopilot()

@app.on_event("startup")
async def startup_event():
    """Initialize database and views on startup."""
    init_db()
    create_kpi_views(engine)
    print("Database initialized and KPI views created")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "FDE MVP API",
        "version": "1.0.0",
        "endpoints": {
            "events": "/events",
            "ingest": "/ingest",
            "predict": "/predict",
            "copilot": "/copilot",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "FDE MVP API"}

# Event Management Endpoints
@app.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new event with validation."""
    try:
        db_event = Event(
            event_type=event.event_type,
            customer_id=event.customer_id,
            timestamp=event.timestamp,
            value=event.value,
            status=event.status,
            metadata=event.metadata
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        # Calculate risk score
        predictor = RiskPredictor(db)
        risk_result = predictor.calculate_risk_score(
            customer_id=event.customer_id,
            event_type=event.event_type,
            value=event.value,
            metadata=event.metadata
        )
        db_event.risk_score = risk_result['risk_score']
        db.commit()
        db.refresh(db_event)
        
        return db_event
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating event: {str(e)}")

@app.get("/events", response_model=List[EventResponse])
async def get_events(
    skip: int = 0, 
    limit: int = 100, 
    customer_id: str = None,
    db: Session = Depends(get_db)
):
    """Retrieve events with optional filtering."""
    query = db.query(Event)
    
    if customer_id:
        query = query.filter(Event.customer_id == customer_id)
    
    events = query.offset(skip).limit(limit).all()
    return events

@app.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific event by ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

# Data Ingestion Endpoints
@app.post("/ingest")
async def ingest_data(events: List[EventCreate], db: Session = Depends(get_db)):
    """Ingest a batch of events with validation and quality reporting."""
    try:
        ingestion = DataIngestion(db)
        events_dict = [event.dict() for event in events]
        result = ingestion.ingest_from_dict(events_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")

@app.get("/data-quality/reports")
async def get_data_quality_reports(limit: int = 10, db: Session = Depends(get_db)):
    """Retrieve recent data quality reports."""
    ingestion = DataIngestion(db)
    reports = ingestion.get_data_quality_reports(limit)
    return [
        {
            "id": r.id,
            "timestamp": r.report_timestamp,
            "total_records": r.total_records,
            "valid_records": r.valid_records,
            "invalid_records": r.invalid_records,
            "quality_score": r.quality_score,
            "errors": r.validation_errors
        }
        for r in reports
    ]

# Risk Prediction Endpoint
@app.post("/predict", response_model=RiskPredictionResponse)
async def predict_risk(request: RiskPredictionRequest, db: Session = Depends(get_db)):
    """Predict risk score and label for a customer event."""
    try:
        predictor = RiskPredictor(db)
        result = predictor.calculate_risk_score(
            customer_id=request.customer_id,
            event_type=request.event_type,
            value=request.value,
            metadata=request.metadata
        )
        
        return RiskPredictionResponse(
            customer_id=request.customer_id,
            risk_score=result['risk_score'],
            risk_label=result['risk_label'],
            factors=result['factors']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# RAG Copilot Endpoints
@app.post("/copilot", response_model=RAGResponse)
async def copilot_query(query: RAGQuery):
    """Query the RAG copilot with a question."""
    try:
        result = rag_copilot.query(
            question=query.question,
            max_sources=query.max_sources
        )
        return RAGResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copilot error: {str(e)}")

@app.post("/copilot/index")
async def index_documents():
    """Index documents for the RAG copilot."""
    try:
        result = rag_copilot.index_documents()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing error: {str(e)}")

@app.post("/copilot/reset")
async def reset_copilot():
    """Reset the RAG copilot collection."""
    try:
        result = rag_copilot.reset_collection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
