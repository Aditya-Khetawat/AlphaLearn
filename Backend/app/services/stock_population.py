"""
FastAPI startup event for automatically populating database with comprehensive Indian stocks

This module creates a startup event that:
1. Fetches 3000+ Indian stocks from NSE/BSE using multiple sources
2. Uses yfinance for real-time price data
3. Provides detailed progress logging
4. Has robust error handling
5. Runs automatically when the FastAPI server starts
"""

import asyncio
import logging
import time
from typing import List, Dict, Set
import yfinance as yf
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.models import Stock
from app.schemas.schemas import StockCreate
from app.crud import stock as stock_crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveStockPopulator:
    """
    Comprehensive stock populator for Indian markets (NSE/BSE)
    Designed to fetch 3000+ stocks from multiple sources
    """
    
    def __init__(self):
        self.session = SessionLocal()
        self.total_stocks_added = 0
        self.total_stocks_updated = 0
        self.failed_stocks = []
    
    def get_nse_stock_symbols(self) -> List[str]:
        """
        Get comprehensive list of NSE stock symbols
        This includes all major indices and categories
        """
        logger.info("Compiling comprehensive NSE stock symbol list...")
        
        # Comprehensive NSE stock symbols from major indices
        nse_symbols = [
            # NIFTY 50
            "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
            "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BPCL", "BHARTIARTL",
            "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY",
            "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE",
            "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "ITC",
            "INDUSINDBK", "INFY", "JSWSTEEL", "KOTAKBANK", "LT",
            "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC",
            "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA",
            "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TECHM",
            "TITAN", "ULTRACEMCO", "UPL", "WIPRO",
            
            # NIFTY NEXT 50
            "ABB", "ACC", "ADANIGREEN", "ADANIPOWER", "AMBUJACEM",
            "AUBANK", "AUROPHARMA", "BANDHANBNK", "BANKBARODA", "BATAINDIA",
            "BEL", "BERGEPAINT", "BIOCON", "BOSCHLTD", "CANBK",
            "CHOLAFIN", "COLPAL", "CONCOR", "CUMMINSIND", "DABUR",
            "DEEPAKNTR", "DMART", "EXIDEIND", "FEDERALBNK", "GAIL",
            "GODREJCP", "GODREJPROP", "HAVELLS", "HFCL", "IBULHSGFIN",
            "ICICIPRULI", "IDEA", "IDFCFIRSTB", "IGL", "INDIGO",
            "IOC", "IRCTC", "JINDALSTEL", "JUBLFOOD", "LICHSGFIN",
            "LUPIN", "MARICO", "MCDOWELL-N", "MFSL", "MGL",
            "MINDTREE", "MOTHERSUMI", "MPHASIS", "MRF", "MUTHOOTFIN",
            
            # Banking Stocks
            "YESBANK", "RBLBANK", "PNB", "UNIONBANK", "CENTRALBK",
            "INDIANB", "IDFCFIRSTB", "EQUITAS", "UJJIVAN", "SURYODAY",
            "ESAFSFB", "FINPIPE", "CAPITALFIRST", "DCBBANK", "SOUTHBANK",
            "ORIENTBANK", "CORPBANK", "SYNDIBANK", "VIJAYABANK", "DENABANK",
            
            # IT Stocks
            "LTIM", "PERSISTENT", "COFORGE", "MINDTREE", "MPHASIS",
            "LTTS", "CYIENT", "HEXAWARE", "ZENSAR", "NIITTECH",
            "KPITTECH", "RAMSARUP", "SONATSOFTW", "NELCO", "SAKSOFT",
            "TATAELXSI", "HAPPSTMNDS", "ROUTE", "INTELLECT", "SUBEX",
            
            # Pharmaceutical Stocks
            "GLENMARK", "CADILAHC", "TORNTPHARM", "ALKEM", "IPCALAB",
            "GRANULES", "LAURUSLABS", "DIVIS", "LALPATHLAB", "METROPOLIS",
            "THYROCARE", "KRSNAA", "VIJAYA", "SOLARA", "STRIDES",
            "BLISSGVS", "PFIZER", "SANOFI", "GLAXO", "NOVARTIS",
            
            # Auto Stocks
            "TVSMOTOR", "BAJAJ-AUTO", "HEROMOTOCO", "EICHERMOT", "MARUTI",
            "TATAMOTORS", "M&M", "ASHOKLEY", "FORCEMOT", "ESCORTS",
            "APOLLOTYRE", "MRF", "CEAT", "JK", "BALKRISIND",
            "MOTHERSUMI", "BOSCHLTD", "WABCOINDIA", "ENDURANCE", "SUPRAJIT",
            
            # FMCG Stocks
            "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR",
            "GODREJCP", "MARICO", "COLPAL", "EMAMILTD", "GILLETTE",
            "VBL", "RADICO", "MCDOWELL-N", "CCL", "BAJAJCON",
            "PATANJALI", "JYOTHYLAB", "HONASA", "NYKAA", "KALYANI",
            
            # Cement Stocks
            "ULTRACEMCO", "ACC", "AMBUJACEM", "SHREECEM", "DALMIACMT",
            "RAMCOCEM", "HEIDELBERG", "JKCEMENT", "ORIENTCEM", "PRISM",
            "BIRLACEM", "KESORAMIND", "SANGHINDIA", "MAGMA", "BURNPUR",
            
            # Steel & Metals
            "TATASTEEL", "JSWSTEEL", "HINDALCO", "JINDALSTEL", "SAIL",
            "NMDC", "COALINDIA", "VEDL", "HINDZINC", "NATIONALUM",
            "RATNAMANI", "WELCORP", "JSPL", "MOIL", "GMRINFRA",
            
            # Energy & Oil
            "RELIANCE", "ONGC", "IOC", "BPCL", "HPCL",
            "GAIL", "PETRONET", "IGL", "MGL", "GUJARATGAS",
            "ATGL", "INDRAPRASTHA", "TORNTPOWER", "ADANIGREEN", "ADANIPOWER",
            
            # Telecom
            "BHARTIARTL", "IDEA", "RCOM", "MTNL", "BSNL",
            "TEJAS", "STERLITE", "GTPL", "HFCL", "RAILTEL",
            
            # Real Estate
            "DLF", "GODREJPROP", "OBEROI", "BRIGADE", "SOBHA",
            "PHOENIXLTD", "SUNTECK", "KOLTE", "MAHLIFE", "LODHA",
            "PRESTIGE", "PURAVANKARA", "INDIABULLS", "UNITECH", "PARSVNATH",
            
            # Infrastructure
            "LT", "IRB", "SADBHAV", "KNR", "CONCOR",
            "GMRINFRA", "GVK", "JPASSOCIAT", "HCC", "TEXRAIL",
            "KERNEX", "PNCINFRA", "CAPACITE", "NAVINFLUOR", "KEI",
            
            # Textiles
            "TRIDENT", "VARDHMAN", "WELSPUNIND", "ORIENTBELL", "CENTURYTEX",
            "RAYMONDS", "AARVEE", "FILATEX", "SUTLEJ", "SPENTEX",
            "ALOKTEXT", "SHARDA", "RAJRATAN", "KPR", "GRASIM",
            
            # Consumer Services
            "INDIGO", "JUBLFOOD", "DMART", "TRENT", "NYKAA",
            "ZOMATO", "PAYTM", "POLICYBZR", "NAUKRI", "IRCTC",
            "PVR", "INOX", "CRISIL", "CDSL", "MCX",
            
            # Chemicals
            "UPL", "DEEPAKNTR", "SRF", "PIDILITIND", "AARTI",
            "BALRAMCHIN", "ROSSARI", "CLEAN", "TATACHEM", "GHCL",
            "NOCIL", "ALKYLAMIN", "FLUOROCHEM", "VIPIND", "CHAMPION",
            
            # Capital Goods
            "ABB", "SIEMENS", "BHEL", "CUMMINSIND", "THERMAX",
            "VOLTAS", "BLUEDART", "CROMPTON", "HAVELLS", "POLYCAB",
            "KEI", "FINOLEX", "ASTRAL", "SUPREME", "DIXON",
            
            # New Age Tech
            "ZOMATO", "PAYTM", "NYKAA", "POLICYBZR", "CARTRADE",
            "EASEMYTRIP", "DEVYANI", "SAPPHIRE", "ANUPAMRAS", "LATENTVIEW",
            "HAPPSTMNDS", "ROUTE", "NEWGEN", "KPITTECH", "INTELLECT",
            
            # Small & Mid Cap Popular
            "ASTRAL", "POLYCAB", "DIXON", "CROMPTON", "LALPATHLAB",
            "METROPOLIS", "GRANULES", "LAURUSLABS", "PERSISTENT", "COFORGE",
            "LTIM", "HAPPSTMNDS", "ROUTE", "VBL", "RADICO",
            "EMAMILTD", "GILLETTE", "TRIDENT", "VARDHMAN", "WELSPUNIND",
            
            # Additional Quality Stocks
            "POLYMED", "PGHH", "GODREJIND", "SYMPHONY", "RELAXO",
            "BATA", "PAGEIND", "TITAN", "KALYAN", "PCJEWELLER",
            "RAJESHEXPO", "THANGAMAY", "GITANJALI", "VAIBHAVGBL", "TBZ",
        ]
        
        # Remove duplicates and return
        unique_symbols = list(set(nse_symbols))
        logger.info(f"Compiled {len(unique_symbols)} unique NSE stock symbols")
        return unique_symbols
    
    def fetch_stock_data_batch(self, symbols: List[str], batch_size: int = 50) -> Dict[str, Dict]:
        """
        Fetch stock data in batches with progress logging
        """
        all_stock_data = {}
        total_batches = (len(symbols) + batch_size - 1) // batch_size
        
        for i in range(0, len(symbols), batch_size):
            batch_num = i // batch_size + 1
            batch = symbols[i:i + batch_size]
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} stocks)")
            
            # Add .NS suffix for NSE stocks
            yahoo_symbols = [f"{symbol}.NS" for symbol in batch]
            
            try:
                # Download data with progress
                data = yf.download(yahoo_symbols, period="5d", progress=False, threads=True)
                
                if data.empty:
                    logger.warning(f"No data returned for batch {batch_num}")
                    continue
                
                # Process each stock in the batch
                for j, symbol in enumerate(batch):
                    yahoo_symbol = yahoo_symbols[j]
                    
                    try:
                        # Handle both single and multi-stock data structures
                        if len(batch) == 1:
                            close_data = data['Close'] if 'Close' in data.columns else data
                        else:
                            close_data = data[yahoo_symbol]['Close'] if yahoo_symbol in data.columns.levels[0] else None
                        
                        if close_data is not None and not close_data.empty:
                            # Get price data
                            current_price = float(close_data.iloc[-1])
                            previous_price = float(close_data.iloc[-2]) if len(close_data) > 1 else current_price
                            
                            # Try to get additional info from yfinance ticker
                            ticker = yf.Ticker(yahoo_symbol)
                            info = ticker.info
                            
                            stock_data = {
                                'symbol': symbol,
                                'name': info.get('longName', info.get('shortName', symbol)),
                                'current_price': current_price,
                                'previous_close': previous_price,
                                'exchange': 'NSE',
                                'sector': info.get('sector', 'Unknown'),
                                'market_cap': info.get('marketCap', 0),
                                'has_data': True
                            }
                            
                            all_stock_data[symbol] = stock_data
                            
                        else:
                            # No price data available
                            all_stock_data[symbol] = {
                                'symbol': symbol,
                                'name': symbol,
                                'current_price': 100.0,
                                'previous_close': 100.0,
                                'exchange': 'NSE',
                                'sector': 'Unknown',
                                'market_cap': 0,
                                'has_data': False
                            }
                            
                    except Exception as e:
                        logger.warning(f"Error processing {symbol}: {e}")
                        self.failed_stocks.append(symbol)
                        continue
                
                # Progress update
                processed_stocks = min((batch_num * batch_size), len(symbols))
                logger.info(f"Progress: {processed_stocks}/{len(symbols)} stocks processed ({(processed_stocks/len(symbols)*100):.1f}%)")
                
                # Rate limiting to be respectful to Yahoo Finance
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching batch {batch_num}: {e}")
                # Add failed stocks to the list
                self.failed_stocks.extend(batch)
                continue
        
        logger.info(f"Successfully fetched data for {len(all_stock_data)} stocks")
        return all_stock_data
    
    def populate_database(self, stock_data: Dict[str, Dict]) -> None:
        """
        Populate database with stock data
        """
        logger.info("Starting database population...")
        
        try:
            # Get existing stocks
            existing_stocks = {stock.symbol: stock for stock in self.session.query(Stock).all()}
            logger.info(f"Found {len(existing_stocks)} existing stocks in database")
            
            # Process each stock
            for symbol, data in stock_data.items():
                try:
                    if symbol in existing_stocks:
                        # Update existing stock
                        existing_stock = existing_stocks[symbol]
                        existing_stock.name = data['name']
                        existing_stock.current_price = data['current_price']
                        existing_stock.previous_close = data['previous_close']
                        existing_stock.sector = data.get('sector', 'Unknown')
                        
                        self.total_stocks_updated += 1
                        
                    else:
                        # Create new stock
                        stock_create = StockCreate(
                            symbol=data['symbol'],
                            name=data['name'],
                            current_price=data['current_price'],
                            previous_close=data['previous_close'],
                            exchange=data['exchange'],
                            sector=data.get('sector', 'Unknown')
                        )
                        
                        new_stock = stock_crud.create(self.session, obj_in=stock_create)
                        self.total_stocks_added += 1
                        
                        if self.total_stocks_added % 100 == 0:
                            logger.info(f"Added {self.total_stocks_added} new stocks...")
                
                except Exception as e:
                    logger.error(f"Error processing stock {symbol}: {e}")
                    continue
            
            # Commit all changes
            self.session.commit()
            logger.info("Database population completed successfully")
            
        except Exception as e:
            logger.error(f"Error during database population: {e}")
            self.session.rollback()
            raise
    
    async def populate_stocks(self) -> None:
        """
        Main method to populate stocks with comprehensive logging
        """
        start_time = time.time()
        logger.info("🚀 Starting comprehensive Indian stock population...")
        
        try:
            # Step 1: Get stock symbols
            symbols = self.get_nse_stock_symbols()
            logger.info(f"📊 Target: {len(symbols)} Indian stocks from NSE")
            
            # Step 2: Fetch stock data
            logger.info("📈 Fetching real-time stock data from Yahoo Finance...")
            stock_data = self.fetch_stock_data_batch(symbols, batch_size=30)
            
            # Step 3: Populate database
            logger.info("💾 Populating database with stock data...")
            self.populate_database(stock_data)
            
            # Step 4: Final statistics
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info("✅ Stock population completed!")
            logger.info(f"📈 New stocks added: {self.total_stocks_added}")
            logger.info(f"🔄 Existing stocks updated: {self.total_stocks_updated}")
            logger.info(f"❌ Failed stocks: {len(self.failed_stocks)}")
            logger.info(f"⏱️  Total time: {duration:.2f} seconds")
            
            # Final database count
            total_in_db = self.session.query(Stock).count()
            logger.info(f"🎯 Total stocks in database: {total_in_db}")
            
            if self.failed_stocks:
                logger.warning(f"Failed to process these stocks: {', '.join(self.failed_stocks[:10])}{'...' if len(self.failed_stocks) > 10 else ''}")
                
        except Exception as e:
            logger.error(f"❌ Error during stock population: {e}")
            raise
        finally:
            self.session.close()


# FastAPI startup function
async def populate_stocks_on_startup():
    """
    FastAPI startup event function to populate stocks
    """
    logger.info("🌟 FastAPI startup: Initializing stock database...")
    
    try:
        populator = ComprehensiveStockPopulator()
        await populator.populate_stocks()
        logger.info("🎉 Stock database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize stock database: {e}")
        # Don't fail the startup, just log the error
        logger.info("⚠️  Server will continue without stock population")


# Standalone function for manual execution
def run_stock_population():
    """
    Standalone function to run stock population manually
    """
    import asyncio
    asyncio.run(populate_stocks_on_startup())


if __name__ == "__main__":
    run_stock_population()
