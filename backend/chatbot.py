
"""Control conversacional V11 y RAG público controlado."""

from dataclasses import dataclass, field
from collections import deque

from .security import (
    evaluate,
    REVIEW_MESSAGE,
    RESPUESTA_SEGUIMIENTO,
    es_pregunta_seguimiento,
)

from .validated import (
    exact_route,
    respond_casa,
    respond_law,
)


ABSTAIN = (
    "Todavía no dispongo de una respuesta documental "
    "validada para esta consulta."
)


@dataclass
class Session:
    # Historial de metadatos, sin texto de consultas sensibles.
    history: deque = field(
        default_factory=lambda: deque(maxlen=4)
    )

    # Indicador temporal de orientación preventiva.
    # No almacena nombres, relatos ni datos identificables.
    support_context: bool = False

    def reset(self):
        self.history.clear()
        self.support_context = False


class Chatbot:

    def __init__(self, retriever=None, demo_retriever=None):
        self.retriever = retriever
        self.demo_retriever = demo_retriever

    def reply(self, text, session: Session):

        # 1. Validar entrada.
        if not isinstance(text, str) or not text.strip():
            return {
                "route": "ENTRADA_INVALIDA",
                "answer": "Por favor, escribe una consulta.",
                "qwen_executed": False,
                "memory": len(session.history),
            }

        # 2. Evaluación preventiva previa a RAG.
        pre = evaluate(text)

        if pre["ruta"] in (
            "SEGURIDAD_INMEDIATA_189",
            "ORIENTACION_PREVENTIVA_V11",
        ):
            # No conservar el historial documental previo.
            session.reset()

            # Mantener únicamente una señal temporal para
            # permitir una pregunta breve de seguimiento.
            session.support_context = True

            return {
                "route": pre["ruta"],
                "answer": pre["respuesta"],
                "qwen_executed": False,
                "memory": 0,
            }

        # 3. Pregunta breve de seguimiento a una situación
        # previamente reconocida como sensible.
        if (
            session.support_context
            and es_pregunta_seguimiento(text)
        ):
            session.reset()

            return {
                "route": "ORIENTACION_PREVENTIVA_V11",
                "answer": RESPUESTA_SEGUIMIENTO,
                "qwen_executed": False,
                "memory": 0,
            }

        # Una consulta ajena al seguimiento elimina
        # el indicador temporal de orientación.
        session.support_context = False

        # 4. Rutas documentales validadas.
        # El corpus V11 especializado no se publica
        # automáticamente.
        route = exact_route(text)

        # 5. RAG educativo público.
        # Se mantienen respuestas extractivas,
        # sin generación automática mediante Qwen.
        if self.demo_retriever is not None and not route:

            from .demo_rag import demo_topic

            if demo_topic(text):

                try:
                    found = self.demo_retriever.retrieve(text)
                except Exception:
                    found = []

                if found:

                    content = "\n\n".join(
                        (
                            f"**{f['titulo']}** — {f['texto']}\n\n"
                            f"Fuente: ficha educativa original "
                            f"`{f['id']}`."
                        )
                        for f in found
                    )

                    session.history.append({
                        "topic": "demo"
                    })

                    return {
                        "route": "RAG_DEMO_EXTRACTIVO",
                        "answer": content,
                        "qwen_executed": False,
                        "memory": len(session.history),
                        "sources": [f["id"] for f in found],
                    }

        # 6. Abstención documental cuando no hay ruta
        # o el corpus especializado no está disponible.
        if not route or not self.retriever:

            return {
                "route": "DOCUMENTACION_PENDIENTE",
                "answer": ABSTAIN,
                "qwen_executed": False,
                "memory": len(session.history),
            }

        # 7. Respuestas documentales controladas V11.
        try:

            answer = (
                respond_casa(self.retriever)
                if route == "casa"
                else respond_law(self.retriever)
            )

        except (
            ValueError,
            KeyError,
            RuntimeError,
            TypeError,
            IndexError,
        ) as err:

            return {
                "route": "SIN_EVIDENCIA_DOCUMENTAL",
                "answer": ABSTAIN,
                "qwen_executed": False,
                "memory": len(session.history),
                "diagnostic": type(err).__name__,
            }

        # Solo se registran temas, nunca relatos sensibles.
        session.history.append({
            "topic": route
        })

        return {
            "route": (
                "DOCUMENTAL_CONTROLADA"
                if route == "casa"
                else "DOCUMENTAL_JURIDICA"
            ),
            "answer": answer,
            "qwen_executed": False,
            "memory": len(session.history),
        }

