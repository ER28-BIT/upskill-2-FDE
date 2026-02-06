"""SQL views for KPI analytics."""

# KPI Views SQL definitions
KPI_VIEWS = {
    'event_summary': """
        CREATE OR REPLACE VIEW event_summary AS
        SELECT 
            event_type,
            COUNT(*) as event_count,
            COUNT(DISTINCT customer_id) as unique_customers,
            AVG(value) as avg_value,
            MIN(value) as min_value,
            MAX(value) as max_value,
            DATE(timestamp) as event_date
        FROM events
        GROUP BY event_type, DATE(timestamp)
        ORDER BY event_date DESC, event_count DESC;
    """,
    
    'customer_activity': """
        CREATE OR REPLACE VIEW customer_activity AS
        SELECT 
            customer_id,
            COUNT(*) as total_events,
            COUNT(DISTINCT event_type) as event_types,
            AVG(value) as avg_value,
            MAX(timestamp) as last_activity,
            AVG(risk_score) as avg_risk_score,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count
        FROM events
        GROUP BY customer_id
        ORDER BY total_events DESC;
    """,
    
    'daily_metrics': """
        CREATE OR REPLACE VIEW daily_metrics AS
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as total_events,
            COUNT(DISTINCT customer_id) as active_customers,
            AVG(value) as avg_transaction_value,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_events,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_events,
            ROUND(100.0 * SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate,
            AVG(risk_score) as avg_risk_score
        FROM events
        GROUP BY DATE(timestamp)
        ORDER BY date DESC;
    """,
    
    'high_risk_customers': """
        CREATE OR REPLACE VIEW high_risk_customers AS
        SELECT 
            customer_id,
            AVG(risk_score) as avg_risk_score,
            COUNT(*) as event_count,
            MAX(timestamp) as last_event,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_events
        FROM events
        WHERE risk_score > 0.7
        GROUP BY customer_id
        HAVING AVG(risk_score) > 0.7
        ORDER BY avg_risk_score DESC;
    """,
    
    'data_quality_summary': """
        CREATE OR REPLACE VIEW data_quality_summary AS
        SELECT 
            DATE(report_timestamp) as report_date,
            AVG(quality_score) as avg_quality_score,
            SUM(total_records) as total_records_processed,
            SUM(valid_records) as total_valid,
            SUM(invalid_records) as total_invalid,
            COUNT(*) as report_count
        FROM data_quality_reports
        GROUP BY DATE(report_timestamp)
        ORDER BY report_date DESC;
    """
}

def create_kpi_views(engine):
    """Create all KPI views in the database."""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        for view_name, view_sql in KPI_VIEWS.items():
            try:
                conn.execute(text(view_sql))
                conn.commit()
                print(f"Created view: {view_name}")
            except Exception as e:
                print(f"Error creating view {view_name}: {e}")
                conn.rollback()

def drop_kpi_views(engine):
    """Drop all KPI views from the database."""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        for view_name in KPI_VIEWS.keys():
            try:
                conn.execute(text(f"DROP VIEW IF EXISTS {view_name};"))
                conn.commit()
                print(f"Dropped view: {view_name}")
            except Exception as e:
                print(f"Error dropping view {view_name}: {e}")
                conn.rollback()
