"""
RAG Service
Retrieval-Augmented Generation service using TF-IDF/BM25 for document retrieval.
Always returns sources; refuses to answer if confidence is low.
"""
import os
import logging
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FDE RAG API",
    description="Retrieval-Augmented Generation API with citation discipline",
    version="1.0.0"
)


class AskRequest(BaseModel):
    """Request schema for asking questions"""
    question: str = Field(..., min_length=1, description="Question to ask")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of sources to retrieve")
    confidence_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum confidence threshold")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "How does the ingestion service work?",
                "top_k": 3,
                "confidence_threshold": 0.3
            }
        }


class Source(BaseModel):
    """Source document model"""
    document: str
    content: str
    score: float
    excerpt: str


class AskResponse(BaseModel):
    """Response schema for questions"""
    question: str
    answer: str
    sources: List[Source]
    confidence: float
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "How does the system work?",
                "answer": "Based on the documentation...",
                "sources": [
                    {
                        "document": "architecture.md",
                        "content": "Full content...",
                        "score": 0.85,
                        "excerpt": "Relevant excerpt..."
                    }
                ],
                "confidence": 0.85,
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    documents_loaded: int
    retriever_ready: bool


class DocumentRetriever:
    """TF-IDF based document retriever"""
    
    def __init__(self, docs_dir: str = "/data/docs"):
        self.docs_dir = Path(docs_dir)
        self.documents = []
        self.document_names = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_documents()
    
    def load_documents(self):
        """Load documents from the docs directory"""
        logger.info(f"Loading documents from {self.docs_dir}")
        
        # Create docs directory if it doesn't exist
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Load all text and markdown files
        for ext in ['*.txt', '*.md']:
            for doc_path in self.docs_dir.glob(ext):
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            self.documents.append(content)
                            self.document_names.append(doc_path.name)
                            logger.info(f"Loaded document: {doc_path.name}")
                except Exception as e:
                    logger.error(f"Failed to load {doc_path}: {e}")
        
        # If no documents found, create a sample one
        if not self.documents:
            logger.warning("No documents found, creating sample documentation")
            sample_doc = """
# FDE Platform Documentation

## Overview
The FDE Platform is a comprehensive data engineering and machine learning system.

## Components

### Ingest Service
The ingest service loads data from CSV files or APIs, validates the schema using Pydantic,
writes to PostgreSQL database, and generates JSON quality reports.

Key features:
- Idempotent writes using ON CONFLICT
- Schema validation with Pydantic
- Quality report generation
- Blocks writes when required fields are missing

### API Service
The API service provides prediction endpoints using FastAPI.

Endpoints:
- /health: Health check endpoint
- /predict: Prediction endpoint with Pydantic validation

The service uses structured logging and includes basic tests.

### RAG Service
The RAG service provides retrieval-augmented generation using TF-IDF.
It always returns sources and refuses to answer when confidence is low.

### UI Service
The UI service is built with Streamlit and provides three tabs:
- Dashboard: Shows KPIs from curated SQL views
- Prediction: Calls the API /predict endpoint
- Copilot: Calls the RAG /ask endpoint and displays sources

## Database Schema
The system uses PostgreSQL with the following tables:
- raw_data: Stores ingested metrics
- predictions: Stores prediction results
- kpi_daily: Curated view for daily KPIs

## Running the Platform
Use Docker Compose to run the entire platform:
```
docker compose up --build
```

This will start all services: PostgreSQL, Ingest, API, RAG, and UI.
"""
            sample_path = self.docs_dir / "platform_docs.md"
            with open(sample_path, 'w') as f:
                f.write(sample_doc)
            
            self.documents.append(sample_doc)
            self.document_names.append(sample_path.name)
            logger.info("Created sample documentation")
        
        # Build TF-IDF index
        if self.documents:
            self.build_index()
    
    def build_index(self):
        """Build TF-IDF index for retrieval"""
        logger.info(f"Building TF-IDF index for {len(self.documents)} documents")
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english'
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
        logger.info("TF-IDF index built successfully")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve top-k most relevant documents"""
        if not self.documents:
            logger.warning("No documents available for retrieval")
            return []
        
        # Vectorize query
        query_vec = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Prepare results
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            content = self.documents[idx]
            
            # Create excerpt (first 200 chars that contain query terms)
            query_terms = query.lower().split()
            content_lower = content.lower()
            
            excerpt_start = 0
            for term in query_terms:
                pos = content_lower.find(term)
                if pos != -1:
                    excerpt_start = max(0, pos - 50)
                    break
            
            excerpt = content[excerpt_start:excerpt_start + 200] + "..."
            
            results.append({
                "document": self.document_names[idx],
                "content": content,
                "score": score,
                "excerpt": excerpt.strip()
            })
        
        return results


# Global retriever instance
retriever = DocumentRetriever()


def generate_answer(query: str, sources: List[Dict], confidence: float) -> str:
    """Generate answer based on retrieved sources"""
    
    # If confidence is too low, refuse to answer
    if confidence < 0.3 or not sources:
        return "I don't have enough supporting documentation to answer this question confidently. Please rephrase your question or consult the documentation directly."
    
    # Simple answer generation: summarize the top source
    top_source = sources[0]
    
    answer = f"Based on the documentation, {top_source['excerpt']}\n\n"
    answer += f"This information comes from {top_source['document']} with a confidence score of {confidence:.2f}."
    
    return answer


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    
    return HealthResponse(
        status="healthy",
        documents_loaded=len(retriever.documents),
        retriever_ready=retriever.vectorizer is not None
    )


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """
    Ask a question and get an answer with sources.
    Always returns sources; refuses to answer if confidence is low.
    """
    logger.info(f"Question received: {request.question}")
    
    try:
        # Retrieve relevant documents
        sources = retriever.retrieve(request.question, request.top_k)
        
        # Calculate overall confidence (max score of retrieved sources)
        confidence = max([s["score"] for s in sources]) if sources else 0.0
        
        # Generate answer with citation discipline
        answer = generate_answer(request.question, sources, confidence)
        
        # Create source objects
        source_objects = [
            Source(
                document=s["document"],
                content=s["content"],
                score=s["score"],
                excerpt=s["excerpt"]
            )
            for s in sources
        ]
        
        # Create response
        response = AskResponse(
            question=request.question,
            answer=answer,
            sources=source_objects,
            confidence=confidence
        )
        
        logger.info(f"Answer generated with {len(sources)} sources, confidence: {confidence:.3f}")
        return response
        
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question answering failed: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FDE RAG API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "ask": "/ask",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
