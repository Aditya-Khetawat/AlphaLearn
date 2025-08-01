from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn
import logging
import os

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.services.stock_population import populate_stocks_on_startup
from app.services.comprehensive_indian_stocks import populate_all_indian_stocks
from app.services.price_scheduler import price_scheduler
from app.services.market_timing import market_timer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AlphaLearn - Stock Trading Platform for Indian Students with Comprehensive Indian Stock Market Coverage",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS - Specific to your deployment domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # for local dev
        "https://alpha-learn-xxv4.vercel.app"  # for production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Enhanced startup event with comprehensive stock population
@app.on_event("startup")
async def startup_event():
    """
    Railway-optimized startup event - lightweight initialization
    """
    logger.info("🌟 AlphaLearn FastAPI server starting up...")
    
    # Check if we're in Railway environment
    is_railway = os.getenv("RAILWAY_ENVIRONMENT_NAME") is not None
    
    if is_railway:
        logger.info("🚂 Railway deployment detected - using lightweight startup")
        logger.info("✅ Server ready for health checks")
        return
    
    logger.info("🚀 Initializing comprehensive Indian stock database...")
    logger.info("📊 Data sources: NSE API, Yahoo Finance, curated stock lists")
    
    # Use comprehensive stock population service to get ALL Indian stocks
    try:
        stock_count = await populate_all_indian_stocks()
        logger.info("✅ COMPREHENSIVE stock database initialization completed!")
        logger.info(f"🎯 Database now contains {stock_count} Indian stocks (Target: 3000+)")
        logger.info("💹 Includes NSE + BSE with real-time prices from yfinance")
        
        # Start real-time price updates if market conditions are favorable
        market_status = market_timer.get_market_status_message()
        logger.info(f"📊 Market Status: {market_status['message']}")
        
        # Auto-start price scheduler
        try:
            price_scheduler.start_scheduler()
            logger.info("🚀 Real-time price update scheduler started!")
            logger.info("⏰ Updates every 20s during market hours, 5min when closed")
        except Exception as scheduler_error:
            logger.warning(f"⚠️  Could not start price scheduler: {scheduler_error}")
            logger.info("💡 You can manually start it via /api/v1/stocks/start-real-time")
        
    except Exception as e:
        logger.error(f"❌ Enhanced stock database initialization failed: {e}")
        logger.info("🔄 Falling back to basic stock population...")
        
        # Fallback to original method
        try:
            await populate_stocks_on_startup()
            logger.info("✅ Fallback stock population completed!")
        except Exception as fallback_error:
            logger.error(f"❌ Fallback also failed: {fallback_error}")
            logger.info("⚠️  Server will continue running with limited stock data")

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint for health check
@app.get("/")
def root():
    return {
        "message": "AlphaLearn Backend API is running!",
        "status": "healthy",
        "version": "2.0.0",
        "docs_url": "/docs"
    }

# Dedicated health check endpoint for Railway
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "alphalearn-backend",
        "version": "2.0.0"
    }

# Database health check endpoint
@app.get("/db-health")
def database_health_check():
    try:
        from app.api.deps import get_db
        from app.models.models import User
        
        # Try to get a database session
        db = next(get_db())
        
        # Try a simple query
        count = db.query(User).count()
        
        return {
            "status": "ok",
            "database": "connected",
            "user_count": count,
            "database_url": settings.SQLALCHEMY_DATABASE_URI[:50] + "..." if settings.SQLALCHEMY_DATABASE_URI else "Not configured"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e),
            "database_url": settings.SQLALCHEMY_DATABASE_URI[:50] + "..." if settings.SQLALCHEMY_DATABASE_URI else "Not configured"
        }

# Database initialization endpoint
@app.post("/init-db")
def initialize_database():
    """Initialize database tables if they don't exist"""
    try:
        from app.core.database import Base, engine
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        return {
            "status": "success",
            "message": "Database tables created successfully",
            "timestamp": "2025-08-02T12:00:00Z"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create database tables: {str(e)}"
        }

# CORS test endpoint
@app.get("/cors-test")
def cors_test():
    return {
        "message": "CORS is working!",
        "timestamp": "2025-08-02T12:00:00Z",
        "cors_enabled": True,
        "deployment_version": "v2.8",
        "cors_method": "specific_domain_only",
        "allowed_origins": ["http://localhost:3000", "https://alpha-learn-xxv4.vercel.app"],
        "new_endpoints": ["/auth/login-json", "/db-health", "/init-db"],
        "database_url_configured": bool(settings.SQLALCHEMY_DATABASE_URI),
        "env_vars_available": {
            "DATABASE_URL": bool(os.getenv("DATABASE_URL")),
            "POSTGRES_SERVER": bool(os.getenv("POSTGRES_SERVER")),
            "RAILWAY_ENVIRONMENT": bool(os.getenv("RAILWAY_ENVIRONMENT_NAME"))
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)