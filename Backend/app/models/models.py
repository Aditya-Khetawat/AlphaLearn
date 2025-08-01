from datetime import datetime
from sqlalchemy import Boolean, Column, String, Integer, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.timezone_utils import get_ist_timestamp

class User(Base):
    """User model for authentication and profile data"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_admin = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=get_ist_timestamp)
    updated_at = Column(DateTime, default=get_ist_timestamp, onupdate=get_ist_timestamp)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
    transactions = relationship("Transaction", back_populates="user")


class Portfolio(Base):
    """Portfolio model for user's overall account and balance"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    cash_balance = Column(Float, nullable=False, default=100000.0)  # ₹1,00,000 starting balance
    created_at = Column(DateTime, default=get_ist_timestamp)
    updated_at = Column(DateTime, default=get_ist_timestamp, onupdate=get_ist_timestamp)

    # Relationships
    user = relationship("User", back_populates="portfolio")
    positions = relationship("Position", back_populates="portfolio")


class Stock(Base):
    """Stock model for storing Indian stock data"""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    current_price = Column(Float, nullable=False)
    previous_close = Column(Float, nullable=True)
    exchange = Column(String, nullable=False, default="NSE")  # NSE or BSE
    sector = Column(String, nullable=True)
    is_active = Column(Boolean(), default=True)
    last_updated = Column(DateTime, default=get_ist_timestamp)

    # Relationships
    positions = relationship("Position", back_populates="stock")
    transactions = relationship("Transaction", back_populates="stock")


class Position(Base):
    """Position model for storing user's stock holdings"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    shares = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=get_ist_timestamp)
    updated_at = Column(DateTime, default=get_ist_timestamp, onupdate=get_ist_timestamp)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")
    stock = relationship("Stock", back_populates="positions")


class Transaction(Base):
    """Transaction model for logging all buy/sell operations"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    transaction_type = Column(Enum("BUY", "SELL", name="transaction_type"), nullable=False)
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=get_ist_timestamp)
    status = Column(Enum("PENDING", "COMPLETED", "FAILED", name="transaction_status"), default="COMPLETED")
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
    stock = relationship("Stock", back_populates="transactions")
