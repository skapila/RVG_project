"""Configuration module for RVG Project"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class"""

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")

    # Project Settings
    PROJECT_NAME = os.getenv("PROJECT_NAME", "RVG_Project")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Vector Generation
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")
    VECTORS_DIR = os.path.join(DATA_DIR, "vectors")

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        return True


if __name__ == "__main__":
    print(f"Project: {Config.PROJECT_NAME}")
    print(f"Base Directory: {Config.BASE_DIR}")
