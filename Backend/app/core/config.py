import os
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AlphaLearn"
    
    # Server
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS Configuration - Railway compatible
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002", 
        "http://localhost:3003", 
        "http://localhost", 
        "https://alphalearn.vercel.app",
        "https://alpha-learn-xxv4.vercel.app",  # Your actual Vercel deployment
        "*"  # Allow all origins for development - restrict in production if needed
        # Note: Railway and Vercel domains added dynamically in main.py
    ]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins including dynamic Railway/Vercel domains"""
        origins = self.CORS_ORIGINS.copy()
        
        # Add Railway domain if available
        railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        if railway_domain:
            origins.append(f"https://{railway_domain}")
            
        # Add Vercel domain if available
        vercel_url = os.getenv("VERCEL_URL")
        if vercel_url:
            origins.append(f"https://{vercel_url}")
            
        return origins
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "alphalearn")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Stock Data Configuration
    STOCK_DATA_SOURCE: str = os.getenv("STOCK_DATA_SOURCE", "yfinance")
    DEFAULT_EXCHANGE: str = os.getenv("DEFAULT_EXCHANGE", "NSE")
    
    # Timezone Configuration
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Kolkata")
    
    # User settings
    INITIAL_BALANCE: float = 100000.0  # ₹1,00,000 starting balance
    
    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str]) -> Any:
        # First check if DATABASE_URL is provided (Railway/Heroku style)
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url
            
        # If direct URI is provided, use it
        if isinstance(v, str) and v:
            return v
            
        # Fallback to building from components (local development)
        postgres_server = os.getenv("POSTGRES_SERVER", "localhost")
        postgres_user = os.getenv("POSTGRES_USER", "postgres")
        postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
        postgres_db = os.getenv("POSTGRES_DB", "alphalearn")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        
        return f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}:{postgres_port}/{postgres_db}"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
