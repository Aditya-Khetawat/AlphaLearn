from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.models import Stock
from app.schemas.schemas import StockCreate, StockUpdate
from app.services.stock_data import StockDataService  # Added import for stock data service


def get_by_id(db: Session, stock_id: int) -> Optional[Stock]:
    """
    Get a stock by ID
    """
    return db.query(Stock).filter(Stock.id == stock_id).first()


def get_by_symbol(db: Session, symbol: str) -> Optional[Stock]:
    """
    Get a stock by symbol
    """
    return db.query(Stock).filter(Stock.symbol == symbol).first()


def get_stocks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    exchange: Optional[str] = None,
    sector: Optional[str] = None
) -> List[Stock]:
    """
    Get multiple stocks with optional filters
    """
    query = db.query(Stock)
    
    if exchange:
        query = query.filter(Stock.exchange == exchange)
    
    if sector:
        query = query.filter(Stock.sector == sector)
        
    return query.filter(Stock.is_active == True).offset(skip).limit(limit).all()


def create(db: Session, obj_in: StockCreate) -> Stock:
    """
    Create a new stock
    """
    db_obj = Stock(
        symbol=obj_in.symbol,
        name=obj_in.name,
        current_price=obj_in.current_price,
        previous_close=obj_in.previous_close,
        exchange=obj_in.exchange,
        sector=obj_in.sector,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session,
    db_obj: Stock,
    obj_in: Union[StockUpdate, Dict[str, Any]]
) -> Stock:
    """
    Update a stock
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field in update_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_prices(
    db: Session,
    stock_updates: List[Dict[str, Any]]
) -> List[Stock]:
    """
    Update prices for multiple stocks
    """
    updated_stocks = []
    
    for update in stock_updates:
        stock = get_by_symbol(db, update["symbol"])
        if stock:
            stock.previous_close = stock.current_price
            stock.current_price = update["current_price"]
            db.add(stock)
            updated_stocks.append(stock)
    
    db.commit()
    for stock in updated_stocks:
        db.refresh(stock)
    
    return updated_stocks


def search(
    db: Session,
    query: str,
    limit: int = 10
) -> List[Stock]:
    """
    Search for stocks by name or symbol
    """
    return db.query(Stock).filter(
        and_(
            Stock.is_active == True,
            (Stock.symbol.ilike(f"%{query}%") | Stock.name.ilike(f"%{query}%"))
        )
    ).limit(limit).all()


def refresh_stock_data(db: Session, stock: Stock) -> Stock:
    """
    Refresh stock data from Yahoo Finance
    """
    try:
        stock_data = StockDataService.get_stock_data(stock.symbol)
        if stock_data:
            # Save current price as previous close if it exists
            if stock.current_price > 0:
                stock.previous_close = stock.current_price
            
            # Update with new data
            stock.current_price = stock_data["current_price"]
            if "name" in stock_data and stock_data["name"]:
                stock.name = stock_data["name"]
                
            stock.last_updated = stock_data["updated_at"]
            
            db.add(stock)
            db.commit()
            db.refresh(stock)
    except Exception as e:
        # Log the error but don't break the function
        print(f"Error refreshing data for {stock.symbol}: {str(e)}")
    
    return stock


def refresh_all_stocks(db: Session) -> int:
    """
    Refresh all active stocks from Yahoo Finance
    """
    stocks = db.query(Stock).filter(Stock.is_active == True).all()
    updated_count = 0
    
    # Get all symbols
    symbols = [stock.symbol for stock in stocks]
    
    # If we don't have any stocks yet, add some default Indian stocks
    if not symbols:
        default_symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN", "BAJFINANCE"]
        for symbol in default_symbols:
            # Create empty stock entries
            stock = Stock(
                symbol=symbol,
                name=symbol,  # Will be updated with real name
                current_price=0.0,
                previous_close=0.0,
                exchange="NSE",
                is_active=True
            )
            db.add(stock)
        db.commit()
        
        # Now get the newly created stocks
        stocks = db.query(Stock).all()
        symbols = [stock.symbol for stock in stocks]
    
    # Update in batches to avoid too many API calls
    batch_size = 10
    for i in range(0, len(symbols), batch_size):
        batch_symbols = symbols[i:i+batch_size]
        stock_data_list = StockDataService.get_multiple_stocks(batch_symbols)
        
        for stock_data in stock_data_list:
            stock = get_by_symbol(db, stock_data["symbol"])
            if stock:
                # Save current price as previous close if it exists
                if stock.current_price > 0:
                    stock.previous_close = stock.current_price
                
                # Update with new data
                stock.current_price = stock_data["current_price"]
                if "name" in stock_data and stock_data["name"]:
                    stock.name = stock_data["name"]
                    
                stock.last_updated = stock_data["updated_at"]
                
                db.add(stock)
                updated_count += 1
        
        db.commit()
    
    return updated_count
