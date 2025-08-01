from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Set up CORS - More permissive for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)