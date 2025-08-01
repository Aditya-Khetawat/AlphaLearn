"""
Stock routes for the API
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db  # Updated import
from app.models.schemas import StockResponse, StockCreate
from app.models.models import Stock
from app.services.stock_data import StockDataService

router = APIRouter()

@router.get("/", response_model=List[StockResponse])
def get_stocks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all stocks from database
    """
    stocks = db.query(Stock).offset(skip).limit(limit).all()
    return stocks


@router.get("/search", response_model=List[StockResponse])
def search_stocks(
    query: str,
    db: Session = Depends(get_db),
    limit: int = 1000
):
    """
    Search stocks by name or symbol
    """
    stocks = db.query(Stock).filter(
        (Stock.symbol.ilike(f"%{query}%")) | 
        (Stock.name.ilike(f"%{query}%"))
    ).limit(limit).all()
    
    return stocks


@router.get("/refresh")
def refresh_stocks(
    symbols: List[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Refresh stock data from Yahoo Finance
    If symbols is provided, only refresh those symbols
    Otherwise refresh all stocks in the database
    """
    if not symbols:
        # Get all symbols from database
        db_stocks = db.query(Stock).all()
        symbols = [stock.symbol for stock in db_stocks]
    
    # If still no symbols (empty database), use some defaults
    if not symbols:
        symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN", "BAJFINANCE", "WIPRO", "ICICIBANK"]
    
    # Update the database
    StockDataService.update_stock_database(db, symbols)
    
    return {"message": f"Refreshed {len(symbols)} stocks"}


@router.get("/{symbol}", response_model=StockResponse)
def get_stock(symbol: str, db: Session = Depends(get_db)):
    """
    Get a specific stock by symbol
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if stock is None:
        # Try to fetch from Yahoo Finance
        stock_data = StockDataService.get_stock_data(symbol)
        if stock_data:
            stock = Stock(**stock_data)
            db.add(stock)
            db.commit()
            db.refresh(stock)
        else:
            raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.post("/", response_model=StockResponse)
def create_stock(stock_data: StockCreate, db: Session = Depends(get_db)):
    """
    Create a new stock in the database
    Usually, you'd fetch the stock data from Yahoo Finance instead
    """
    # Check if stock already exists
    db_stock = db.query(Stock).filter(Stock.symbol == stock_data.symbol).first()
    if db_stock:
        raise HTTPException(status_code=400, detail="Stock already exists")
    
    # Fetch latest data
    fresh_data = StockDataService.get_stock_data(stock_data.symbol)
    if not fresh_data:
        raise HTTPException(status_code=404, detail="Stock not found in Yahoo Finance")
    
    # Create new stock
    new_stock = Stock(**fresh_data)
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    
    return new_stock
