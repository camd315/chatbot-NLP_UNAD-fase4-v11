"""Control de publicación V11: urgencias prioritarias; solo respuestas documentales validadas."""
from dataclasses import dataclass,field
from collections import deque
from .security import evaluate,REVIEW_MESSAGE
from .validated import exact_route,respond_casa,respond_law

ABSTAIN = "Todavía no dispongo de una respuesta documental validada para esta consulta."
@dataclass
class Session:
    history: deque = field(default_factory=lambda:deque(maxlen=4))
    def reset(self): self.history.clear()

class Chatbot:
    def __init__(self,retriever=None): self.retriever=retriever
    def reply(self,text,session:Session):
        if not isinstance(text,str) or not text.strip():
            return {"route":"ENTRADA_INVALIDA","answer":"Por favor, escribe una consulta.","qwen_executed":False}
        pre=evaluate(text)
        if pre['ruta']=='SEGURIDAD_INMEDIATA_189':
            session.reset()
            return {"route":pre['ruta'],"answer":pre['respuesta'],"qwen_executed":False,"memory":0}
        # El componente de comparación semántica V11 depende de 32 referencias V10 NO incluidas.
        # Esta adaptación falla de modo conservador: no abre la generación automática.
        route=exact_route(text)
        if not route or not self.retriever:
            return {"route":"DOCUMENTACION_PENDIENTE","answer":ABSTAIN,"qwen_executed":False,
                    "memory":len(session.history)}
        try:
            answer=respond_casa(self.retriever) if route=='casa' else respond_law(self.retriever)
        except (ValueError,KeyError,RuntimeError,TypeError,IndexError) as err:
            return {"route":"SIN_EVIDENCIA_DOCUMENTAL","answer":ABSTAIN,"qwen_executed":False,
                    "memory":len(session.history),"diagnostic":type(err).__name__}
        session.history.append({"topic":route})  # metadatos, no texto sensible
        return {"route":"DOCUMENTAL_CONTROLADA" if route=='casa' else "DOCUMENTAL_JURIDICA",
                "answer":answer,"qwen_executed":False,"memory":len(session.history)}
