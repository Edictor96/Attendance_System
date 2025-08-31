"""
Configuration settings from environment variables.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/attendance_system"
    
    # Professor authentication
    PROFESSOR_TOKEN: str = "default_professor_token_change_in_production"
    
    # BLE settings
    BEACON_UUID: str = "0000ffff-0000-1000-8000-00805f9b34fb"
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()