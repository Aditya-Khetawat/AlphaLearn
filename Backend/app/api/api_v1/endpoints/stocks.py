from typing import Any, List, Optional, Dict
import math
import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_active_admin
from app.crud import stock as stock_crud
from app.models.models import User, Stock
from app.schemas.schemas import Stock as StockSchema, StockCreate, StockUpdate
from app.core.json_utils import safe_jsonable_encoder, SafeJSONResponse
from app.services.real_time_prices import real_time_fetcher as old_fetcher
from app.services.real_time_fetcher import real_time_fetcher
from app.services.market_timing import market_timer
from app.services.price_scheduler import price_scheduler
from app.core.timezone_utils import format_ist_for_api

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_class=SafeJSONResponse)
async def read_stocks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    exchange: Optional[str] = Query(None, description="Filter by exchange (NSE or BSE)"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    refresh_trending: bool = Query(False, description="Refresh prices for trending stocks in the list")
) -> Any:
    """
    Retrieve stocks with optional filters and on-demand price updates (public endpoint)
    """
    try:
        stocks = stock_crud.get_stocks(
            db=db, 
            skip=skip, 
            limit=limit, 
            exchange=exchange,
            sector=sector
        )
        
        # 🎯 OPTIONAL ON-DEMAND UPDATE: Refresh trending stocks if requested
        if refresh_trending and stocks:
            try:
                # Update only the first 20 stocks (trending/top stocks) to avoid API overuse
                trending_stocks = stocks[:20]
                symbols_to_update = [stock.symbol for stock in trending_stocks]
                
                logger.info(f"📈 Refreshing prices for {len(symbols_to_update)} trending stocks on-demand")
                
                updated_count = await real_time_fetcher.update_database_prices(db, symbols_to_update)
                logger.info(f"✅ Updated {updated_count} trending stock prices on-demand")
                
                # Refresh the stocks from database to get updated prices
                stocks = stock_crud.get_stocks(
                    db=db, 
                    skip=skip, 
                    limit=limit, 
                    exchange=exchange,
                    sector=sector
                )
                
            except Exception as price_error:
                logger.warning(f"⚠️ Could not update trending stock prices: {price_error}")
                # Continue with existing prices if update fails
    
    except Exception as e:
        # Return demo data if database is unavailable
        return safe_jsonable_encoder([
            {
                "id": 1,
                "symbol": "TCS",
                "name": "Tata Consultancy Services Limited",
                "current_price": 3250.50,
                "previous_close": 3200.00,
                "price_change": 50.50,
                "price_change_percent": 1.58,
                "exchange": "NSE",
                "sector": "Information Technology",
                "is_active": True,
                "last_updated": "2025-07-27T10:00:00"
            },
            {
                "id": 2,
                "symbol": "RELIANCE",
                "name": "Reliance Industries Limited",
                "current_price": 2845.75,
                "previous_close": 2880.00,
                "price_change": -34.25,
                "price_change_percent": -1.19,
                "exchange": "NSE",
                "sector": "Energy",
                "is_active": True,
                "last_updated": "2025-07-27T10:00:00"
            },
            {
                "id": 3,
                "symbol": "HDFCBANK",
                "name": "HDFC Bank Limited",
                "current_price": 1650.20,
                "previous_close": 1630.50,
                "price_change": 19.70,
                "price_change_percent": 1.21,
                "exchange": "NSE",
                "sector": "Financial Services",
                "is_active": True,
                "last_updated": "2025-07-27T10:00:00"
            }
        ])
    
    # Calculate price change metrics for each stock with NaN safety
    result = []
    for stock in stocks:
        stock_data = StockSchema.from_orm(stock)
        
        # Clean any NaN values from the base stock data
        if stock.current_price is not None and (math.isnan(stock.current_price) or math.isinf(stock.current_price)):
            stock_data.current_price = 0.0
        if stock.previous_close is not None and (math.isnan(stock.previous_close) or math.isinf(stock.previous_close)):
            stock_data.previous_close = 0.0
            
        if (stock.previous_close and stock.previous_close > 0 and 
            stock.current_price is not None and stock.current_price > 0):
            try:
                price_change = stock.current_price - stock.previous_close
                price_change_percent = (price_change / stock.previous_close) * 100
                
                # Ensure no NaN or infinity values
                if not (math.isnan(price_change) or math.isinf(price_change)):
                    stock_data.price_change = price_change
                else:
                    stock_data.price_change = 0.0
                    
                if not (math.isnan(price_change_percent) or math.isinf(price_change_percent)):
                    stock_data.price_change_percent = price_change_percent
                else:
                    stock_data.price_change_percent = 0.0
            except (ZeroDivisionError, ValueError, TypeError):
                stock_data.price_change = 0.0
                stock_data.price_change_percent = 0.0
        else:
            stock_data.price_change = 0.0
            stock_data.price_change_percent = 0.0
        result.append(stock_data)
    
    return safe_jsonable_encoder(result)


