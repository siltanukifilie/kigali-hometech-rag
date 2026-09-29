import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _path_from_env(name: str, default: str) -> Path:
    value = Path(os.getenv(name, default))
    return value if value.is_absolute() else BASE_DIR / value


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
    embedding_dimensions: int = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))
    embedding_batch_size: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "10"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "350"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "60"))
    top_k: int = int(os.getenv("TOP_K", "4"))
    data_path: Path = BASE_DIR / "data"
    chroma_path: Path = _path_from_env("CHROMA_DB_PATH", "./chroma_db")
    chroma_collection: str = os.getenv(
        "CHROMA_COLLECTION", "kigali_hometech_documents"
    )
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://127.0.0.1:5174,http://localhost:5174"
        ).split(",")
        if origin.strip()
    )


settings = Settings()


def require_api_key() -> None:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to rag-based-chatbot/.env."
        )
