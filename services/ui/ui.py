"""
UI Service
Streamlit application with Dashboard, Prediction, and Copilot tabs.
"""
import os
import logging
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import plotly.graph_objects as go

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = os.getenv("API_URL", "http://api:8000")
RAG_URL = os.getenv("RAG_URL", "http://rag:8001")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://fde_user:fde_pass@postgres:5432/fde_db")

# Page config
st.set_page_config(
    page_title="FDE Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        st.error(f"Database connection failed: {e}")
        return None


def fetch_kpi_data():
    """Fetch KPI data from curated SQL view"""
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        query = """
        SELECT * FROM kpi_daily
        ORDER BY date DESC
        LIMIT 100
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        logger.error(f"Failed to fetch KPI data: {e}")
        st.error(f"Failed to fetch KPI data: {e}")
        return None


def call_predict_api(features: dict):
    """Call the prediction API"""
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={"features": features},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API call failed: {e}")
        st.error(f"API call failed: {e}")
        return None


def call_rag_api(question: str, top_k: int = 3, confidence_threshold: float = 0.3):
    """Call the RAG API"""
    try:
        response = requests.post(
            f"{RAG_URL}/ask",
            json={
                "question": question,
                "top_k": top_k,
                "confidence_threshold": confidence_threshold
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"RAG API call failed: {e}")
        st.error(f"RAG API call failed: {e}")
        return None


def check_services_health():
    """Check health of all services"""
    services = {
        "API": f"{API_URL}/health",
        "RAG": f"{RAG_URL}/health"
    }
    
    status = {}
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            status[name] = "✅ Healthy" if response.status_code == 200 else "❌ Unhealthy"
        except:
            status[name] = "❌ Unreachable"
    
    # Check database
    conn = get_db_connection()
    if conn:
        status["Database"] = "✅ Connected"
        conn.close()
    else:
        status["Database"] = "❌ Disconnected"
    
    return status


# Sidebar
with st.sidebar:
    st.title("📊 FDE Platform")
    st.markdown("---")
    
    # Service health status
    st.subheader("Service Health")
    with st.expander("Check Services", expanded=False):
        if st.button("Refresh Health Status"):
            health_status = check_services_health()
            for service, status in health_status.items():
                st.write(f"{service}: {status}")
    
    st.markdown("---")
    st.info("Use the tabs above to navigate between Dashboard, Prediction, and Copilot features.")


# Main content with tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎯 Prediction", "🤖 Copilot"])

# Tab 1: Dashboard
with tab1:
    st.header("📊 KPI Dashboard")
    st.markdown("View key performance indicators from curated SQL views")
    
    if st.button("Load KPI Data", key="load_kpi"):
        with st.spinner("Loading KPI data..."):
            kpi_df = fetch_kpi_data()
            
            if kpi_df is not None and not kpi_df.empty:
                st.success(f"Loaded {len(kpi_df)} KPI records")
                
                # Store in session state
                st.session_state['kpi_data'] = kpi_df
            else:
                st.warning("No KPI data available")
    
    # Display KPI data if available
    if 'kpi_data' in st.session_state:
        kpi_df = st.session_state['kpi_data']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", len(kpi_df))
        with col2:
            st.metric("Metrics", kpi_df['metric_name'].nunique())
        with col3:
            st.metric("Categories", kpi_df['category'].nunique())
        with col4:
            latest_date = kpi_df['date'].max()
            st.metric("Latest Date", latest_date.strftime('%Y-%m-%d') if pd.notna(latest_date) else "N/A")
        
        st.markdown("---")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            selected_metric = st.selectbox(
                "Select Metric",
                options=['All'] + list(kpi_df['metric_name'].unique())
            )
        with col2:
            selected_category = st.selectbox(
                "Select Category",
                options=['All'] + list(kpi_df['category'].unique())
            )
        
        # Filter data
        filtered_df = kpi_df.copy()
        if selected_metric != 'All':
            filtered_df = filtered_df[filtered_df['metric_name'] == selected_metric]
        if selected_category != 'All':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
        # Visualizations
        if not filtered_df.empty:
            st.subheader("Average Value Over Time")
            fig = px.line(
                filtered_df.sort_values('date'),
                x='date',
                y='avg_value',
                color='metric_name' if selected_metric == 'All' else None,
                title=f"Average Value Trend"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Total Value by Category")
            category_totals = filtered_df.groupby('category')['total_value'].sum().reset_index()
            fig2 = px.bar(
                category_totals,
                x='category',
                y='total_value',
                title="Total Value by Category"
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Data table
            st.subheader("Detailed Data")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No data matches the selected filters")

# Tab 2: Prediction
with tab2:
    st.header("🎯 Prediction Service")
    st.markdown("Make predictions using the API /predict endpoint")
    
    st.subheader("Input Features")
    
    # Dynamic feature input
    num_features = st.number_input("Number of features", min_value=1, max_value=10, value=3)
    
    features = {}
    cols = st.columns(3)
    for i in range(num_features):
        with cols[i % 3]:
            feature_name = st.text_input(f"Feature {i+1} name", value=f"feature{i+1}", key=f"fname_{i}")
            feature_value = st.number_input(f"Feature {i+1} value", value=1.0, key=f"fval_{i}")
            features[feature_name] = feature_value
    
    if st.button("Make Prediction", key="predict"):
        with st.spinner("Making prediction..."):
            result = call_predict_api(features)
            
            if result:
                st.success("Prediction complete!")
                
                # Display results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prediction", f"{result['prediction']:.4f}")
                with col2:
                    st.metric("Label", result['prediction_label'])
                with col3:
                    st.metric("Confidence", f"{result['confidence']:.2%}")
                
                st.json(result)
            else:
                st.error("Prediction failed")

# Tab 3: Copilot
with tab3:
    st.header("🤖 AI Copilot")
    st.markdown("Ask questions about the FDE platform and get answers with sources")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    # Question input
    question = st.text_input("Ask a question:", placeholder="e.g., How does the ingestion service work?")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        top_k = st.number_input("Top K sources", min_value=1, max_value=10, value=3)
    with col2:
        confidence_threshold = st.slider("Confidence threshold", 0.0, 1.0, 0.3, 0.05)
    
    if st.button("Ask", key="ask") and question:
        with st.spinner("Thinking..."):
            result = call_rag_api(question, top_k, confidence_threshold)
            
            if result:
                # Add to chat history
                st.session_state['chat_history'].append({
                    'question': question,
                    'result': result
                })
    
    # Display chat history (most recent first)
    for i, chat in enumerate(reversed(st.session_state['chat_history'])):
        st.markdown("---")
        
        # Question
        st.markdown(f"**Q:** {chat['question']}")
        
        # Answer
        result = chat['result']
        st.markdown(f"**A:** {result['answer']}")
        
        # Confidence
        confidence_color = "green" if result['confidence'] > 0.5 else "orange" if result['confidence'] > 0.3 else "red"
        st.markdown(f"**Confidence:** :{confidence_color}[{result['confidence']:.2%}]")
        
        # Sources
        with st.expander(f"📚 Sources ({len(result['sources'])})"):
            for j, source in enumerate(result['sources'], 1):
                st.markdown(f"**Source {j}: {source['document']}** (Score: {source['score']:.3f})")
                st.markdown(f"> {source['excerpt']}")
                st.markdown("")
    
    if not st.session_state['chat_history']:
        st.info("👆 Ask a question to get started!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>FDE Platform v1.0.0 | Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
