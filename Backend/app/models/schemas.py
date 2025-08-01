"""
Pydantic schemas for API request and response validation
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Stock schemas
class StockBase(BaseModel):
    """Base schema for Stock data"""
    symbol: str
    name: str
    

class StockCreate(StockBase):
    """Schema for creating a new Stock"""
    exchange: str = "NSE"
    sector: Optional[str] = None


class StockUpdate(BaseModel):
    """Schema for updating a Stock"""
    name: Optional[str] = None
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    exchange: Optional[str] = None
    sector: Optional[str] = None
    is_active: Optional[bool] = None


class StockResponse(StockBase):
    """Schema for Stock response"""
    id: int
    current_price: float
    previous_close: Optional[float] = None
    exchange: str
    sector: Optional[str] = None
    is_active: bool
    last_updated: datetime
    
    class Config:
        orm_mode = True


# Position schemas
class PositionBase(BaseModel):
    """Base schema for Position data"""
    stock_id: int
    shares: float
    average_price: float


class PositionCreate(PositionBase):
    """Schema for creating a new Position"""
    pass


class PositionUpdate(BaseModel):
    """Schema for updating a Position"""
    shares: Optional[float] = None
    average_price: Optional[float] = None


class PositionResponse(PositionBase):
    """Schema for Position response"""
    id: int
    portfolio_id: int
    created_at: datetime
    updated_at: datetime
    stock: StockResponse
    
    # Calculate the current value and profit/loss
    @property
    def current_value(self) -> float:
        return self.shares * self.stock.current_price
    
    @property
    def purchase_value(self) -> float:
        return self.shares * self.average_price
    
    @property
    def profit_loss(self) -> float:
        return self.current_value - self.purchase_value
    
    @property
    def profit_loss_percent(self) -> float:
        if self.purchase_value == 0:
            return 0
        return (self.profit_loss / self.purchase_value) * 100
    
    class Config:
        orm_mode = True


# Transaction schemas
class TransactionBase(BaseModel):
    """Base schema for Transaction data"""
    stock_id: int
    transaction_type: TransactionType
    shares: float
    price: float


class TransactionCreate(TransactionBase):
    """Schema for creating a new Transaction"""
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    """Schema for updating a Transaction"""
    status: Optional[TransactionStatus] = None
    notes: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Schema for Transaction response"""
    id: int
    user_id: int
    total_amount: float
    timestamp: datetime
    status: TransactionStatus
    notes: Optional[str] = None
    stock: StockResponse
    
    class Config:
        orm_mode = True


# Portfolio schemas
class PortfolioBase(BaseModel):
    """Base schema for Portfolio data"""
    pass


class PortfolioCreate(PortfolioBase):
    """Schema for creating a new Portfolio"""
    pass


class PortfolioUpdate(BaseModel):
    """Schema for updating a Portfolio"""
    cash_balance: Optional[float] = None


class PortfolioResponse(BaseModel):
    """Schema for Portfolio response"""
    id: int
    user_id: int
    cash_balance: float
    created_at: datetime
    updated_at: datetime
    positions: List[PositionResponse] = []
    
    @property
    def total_stock_value(self) -> float:
        return sum(position.current_value for position in self.positions)
    
    @property
    def total_portfolio_value(self) -> float:
        return self.cash_balance + self.total_stock_value
    
    @property
    def total_profit_loss(self) -> float:
        return sum(position.profit_loss for position in self.positions)
    
    @property
    def total_profit_loss_percent(self) -> float:
        total_invested = sum(position.purchase_value for position in self.positions)
        if total_invested == 0:
            return 0
        return (self.total_profit_loss / total_invested) * 100
    
    class Config:
        orm_mode = True


# User schemas
class UserBase(BaseModel):
    """Base schema for User data"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new User"""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a User"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for User response"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        orm_mode = True


# Auth schemas
class Token(BaseModel):
    """Schema for JWT token"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for JWT token payload"""
    sub: str  # user ID
    exp: int  # expiration timestamp
