from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import traceback

from app.api.deps import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/")
def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "AlphaLearn Backend",
        "database_configured": bool(settings.POSTGRES_SERVER)
    }

@router.get("/db")
def database_health_check(db: Session = Depends(get_db)):
    """Database health check endpoint"""
    try:
        # Simple query to test database connection
        result = db.execute(text("SELECT 1 as test"))
        test_value = result.scalar()
        
        if test_value == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "database_url": f"postgresql://{settings.POSTGRES_USER}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
            }
        else:
            return {
                "status": "error",
                "database": "connection_failed",
                "message": "Database query returned unexpected result"
            }
    except Exception as e:
        return {
            "status": "error",
            "database": "connection_failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
