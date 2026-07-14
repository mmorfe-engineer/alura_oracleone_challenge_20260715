"""Configuración centralizada — Production-ready."""

import os
import logging
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuración application."""

    # ===== MISTRAL API (REAL) =====
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = "mistral-large"
    MISTRAL_TEMPERATURE: float = 0.3
    MISTRAL_MAX_TOKENS: int = 1024
    MISTRAL_TIMEOUT: int = 30

    # ===== DOCUMENT & VECTOR DB =====
    DOCUMENT_PATH: str = os.getenv(
        "DOCUMENT_PATH",
        "./data/bdt_fintech_policies.csv"
    )
    CHROMA_DB_PATH: str = os.getenv(
        "CHROMA_DB_PATH",
        "./chroma_data"
    )

    # ===== EMBEDDINGS =====
    EMBEDDINGS_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDINGS_DEVICE: str = "cpu"  # O "cuda" si tienes GPU

    # ===== RAG =====
    RAG_TOP_K: int = 5
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50

    # ===== APP =====
    APP_ENV: str = os.getenv("APP_ENV", "development")
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", 8501))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ===== LOGGING =====
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def validate(self) -> None:
        """Valida configuración crítica."""
        if not self.MISTRAL_API_KEY:
            raise ValueError("❌ MISTRAL_API_KEY no está configurada")

        if not Path(self.DOCUMENT_PATH).exists():
            raise ValueError(f"❌ Documento no encontrado: {self.DOCUMENT_PATH}")

        if self.APP_ENV not in ["development", "production", "testing"]:
            raise ValueError(f"❌ APP_ENV inválido: {self.APP_ENV}")

        logger.info("✅ Configuración válida")

    @classmethod
    def from_env(cls) -> "Config":
        """Carga config desde environment."""
        config = cls()
        config.validate()
        return config

def get_config() -> Config:
    """Singleton de configuración."""
    if not hasattr(get_config, "_instance"):
        get_config._instance = Config.from_env()
    return get_config._instance


# Setup logging
def setup_logging(config: Config):
    """Configura logging de la app."""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log", encoding="utf-8")
        ]
    )
