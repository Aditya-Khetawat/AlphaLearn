"""
Script to test database connection and print connection info
"""
import sys
from pathlib import Path

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

import logging
from sqlalchemy import inspect, text
from app.core.config import settings
from app.core.database import engine, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test connection to the database and print tables"""
    logger.info(f"SQLALCHEMY_DATABASE_URI: {settings.SQLALCHEMY_DATABASE_URI}")
    
    try:
        # Test the connection
        logger.info("Testing database connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info(f"Connection successful! Result: {result.fetchone()}")
        
        # Get existing tables
        logger.info("Checking existing tables...")
        inspector = inspect(engine)
        schemas = inspector.get_schema_names()
        logger.info(f"Available schemas: {schemas}")
        
        for schema in schemas:
            tables = inspector.get_table_names(schema=schema)
            logger.info(f"Tables in schema '{schema}': {tables}")
        
        return True
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    logger.info("Testing database connection...")
    test_connection()
