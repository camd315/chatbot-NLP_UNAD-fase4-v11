"""Control de publicación V11: seguridad prioritaria y recuperación documental validada.

La orientación preventiva a terceras personas se resuelve antes del RAG.
No se envía texto sensible a modelos generativos y no se conserva en memoria.
"""

from dataclasses import dataclass, field
from collections import deque
import re

from .security import evaluate
from .seguridad_v11_original import normalizar_alerta_v11
from .validated import exact_route, respond_casa, respond_law

ABSTAIN = "Todavía no dispongo de una respuesta documental validada para esta consulta."

# Respuesta educativa de seguridad, sin afirmaciones sobre disponibilidad actual
# de servicios locales que no hayan sido verificadas en tiempo real.
ORIENTACION_TERCEROS = (
    "Si una familiar o conocida está viviendo una situación de violencia, "
    "puedes apoyarla escuchándola sin juzgarla y tomándola en serio.\n\n"
    "- Pregúntale qué apoyo necesita y respeta sus decisiones, sin presionarla.\n"
    "- Evita confrontar al agresor o exponerte a una situación peligrosa.\n"
    "- Si es seguro, ofrécele acompañarla a buscar orientación profesional o institucional.\n"
    "- Si teme por su seguridad, ayúdala a considerar un lugar seguro y una persona de confianza.\n\n"
    "En Colombia, si hay peligro inmediato, pueden contactar al **123** "
    "cuando sea seguro hacerlo. La línea **155** ofrece orientación "
    "sobre violencias de género.\n\n"
    "Este chatbot no contacta autoridades ni sustituye la atención profesional "
    "o los servicios de emergencia."
)

# La capa security.py mantiene la prioridad de las alertas urgentes.
# Esta regla adicional solo identifica consultas preventivas de apoyo a terceros.
_TERCERA_PERSONA = re.compile(
    r"\b(?:mi hermana|mi madre|mi mama|mi hija|mi amiga|mi vecina|"
    r"mi familiar|mi companera|mi prima|mi tia|mi pareja|una mujer|"
    r"una amiga|una familiar|una conocida|ella)\b"
)
_VIOLENCIA = re.compile(
    r"\b(?:golpead[ao]|golpeando|agredid[ao]|agrediendo|maltratad[ao]|"
    r"maltrato|violencia|amenazad[ao]|amenazando|abusad[ao]|abuso|"
    r"controlad[ao]|acoso)\b"
)
_SOLICITA_APOYO = re.compile(
    r"\b(?:como (?:puedo|podemos|debo) ayudarla|como (?:la|le) ayudo|"
    r"que puedo hacer|que deberia hacer|que hago|como apoyar(?:la)?|"
    r"(?:puedo|podemos) apoyarla|"
    r"donde (?:puede|podemos) (?:acudir|buscar ayuda)|"
    r"a quien (?:puede|podemos) llamar|necesita ayuda|"
    r"quiero ayudarla|orientacion para ayudarla)\b"
)
_CONSULTA_CONCEPTUAL = re.compile(
    r"^(?:que es|que significa|define|explica|"
    r"cuales son las senales|tipos de|dame un ejemplo)\b"
)


def _consulta_preventiva_terceros(texto):
    """No sustituye la detección de urgencias ejecutada previamente."""
    q = normalizar_alerta_v11(texto)
    return bool(
        q
        and not _CONSULTA_CONCEPTUAL.search(q)
        and _TERCERA_PERSONA.search(q)
        and _VIOLENCIA.search(q)
        and _SOLICITA_APOYO.search(q)
    )


@dataclass
class Session:
    history: deque = field(default_factory=lambda: deque(maxlen=4))

    def reset(self):
        self.history.clear()


