"""
Enhanced Stock API Endpoints
Following the comprehensive approach from StockManagement.py

Provides:
1. Advanced search with pagination
2. Manual seeding with background tasks
3. Comprehensive statistics
4. Database health checks
5. Individual stock details
6. Force refresh capabilities
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models.models import Stock
from app.schemas.schemas import StockCreate

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def stock_api_info():
    """API information endpoint"""
    return {
        "message": "AlphaLearn Enhanced Stock Trading Platform API",
        "version": "2.0.0",
        "features": [
            "Comprehensive Indian stock database (500+ stocks)",
            "Real-time price updates via Yahoo Finance",
            "NSE API integration",
            "Advanced search with pagination",
            "Automated daily updates",
            "Background task processing"
        ],
        "data_sources": ["NSE API", "Yahoo Finance", "Curated Stock Lists"],
        "coverage": "NSE, BSE Indian Stock Exchanges"
    }

@router.get("/search")
async def search_stocks_enhanced(
    q: str = Query(..., min_length=1, description="Search query (symbol, name, or sector)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db)
):
    """
    Enhanced stock search with fuzzy matching and pagination
    Following StockManagement.py approach
    
    - Searches by symbol, name, and sector
    - Supports pagination
    - Returns comprehensive stock information
    """
    try:
        if len(q.strip()) < 1:
            raise HTTPException(status_code=400, detail="Search query must be at least 1 character")
        
        result = enhanced_stock_service.search_stocks_advanced(db, q.strip(), page, per_page)
        
        # If no results found, log for potential fallback
        if result["total"] == 0:
            logger.info(f"No results found for '{q}' in database")
            # Could implement live API fallback here if needed
        
        return {
            **result,
            "query": q,
            "message": f"Found {result['total']} stocks matching '{q}'"
        }
        
    except Exception as e:
        logger.error(f"Search error for query '{q}': {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/all")
async def get_all_stocks_paginated(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db)
):
    """
    Get all stocks with pagination
    Following StockManagement.py pagination approach
    """
    try:
        result = enhanced_stock_service.search_stocks_advanced(db, "", page, per_page)
        return {
            **result,
            "message": f"Retrieved page {page} of all stocks"
        }
    except Exception as e:
        logger.error(f"Error fetching all stocks: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching stocks: {str(e)}")

@router.post("/seed")
async def seed_stocks_enhanced(
    background_tasks: BackgroundTasks,
    force: bool = Query(False, description="Force refresh even if database has stocks"),
    background: bool = Query(True, description="Run in background"),
    db: Session = Depends(get_db)
):
    """
    Enhanced manual stock database seeding
    Following StockManagement.py background task approach
    
    - Supports force refresh
    - Background task processing
    - Comprehensive data sources
    """
    try:
        if background:
            # Run as background task
            background_tasks.add_task(
                enhanced_stock_service.populate_database_comprehensive, 
                db, 
                force_refresh=force
            )
            return {
                "message": "Enhanced stock seeding started in background",
                "force_refresh": force,
                "status": "processing",
                "data_sources": ["NSE API", "Yahoo Finance", "Curated Lists"]
            }
        else:
            # Run synchronously
            stock_count = await enhanced_stock_service.populate_database_comprehensive(db, force_refresh=force)
            return {
                "message": "Enhanced stock database population completed",
                "total_stocks": stock_count,
                "force_refresh": force,
                "status": "completed"
            }
    except Exception as e:
        logger.error(f"Error in enhanced stock seeding: {e}")
        raise HTTPException(status_code=500, detail=f"Error seeding stocks: {str(e)}")

@router.get("/stats")
async def get_enhanced_stock_statistics(db: Session = Depends(get_db)):
    """
    Enhanced database statistics
    Following StockManagement.py comprehensive stats approach
    
    Returns detailed breakdown by:
    - Total and active stocks
    - Exchange distribution
    - Sector breakdown
    - Price statistics
    """
    try:
        stats = enhanced_stock_service.get_database_stats(db)
        
        return {
            **stats,
            "api_version": "2.0.0",
            "features": {
                "multi_source_data": True,
                "real_time_prices": True,
                "daily_updates": True,
                "comprehensive_search": True
            }
        }
    except Exception as e:
        logger.error(f"Error fetching enhanced statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@router.get("/health")
async def stock_database_health_check(db: Session = Depends(get_db)):
    """
    Database health check endpoint
    Following StockManagement.py health monitoring approach
    """
    try:
        total_stocks = db.query(Stock).count()
        active_stocks = db.query(Stock).filter(Stock.is_active == True).count()
        
        # Health criteria
        is_healthy = total_stocks > 100 and active_stocks > 50
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "total_stocks": total_stocks,
            "active_stocks": active_stocks,
            "health_criteria": {
                "min_total_stocks": 100,
                "min_active_stocks": 50,
                "meets_criteria": is_healthy
            },
            "recommendations": [] if is_healthy else [
                "Run /stocks/seed to populate database",
                "Check data source connectivity"
            ]
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "recommendations": ["Check database connectivity"]
        }

@router.get("/{symbol}")
async def get_stock_details(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get individual stock details
    Following StockManagement.py detailed stock info approach
    """
    try:
        # Convert to uppercase for consistency
        symbol = symbol.upper()
        
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        
        if not stock:
            raise HTTPException(
                status_code=404, 
                detail=f"Stock '{symbol}' not found in database"
            )
        
        return {
            "symbol": stock.symbol,
            "name": stock.name,
            "exchange": stock.exchange,
            "sector": stock.sector,
            "current_price": stock.current_price,
            "previous_close": stock.previous_close,
            "is_active": stock.is_active,
            "created_at": stock.created_at,
            "updated_at": stock.updated_at,
            "price_change": stock.current_price - stock.previous_close if stock.current_price and stock.previous_close else 0,
            "price_change_percent": ((stock.current_price - stock.previous_close) / stock.previous_close * 100) if stock.current_price and stock.previous_close and stock.previous_close != 0 else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock details for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock details: {str(e)}")

@router.get("/sample/top-stocks")
async def get_sample_top_stocks(
    limit: int = Query(10, ge=1, le=50, description="Number of stocks to return"),
    db: Session = Depends(get_db)
):
    """
    Get sample of top stocks for quick testing
    """
    try:
        top_stocks = db.query(Stock)\
                      .filter(Stock.is_active == True)\
                      .order_by(Stock.current_price.desc())\
                      .limit(limit)\
                      .all()
        
        return {
            "message": f"Top {len(top_stocks)} stocks by price",
            "stocks": [
                {
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "current_price": stock.current_price,
                    "sector": stock.sector,
                    "exchange": stock.exchange
                }
                for stock in top_stocks
            ],
            "total_returned": len(top_stocks)
        }
    except Exception as e:
        logger.error(f"Error fetching sample stocks: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching sample stocks: {str(e)}")
