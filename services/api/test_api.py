"""
Tests for API Service
"""
import pytest
from fastapi.testclient import TestClient
from api import app, RulesBasedModel


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "database_connected" in data
    assert "model_loaded" in data


def test_predict_endpoint(client):
    """Test predict endpoint"""
    test_input = {
        "features": {
            "feature1": 1.5,
            "feature2": 2.3,
            "feature3": 0.8
        }
    }
    
    response = client.post("/predict", json=test_input)
    assert response.status_code == 200
    
    data = response.json()
    assert "prediction" in data
    assert "prediction_label" in data
    assert "confidence" in data
    assert "model_version" in data
    assert "timestamp" in data
    
    # Validate prediction value
    assert isinstance(data["prediction"], (int, float))
    assert data["prediction_label"] in ["low", "medium", "high"]


def test_predict_with_invalid_input(client):
    """Test predict endpoint with invalid input"""
    test_input = {
        "features": {}  # Empty features should fail
    }
    
    response = client.post("/predict", json=test_input)
    assert response.status_code == 422  # Validation error


def test_rules_based_model():
    """Test rules-based model directly"""
    model = RulesBasedModel()
    
    features = {"f1": 1.0, "f2": 2.0, "f3": 3.0}
    prediction, confidence = model.predict(features)
    
    assert isinstance(prediction, float)
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 1
    assert prediction == 2.0  # Average of 1, 2, 3


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data