class Chatbot:
    def __init__(self, retriever=None, demo_retriever=None):
        self.retriever = retriever
        self.demo_retriever = demo_retriever

    def reply(self, text, session: Session):
        if not isinstance(text, str) or not text.strip():
            return {
                "route": "ENTRADA_INVALIDA",
                "answer": "Por favor, escribe una consulta.",
                "qwen_executed": False,
            }

        # 1. Las urgencias siempre se resuelven antes de cualquier RAG.
        pre = evaluate(text)
        if pre["ruta"] == "SEGURIDAD_INMEDIATA_189":
            session.reset()
            return {
                "route": pre["ruta"],
                "answer": pre["respuesta"],
                "qwen_executed": False,
                "memory": 0,
            }

        # 2. Orientación preventiva: consulta sobre tercera persona
        # sin indicadores que hayan activado emergencia inmediata.
        if pre["ruta"] == "ORIENTACION_PREVENTIVA_V11" or _consulta_preventiva_terceros(text):
            session.reset()
            return {
                "route": "ORIENTACION_PREVENTIVA_V11",
                "answer": pre.get("respuesta") or ORIENTACION_TERCEROS,
                "qwen_executed": False,
                "memory": 0,
            }

        # Contenido educativo público original, independiente de ChromaDB privado.
        # Se evalúa únicamente después de los controles de seguridad.
        from .public_education import respuesta_publica
        contenido_publico = respuesta_publica(text) if self.retriever is None else None
        if contenido_publico is not None:
            tema, respuesta = contenido_publico
            session.history.append({"topic": tema})
            return {
                "route": tema,
                "answer": respuesta,
                "qwen_executed": False,
                "memory": len(session.history),
            }

        # El componente de comparación semántica V11 depende de 32
        # referencias V10 NO incluidas. No se habilita generación automática.
        route = exact_route(text)

        # 3. Demostración independiente del corpus V11.
        if self.demo_retriever is not None and not route:
            from .demo_rag import demo_topic
            if demo_topic(text):
                try:
                    found = self.demo_retriever.retrieve(text, k=2)
                except Exception:
                    found = []
                if found:
                    content = "\n\n".join(
                        f"**{f['titulo']}** — {f['texto']}\n\n"
                        f"Fuente: ficha educativa original `{f['id']}`."
                        for f in found
                    )
                    session.history.append({"topic": "demo"})
                    return {
                        "route": "RAG_DEMO_EXTRACTIVO",
                        "answer": content,
                        "qwen_executed": False,
                        "memory": len(session.history),
                        "sources": [f["id"] for f in found],
                    }

        # 4. Recuperación privada V11, si está autorizada y disponible.
        if self.retriever is not None and not route:
            from .v11_extractive import retrieve_v11_answer
            try:
                respuesta_v11 = retrieve_v11_answer(
                    self.retriever, text, top_k=4
                )
            except Exception:
                respuesta_v11 = None

            if respuesta_v11:
                session.history.append({"topic": "v11_private"})
                return {
                    "route": "RAG_V11_PRIVADO_EXTRACTIVO",
                    "answer": respuesta_v11,
                    "qwen_executed": False,
                    "memory": len(session.history),
                }

        if not route or not self.retriever:
            return {
                "route": "DOCUMENTACION_PENDIENTE",
                "answer": ABSTAIN,
                "qwen_executed": False,
                "memory": len(session.history),
            }

        try:
            answer = (
                respond_casa(self.retriever)
                if route == "casa"
                else respond_law(self.retriever)
            )
        except (ValueError, KeyError, RuntimeError, TypeError, IndexError) as err:
            return {
                "route": "SIN_EVIDENCIA_DOCUMENTAL",
                "answer": ABSTAIN,
                "qwen_executed": False,
                "memory": len(session.history),
                "diagnostic": type(err).__name__,
            }

        session.history.append({"topic": route})
        return {
            "route": (
                "DOCUMENTAL_CONTROLADA" if route == "casa"
                else "DOCUMENTAL_JURIDICA"
            ),
            "answer": answer,
            "qwen_executed": False,
            "memory": len(session.history),
        }
