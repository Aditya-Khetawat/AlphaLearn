from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.models import Portfolio, Position, Stock
from app.schemas.schemas import PortfolioCreate, PortfolioUpdate


def get_by_user_id(db: Session, user_id: int) -> Optional[Portfolio]:
    """
    Get a portfolio by user ID
    """
    return db.query(Portfolio).filter(Portfolio.user_id == user_id).first()


def create(db: Session, obj_in: PortfolioCreate) -> Portfolio:
    """
    Create a new portfolio
    """
    db_obj = Portfolio(
        user_id=obj_in.user_id,
        cash_balance=obj_in.cash_balance,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_cash_balance(db: Session, portfolio_id: int, amount: float) -> Portfolio:
    """
    Update a portfolio's cash balance
    """
    db_obj = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if db_obj:
        db_obj.cash_balance = amount
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    return db_obj


def get_positions_by_portfolio_id(db: Session, portfolio_id: int) -> List[Position]:
    """
    Get all positions for a portfolio
    """
    return db.query(Position).filter(Position.portfolio_id == portfolio_id).all()


def get_position(db: Session, portfolio_id: int, stock_id: int) -> Optional[Position]:
    """
    Get a specific position
    """
    return db.query(Position).filter(
        and_(
            Position.portfolio_id == portfolio_id,
            Position.stock_id == stock_id
        )
    ).first()


def create_position(
    db: Session, 
    portfolio_id: int, 
    stock_id: int,
    shares: float,
    average_price: float
) -> Position:
    """
    Create a new position
    """
    db_obj = Position(
        portfolio_id=portfolio_id,
        stock_id=stock_id,
        shares=shares,
        average_price=average_price
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_position(
    db: Session,
    db_obj: Position,
    shares: float,
    average_price: float
) -> Position:
    """
    Update an existing position
    """
    db_obj.shares = shares
    db_obj.average_price = average_price
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_position(db: Session, position_id: int) -> None:
    """
    Delete a position
    """
    db_obj = db.query(Position).filter(Position.id == position_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()


def calculate_portfolio_value(db: Session, portfolio_id: int) -> Dict[str, Any]:
    """
    Calculate the total value of a portfolio
    """
    # Get the portfolio and its positions
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        return {
            "cash_balance": 0,
            "positions_value": 0,
            "total_value": 0,
            "total_return": 0,
            "total_return_percent": 0
        }
    
    # Get all positions with their current stock prices
    positions = db.query(Position, Stock).join(
        Stock, Position.stock_id == Stock.id
    ).filter(
        Position.portfolio_id == portfolio_id
    ).all()
    
    # Calculate positions value
    positions_value = 0
    invested_value = 0
    
    for position, stock in positions:
        position_value = position.shares * stock.current_price
        position_cost = position.shares * position.average_price
        positions_value += position_value
        invested_value += position_cost
    
    # Calculate total value and return
    total_portfolio_value = portfolio.cash_balance + positions_value  # Total portfolio including cash
    
    # For the frontend, we want to show:
    # - total_value: market value of stocks only (what the UI calls "Current Value")
    # - invested_value: total amount invested in stocks
    # - total_return: profit/loss on stocks only
    
    stock_return = positions_value - invested_value
    stock_return_percent = (stock_return / invested_value) * 100 if invested_value > 0 else 0
    
    return {
        "cash_balance": portfolio.cash_balance,
        "positions_value": positions_value,
        "invested_value": invested_value,
        "total_value": positions_value,  # Market value of stocks only
        "total_return": stock_return,     # P&L on stocks only
        "total_return_percent": stock_return_percent,
        "total_portfolio_value": total_portfolio_value  # Total including cash (if needed)
    }
