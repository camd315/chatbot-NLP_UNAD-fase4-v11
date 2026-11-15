"""Streamlit – Ejercicio 3 / UNAD Fase 4 (demostración RAG controlada)."""
import streamlit as st
from config import SETTINGS
from backend.chatbot import Chatbot, Session
from backend.rag import V11Retriever

st.set_page_config(page_title=SETTINGS.app_title,page_icon="💬",layout="centered")
st.title("Asistente académico NLP · Fase 4")
st.caption("Prototipo educativo. No sustituye orientación profesional ni servicios de emergencias.")
with st.expander("Alcance, fuentes y limitaciones",expanded=True):
    st.write("Modo de demostración: recuperación semántica E5 + ChromaDB con textos educativos originales. "
             "La base documental V11 y Qwen NO están publicados. No corresponde a un servicio institucional.")
    st.write("Las respuestas documentales del prototipo V11 siguen sujetas a validaciones estrictas. "
             "El sistema puede equivocarse y no consulta información de servicios en tiempo real.")
    st.write("Preguntas de demostración: «¿Qué es RAG?», «¿Para qué sirve ChromaDB?», "
             "«¿Qué es un embedding?» o «¿Cómo se evalúa un chatbot?». "
             "Las consultas de urgencia se atienden antes que la recuperación documental.")

@st.cache_resource(show_spinner=False)
def load_original():
    if not SETTINGS.authorized_corpus:return None,"Base V11 no habilitada: faltan autorizaciones de publicación."
    try:
        ret=V11Retriever()
        return ret,"Corpus V11 autorizado cargado (173 fragmentos)."
    except Exception as exc:
        return None,"Corpus V11 no disponible: "+type(exc).__name__

@st.cache_resource(show_spinner=False)
def load_demo():
    if not SETTINGS.demo_rag_enabled:return None,"Demostración RAG deshabilitada."
    from backend.demo_rag import DemoRetriever
    return DemoRetriever(),"Demostración educativa RAG activa (8 fichas originales)."

original,status=load_original()
st.info(status)
demo=None
if SETTINGS.demo_rag_enabled:
    try:
        with st.spinner("Cargando modelo de embeddings E5 para la demostración…"):
            demo,demo_status=load_demo()
        st.success(demo_status)
    except Exception as exc:
        st.warning("La demostración RAG no pudo cargarse: "+type(exc).__name__)
        st.caption("Si es el primer inicio, revisa los registros de dependencias y descarga del modelo.")

if 'chat_session' not in st.session_state:st.session_state.chat_session=Session()
if 'messages' not in st.session_state:st.session_state.messages=[]
if st.button("Nueva conversación"):
    st.session_state.chat_session.reset()
    st.session_state.messages=[]
    st.rerun()
for msg in st.session_state.messages:
    with st.chat_message(msg['role']): st.markdown(msg['content'])
question=st.chat_input("Escribe tu consulta")
if question:
    with st.chat_message('user'):st.markdown(question)
    result=Chatbot(original,demo).reply(question,st.session_state.chat_session)
    emergency=result['route']=='SEGURIDAD_INMEDIATA_189'
    if emergency:
        st.session_state.messages=[]
        st.session_state.chat_session.reset()
    else:
        st.session_state.messages.append({'role':'user','content':question})
    with st.chat_message('assistant'):
        st.markdown(result['answer'])
        st.caption('Ruta: '+result['route'])
    if not emergency:
        st.session_state.messages.append({'role':'assistant','content':result['answer']})
