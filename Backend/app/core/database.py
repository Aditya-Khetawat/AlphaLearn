from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from app.core.config import settings

# Create the SQLAlchemy engine with proper connection pooling
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_size=5,              # number of persistent connections
    max_overflow=10,          # extra connections if pool is full
    pool_timeout=30,          # seconds to wait before giving up
    pool_recycle=1800,        # refresh connections every 30 mins
    pool_pre_ping=True,       # validate connections before use
    echo=False,               # set to True for SQL logging in development
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# Function to get DB session (for FastAPI dependency injection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Context manager for manual session management (for background tasks)
@contextmanager
def get_db_session():
    """
    Context manager for database sessions - ensures proper cleanup
    Use this for background tasks and services that need manual session control
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Auto-commit on success
    except Exception:
        db.rollback()  # Auto-rollback on error
        raise
    finally:
        db.close()  # Always close the session
