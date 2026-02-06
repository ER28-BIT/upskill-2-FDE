"""Streamlit dashboard for KPI visualization."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="FDE MVP Dashboard",
    page_icon="📊",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_engine():
    """Get database engine."""
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/fde_mvp")
    return create_engine(database_url)

def load_data(query: str) -> pd.DataFrame:
    """Load data from database."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Title and description
st.title("📊 FDE MVP Dashboard")
st.markdown("### Key Performance Indicators and Analytics")

# Sidebar
st.sidebar.header("Dashboard Controls")
refresh = st.sidebar.button("🔄 Refresh Data")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Daily Metrics", 
    "👥 Customer Activity", 
    "⚠️ Risk Analysis",
    "📊 Event Summary",
    "✅ Data Quality"
])

# Tab 1: Daily Metrics
with tab1:
    st.header("Daily Metrics Overview")
    
    daily_data = load_data("SELECT * FROM daily_metrics ORDER BY date DESC LIMIT 30")
    
    if not daily_data.empty:
        # Convert date column to datetime
        daily_data['date'] = pd.to_datetime(daily_data['date'])
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_events = daily_data['total_events'].sum()
            st.metric("Total Events", f"{total_events:,}")
        
        with col2:
            avg_success_rate = daily_data['success_rate'].mean()
            st.metric("Avg Success Rate", f"{avg_success_rate:.1f}%")
        
        with col3:
            active_customers = daily_data['active_customers'].iloc[0] if len(daily_data) > 0 else 0
            st.metric("Active Customers (Today)", f"{active_customers:,}")
        
        with col4:
            avg_risk = daily_data['avg_risk_score'].mean()
            st.metric("Avg Risk Score", f"{avg_risk:.2f}")
        
        # Daily events trend
        st.subheader("Daily Events Trend")
        fig_events = px.line(
            daily_data, 
            x='date', 
            y='total_events',
            title='Total Events Over Time'
        )
        st.plotly_chart(fig_events, use_container_width=True)
        
        # Success vs Failed events
        st.subheader("Success vs Failed Events")
        fig_success = go.Figure()
        fig_success.add_trace(go.Bar(
            x=daily_data['date'],
            y=daily_data['successful_events'],
            name='Successful',
            marker_color='green'
        ))
        fig_success.add_trace(go.Bar(
            x=daily_data['date'],
            y=daily_data['failed_events'],
            name='Failed',
            marker_color='red'
        ))
        fig_success.update_layout(barmode='stack', title='Event Status Distribution')
        st.plotly_chart(fig_success, use_container_width=True)
    else:
        st.info("No daily metrics data available yet.")

# Tab 2: Customer Activity
with tab2:
    st.header("Customer Activity Analysis")
    
    customer_data = load_data("SELECT * FROM customer_activity ORDER BY total_events DESC LIMIT 50")
    
    if not customer_data.empty:
        # Top customers by events
        st.subheader("Top Customers by Event Count")
        fig_top = px.bar(
            customer_data.head(10),
            x='customer_id',
            y='total_events',
            title='Top 10 Customers by Event Count',
            color='avg_risk_score',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig_top, use_container_width=True)
        
        # Customer metrics table
        st.subheader("Customer Details")
        st.dataframe(
            customer_data[[
                'customer_id', 'total_events', 'event_types', 
                'success_count', 'failed_count', 'avg_risk_score'
            ]].head(20),
            use_container_width=True
        )
    else:
        st.info("No customer activity data available yet.")

