from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, stocks, portfolios, transactions, stock_monitoring, health, leaderboard, websocket

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["Portfolios"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(stock_monitoring.router, prefix="/monitoring", tags=["Stock Monitoring"])
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
