from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    pass


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


# Stock schemas
class StockBase(BaseModel):
    symbol: str
    name: str
    current_price: float
    previous_close: Optional[float] = None
    exchange: str = "NSE"
    sector: Optional[str] = None


class StockCreate(StockBase):
    pass


class StockUpdate(BaseModel):
    name: Optional[str] = None
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    sector: Optional[str] = None
    is_active: Optional[bool] = None


class StockInDB(StockBase):
    id: int
    is_active: bool
    last_updated: datetime

    class Config:
        from_attributes = True


class Stock(StockInDB):
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None


# Position schemas
class PositionBase(BaseModel):
    shares: float
    average_price: float


class PositionCreate(PositionBase):
    stock_id: int


class PositionInDB(PositionBase):
    id: int
    portfolio_id: int
    stock_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Position(BaseModel):
    id: int
    stock: Stock
    shares: float
    average_price: float
    current_value: float
    total_return: float
    total_return_percent: float

    class Config:
        from_attributes = True


# Portfolio schemas
class PortfolioBase(BaseModel):
    cash_balance: float = 100000.0


class PortfolioCreate(PortfolioBase):
    user_id: int


class PortfolioUpdate(BaseModel):
    cash_balance: Optional[float] = None


class PortfolioInDB(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Portfolio(PortfolioInDB):
    positions: List[Position] = []
    total_value: float
    invested_value: float
    total_return: float
    total_return_percent: float

    class Config:
        from_attributes = True


# Transaction schemas
class TransactionBase(BaseModel):
    transaction_type: str
    shares: float
    price: float
    total_amount: float


class TransactionCreate(TransactionBase):
    stock_id: int
    notes: Optional[str] = None


class TransactionInDB(TransactionBase):
    id: int
    user_id: int
    stock_id: int
    timestamp: datetime
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class Transaction(BaseModel):
    id: int
    stock: Stock
    transaction_type: str
    shares: float
    price: float
    total_amount: float
    timestamp: datetime
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True