@router.post("/", response_model=StockSchema)
def create_stock(
    *,
    db: Session = Depends(get_db),
    stock_in: StockCreate,
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Create new stock (admin only)
    """
    stock = stock_crud.get_by_symbol(db, symbol=stock_in.symbol)
    if stock:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Stock with symbol {stock_in.symbol} already exists",
        )
    stock = stock_crud.create(db, obj_in=stock_in)
    return stock


@router.get("/search", response_class=SafeJSONResponse)
async def search_stocks(
    *,
    db: Session = Depends(get_db),
    query: str = Query(..., min_length=1),
    limit: int = 1000,
    refresh_prices: bool = Query(True, description="Auto-refresh prices for search results")
) -> Any:
    """
    Search stocks by name or symbol with on-demand price updates (public endpoint)
    """
    try:
        stocks = stock_crud.search(db=db, query=query, limit=limit)
        
        # 🎯 ON-DEMAND PRICE UPDATE: Update prices for search results
        if refresh_prices and stocks:
            try:
                # Get symbols from search results (limit to top 20 for API efficiency)
                symbols_to_update = [stock.symbol for stock in stocks[:20]]
                logger.info(f"🔍 User searched '{query}' - updating prices for {len(symbols_to_update)} results on-demand")
                
                # Update prices for these specific stocks
                updated_count = await real_time_fetcher.update_database_prices(db, symbols_to_update)
                logger.info(f"✅ Updated {updated_count} stock prices on-demand for search results")
                
                # Refresh the stocks from database to get updated prices
                stocks = stock_crud.search(db=db, query=query, limit=limit)
                
            except Exception as price_error:
                logger.warning(f"⚠️ Could not update prices for search results: {price_error}")
                # Continue with existing prices if update fails
        
    except Exception as e:
        # Return demo search results if database is unavailable
        query_lower = query.lower()
        demo_stocks = [
            {
                "id": 1,
                "symbol": "TCS",
                "name": "Tata Consultancy Services Limited",
                "current_price": 3250.50,
                "previous_close": 3200.00,
                "price_change": 50.50,
                "price_change_percent": 1.58,
                "exchange": "NSE",
                "sector": "Information Technology",
                "is_active": True,
                "last_updated": "2025-07-27T10:00:00"
            },
            {
                "id": 2,
                "symbol": "RELIANCE",
                "name": "Reliance Industries Limited",
                "current_price": 2845.75,
                "previous_close": 2880.00,
                "price_change": -34.25,
                "price_change_percent": -1.19,
                "exchange": "NSE",
                "sector": "Energy",
                "is_active": True,
                "last_updated": "2025-07-27T10:00:00"
            },
            {
                "id": 3,
                "symbol": "HDFCBANK",
                "name": "HDFC Bank Limited",
                "current_price": 1650.20,
                "previous_close": 1630.50,
                "price_change": 19.70,
                "price_change_percent": 1.21,
                "exchange": "NSE",
                "sector": "Financial Services",
                "is_active": True,
                "last_updated": "2025-07-27T10:00:00"
            }
        ]
        
        # Filter demo stocks based on search query
        filtered_stocks = [
            stock for stock in demo_stocks 
            if query_lower in stock["symbol"].lower() or query_lower in stock["name"].lower()
        ]
        
        return safe_jsonable_encoder(filtered_stocks if filtered_stocks else demo_stocks)
    
    # Calculate price change metrics for each stock with NaN safety (same as main endpoint)
    result = []
    for stock in stocks:
        stock_data = StockSchema.from_orm(stock)
        
        # Clean any NaN values from the base stock data
        if stock.current_price is not None and (math.isnan(stock.current_price) or math.isinf(stock.current_price)):
            stock_data.current_price = 0.0
            
        if stock.previous_close is not None and (math.isnan(stock.previous_close) or math.isinf(stock.previous_close)):
            stock_data.previous_close = 0.0
            
        if (stock.previous_close and stock.previous_close > 0 and 
            stock.current_price is not None and stock.current_price > 0):
            try:
                price_change = stock.current_price - stock.previous_close
                price_change_percent = (price_change / stock.previous_close) * 100
                
                # Ensure no NaN or infinity values
                if not (math.isnan(price_change) or math.isinf(price_change)):
                    stock_data.price_change = price_change
                else:
                    stock_data.price_change = 0.0
                    
                if not (math.isnan(price_change_percent) or math.isinf(price_change_percent)):
                    stock_data.price_change_percent = price_change_percent
                else:
                    stock_data.price_change_percent = 0.0
            except (ZeroDivisionError, ValueError, TypeError):
                stock_data.price_change = 0.0
                stock_data.price_change_percent = 0.0
        else:
            stock_data.price_change = 0.0
            stock_data.price_change_percent = 0.0
            
        result.append(stock_data)
    
    return safe_jsonable_encoder(result)


# Real-time market status and price endpoints (must be before /{stock_id} route)
@router.get("/market-status", response_class=SafeJSONResponse)
def get_market_status() -> Any:
    """
    Get current Indian stock market status and timing information
    """
    try:
        market_status = market_timer.get_market_status_message()
        scheduler_status = price_scheduler.get_scheduler_status()
        
        return safe_jsonable_encoder({
            "market": market_status,
            "real_time_updates": scheduler_status,
            "timestamp": market_timer.get_current_ist_time().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        return safe_jsonable_encoder({
            "market": {
                "status": "unknown",
                "message": "Unable to determine market status",
                "session_type": "unknown"
            },
            "real_time_updates": {
                "scheduler_running": False,
                "error": str(e)
            },
            "timestamp": format_ist_for_api()
        })


@router.get("/real-time-prices", response_class=SafeJSONResponse)
async def get_real_time_stock_prices(
    symbols: str = Query(..., description="Comma-separated stock symbols"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get real-time prices for specific stocks
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        
        if not symbol_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one symbol must be provided"
            )
        
        if len(symbol_list) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 20 symbols allowed per request"
            )
            
        # Check market status
        market_session = market_timer.get_market_session()
        
        # Get real-time prices
        price_data = await real_time_fetcher.get_real_time_prices(symbol_list, force_refresh=market_session.is_open)
        
        # Format response
        response_data = []
        for symbol in symbol_list:
            if symbol in price_data:
                data = price_data[symbol]
                response_data.append({
                    "symbol": data.symbol,
                    "current_price": data.current_price,
                    "previous_close": data.previous_close,
                    "price_change": data.price_change,
                    "price_change_percent": data.price_change_percent,
                    "volume": data.volume,
                    "last_updated": data.last_updated.isoformat() if data.last_updated else None
                })
            else:
                # Return stock from database if real-time data not available
                try:
                    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
                    if stock:
                        response_data.append({
                            "symbol": stock.symbol,
                            "current_price": stock.current_price,
                            "previous_close": stock.previous_close,
                            "price_change": stock.price_change,
                            "price_change_percent": stock.price_change_percent,
                            "volume": stock.volume,
                            "last_updated": stock.last_updated.isoformat() if stock.last_updated else None
                        })
                    else:
                        response_data.append({
                            "symbol": symbol,
                            "error": "Stock not found"
                        })
                except Exception as db_error:
                    logger.warning(f"Database error for {symbol}: {db_error}")
                    response_data.append({
                        "symbol": symbol,
                        "error": "Data temporarily unavailable"
                    })
        
        return safe_jsonable_encoder({
            "data": response_data,
            "market_status": market_session.session_type,
            "is_market_open": market_session.is_open,
            "timestamp": format_ist_for_api()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting real-time prices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get real-time prices: {str(e)}"
        )


@router.post("/start-real-time", response_model=Dict[str, Any])
def start_real_time_updates(
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Start real-time price updates (admin only)
    """
    try:
        price_scheduler.start_scheduler()
        return {
            "message": "Real-time price updates started",
            "status": "started"
        }
    except Exception as e:
        logger.error(f"Error starting real-time updates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start real-time updates: {str(e)}"
        )


@router.post("/stop-real-time", response_model=Dict[str, Any])
def stop_real_time_updates(
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Stop real-time price updates (admin only)
    """
    try:
        price_scheduler.stop_scheduler()
        return {
            "message": "Real-time price updates stopped",
            "status": "stopped"
        }
    except Exception as e:
        logger.error(f"Error stopping real-time updates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop real-time updates: {str(e)}"
        )


@router.get("/{stock_id}", response_class=SafeJSONResponse)
async def read_stock(
    *,
    db: Session = Depends(get_db),
    stock_id: int,
    refresh_price: bool = Query(True, description="Auto-refresh price when viewing stock details")
) -> Any:
    """
    Get stock by ID with on-demand price update (public endpoint)
    """
    try:
        stock = stock_crud.get_by_id(db, stock_id=stock_id)
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock not found",
            )
        
        # 🎯 ON-DEMAND PRICE UPDATE: Update price when user views stock details
        if refresh_price:
            try:
                logger.info(f"👁️ User viewing stock details for {stock.symbol} - updating price on-demand")
                
                # Update price for this specific stock
                updated_count = await real_time_fetcher.update_database_prices(db, [stock.symbol])
                logger.info(f"✅ Updated price for {stock.symbol} on-demand")
                
                # Refresh the stock from database to get updated price
                stock = stock_crud.get_by_id(db, stock_id=stock_id)
                
            except Exception as price_error:
                logger.warning(f"⚠️ Could not update price for {stock.symbol}: {price_error}")
                # Continue with existing price if update fails
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        # Return demo stock data if database is unavailable
        demo_stocks = {
            1: {
                "id": 1,
                "symbol": "TCS",
                "name": "Tata Consultancy Services Limited",
                "current_price": 3250.50,
                "previous_close": 3200.00,
                "price_change": 50.50,
                "price_change_percent": 1.58,
                "exchange": "NSE",
                "sector": "Information Technology",
                "is_active": True,
                "last_updated": "2025-07-27T10:00:00"
            },
            2: {
                "id": 2,
                "symbol": "RELIANCE",
                "name": "Reliance Industries Limited",
                "current_price": 2845.75,
                "previous_close": 2880.00,
                "price_change": -34.25,
                "price_change_percent": -1.19,
                "exchange": "NSE",
                "sector": "Energy",
                "is_active": True,
                "last_updated": "2025-07-27T10:00:00"
            }
        }
        
        if stock_id in demo_stocks:
            return safe_jsonable_encoder(demo_stocks[stock_id])
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock not found",
            )
    
    # Calculate price change metrics with NaN safety
    stock_data = StockSchema.from_orm(stock)
    
    # Clean any NaN values from the base stock data
    if stock.current_price is not None and (math.isnan(stock.current_price) or math.isinf(stock.current_price)):
        stock_data.current_price = 0.0
        
    if stock.previous_close is not None and (math.isnan(stock.previous_close) or math.isinf(stock.previous_close)):
        stock_data.previous_close = 0.0
        
    if (stock.previous_close and stock.previous_close > 0 and 
        stock.current_price is not None and stock.current_price > 0):
        try:
            price_change = stock.current_price - stock.previous_close
            price_change_percent = (price_change / stock.previous_close) * 100
            
            # Ensure no NaN or infinity values
            if not (math.isnan(price_change) or math.isinf(price_change)):
                stock_data.price_change = price_change
            else:
                stock_data.price_change = 0.0
                
            if not (math.isnan(price_change_percent) or math.isinf(price_change_percent)):
                stock_data.price_change_percent = price_change_percent
            else:
                stock_data.price_change_percent = 0.0
        except (ZeroDivisionError, ValueError, TypeError):
            stock_data.price_change = 0.0
            stock_data.price_change_percent = 0.0
    else:
        stock_data.price_change = 0.0
        stock_data.price_change_percent = 0.0
    
    return safe_jsonable_encoder(stock_data)


@router.put("/{stock_id}", response_model=StockSchema)
def update_stock(
    *,
    db: Session = Depends(get_db),
    stock_id: int,
    stock_in: StockUpdate,
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Update a stock (admin only)
    """
    stock = stock_crud.get_by_id(db, stock_id=stock_id)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found",
        )
    stock = stock_crud.update(db=db, db_obj=stock, obj_in=stock_in)
    return stock


@router.get("/refresh/{symbol}", response_model=StockSchema)
def refresh_stock(
    *,
    db: Session = Depends(get_db),
    symbol: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Refresh stock data from Yahoo Finance
    """
    stock = stock_crud.get_by_symbol(db, symbol=symbol)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found",
        )
    
    stock = stock_crud.refresh_stock_data(db=db, stock=stock)
    return stock


@router.post("/refresh-all", response_model=Dict[str, Any])
def refresh_all_stocks(
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Refresh all stocks from Yahoo Finance (admin only)
    """
    # Run in background to avoid timeout
    background_tasks.add_task(stock_crud.refresh_all_stocks, db)
    
    return {
        "message": "Stock refresh started in background",
        "status": "processing"
    }


@router.post("/update-prices", response_model=Dict[str, Any])
def update_stock_prices(
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    quick: bool = Query(False, description="Quick update for popular stocks only"),
) -> Any:
    """
    Update real-time stock prices (public endpoint for development)
    """
    async def run_price_update():
        if quick:
            updated = await real_time_fetcher.update_popular_stocks(50)
            return {"updated_count": updated, "type": "quick"}
        else:
            # For full update, we'd implement update_all_active_stocks method
            updated = await real_time_fetcher.update_popular_stocks(200)  # Update more stocks
            return {"updated_count": updated, "type": "extended"}
    
    # Run the async function in background
    background_tasks.add_task(lambda: asyncio.run(run_price_update()))
    
    update_type = "quick (50 popular stocks)" if quick else "extended (200 stocks)"
    return {
        "message": f"Price update started in background - {update_type}",
        "status": "processing"
    }


@router.get("/{symbol}/history", response_class=SafeJSONResponse)
async def get_stock_history(
    symbol: str,
    timeframe: str = Query("1d", description="Timeframe: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y"),
    interval: str = Query("1d", description="Data interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get historical price data for a stock
    """
    try:
        from app.services.stock_market import StockMarketService
        
        # Convert symbol to uppercase for consistency
        symbol = symbol.upper()
        
        # Check if stock exists in database
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            raise HTTPException(
                status_code=404,
                detail=f"Stock '{symbol}' not found in database"
            )
        
        # Fetch historical data
        historical_data = StockMarketService.fetch_stock_history(
            symbol=symbol,
            period=timeframe,
            interval=interval
        )
        
        if historical_data is None or historical_data.empty:
            logger.warning(f"No historical data available for {symbol}")
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "data": [],
                "message": "No historical data available"
            }
        
        # Convert DataFrame to list of dictionaries
        data_list = []
        for index, row in historical_data.iterrows():
            # Format date/datetime appropriately based on interval
            if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
                # For intraday intervals, include time
                date_str = index.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # For daily and longer intervals, just date
                date_str = index.strftime("%Y-%m-%d")
            
            data_list.append({
                "date": date_str,
                "timestamp": int(index.timestamp() * 1000),  # Add timestamp in milliseconds
                "open": round(float(row['Open']), 2) if not math.isnan(row['Open']) else None,
                "high": round(float(row['High']), 2) if not math.isnan(row['High']) else None,
                "low": round(float(row['Low']), 2) if not math.isnan(row['Low']) else None,
                "close": round(float(row['Close']), 2) if not math.isnan(row['Close']) else None,
                "volume": int(row['Volume']) if not math.isnan(row['Volume']) else 0
            })
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "interval": interval,
            "data": data_list,
            "count": len(data_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch historical data: {str(e)}"
        )


@router.get("/symbol/{symbol}", response_class=SafeJSONResponse)
async def get_stock_by_symbol(
    symbol: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get stock details by symbol
    """
    try:
        # Convert symbol to uppercase for consistency
        symbol = symbol.upper()
        
        # Find stock by symbol
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            raise HTTPException(
                status_code=404,
                detail=f"Stock '{symbol}' not found in database"
            )
        
        return {
            "id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "exchange": stock.exchange,
            "sector": stock.sector,
            "current_price": stock.current_price,
            "previous_close": stock.previous_close,
            "is_active": stock.is_active,
            "last_updated": stock.last_updated,
            "price_change": stock.current_price - stock.previous_close if stock.current_price and stock.previous_close else 0,
            "price_change_percent": ((stock.current_price - stock.previous_close) / stock.previous_close * 100) if stock.current_price and stock.previous_close and stock.previous_close != 0 else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock details for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch stock details: {str(e)}"
        )
