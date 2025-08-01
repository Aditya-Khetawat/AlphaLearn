"""
Script to create database tables for the AlphaLearn application
"""

import logging
import sys
from pathlib import Path

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).parent)
sys.path.append(parent_dir)

from app.core.database import Base, engine
from app.models.models import User, Portfolio, Stock, Position, Transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Create database tables"""
    logger.info("Creating database tables")
    
    # Import all models to ensure they're registered with the metadata
    logger.info("Registered models:")
    for table_name, table in Base.metadata.tables.items():
        logger.info(f" - {table_name}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

if __name__ == "__main__":
    logger.info("Initializing database")
    init_db()
    logger.info("Database initialization complete")
