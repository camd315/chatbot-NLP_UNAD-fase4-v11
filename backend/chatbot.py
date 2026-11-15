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
    def __init__(self,retriever=None, demo_retriever=None):
        self.retriever=retriever
        self.demo_retriever=demo_retriever
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
        # Demostración independiente del corpus V11: respuestas EXTRACTIVAS originales.
        if self.demo_retriever is not None and not route:
            from .demo_rag import demo_topic
            if demo_topic(text):
                try:
                    found=self.demo_retriever.retrieve(text,k=2)
                except Exception:
                    found=[]
                if found:
                    content='\n\n'.join(f"**{f['titulo']}** — {f['texto']}\n\nFuente: ficha educativa original `{f['id']}`." for f in found)
                    session.history.append({'topic':'demo'})
                    return {'route':'RAG_DEMO_EXTRACTIVO','answer':content,'qwen_executed':False,
                            'memory':len(session.history),'sources':[f['id'] for f in found]}
        
        # Recuperación privada V11 con 173 fragmentos.
        # Se ejecuta después de las reglas preventivas
        # y antes de la abstención documental.
        if self.retriever is not None and not route:
            from .v11_extractive import retrieve_v11_answer

            try:
                respuesta_v11 = retrieve_v11_answer(
                    self.retriever,
                    text,
                    top_k=4
                )
            except Exception:
                respuesta_v11 = None

            if respuesta_v11:
                session.history.append({
                    "topic": "v11_private"
                })

                return {
                    "route": "RAG_V11_PRIVADO_EXTRACTIVO",
                    "answer": respuesta_v11,
                    "qwen_executed": False,
                    "memory": len(session.history)
                }

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
