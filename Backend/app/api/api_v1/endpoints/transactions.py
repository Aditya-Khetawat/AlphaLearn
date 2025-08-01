from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud import portfolio as portfolio_crud
from app.crud import stock as stock_crud
from app.models.models import User, Transaction, Stock
from app.schemas.schemas import Transaction as TransactionSchema, TransactionCreate
from app.core.timezone_utils import format_ist_for_api

router = APIRouter()


@router.post("/buy", response_model=TransactionSchema)
def buy_stock(
    *,
    db: Session = Depends(get_db),
    stock_id: int = Body(...),
    shares: float = Body(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Buy stock
    """
    # Get the stock
    stock = stock_crud.get_by_id(db, stock_id=stock_id)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found",
        )
    
    # Get user's portfolio
    portfolio = portfolio_crud.get_by_user_id(db, user_id=current_user.id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    # Calculate cost
    total_cost = shares * stock.current_price
    
    # Check if user has enough cash
    if portfolio.cash_balance < total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds",
        )
    
    # Update portfolio cash balance
    portfolio.cash_balance -= total_cost
    db.add(portfolio)
    
    # Check if position already exists
    position = portfolio_crud.get_position(db, portfolio_id=portfolio.id, stock_id=stock_id)
    
    if position:
        # Update existing position
        new_total_shares = position.shares + shares
        new_total_cost = (position.shares * position.average_price) + total_cost
        new_average_price = new_total_cost / new_total_shares
        
        portfolio_crud.update_position(
            db=db,
            db_obj=position,
            shares=new_total_shares,
            average_price=new_average_price
        )
    else:
        # Create new position
        portfolio_crud.create_position(
            db=db,
            portfolio_id=portfolio.id,
            stock_id=stock_id,
            shares=shares,
            average_price=stock.current_price
        )
    
    # Record transaction
    transaction = Transaction(
        user_id=current_user.id,
        stock_id=stock_id,
        transaction_type="BUY",
        shares=shares,
        price=stock.current_price,
        total_amount=total_cost,
        status="COMPLETED"
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Return transaction with stock data
    return TransactionSchema(
        id=transaction.id,
        stock=stock,
        transaction_type=transaction.transaction_type,
        shares=transaction.shares,
        price=transaction.price,
        total_amount=transaction.total_amount,
        timestamp=transaction.timestamp,
        status=transaction.status,
        notes=transaction.notes
    )


@router.post("/sell", response_model=TransactionSchema)
def sell_stock(
    *,
    db: Session = Depends(get_db),
    stock_id: int = Body(...),
    shares: float = Body(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Sell stock
    """
    # Get the stock
    stock = stock_crud.get_by_id(db, stock_id=stock_id)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found",
        )
    
    # Get user's portfolio
    portfolio = portfolio_crud.get_by_user_id(db, user_id=current_user.id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    # Check if position exists and user has enough shares
    position = portfolio_crud.get_position(db, portfolio_id=portfolio.id, stock_id=stock_id)
    if not position or position.shares < shares:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough shares to sell",
        )
    
    # Calculate sale amount
    sale_amount = shares * stock.current_price
    
    # Update portfolio cash balance
    portfolio.cash_balance += sale_amount
    db.add(portfolio)
    
    # Update position
    remaining_shares = position.shares - shares
    if remaining_shares > 0:
        # Update position with remaining shares
        portfolio_crud.update_position(
            db=db,
            db_obj=position,
            shares=remaining_shares,
            average_price=position.average_price  # Keep the same average price
        )
    else:
        # Delete position if no shares remain
        db.delete(position)
    
    # Record transaction
    transaction = Transaction(
        user_id=current_user.id,
        stock_id=stock_id,
        transaction_type="SELL",
        shares=shares,
        price=stock.current_price,
        total_amount=sale_amount,
        status="COMPLETED"
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Return transaction with stock data
    return TransactionSchema(
        id=transaction.id,
        stock=stock,
        transaction_type=transaction.transaction_type,
        shares=transaction.shares,
        price=transaction.price,
        total_amount=transaction.total_amount,
        timestamp=transaction.timestamp,
        status=transaction.status,
        notes=transaction.notes
    )


@router.get("/history")
def get_transaction_history(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user's transaction history
    """
    # Query transactions
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(
        Transaction.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    # Create response with stock data and formatted timestamps
    result = []
    for transaction in transactions:
        stock = stock_crud.get_by_id(db, stock_id=transaction.stock_id)
        if stock:
            # Create transaction data with formatted timestamp
            transaction_data = {
                "id": transaction.id,
                "stock": {
                    "id": stock.id,
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "current_price": stock.current_price,
                    "previous_close": stock.previous_close,
                    "exchange": stock.exchange,
                    "sector": stock.sector,
                    "is_active": stock.is_active
                },
                "transaction_type": transaction.transaction_type,
                "shares": transaction.shares,
                "price": transaction.price,
                "total_amount": transaction.total_amount,
                "timestamp": format_ist_for_api(transaction.timestamp),
                "status": transaction.status,
                "notes": transaction.notes
            }
            result.append(transaction_data)
    
    return result
