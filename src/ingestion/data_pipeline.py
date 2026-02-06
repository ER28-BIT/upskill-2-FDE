"""Data ingestion and validation module."""
import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.database_models import Event, DataQualityReport
from src.models.api_models import EventCreate

class DataValidator:
    """Validator for event data."""
    
    def __init__(self):
        self.errors = []
    
    def validate_event(self, event_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single event record."""
        errors = []
        
        # Required fields
        required_fields = ['event_type', 'customer_id', 'status']
        for field in required_fields:
            if field not in event_data or event_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Event type validation
        allowed_types = ['transaction', 'login', 'logout', 'error', 'warning', 'info']
        if 'event_type' in event_data and event_data['event_type'] not in allowed_types:
            errors.append(f"Invalid event_type: {event_data.get('event_type')}")
        
        # Status validation
        allowed_statuses = ['success', 'failed', 'pending', 'cancelled']
        if 'status' in event_data and event_data['status'] not in allowed_statuses:
            errors.append(f"Invalid status: {event_data.get('status')}")
        
        # Value validation
        if 'value' in event_data and event_data['value'] is not None:
            try:
                val = float(event_data['value'])
                if val < 0:
                    errors.append("Value must be non-negative")
            except (ValueError, TypeError):
                errors.append(f"Invalid value format: {event_data.get('value')}")
        
        return len(errors) == 0, errors
    
    def validate_batch(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of events and return validation report."""
        valid_events = []
        invalid_events = []
        all_errors = []
        
        for idx, event in enumerate(events):
            is_valid, errors = self.validate_event(event)
            if is_valid:
                valid_events.append(event)
            else:
                invalid_events.append({'index': idx, 'data': event, 'errors': errors})
                all_errors.extend([f"Record {idx}: {err}" for err in errors])
        
        total = len(events)
        valid_count = len(valid_events)
        invalid_count = len(invalid_events)
        quality_score = valid_count / total if total > 0 else 0
        
        return {
            'total_records': total,
            'valid_records': valid_count,
            'invalid_records': invalid_count,
            'quality_score': quality_score,
            'valid_events': valid_events,
            'invalid_events': invalid_events,
            'errors': all_errors
        }

class DataIngestion:
    """Data ingestion pipeline."""
    
    def __init__(self, db: Session):
        self.db = db
        self.validator = DataValidator()
    
    def ingest_from_dict(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ingest events from dictionary list with validation."""
        # Validate batch
        validation_result = self.validator.validate_batch(events)
        
        # Insert valid events
        inserted_count = 0
        for event_data in validation_result['valid_events']:
            try:
                event = Event(
                    event_type=event_data['event_type'],
                    customer_id=event_data['customer_id'],
                    timestamp=event_data.get('timestamp', datetime.utcnow()),
                    value=event_data.get('value'),
                    status=event_data['status'],
                    event_metadata=event_data.get('metadata', {})
                )
                self.db.add(event)
                inserted_count += 1
            except Exception as e:
                validation_result['errors'].append(f"Database insertion error: {str(e)}")
        
        self.db.commit()
        
        # Create data quality report
        report = DataQualityReport(
            total_records=validation_result['total_records'],
            valid_records=validation_result['valid_records'],
            invalid_records=validation_result['invalid_records'],
            validation_errors=validation_result['errors'],
            quality_score=validation_result['quality_score'],
            details={
                'inserted_count': inserted_count,
                'invalid_events': validation_result['invalid_events']
            }
        )
        self.db.add(report)
        self.db.commit()
        
        return {
            'status': 'completed',
            'inserted_records': inserted_count,
            'total_records': validation_result['total_records'],
            'valid_records': validation_result['valid_records'],
            'invalid_records': validation_result['invalid_records'],
            'quality_score': validation_result['quality_score'],
            'report_id': report.id,
            'errors': validation_result['errors']
        }
    
    def ingest_from_csv(self, file_path: str) -> Dict[str, Any]:
        """Ingest events from CSV file."""
        df = pd.read_csv(file_path)
        events = df.to_dict('records')
        return self.ingest_from_dict(events)
    
    def get_data_quality_reports(self, limit: int = 10) -> List[DataQualityReport]:
        """Retrieve recent data quality reports."""
        return self.db.query(DataQualityReport).order_by(
            DataQualityReport.report_timestamp.desc()
        ).limit(limit).all()
