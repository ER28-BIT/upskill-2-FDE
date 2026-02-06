"""Pydantic models for API validation."""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class EventCreate(BaseModel):
    """Schema for creating a new event."""
    event_type: str = Field(..., description="Type of event (e.g., 'transaction', 'login', 'error')")
    customer_id: str = Field(..., description="Customer identifier")
    timestamp: Optional[datetime] = None
    value: Optional[float] = Field(None, ge=0, description="Event value (must be non-negative)")
    status: str = Field(..., description="Event status (e.g., 'success', 'failed', 'pending')")
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        allowed_types = ['transaction', 'login', 'logout', 'error', 'warning', 'info']
        if v not in allowed_types:
            raise ValueError(f"event_type must be one of {allowed_types}")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['success', 'failed', 'pending', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}")
        return v

class EventResponse(BaseModel):
    """Schema for event response."""
    id: int
    event_type: str
    customer_id: str
    timestamp: datetime
    value: Optional[float]
    status: str
    metadata: Optional[Dict[str, Any]]
    risk_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class RiskPredictionRequest(BaseModel):
    """Schema for risk prediction request."""
    customer_id: str
    event_type: str
    value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class RiskPredictionResponse(BaseModel):
    """Schema for risk prediction response."""
    customer_id: str
    risk_score: float = Field(..., ge=0, le=1, description="Risk score between 0 and 1")
    risk_label: str = Field(..., description="Risk label: 'low', 'medium', or 'high'")
    factors: Dict[str, Any] = Field(..., description="Factors contributing to risk score")

class RAGQuery(BaseModel):
    """Schema for RAG copilot query."""
    question: str = Field(..., min_length=1, description="Question to ask the copilot")
    max_sources: int = Field(default=3, ge=1, le=10, description="Maximum number of sources to retrieve")

class RAGResponse(BaseModel):
    """Schema for RAG copilot response."""
    answer: str = Field(..., description="Answer to the question")
    sources: list[Dict[str, str]] = Field(..., description="List of source citations")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in the answer")
    has_sufficient_sources: bool = Field(..., description="Whether sufficient sources were found")
