"""
Stock statistics and monitoring endpoints for AlphaLearn

This module provides endpoints to monitor stock population status,
get statistics, and manually trigger stock updates if needed.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from app.core.database import get_db
from app.models.models import Stock
from app.services.stock_population import ComprehensiveStockPopulator

router = APIRouter()

@router.get("/stocks/stats", response_model=Dict[str, Any])
def get_stock_statistics(db: Session = Depends(get_db)):
    """
    Get comprehensive stock database statistics
    """
    try:
        # Basic counts
        total_stocks = db.query(Stock).count()
        active_stocks = db.query(Stock).filter(Stock.is_active == True).count()
        
        # Exchange breakdown
        exchange_stats = db.query(
            Stock.exchange, 
            func.count(Stock.id).label('count')
        ).group_by(Stock.exchange).all()
        
        # Sector breakdown
        sector_stats = db.query(
            Stock.sector, 
            func.count(Stock.id).label('count')
        ).group_by(Stock.sector).all()
        
        # Price statistics
        price_stats = db.query(
            func.min(Stock.current_price).label('min_price'),
            func.max(Stock.current_price).label('max_price'),
            func.avg(Stock.current_price).label('avg_price')
        ).first()
        
        return {
            "total_stocks": total_stocks,
            "active_stocks": active_stocks,
            "exchange_breakdown": {
                exchange: count for exchange, count in exchange_stats
            },
            "sector_breakdown": {
                sector or "Unknown": count for sector, count in sector_stats
            },
            "price_statistics": {
                "min_price": float(price_stats.min_price) if price_stats.min_price else 0,
                "max_price": float(price_stats.max_price) if price_stats.max_price else 0,
                "avg_price": float(price_stats.avg_price) if price_stats.avg_price else 0
            },
            "status": "healthy" if total_stocks > 100 else "needs_population"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock statistics: {str(e)}")


@router.get("/stocks/health")
def check_stock_health(db: Session = Depends(get_db)):
    """
    Quick health check for stock database
    """
    try:
        total_stocks = db.query(Stock).count()
        
        if total_stocks == 0:
            return {
                "status": "empty",
                "message": "No stocks in database. Run stock population.",
                "total_stocks": 0
            }
        elif total_stocks < 50:
            return {
                "status": "low",
                "message": "Low stock count. Consider running stock population.",
                "total_stocks": total_stocks
            }
        elif total_stocks < 200:
            return {
                "status": "medium",
                "message": "Moderate stock coverage.",
                "total_stocks": total_stocks
            }
        else:
            return {
                "status": "excellent",
                "message": "Comprehensive stock coverage available.",
                "total_stocks": total_stocks
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}",
            "total_stocks": 0
        }


@router.post("/stocks/populate")
async def trigger_stock_population():
    """
    Manually trigger stock population (use with caution in production)
    """
    try:
        populator = ComprehensiveStockPopulator()
        await populator.populate_stocks()
        
        return {
            "status": "success",
            "message": "Stock population completed successfully",
            "new_stocks_added": populator.total_stocks_added,
            "stocks_updated": populator.total_stocks_updated,
            "failed_stocks": len(populator.failed_stocks)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Stock population failed: {str(e)}"
        )


@router.get("/stocks/sample")
def get_sample_stocks(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get a sample of stocks from the database
    """
    try:
        stocks = db.query(Stock).limit(limit).all()
        
        return {
            "count": len(stocks),
            "stocks": [
                {
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "current_price": stock.current_price,
                    "exchange": stock.exchange,
                    "sector": stock.sector
                }
                for stock in stocks
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sample stocks: {str(e)}")


@router.get("/stocks/search-test")
def test_stock_search(query: str = "bank", db: Session = Depends(get_db)):
    """
    Test stock search functionality
    """
    try:
        # Simple search implementation
        stocks = db.query(Stock).filter(
            (Stock.name.ilike(f"%{query}%")) | 
            (Stock.symbol.ilike(f"%{query}%"))
        ).limit(20).all()
        
        return {
            "query": query,
            "count": len(stocks),
            "stocks": [
                {
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "current_price": stock.current_price,
                    "exchange": stock.exchange
                }
                for stock in stocks
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search test failed: {str(e)}")
