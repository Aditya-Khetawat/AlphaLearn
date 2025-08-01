from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.services.stock_population import populate_stocks_on_startup
from app.services.comprehensive_indian_stocks import populate_all_indian_stocks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AlphaLearn - Stock Trading Platform with COMPREHENSIVE Indian Stock Database (3000+ Stocks)",
    version="3.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# COMPREHENSIVE startup event - Get ALL Indian stocks
@app.on_event("startup")
async def startup_event():
    """
    COMPREHENSIVE FastAPI startup event - populate with ALL Indian stocks
    Target: 3000+ stocks from NSE + BSE using official APIs
    """
    logger.info("🌟 AlphaLearn FastAPI server starting up...")
    logger.info("🚀 Initializing COMPREHENSIVE Indian stock database...")
    logger.info("🎯 Target: 3000+ stocks from NSE + BSE APIs")
    logger.info("📊 Data sources: NSE APIs, BSE data, Yahoo Finance enrichment")
    
    # Use comprehensive stock population service to get ALL Indian stocks
    try:
        stock_count = await populate_all_indian_stocks()
        logger.info(f"✅ COMPREHENSIVE stock database initialization completed!")
        logger.info(f"🎯 Database now contains {stock_count} Indian stocks (Target: 3000+)")
        logger.info("📊 Includes NSE + BSE with real-time prices from yfinance")
        
        if stock_count > 1000:
            logger.info("🎉 SUCCESS: You now have a truly comprehensive Indian stock database!")
        else:
            logger.warning("⚠️  Lower than expected stock count. Some APIs may have failed.")
            
    except Exception as e:
        logger.error(f"❌ Comprehensive stock database initialization failed: {e}")
        logger.info("🔄 Falling back to basic stock population...")
        
        # Fallback to original method
        try:
            await populate_stocks_on_startup()
            logger.info("✅ Fallback stock population completed!")
        except Exception as fallback_error:
            logger.error(f"❌ Fallback also failed: {fallback_error}")
            logger.info("⚠️  Server will continue running with limited stock data")

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
