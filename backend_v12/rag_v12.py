"""Recuperador privado V12: E5 + ChromaDB. No modifica V11.

Diseñado para evaluación local/Colab; no habilitar en portal público hasta
validar licencia de documentos, pertinencia y controles funcionales.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

COLLECTION_NAME = "conaldem_v12_piloto_privado"
MODEL_NAME = "intfloat/multilingual-e5-small"


@dataclass(frozen=True)
class Evidencia:
    id: str
    texto: str
    documento: str
    pagina: Optional[int]
    origen: str
    eje: str
    similitud: float

    @property
    def cita(self) -> str:
        pagina = f", p. {self.pagina}" if self.pagina and self.pagina > 0 else ""
        return f"{self.documento}{pagina}"


class RecuperadorV12:
    """Consulta la colección V12 de solo lectura, usando prefijo E5 `query:`."""

    def __init__(self, ruta_chroma: str | Path, *, modelo=None,
                 nombre_coleccion: str = COLLECTION_NAME):
        from chromadb import PersistentClient
        from sentence_transformers import SentenceTransformer

        self.ruta_chroma = Path(ruta_chroma)
        if not self.ruta_chroma.is_dir():
            raise FileNotFoundError(f"No existe la carpeta de ChromaDB: {self.ruta_chroma}")
        self.modelo = modelo if modelo is not None else SentenceTransformer(MODEL_NAME)
        self.cliente = PersistentClient(path=str(self.ruta_chroma))
        self.coleccion = self.cliente.get_collection(name=nombre_coleccion)
        if self.coleccion.count() == 0:
            raise ValueError("La colección V12 está vacía")

    def recuperar(self, pregunta: str, *, cantidad: int = 5) -> list[Evidencia]:
        pregunta = pregunta.strip()
        if not pregunta:
            raise ValueError("La pregunta no puede estar vacía")
        if not 1 <= cantidad <= 20:
            raise ValueError("cantidad debe estar entre 1 y 20")

        vector = self.modelo.encode(
            ["query: " + pregunta], normalize_embeddings=True
        )[0].tolist()
        respuesta = self.coleccion.query(
            query_embeddings=[vector],
            n_results=min(cantidad, self.coleccion.count()),
            include=["documents", "metadatas", "distances"],
        )
        evidencias = []
        for id_, texto, meta, distancia in zip(
            respuesta["ids"][0],
            respuesta["documents"][0],
            respuesta["metadatas"][0],
            respuesta["distances"][0],
        ):
            meta = meta or {}
            pagina_raw = meta.get("pagina")
            try:
                pagina = int(pagina_raw) if pagina_raw is not None else None
            except (TypeError, ValueError):
                pagina = None
            if pagina is not None and pagina <= 0:
                pagina = None  # V11: 0 equivale a página desconocida
            evidencias.append(Evidencia(
                id=str(id_), texto=str(texto or ""),
                documento=str(meta.get("documento") or "Documento sin identificar"),
                pagina=pagina, origen=str(meta.get("origen") or "desconocido"),
                eje=str(meta.get("eje") or "sin_etiqueta"),
                similitud=max(0.0, min(1.0, 1.0 - float(distancia))),
            ))
        return evidencias
