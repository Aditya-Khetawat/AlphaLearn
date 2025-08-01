# # requirements.txt additions
# # Add these to your requirements.txt:
# # yfinance>=0.2.18
# # requests>=2.31.0
# # beautifulsoup4>=4.12.0
# # apscheduler>=3.10.0
# # sqlalchemy>=2.0.0
# # python-multipart>=0.0.6

# import asyncio
# import logging
# from datetime import datetime, timedelta
# from typing import List, Optional, Dict, Any
# import requests
# import yfinance as yf
# from bs4 import BeautifulSoup
# from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
# from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, or_
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from sqlalchemy import create_engine
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from pydantic import BaseModel
# import json
# import time

# # Database setup
# DATABASE_URL = "sqlite:///./stocks.db"  # Change to PostgreSQL in production
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # Models
# class Stock(Base):
#     __tablename__ = "stocks"
    
#     id = Column(Integer, primary_key=True, index=True)
#     symbol = Column(String, unique=True, index=True, nullable=False)
#     name = Column(String, nullable=False)
#     exchange = Column(String, nullable=False)  # NSE, BSE
#     sector = Column(String, nullable=True)
#     market_cap = Column(Float, nullable=True)
#     last_price = Column(Float, nullable=True)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# # Pydantic models
# class StockResponse(BaseModel):
#     symbol: str
#     name: str
#     exchange: str
#     sector: Optional[str] = None
#     market_cap: Optional[float] = None
#     last_price: Optional[float] = None
    
#     class Config:
#         from_attributes = True

# class StockSearchResponse(BaseModel):
#     stocks: List[StockResponse]
#     total: int
#     page: int
#     per_page: int

# # Create tables
# Base.metadata.create_all(bind=engine)

# # Database dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # FastAPI app
# app = FastAPI(title="Indian Stock Trading Platform", version="1.0.0")

# # Logging setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class StockDataFetcher:
#     """Handles fetching stock data from various free sources"""
    
#     @staticmethod
#     async def fetch_nse_stocks() -> List[Dict[str, Any]]:
#         """Fetch stocks from NSE public API"""
#         try:
#             headers = {
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#             }
            
#             # NSE All stocks API
#             url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20TOTAL%20MARKET"
#             response = requests.get(url, headers=headers, timeout=30)
            
#             if response.status_code == 200:
#                 data = response.json()
#                 stocks = []
                
#                 for stock in data.get('data', []):
#                     stocks.append({
#                         'symbol': f"{stock['symbol']}.NS",
#                         'name': stock.get('companyName', stock['symbol']),
#                         'exchange': 'NSE',
#                         'last_price': stock.get('lastPrice'),
#                         'market_cap': stock.get('totalTradedValue')
#                     })
                
#                 logger.info(f"Fetched {len(stocks)} stocks from NSE")
#                 return stocks
                
#         except Exception as e:
#             logger.error(f"Error fetching NSE stocks: {e}")
#             return []
    
#     @staticmethod
#     async def fetch_yahoo_finance_stocks() -> List[Dict[str, Any]]:
#         """Fetch Indian stocks using yfinance"""
#         try:
#             # Popular Indian stock symbols
#             nse_symbols = [
#                 "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
#                 "HDFC.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "BHARTIARTL.NS", "ITC.NS",
#                 "SBIN.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS", "AXISBANK.NS",
#                 "LT.NS", "SUNPHARMA.NS", "ULTRACEMCO.NS", "TITAN.NS", "WIPRO.NS",
#                 "NESTLEIND.NS", "POWERGRID.NS", "NTPC.NS", "JSWSTEEL.NS", "TATAMOTORS.NS",
#                 "HCLTECH.NS", "INDUSINDBK.NS", "ADANIPORTS.NS", "GRASIM.NS", "COALINDIA.NS"
#             ]
            
#             stocks = []
            
#             # Fetch in batches to avoid rate limits
#             for i in range(0, len(nse_symbols), 10):
#                 batch = nse_symbols[i:i+10]
#                 try:
#                     tickers = yf.Tickers(' '.join(batch))
                    
#                     for symbol in batch:
#                         try:
#                             ticker = tickers.tickers[symbol]
#                             info = ticker.info
                            
#                             stocks.append({
#                                 'symbol': symbol,
#                                 'name': info.get('longName', symbol.replace('.NS', '')),
#                                 'exchange': 'NSE',
#                                 'sector': info.get('sector'),
#                                 'market_cap': info.get('marketCap'),
#                                 'last_price': info.get('currentPrice')
#                             })
                            
#                         except Exception as e:
#                             logger.warning(f"Error fetching {symbol}: {e}")
#                             # Add basic info even if detailed fetch fails
#                             stocks.append({
#                                 'symbol': symbol,
#                                 'name': symbol.replace('.NS', ''),
#                                 'exchange': 'NSE'
#                             })
                    
