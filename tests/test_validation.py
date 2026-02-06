"""Test data validation and ingestion."""
import pytest
from src.ingestion.data_pipeline import DataValidator

def test_event_validation_valid():
    """Test validation of valid event."""
    validator = DataValidator()
    
    event = {
        'event_type': 'transaction',
        'customer_id': 'CUST_0001',
        'status': 'success',
        'value': 100.0
    }
    
    is_valid, errors = validator.validate_event(event)
    assert is_valid is True
    assert len(errors) == 0

def test_event_validation_missing_required():
    """Test validation with missing required field."""
    validator = DataValidator()
    
    event = {
        'event_type': 'transaction',
        'status': 'success'
        # missing customer_id
    }
    
    is_valid, errors = validator.validate_event(event)
    assert is_valid is False
    assert any('customer_id' in err for err in errors)

def test_event_validation_invalid_type():
    """Test validation with invalid event type."""
    validator = DataValidator()
    
    event = {
        'event_type': 'invalid_type',
        'customer_id': 'CUST_0001',
        'status': 'success'
    }
    
    is_valid, errors = validator.validate_event(event)
    assert is_valid is False
    assert any('event_type' in err for err in errors)

def test_event_validation_negative_value():
    """Test validation with negative value."""
    validator = DataValidator()
    
    event = {
        'event_type': 'transaction',
        'customer_id': 'CUST_0001',
        'status': 'success',
        'value': -100.0
    }
    
    is_valid, errors = validator.validate_event(event)
    assert is_valid is False
    assert any('negative' in err.lower() for err in errors)

def test_batch_validation():
    """Test batch validation."""
    validator = DataValidator()
    
    events = [
        {
            'event_type': 'transaction',
            'customer_id': 'CUST_0001',
            'status': 'success',
            'value': 100.0
        },
        {
            'event_type': 'invalid',
            'customer_id': 'CUST_0002',
            'status': 'success'
        },
        {
            'event_type': 'login',
            'customer_id': 'CUST_0003',
            'status': 'success'
        }
    ]
    
    result = validator.validate_batch(events)
    
    assert result['total_records'] == 3
    assert result['valid_records'] == 2
    assert result['invalid_records'] == 1
    assert result['quality_score'] == pytest.approx(2/3, 0.01)
