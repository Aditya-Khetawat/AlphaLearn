# AlphaLearn Backend

This is the backend for the AlphaLearn platform, a mock stock trading application for Indian students to learn about the Indian stock market.

## Features

- User authentication and authorization
- Portfolio management with ₹1,00,000 starting balance
- Indian stock market data (NSE/BSE stocks)
- Trading simulation (buy/sell)
- Portfolio tracking and performance analytics

## Technology Stack

- Python 3.11+
- FastAPI for API development
- PostgreSQL 15+ for database
- Redis 7+ for caching
- SQLAlchemy ORM for database access
- Pydantic for data validation
- JWT for authentication
- yfinance and nsepy for Indian stock market data

## Project Structure

```
app/
  ├── api/               # API routes
  │   ├── api_v1/        # API v1 endpoints
  │   └── deps.py        # API dependencies
  ├── core/              # Core modules
  │   ├── config.py      # Application configuration
  │   ├── database.py    # Database connection
  │   └── security.py    # Security utilities
  ├── crud/              # Database CRUD operations
  ├── models/            # SQLAlchemy models
  ├── schemas/           # Pydantic schemas
  └── services/          # Business logic services
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Create a `.env` file in the project root with the following variables:

   ```
   # Database
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=alphalearn
   POSTGRES_PORT=5432

   # Security
   SECRET_KEY=your-super-secret-key

   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

### Running Migrations

Initialize the database with:

```bash
alembic upgrade head
```

### Starting the Server

Run the FastAPI application:

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

API documentation will be available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- POST `/api/v1/auth/login` - User login
- POST `/api/v1/auth/register` - User registration

### Users

- GET `/api/v1/users/me` - Get current user
- PUT `/api/v1/users/me` - Update current user

### Stocks

- GET `/api/v1/stocks` - List stocks
- GET `/api/v1/stocks/{id}` - Get stock by ID
- GET `/api/v1/stocks/search` - Search stocks

### Portfolios

- GET `/api/v1/portfolios/me` - Get user's portfolio
- GET `/api/v1/portfolios/me/positions` - Get user's positions

### Transactions

- POST `/api/v1/transactions/buy` - Buy stocks
- POST `/api/v1/transactions/sell` - Sell stocks
- GET `/api/v1/transactions/history` - Get transaction history