#                     # Rate limiting
#                     await asyncio.sleep(1)
                    
#                 except Exception as e:
#                     logger.error(f"Error fetching batch {batch}: {e}")
            
#             logger.info(f"Fetched {len(stocks)} stocks from Yahoo Finance")
#             return stocks
            
#         except Exception as e:
#             logger.error(f"Error in Yahoo Finance fetch: {e}")
#             return []
    
#     @staticmethod
#     async def fetch_popular_indian_stocks() -> List[Dict[str, Any]]:
#         """Fallback: Return popular Indian stocks"""
#         popular_stocks = [
#             {"symbol": "RELIANCE.NS", "name": "Reliance Industries Limited", "exchange": "NSE", "sector": "Oil & Gas"},
#             {"symbol": "TCS.NS", "name": "Tata Consultancy Services Limited", "exchange": "NSE", "sector": "IT"},
#             {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Limited", "exchange": "NSE", "sector": "Banking"},
#             {"symbol": "INFY.NS", "name": "Infosys Limited", "exchange": "NSE", "sector": "IT"},
#             {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Limited", "exchange": "NSE", "sector": "FMCG"},
#             {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Limited", "exchange": "NSE", "sector": "Banking"},
#             {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Limited", "exchange": "NSE", "sector": "Banking"},
#             {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Limited", "exchange": "NSE", "sector": "Telecom"},
#             {"symbol": "ITC.NS", "name": "ITC Limited", "exchange": "NSE", "sector": "FMCG"},
#             {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE", "sector": "Banking"},
#             {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance Limited", "exchange": "NSE", "sector": "Financial Services"},
#             {"symbol": "ASIANPAINT.NS", "name": "Asian Paints Limited", "exchange": "NSE", "sector": "Paints"},
#             {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Limited", "exchange": "NSE", "sector": "Automobile"},
#             {"symbol": "AXISBANK.NS", "name": "Axis Bank Limited", "exchange": "NSE", "sector": "Banking"},
#             {"symbol": "LT.NS", "name": "Larsen & Toubro Limited", "exchange": "NSE", "sector": "Construction"},
#         ]
#         return popular_stocks

# class StockService:
#     """Service layer for stock operations"""
    
#     @staticmethod
#     async def populate_database(db: Session, force_refresh: bool = False):
#         """Populate database with all available Indian stocks"""
        
#         if not force_refresh:
#             # Check if database already has stocks
#             existing_count = db.query(Stock).count()
#             if existing_count > 100:
#                 logger.info(f"Database already has {existing_count} stocks. Skipping population.")
#                 return existing_count
        
#         logger.info("Starting database population...")
#         fetcher = StockDataFetcher()
#         all_stocks = []
        
#         # Try multiple sources
#         try:
#             # Source 1: NSE API
#             nse_stocks = await fetcher.fetch_nse_stocks()
#             all_stocks.extend(nse_stocks)
            
#             # Source 2: Yahoo Finance
#             yf_stocks = await fetcher.fetch_yahoo_finance_stocks()
#             all_stocks.extend(yf_stocks)
            
#             # Source 3: Popular stocks fallback
#             if len(all_stocks) < 50:
#                 popular_stocks = await fetcher.fetch_popular_indian_stocks()
#                 all_stocks.extend(popular_stocks)
            
#         except Exception as e:
#             logger.error(f"Error fetching stocks: {e}")
#             # Use fallback data
#             all_stocks = await fetcher.fetch_popular_indian_stocks()
        
#         # Remove duplicates
#         seen_symbols = set()
#         unique_stocks = []
#         for stock in all_stocks:
#             if stock['symbol'] not in seen_symbols:
#                 seen_symbols.add(stock['symbol'])
#                 unique_stocks.append(stock)
        
#         # Insert into database
#         inserted_count = 0
#         for stock_data in unique_stocks:
#             try:
#                 # Check if stock already exists
#                 existing_stock = db.query(Stock).filter(Stock.symbol == stock_data['symbol']).first()
                
#                 if existing_stock:
#                     # Update existing stock
#                     for key, value in stock_data.items():
#                         if hasattr(existing_stock, key) and value is not None:
#                             setattr(existing_stock, key, value)
#                     existing_stock.updated_at = datetime.utcnow()
#                 else:
#                     # Create new stock
#                     new_stock = Stock(**stock_data)
#                     db.add(new_stock)
#                     inserted_count += 1
                
#                 # Commit in batches
#                 if inserted_count % 100 == 0:
#                     db.commit()
#                     logger.info(f"Inserted {inserted_count} stocks...")
                    
#             except Exception as e:
#                 logger.error(f"Error inserting stock {stock_data.get('symbol')}: {e}")
#                 db.rollback()
        
#         # Final commit
#         try:
#             db.commit()
#             total_stocks = db.query(Stock).count()
#             logger.info(f"Database population complete. Total stocks: {total_stocks}")
#             return total_stocks
#         except Exception as e:
#             logger.error(f"Final commit error: {e}")
#             db.rollback()
#             return 0
    
