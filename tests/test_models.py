"""Test API models."""
import pytest
from pydantic import ValidationError
from src.models.api_models import EventCreate, RiskPredictionRequest

def test_event_create_valid():
    """Test valid event creation."""
    event = EventCreate(
        event_type='transaction',
        customer_id='CUST_0001',
        status='success',
        value=100.0
    )
    
    assert event.event_type == 'transaction'
    assert event.customer_id == 'CUST_0001'
    assert event.status == 'success'
    assert event.value == 100.0

def test_event_create_invalid_type():
    """Test event creation with invalid type."""
    with pytest.raises(ValidationError) as exc_info:
        EventCreate(
            event_type='invalid_type',
            customer_id='CUST_0001',
            status='success'
        )
    
    assert 'event_type' in str(exc_info.value)

def test_event_create_invalid_status():
    """Test event creation with invalid status."""
    with pytest.raises(ValidationError) as exc_info:
        EventCreate(
            event_type='transaction',
            customer_id='CUST_0001',
            status='invalid_status'
        )
    
    assert 'status' in str(exc_info.value)

def test_event_create_negative_value():
    """Test event creation with negative value."""
    with pytest.raises(ValidationError) as exc_info:
        EventCreate(
            event_type='transaction',
            customer_id='CUST_0001',
            status='success',
            value=-100.0
        )
    
    assert 'value' in str(exc_info.value)

def test_risk_prediction_request():
    """Test risk prediction request."""
    request = RiskPredictionRequest(
        customer_id='CUST_0001',
        event_type='transaction',
        value=1000.0
    )
    
    assert request.customer_id == 'CUST_0001'
    assert request.event_type == 'transaction'
    assert request.value == 1000.0
