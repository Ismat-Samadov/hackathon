"""
Configuration settings for the SOCAR Document Processing System.

All settings are loaded from environment variables with sensible defaults.
See .env.example for available configuration options.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Application configuration settings.

    All values are loaded from environment variables with defaults.
    This ensures flexible deployment across different environments.
    """

    # ========================================================================
    # Azure AI Foundry Configuration
    # ========================================================================
    BASE_URL: str = os.getenv(
        "BASE_URL",
        "https://llmapihackathon.services.ai.azure.com/openai/v1/"
    )
    """Azure AI Foundry API endpoint (OpenAI-compatible)"""

    API_KEY: str = os.getenv("API_KEY", "")
    """Azure AI Foundry API authentication key"""

    # ========================================================================
    # Model Configuration
    # ========================================================================
    OCR_MODEL: str = os.getenv(
        "OCR_MODEL",
        "Llama-4-Maverick-17B-128E-Instruct-FP8"
    )
    """Model for OCR (vision/text extraction)"""

    CHAT_MODEL: str = os.getenv(
        "CHAT_MODEL",
        "Llama-4-Maverick-17B-128E-Instruct-FP8"
    )
    """Model for chat/response generation"""

    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "BAAI/bge-large-en-v1.5"
    )
    """Model for text embeddings (1024 dimensions)"""

    # ========================================================================
    # OCR Processing Settings
    # ========================================================================
    OCR_DPI_SCALE: float = float(os.getenv("OCR_DPI_SCALE", "1.5"))
    """PDF page rendering scale (1.5 = 108 DPI)"""

    OCR_MAX_TOKENS: int = int(os.getenv("OCR_MAX_TOKENS", "4000"))
    """Maximum tokens for OCR model responses"""

    JPEG_QUALITY: int = int(os.getenv("JPEG_QUALITY", "90"))
    """JPEG compression quality for PDF images (0-100)"""

    # ========================================================================
    # Knowledge Base Settings
    # ========================================================================
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    """Text chunk size for knowledge base segmentation"""

    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    """Overlap between chunks for context preservation"""

    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    """Number of top results to retrieve in knowledge base search"""

    # ========================================================================
    # Vector Database Configuration (Pinecone)
    # ========================================================================
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    """Pinecone API key for cloud vector database"""

    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "hackathon")
    """Pinecone index name for storing embeddings"""

    PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD", "aws")
    """Pinecone cloud provider (aws, gcp, azure)"""

    PINECONE_REGION: str = os.getenv("PINECONE_REGION", "us-east-1")
    """Pinecone region for index deployment"""

    # ========================================================================
    # API Server Settings
    # ========================================================================
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    """Host address for API server binding"""

    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    """Port number for API server binding"""


# Global settings instance
settings = Settings()
