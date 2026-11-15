"""Parámetros centralizados; ninguna credencial en el repositorio."""
from pathlib import Path
from dataclasses import dataclass
import os

ROOT = Path(__file__).resolve().parent
@dataclass(frozen=True)
class Settings:
    app_title: str = "Asistente académico NLP · Fase 4"
    embedding_model: str = "intfloat/multilingual-e5-small"
    collection_name: str = os.environ.get("CHROMA_COLLECTION_NAME", "")
    chroma_path: Path = ROOT / "data" / "chroma_db"
    top_k: int = 4
    history_limit: int = 4
    # Solo habilitar tras auditoría jurídica y de privacidad del corpus.
    authorized_corpus: bool = os.environ.get("AUTHORIZED_PUBLIC_CORPUS", "false").lower() == "true"
    # V11 no autoriza publicar borradores Qwen.
    allow_generated_answers: bool = False
    # Demo pública con textos didácticos propios. RAG V11 original: NO instalado.
    demo_rag_enabled: bool = os.environ.get("DEMO_RAG_ENABLED", "true").lower() == "true"
    log_events: bool = os.environ.get("LOG_EVENTS", "false").lower() == "true"

SETTINGS = Settings()
