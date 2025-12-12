"""
Application settings and configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    ENVIRONMENT: str = "development"
    PORT: int = 8002
    HOST: str = "0.0.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # MongoDB Configuration
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "matchtal_profiles"
    MONGODB_TEST_DATABASE: str = "matchtal_profiles_test"
    
    # JWT Configuration (shared with auth-service)
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    
    # Auth Service Configuration (for token validation)
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    AUTH_SERVICE_VALIDATE_ENDPOINT: str = "/api/v1/auth/validate"
    
    # Security
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCOUNT_ID: str = ""
    ECS_CLUSTER_NAME: str = "matchtal-cluster"
    ECS_SERVICE_NAME: str = "profile-service"
    ECR_REPOSITORY_NAME: str = "matchtal/profile-service"
    
    # S3 Configuration (for resume storage)
    S3_BUCKET_NAME: str = "matchtal-resumes"
    S3_REGION: str = "us-east-1"
    
    # Application
    APP_NAME: str = "MatchTal Profile Service"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name == 'CORS_ORIGINS':
                try:
                    return json.loads(raw_val)
                except:
                    return raw_val.split(',')
            return cls.json_loads(raw_val)


settings = Settings()





