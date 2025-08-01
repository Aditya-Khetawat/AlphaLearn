import logging
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.initial_data import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init() -> None:
    """Initialize database with seed data"""
    db = SessionLocal()
    try:
        logger.info("Creating initial data")
        init_db(db)
        logger.info("Initial data created")
    finally:
        db.close()

def main() -> None:
    logger.info("Initializing database with sample data")
    init()
    logger.info("Database initialization completed")

if __name__ == "__main__":
    main()
