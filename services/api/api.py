"""
API Service
FastAPI service with /predict and /health endpoints.
Includes Pydantic validation and structured logging.
"""
import os
import logging
from datetime import datetime
from typing import Dict, Optional, List
import json

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from sklearn.linear_model import LogisticRegression
import joblib
from pathlib import Path

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FDE Prediction API",
    description="API for predictions with rules-based and ML models",
    version="1.0.0"
)


class PredictionInput(BaseModel):
    """Input schema for predictions"""
    features: Dict[str, float] = Field(..., description="Feature dictionary for prediction")
    
    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        if not v:
            raise ValueError("features cannot be empty")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": {
                    "feature1": 1.5,
                    "feature2": 2.3,
                    "feature3": 0.8
                }
            }
        }


class PredictionOutput(BaseModel):
    """Output schema for predictions"""
    prediction: float
    prediction_label: str
    confidence: Optional[float] = None
    model_version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction": 0.85,
                "prediction_label": "high",
                "confidence": 0.92,
                "model_version": "rules_v1",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    database_connected: bool
    model_loaded: bool


class RulesBasedModel:
    """Simple rules-based model for initial implementation"""
    
    def __init__(self):
        self.version = "rules_v1"
        logger.info("Initialized rules-based model")
    
    def predict(self, features: Dict[str, float]) -> tuple:
        """
        Simple rule: average of all feature values
        Returns (prediction, confidence)
        """
        values = list(features.values())
        avg = sum(values) / len(values) if values else 0.0
        
        # Simple confidence based on consistency
        if values:
            std = np.std(values)
            confidence = max(0.5, 1.0 - std)
        else:
            confidence = 0.5
        
        logger.info(f"Rules model prediction: {avg:.3f}, confidence: {confidence:.3f}")
        return avg, confidence


class MLModel:
    """Trainable sklearn model (placeholder for future implementation)"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.version = "sklearn_v1"
        self.model = None
        self.model_path = model_path or "/app/models/model.joblib"
        
        # Try to load existing model
        if Path(self.model_path).exists():
            try:
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded ML model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Failed to load ML model: {e}")
        else:
            logger.info("No pre-trained model found, using rules-based fallback")
    
    def predict(self, features: Dict[str, float]) -> tuple:
        """
        Predict using sklearn model if available, otherwise fallback to rules
        """
        if self.model is not None:
            try:
                # Convert features to array
                feature_values = np.array([list(features.values())])
                prediction = self.model.predict(feature_values)[0]
                
                # Get confidence if available
                if hasattr(self.model, 'predict_proba'):
                    proba = self.model.predict_proba(feature_values)[0]
                    confidence = float(max(proba))
                else:
                    confidence = 0.8
                
                logger.info(f"ML model prediction: {prediction:.3f}, confidence: {confidence:.3f}")
                return float(prediction), confidence
            except Exception as e:
                logger.error(f"ML model prediction failed: {e}")
                raise
        else:
            # Fallback to rules
            rules_model = RulesBasedModel()
            return rules_model.predict(features)


# Global model instance
model = RulesBasedModel()


def get_db_connection():
    """Get database connection"""
    database_url = os.getenv("DATABASE_URL", "postgresql://fde_user:fde_pass@postgres:5432/fde_db")
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None


def save_prediction(input_data: Dict, prediction: float, label: str, confidence: float, model_version: str):
    """Save prediction to database"""
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO predictions (input_data, prediction, prediction_label, confidence, model_version)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (json.dumps(input_data), prediction, label, confidence, model_version)
                )
                conn.commit()
            conn.close()
            logger.info("Prediction saved to database")
    except Exception as e:
        logger.error(f"Failed to save prediction: {e}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    
    # Check database connection
    db_connected = False
    conn = get_db_connection()
    if conn:
        db_connected = True
        conn.close()
    
    # Check model loaded
    model_loaded = model is not None
    
    status = "healthy" if (db_connected and model_loaded) else "degraded"
    
    return HealthResponse(
        status=status,
        database_connected=db_connected,
        model_loaded=model_loaded
    )


@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    """
    Prediction endpoint
    Accepts feature dictionary and returns prediction with confidence
    """
    logger.info(f"Prediction requested with features: {list(input_data.features.keys())}")
    
    try:
        # Make prediction
        prediction, confidence = model.predict(input_data.features)
        
        # Determine label based on prediction value
        if prediction < 0.33:
            label = "low"
        elif prediction < 0.67:
            label = "medium"
        else:
            label = "high"
        
        # Create response
        response = PredictionOutput(
            prediction=prediction,
            prediction_label=label,
            confidence=confidence,
            model_version=model.version
        )
        
        # Save to database (async in production)
        save_prediction(
            input_data.features,
            prediction,
            label,
            confidence,
            model.version
        )
        
        logger.info(f"Prediction complete: {prediction:.3f} ({label})")
        return response
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FDE Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
