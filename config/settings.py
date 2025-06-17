import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "localhost"
    api_port: int = 8000

    # Google AI Configuration
    google_api_key: Optional[str] = None

    # LangChain Configuration
    langchain_api_key: Optional[str] = None
    langchain_tracing_v2: bool = True
    langchain_project: str = "content-recommender"

    # ChromaDB Configuration
    chroma_db_path: str = "./data/chroma_db"
    collection_name: str = "content_collection"

    # Gemini Embedding Configuration
    embedding_model: str = "text-embedding-004"
    embedding_dimension: int = 768

    # Gemini LLM Configuration
    llm_model: str = "gemini-2.0-flash-exp"
    llm_temperature: float = 0.3

    # Search Configuration
    max_search_results: int = 10
    similarity_threshold: float = 0.7

    # Content Configuration
    max_content_length: int = 10000
    supported_file_types: list = [".txt", ".md", ".json", ".csv"]

    # Google API Rate Limits
    embedding_rate_limit: int = 1500  # Requests per minute for free tier
    llm_rate_limit: int = 15  # Requests per minute for free tier

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Create directories if they don't exist
Path(settings.chroma_db_path).mkdir(parents=True, exist_ok=True)