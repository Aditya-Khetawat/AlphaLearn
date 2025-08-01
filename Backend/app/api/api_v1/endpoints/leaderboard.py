from typing import Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.models.models import User, Portfolio, Position, Stock
from app.core.json_utils import SafeJSONResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_class=SafeJSONResponse)
def get_leaderboard(
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get leaderboard of top performing traders
    
    Ranks users by their portfolio performance (total return percentage)
    """
    try:
        # Get all users with their portfolios and calculate returns
        leaderboard_data = []
        
        # Query all users who have portfolios
        users_with_portfolios = db.query(User).join(Portfolio).all()
        
        for user in users_with_portfolios:
            portfolio = user.portfolio
            if not portfolio:
                continue
                
            # Calculate portfolio metrics
            positions = db.query(Position, Stock).join(
                Stock, Position.stock_id == Stock.id
            ).filter(Position.portfolio_id == portfolio.id).all()
            
            # Calculate current portfolio value
            positions_value = 0
            invested_value = 0
            
            for position, stock in positions:
                if position.shares > 0:  # Only active positions
                    position_value = position.shares * stock.current_price
                    position_cost = position.shares * position.average_price
                    positions_value += position_value
                    invested_value += position_cost
            
            # Calculate returns (only on invested amount, not including cash)
            total_return = positions_value - invested_value
            total_return_percent = (total_return / invested_value * 100) if invested_value > 0 else 0
            
            # Total portfolio value (stocks + cash)
            total_portfolio_value = positions_value + portfolio.cash_balance
            
            leaderboard_data.append({
                "user_id": user.id,
                "username": user.username or user.email.split('@')[0],
                "full_name": user.full_name,
                "email": user.email,
                "portfolio_value": total_portfolio_value,
                "invested_value": invested_value,
                "positions_value": positions_value,
                "cash_balance": portfolio.cash_balance,
                "total_return": total_return,
                "total_return_percent": total_return_percent,
                "active_positions": len([p for p, s in positions if p.shares > 0])
            })
        
        # Sort by total return percentage (descending), then by portfolio value
        leaderboard_data.sort(key=lambda x: (x['total_return_percent'], x['portfolio_value']), reverse=True)
        
        # Add ranks
        for i, entry in enumerate(leaderboard_data, 1):
            entry['rank'] = i
        
        # Limit results
        leaderboard_data = leaderboard_data[:limit]
        
        return {
            "leaderboard": leaderboard_data,
            "total_users": len(leaderboard_data),
            "message": f"Top {len(leaderboard_data)} traders by performance" if leaderboard_data else "No traders yet - start trading to appear on the leaderboard!"
        }
        
    except Exception as e:
        logger.error(f"Error generating leaderboard: {e}")
        return {
            "leaderboard": [],
            "total_users": 0,
            "error": f"Failed to generate leaderboard: {str(e)}",
            "message": "Leaderboard temporarily unavailable"
        }


@router.get("/user/{user_id}", response_class=SafeJSONResponse)
def get_user_rank(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a specific user's rank and performance metrics
    """
    try:
        # Get the full leaderboard to find user's rank
        leaderboard_response = get_leaderboard(limit=1000, db=db)
        leaderboard = leaderboard_response.get("leaderboard", [])
        
        # Find the user in the leaderboard
        user_entry = None
        for entry in leaderboard:
            if entry["user_id"] == user_id:
                user_entry = entry
                break
        
        if not user_entry:
            return {
                "rank": None,
                "total_users": len(leaderboard),
                "message": "User not found in leaderboard or has no portfolio",
                "error": "User not ranked"
            }
        
        return {
            "rank": user_entry["rank"],
            "total_users": len(leaderboard),
            "user_data": user_entry,
            "message": f"User ranked #{user_entry['rank']} out of {len(leaderboard)} traders"
        }
        
    except Exception as e:
        logger.error(f"Error getting user rank for user_id {user_id}: {e}")
        return {
            "rank": None,
            "total_users": 0,
            "error": f"Failed to get user rank: {str(e)}",
            "message": "Rank lookup temporarily unavailable"
        }
