"""Database models for operational and customer events."""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from src.database.connection import Base

class Event(Base):
    """Event model for operational/customer data."""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    customer_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    value = Column(Float, nullable=True)
    status = Column(String, nullable=False)
    event_metadata = Column(JSON, nullable=True)
    risk_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Event(id={self.id}, type={self.event_type}, customer={self.customer_id})>"

class DataQualityReport(Base):
    """Data quality report model."""
    __tablename__ = "data_quality_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total_records = Column(Integer, nullable=False)
    valid_records = Column(Integer, nullable=False)
    invalid_records = Column(Integer, nullable=False)
    validation_errors = Column(JSON, nullable=True)
    quality_score = Column(Float, nullable=False)
    details = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<DataQualityReport(id={self.id}, score={self.quality_score})>"
