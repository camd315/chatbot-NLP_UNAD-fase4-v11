"""Frontend Streamlit — prototipo académico controlado V11."""
import streamlit as st
from config import SETTINGS
from backend.chatbot import Chatbot,Session
from backend.rag import V11Retriever, CorpusUnavailable

st.set_page_config(page_title=SETTINGS.app_title, page_icon="💬", layout="centered")
st.title("Asistente académico de NLP · Fase 4")
st.caption("Prototipo de investigación. No es un servicio de emergencias ni asesoría jurídica.")
with st.expander("Capacidades y limitaciones",expanded=True):
    st.write("Esta demostración conserva el control de respuestas validadas y las reglas preventivas V11. "
             "No genera ni publica respuestas abiertas de Qwen. La clasificación semántica V11 completa "
             "requiere referencias del cuaderno V10 no incluidas en el paquete.")
    st.write("Los modelos de IA pueden producir errores. La información institucional o jurídica puede haber cambiado.")
    st.write("Consultas de ensayo: orientación psicosocial y jurídica en Casa Matria de Cali; "
             "derechos de la Ley 1257 de 2008; o una consulta general para verificar la abstención.")

@st.cache_resource(show_spinner=False)
def load_retriever():
    if not SETTINGS.authorized_corpus:
        return None,"Corpus público no autorizado: búsqueda documental deshabilitada."
    try:
        return V11Retriever(),"Corpus cargado y verificado: 173 fragmentos."
    except Exception as exc:
        return None,"Corpus no disponible o incompatible: " + type(exc).__name__

retriever,status=load_retriever()
st.info(status)
if "chat_session" not in st.session_state:st.session_state.chat_session=Session()
if "messages" not in st.session_state:st.session_state.messages=[]
if st.button("Nueva conversación"):
    st.session_state.chat_session.reset()
    st.session_state.messages=[]
    st.rerun()
for msg in st.session_state.messages:
    with st.chat_message(msg['role']): st.markdown(msg['content'])
question=st.chat_input("Escribe tu consulta")
if question:
    with st.chat_message('user'):st.markdown(question)
    result=Chatbot(retriever).reply(question,st.session_state.chat_session)
    if result['route']=='SEGURIDAD_INMEDIATA_189':
        # No conservar el texto de emergencia en la interfaz ni en memoria de sesión.
        st.session_state.messages=[]
        st.session_state.chat_session.reset()
    else:
        st.session_state.messages.append({'role':'user','content':question})
    with st.chat_message('assistant'):
        st.markdown(result['answer'])
        st.caption('Ruta de respuesta: '+result['route'])
    if result['route']!='SEGURIDAD_INMEDIATA_189':
        st.session_state.messages.append({'role':'assistant','content':result['answer']})
