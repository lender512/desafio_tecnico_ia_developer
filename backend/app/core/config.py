from typing import List
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings
    """
    # Project info
    PROJECT_NAME: str = "IA Developer Challenge"
    PROJECT_DESCRIPTION: str = "A financial restructuring assistant using AI"
    VERSION: str = "1.0.0"
    
    # API
    API_V1_STR: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Azure AI Configuration
    AZURE_INFERENCE_ENDPOINT: str
    AZURE_INFERENCE_CREDENTIAL: str
    AZURE_INFERENCE_MODEL: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
