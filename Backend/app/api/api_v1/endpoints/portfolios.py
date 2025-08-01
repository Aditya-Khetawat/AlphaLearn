from typing import Any, List
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud import portfolio as portfolio_crud
from app.crud import stock as stock_crud
from app.models.models import User, Position
from app.schemas.schemas import Portfolio, Position as PositionSchema
from app.core.websocket_manager import connection_manager

router = APIRouter()


@router.get("/me", response_model=Portfolio)
def read_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user's portfolio
    """
    # Get the user's portfolio
    portfolio = portfolio_crud.get_by_user_id(db, user_id=current_user.id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    # Calculate portfolio value
    value_data = portfolio_crud.calculate_portfolio_value(db, portfolio_id=portfolio.id)
    
    # Get all positions with stock data
    positions = db.query(Position).filter(Position.portfolio_id == portfolio.id).all()
    position_data = []
    
    for position in positions:
        stock = stock_crud.get_by_id(db, stock_id=position.stock_id)
        if stock and position.shares > 0:
            # Calculate position metrics
            current_value = position.shares * stock.current_price
            cost_basis = position.shares * position.average_price
            total_return = current_value - cost_basis
            total_return_percent = (total_return / cost_basis) * 100 if cost_basis > 0 else 0
            
            # Create position object
            position_obj = PositionSchema(
                id=position.id,
                stock=stock,
                shares=position.shares,
                average_price=position.average_price,
                current_value=current_value,
                total_return=total_return,
                total_return_percent=total_return_percent
            )
            position_data.append(position_obj)
    
    # Compile and return the full portfolio data
    return Portfolio(
        id=portfolio.id,
        user_id=current_user.id,
        cash_balance=portfolio.cash_balance,
        positions=position_data,
        total_value=value_data["total_value"],
        invested_value=value_data["invested_value"],
        total_return=value_data["total_return"],
        total_return_percent=value_data["total_return_percent"],
        created_at=portfolio.created_at,
        updated_at=portfolio.updated_at
    )


async def broadcast_leaderboard_update(db: Session):
    """
    Broadcast updated leaderboard data to all connected WebSocket clients
    """
    try:
        from app.api.api_v1.endpoints.leaderboard import get_leaderboard
        
        # Get updated leaderboard data
        leaderboard_data = get_leaderboard(limit=50, db=db)
        
        # Broadcast to all leaderboard WebSocket connections
        await connection_manager.broadcast_leaderboard_update(leaderboard_data)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error broadcasting leaderboard update: {e}")


@router.post("/buy")
async def buy_stock(
    symbol: str,
    shares: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Buy stocks (placeholder endpoint)
    This would trigger leaderboard updates in a real implementation
    """
    # TODO: Implement actual buy logic
    
    # After successful trade, broadcast leaderboard update
    await broadcast_leaderboard_update(db)
    
    return {"message": f"Buy order placed for {shares} shares of {symbol}"}


@router.post("/sell")
async def sell_stock(
    symbol: str,
    shares: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Sell stocks (placeholder endpoint)  
    This would trigger leaderboard updates in a real implementation
    """
    # TODO: Implement actual sell logic
    
    # After successful trade, broadcast leaderboard update
    await broadcast_leaderboard_update(db)
    
    return {"message": f"Sell order placed for {shares} shares of {symbol}"}
