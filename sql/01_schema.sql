-- Schema for FDE Platform
-- This script is automatically executed when the database initializes

-- Create main data table
CREATE TABLE IF NOT EXISTS raw_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    category VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp, metric_name, category)
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_raw_data_timestamp ON raw_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_data_metric_name ON raw_data(metric_name);
CREATE INDEX IF NOT EXISTS idx_raw_data_category ON raw_data(category);

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    input_data JSONB NOT NULL,
    prediction NUMERIC NOT NULL,
    prediction_label VARCHAR(50),
    confidence NUMERIC,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create curated KPI view
CREATE OR REPLACE VIEW kpi_daily AS
SELECT 
    DATE(timestamp) as date,
    metric_name,
    category,
    COUNT(*) as record_count,
    AVG(metric_value) as avg_value,
    MIN(metric_value) as min_value,
    MAX(metric_value) as max_value,
    STDDEV(metric_value) as stddev_value,
    SUM(metric_value) as total_value
FROM raw_data
GROUP BY DATE(timestamp), metric_name, category
ORDER BY date DESC, metric_name, category;

-- Create a view for recent predictions
CREATE OR REPLACE VIEW recent_predictions AS
SELECT 
    id,
    input_data,
    prediction,
    prediction_label,
    confidence,
    model_version,
    created_at
FROM predictions
ORDER BY created_at DESC
LIMIT 100;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fde_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fde_user;