#     @staticmethod
#     def search_stocks(db: Session, query: str, page: int = 1, per_page: int = 20) -> StockSearchResponse:
#         """Search stocks in database with fuzzy matching"""
        
#         # Calculate offset
#         offset = (page - 1) * per_page
        
#         # Build search query
#         search_filter = or_(
#             Stock.symbol.ilike(f"%{query}%"),
#             Stock.name.ilike(f"%{query}%")
#         )
        
#         # Get total count
#         total = db.query(Stock).filter(search_filter, Stock.is_active == True).count()
        
#         # Get paginated results
#         stocks = db.query(Stock).filter(search_filter, Stock.is_active == True)\
#                    .offset(offset).limit(per_page).all()
        
#         return StockSearchResponse(
#             stocks=[StockResponse.from_orm(stock) for stock in stocks],
#             total=total,
#             page=page,
#             per_page=per_page
#         )

# # Initialize scheduler
# scheduler = AsyncIOScheduler()

# @app.on_event("startup")
# async def startup_event():
#     """Initialize database and start background tasks"""
#     logger.info("Starting up application...")
    
#     # Populate database on startup if empty
#     db = SessionLocal()
#     try:
#         stock_count = await StockService.populate_database(db)
#         logger.info(f"Startup complete. Database has {stock_count} stocks.")
#     finally:
#         db.close()
    
#     # Start scheduler for daily updates
#     scheduler.add_job(
#         daily_stock_update,
#         'cron',
#         hour=1,  # Run at 1 AM daily
#         minute=0
#     )
#     scheduler.start()
#     logger.info("Background scheduler started")

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Cleanup on shutdown"""
#     scheduler.shutdown()
#     logger.info("Application shutdown complete")

# async def daily_stock_update():
#     """Background task to update stock data daily"""
#     logger.info("Starting daily stock update...")
#     db = SessionLocal()
#     try:
#         updated_count = await StockService.populate_database(db, force_refresh=True)
#         logger.info(f"Daily update complete. Updated {updated_count} stocks.")
#     finally:
#         db.close()

# # API Endpoints

# @app.get("/")
# async def root():
#     return {"message": "Indian Stock Trading Platform API", "version": "1.0.0"}

# @app.post("/stocks/seed")
# async def seed_stocks(background_tasks: BackgroundTasks, force: bool = False, db: Session = Depends(get_db)):
#     """Manually trigger stock database population"""
#     try:
#         if force:
#             stock_count = await StockService.populate_database(db, force_refresh=True)
#         else:
#             background_tasks.add_task(StockService.populate_database, db)
#             return {"message": "Stock seeding started in background"}
        
#         return {
#             "message": "Stock database populated successfully",
#             "total_stocks": stock_count
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error seeding stocks: {str(e)}")

# @app.get("/stocks/search", response_model=StockSearchResponse)
# async def search_stocks(q: str, page: int = 1, per_page: int = 20, db: Session = Depends(get_db)):
#     """Search stocks with pagination"""
#     if not q or len(q.strip()) < 1:
#         raise HTTPException(status_code=400, detail="Search query must be at least 1 character")
    
#     if per_page > 100:
#         per_page = 100  # Limit results per page
    
#     try:
#         result = StockService.search_stocks(db, q.strip(), page, per_page)
        
#         # If no results found in database, try live API as fallback
#         if result.total == 0:
#             logger.info(f"No results found for '{q}' in database, trying live API...")
#             # You could implement live API fallback here
            
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# @app.get("/stocks/all")
# async def get_all_stocks(page: int = 1, per_page: int = 50, db: Session = Depends(get_db)):
#     """Get all stocks with pagination"""
#     try:
#         result = StockService.search_stocks(db, "", page, per_page)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching stocks: {str(e)}")

# @app.get("/stocks/stats")
# async def get_stock_stats(db: Session = Depends(get_db)):
#     """Get database statistics"""
#     try:
#         total_stocks = db.query(Stock).count()
#         active_stocks = db.query(Stock).filter(Stock.is_active == True).count()
#         nse_stocks = db.query(Stock).filter(Stock.exchange == "NSE").count()
#         bse_stocks = db.query(Stock).filter(Stock.exchange == "BSE").count()
        
#         return {
#             "total_stocks": total_stocks,
#             "active_stocks": active_stocks,
#             "nse_stocks": nse_stocks,
#             "bse_stocks": bse_stocks,
#             "last_updated": datetime.utcnow().isoformat()
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

# @app.get("/stocks/{symbol}")
# async def get_stock_detail(symbol: str, db: Session = Depends(get_db)):
#     """Get individual stock details"""
#     stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()
    
#     if not stock:
#         raise HTTPException(status_code=404, detail="Stock not found")
    
#     return StockResponse.from_orm(stock)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)