# Tab 3: Risk Analysis
with tab3:
    st.header("Risk Analysis")
    
    risk_data = load_data("SELECT * FROM high_risk_customers ORDER BY avg_risk_score DESC LIMIT 50")
    
    if not risk_data.empty:
        # High risk customers
        st.subheader("High Risk Customers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("High Risk Customers", len(risk_data))
        
        with col2:
            avg_risk = risk_data['avg_risk_score'].mean()
            st.metric("Avg Risk Score", f"{avg_risk:.2f}")
        
        # Risk distribution
        fig_risk = px.scatter(
            risk_data,
            x='event_count',
            y='avg_risk_score',
            size='failed_events',
            color='avg_risk_score',
            hover_data=['customer_id'],
            title='Risk Score vs Event Count',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig_risk, use_container_width=True)
        
        # Risk table
        st.subheader("High Risk Customer Details")
        st.dataframe(
            risk_data[[
                'customer_id', 'avg_risk_score', 'event_count', 'failed_events'
            ]].head(20),
            use_container_width=True
        )
    else:
        st.info("No high-risk customers identified yet.")

# Tab 4: Event Summary
with tab4:
    st.header("Event Summary")
    
    event_data = load_data("SELECT * FROM event_summary ORDER BY event_date DESC, event_count DESC LIMIT 100")
    
    if not event_data.empty:
        # Convert date column to datetime
        event_data['event_date'] = pd.to_datetime(event_data['event_date'])
        
        # Event type distribution
        st.subheader("Event Type Distribution")
        event_type_summary = event_data.groupby('event_type')['event_count'].sum().reset_index()
        fig_types = px.pie(
            event_type_summary,
            values='event_count',
            names='event_type',
            title='Distribution of Event Types'
        )
        st.plotly_chart(fig_types, use_container_width=True)
        
        # Event trends by type
        st.subheader("Event Trends by Type")
        fig_trends = px.line(
            event_data,
            x='event_date',
            y='event_count',
            color='event_type',
            title='Event Count Trends by Type'
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        
        # Event details table
        st.subheader("Recent Event Summary")
        st.dataframe(
            event_data[[
                'event_type', 'event_date', 'event_count', 
                'unique_customers', 'avg_value'
            ]].head(20),
            use_container_width=True
        )
    else:
        st.info("No event summary data available yet.")

# Tab 5: Data Quality
with tab5:
    st.header("Data Quality Monitoring")
    
    quality_data = load_data("SELECT * FROM data_quality_summary ORDER BY report_date DESC LIMIT 30")
    
    if not quality_data.empty:
        # Convert date column to datetime
        quality_data['report_date'] = pd.to_datetime(quality_data['report_date'])
        
        # Quality metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_quality = quality_data['avg_quality_score'].mean()
            st.metric("Avg Quality Score", f"{avg_quality:.2f}")
        
        with col2:
            total_processed = quality_data['total_records_processed'].sum()
            st.metric("Total Records Processed", f"{total_processed:,}")
        
        with col3:
            total_invalid = quality_data['total_invalid'].sum()
            st.metric("Total Invalid Records", f"{total_invalid:,}")
        
        # Quality score trend
        st.subheader("Quality Score Trend")
        fig_quality = px.line(
            quality_data,
            x='report_date',
            y='avg_quality_score',
            title='Data Quality Score Over Time',
            markers=True
        )
        fig_quality.update_layout(yaxis_range=[0, 1])
        st.plotly_chart(fig_quality, use_container_width=True)
        
        # Valid vs Invalid records
        st.subheader("Valid vs Invalid Records")
        fig_valid = go.Figure()
        fig_valid.add_trace(go.Bar(
            x=quality_data['report_date'],
            y=quality_data['total_valid'],
            name='Valid',
            marker_color='green'
        ))
        fig_valid.add_trace(go.Bar(
            x=quality_data['report_date'],
            y=quality_data['total_invalid'],
            name='Invalid',
            marker_color='red'
        ))
        fig_valid.update_layout(barmode='stack', title='Record Validation Status')
        st.plotly_chart(fig_valid, use_container_width=True)
    else:
        st.info("No data quality reports available yet.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "FDE MVP Dashboard v1.0\n\n"
    "This dashboard provides real-time analytics and KPIs for operational data."
)
