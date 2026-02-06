"""Database configuration and connection management."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/fde_mvp")

# Lazy initialization - only create engine when needed
engine = None
SessionLocal = None
Base = declarative_base()

def get_engine():
    """Get or create database engine."""
    global engine
    if engine is None:
        engine = create_engine(DATABASE_URL)
    return engine

def get_session_local():
    """Get or create session local."""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal

def get_db():
    """Dependency for database sessions."""
    session_local = get_session_local()
    db = session_local()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=get_engine())
