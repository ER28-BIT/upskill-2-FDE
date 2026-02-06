"""
Ingest Service
Loads CSV/API data, validates schema, writes to Postgres, generates JSON quality reports.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pydantic import BaseModel, Field, ValidationError, field_validator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataRecord(BaseModel):
    """Schema for incoming data records"""
    timestamp: datetime
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: float
    category: Optional[str] = Field(None, max_length=50)
    metadata: Optional[Dict] = None

    @field_validator('metric_name')
    @classmethod
    def validate_metric_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError("metric_name cannot be empty")
        return v.strip()


class QualityReport(BaseModel):
    """Quality report for ingestion"""
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str
    total_records: int
    valid_records: int
    invalid_records: int
    validation_errors: List[Dict]
    data_quality_metrics: Dict


class IngestService:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.conn = None
        self.reports_dir = Path("/data/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def connect(self):
        """Connect to database"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            logger.info("Connected to database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def validate_data(self, df: pd.DataFrame) -> tuple:
        """Validate data against schema"""
        valid_records = []
        invalid_records = []
        validation_errors = []
        
        for idx, row in df.iterrows():
            try:
                # Convert row to dict
                record_dict = row.to_dict()
                
                # Validate with Pydantic
                record = DataRecord(**record_dict)
                valid_records.append(record)
                
            except (ValidationError, Exception) as e:
                logger.warning(f"Validation error at row {idx}: {e}")
                invalid_records.append(record_dict)
                validation_errors.append({
                    "row": idx,
                    "error": str(e),
                    "data": {k: str(v) for k, v in record_dict.items()}
                })
        
        return valid_records, invalid_records, validation_errors
    
    def write_to_postgres(self, valid_records: List[DataRecord]) -> int:
        """Write valid records to Postgres with idempotency"""
        if not valid_records:
            logger.info("No valid records to write")
            return 0
        
        # Prepare data for insertion
        values = [
            (
                r.timestamp,
                r.metric_name,
                r.metric_value,
                r.category,
                json.dumps(r.metadata) if r.metadata else None
            )
            for r in valid_records
        ]
        
        # Use ON CONFLICT to ensure idempotency
        insert_query = """
            INSERT INTO raw_data (timestamp, metric_name, metric_value, category, metadata)
            VALUES %s
            ON CONFLICT (timestamp, metric_name, category) 
            DO UPDATE SET 
                metric_value = EXCLUDED.metric_value,
                metadata = EXCLUDED.metadata
        """
        
        try:
            with self.conn.cursor() as cur:
                execute_values(cur, insert_query, values)
                self.conn.commit()
                logger.info(f"Successfully wrote {len(valid_records)} records to database")
                return len(valid_records)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to write to database: {e}")
            raise
    
    def generate_quality_report(
        self, 
        source: str, 
        total_records: int,
        valid_records: List[DataRecord],
        invalid_records: List,
        validation_errors: List[Dict]
    ) -> QualityReport:
        """Generate quality report"""
        
        # Calculate quality metrics
        data_quality_metrics = {
            "completeness": len(valid_records) / total_records if total_records > 0 else 0,
            "valid_percentage": (len(valid_records) / total_records * 100) if total_records > 0 else 0,
        }
        
        if valid_records:
            values = [r.metric_value for r in valid_records]
            data_quality_metrics.update({
                "mean_value": sum(values) / len(values),
                "min_value": min(values),
                "max_value": max(values),
            })
        
        report = QualityReport(
            source=source,
            total_records=total_records,
            valid_records=len(valid_records),
            invalid_records=len(invalid_records),
            validation_errors=validation_errors[:10],  # Limit to first 10 errors
            data_quality_metrics=data_quality_metrics
        )
        
        return report
    
    def save_quality_report(self, report: QualityReport):
        """Save quality report to JSON file"""
        timestamp_str = report.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = self.reports_dir / f"quality_report_{timestamp_str}.json"
        
        with open(filename, 'w') as f:
            json.dump(report.model_dump(mode='json'), f, indent=2, default=str)
        
        logger.info(f"Quality report saved to {filename}")
    
    def ingest_csv(self, csv_path: str):
        """Ingest data from CSV file"""
        logger.info(f"Ingesting CSV from {csv_path}")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            logger.info(f"Read {len(df)} records from CSV")
            
            # Convert timestamp column if exists
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Validate data
            valid_records, invalid_records, validation_errors = self.validate_data(df)
            logger.info(f"Validation: {len(valid_records)} valid, {len(invalid_records)} invalid")
            
            # Block writes if required fields are missing in all records
            if not valid_records and len(df) > 0:
                logger.error("No valid records - blocking write to database")
                report = self.generate_quality_report(
                    csv_path, len(df), valid_records, invalid_records, validation_errors
                )
                self.save_quality_report(report)
                return
            
            # Write to database
            written_count = self.write_to_postgres(valid_records)
            
            # Generate and save quality report
            report = self.generate_quality_report(
                csv_path, len(df), valid_records, invalid_records, validation_errors
            )
            self.save_quality_report(report)
            
            logger.info(f"Ingestion complete: {written_count} records written")
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise


def main():
    """Main entry point"""
    database_url = os.getenv("DATABASE_URL", "postgresql://fde_user:fde_pass@postgres:5432/fde_db")
    
    service = IngestService(database_url)
    service.connect()
    
    try:
        # Look for CSV files in /data directory
        data_dir = Path("/data")
        csv_files = list(data_dir.glob("*.csv"))
        
        if csv_files:
            for csv_file in csv_files:
                logger.info(f"Found CSV file: {csv_file}")
                service.ingest_csv(str(csv_file))
        else:
            logger.info("No CSV files found in /data directory")
            
            # Create a sample CSV for demonstration
            logger.info("Creating sample data...")
            sample_data = {
                'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='H'),
                'metric_name': ['revenue'] * 50 + ['users'] * 50,
                'metric_value': [1000 + i * 10 for i in range(100)],
                'category': ['product_a'] * 25 + ['product_b'] * 25 + ['web'] * 25 + ['mobile'] * 25,
            }
            sample_df = pd.DataFrame(sample_data)
            sample_path = data_dir / "sample_data.csv"
            sample_df.to_csv(sample_path, index=False)
            logger.info(f"Created sample data at {sample_path}")
            
            # Ingest the sample data
            service.ingest_csv(str(sample_path))
            
    finally:
        service.close()
    
    logger.info("Ingest service completed")


if __name__ == "__main__":
    main()
