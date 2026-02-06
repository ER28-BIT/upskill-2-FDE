"""Risk scoring and prediction model."""
import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.database_models import Event

class RiskPredictor:
    """Risk prediction model for customer events."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_risk_score(
        self, 
        customer_id: str, 
        event_type: str, 
        value: float = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate risk score based on customer history and event characteristics."""
        
        # Get customer history (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        customer_events = self.db.query(Event).filter(
            Event.customer_id == customer_id,
            Event.timestamp >= thirty_days_ago
        ).all()
        
        # Initialize risk factors
        risk_factors = {}
        risk_score = 0.0
        
        # Factor 1: Event type risk (0-0.3)
        event_type_risk = {
            'error': 0.3,
            'transaction': 0.1,
            'warning': 0.2,
            'login': 0.05,
            'logout': 0.05,
            'info': 0.05
        }
        type_risk = event_type_risk.get(event_type, 0.1)
        risk_factors['event_type_risk'] = type_risk
        risk_score += type_risk
        
        # Factor 2: Failure rate (0-0.3)
        if customer_events:
            failed_count = sum(1 for e in customer_events if e.status == 'failed')
            total_count = len(customer_events)
            failure_rate = failed_count / total_count if total_count > 0 else 0
            risk_factors['failure_rate'] = failure_rate
            risk_score += failure_rate * 0.3
        else:
            risk_factors['failure_rate'] = 0.0
        
        # Factor 3: Transaction value anomaly (0-0.2)
        if value is not None and customer_events:
            values = [e.value for e in customer_events if e.value is not None]
            if values:
                avg_value = np.mean(values)
                std_value = np.std(values) if len(values) > 1 else avg_value * 0.1
                
                if std_value > 0:
                    z_score = abs((value - avg_value) / std_value)
                    value_anomaly = min(z_score / 10, 0.2)  # Normalize to 0-0.2
                else:
                    value_anomaly = 0.0
                
                risk_factors['value_anomaly'] = value_anomaly
                risk_score += value_anomaly
            else:
                risk_factors['value_anomaly'] = 0.0
        else:
            risk_factors['value_anomaly'] = 0.0
        
        # Factor 4: Recent activity frequency (0-0.2)
        if customer_events:
            recent_events = [e for e in customer_events if 
                           (datetime.utcnow() - e.timestamp).days <= 7]
            activity_score = min(len(recent_events) / 50, 0.2)  # High frequency = higher risk
            risk_factors['activity_frequency'] = activity_score
            risk_score += activity_score
        else:
            # New customer = moderate risk
            risk_factors['activity_frequency'] = 0.1
            risk_score += 0.1
        
        # Normalize risk score to 0-1
        risk_score = min(max(risk_score, 0.0), 1.0)
        
        # Determine risk label
        if risk_score < 0.3:
            risk_label = "low"
        elif risk_score < 0.7:
            risk_label = "medium"
        else:
            risk_label = "high"
        
        return {
            'risk_score': round(risk_score, 3),
            'risk_label': risk_label,
            'factors': risk_factors
        }
    
    def update_event_risk_scores(self, limit: int = 100):
        """Update risk scores for recent events without scores."""
        events = self.db.query(Event).filter(
            Event.risk_score.is_(None)
        ).limit(limit).all()
        
        updated = 0
        for event in events:
            prediction = self.calculate_risk_score(
                customer_id=event.customer_id,
                event_type=event.event_type,
                value=event.value,
                metadata=event.event_metadata
            )
            event.risk_score = prediction['risk_score']
            updated += 1
        
        self.db.commit()
        return {'updated_count': updated}
