"""Chatbot Prevención V12: interfaz Streamlit de evaluación privada.

No despliega contenido de forma pública. Requiere habilitación explícita para
pruebas locales. Reutiliza backend_v12 del Paso 28 y la colección existente.
"""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Chatbot Prevención | Prueba V12",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Carpeta de esta aplicación: independiente de Google Colab.
DEFAULT_BASE = Path(__file__).resolve().parent


def _config(name: str, fallback: str = "") -> str:
    """Preferir variables de entorno; aceptar st.secrets cuando existan."""
    if name in os.environ:
        return os.environ[name]
    try:
        return str(st.secrets.get(name, fallback))
    except Exception:
        return fallback


def _enabled() -> bool:
    return _config("CHATBOT_PREVENCION_PRIVATE_TEST", "false").lower() in (
        "1", "true", "yes", "si"
    )


def _base_dir() -> Path:
    raw = _config("CHATBOT_PREVENCION_V12_DIR", str(DEFAULT_BASE))
    return Path(raw).expanduser().resolve()


st.title("🛡️ Chatbot Prevención")
st.caption("Prototipo educativo · Versión V12 · Prueba privada")
st.info(
    "Este prototipo ofrece información educativa basada en documentos. "
    "No sustituye la orientación profesional, jurídica, psicológica o de emergencia. "
    "Las rutas institucionales y la vigencia normativa requieren verificación actualizada."
)

with st.sidebar:
    st.subheader("Áreas de consulta")
    st.markdown(
        "- Autonomía femenina\n"
        "- Prevención de violencias\n"
        "- Orientación institucional"
    )
    st.divider()
    st.caption("Modo privado de evaluación. No constituye un servicio oficial.")
    if st.button("Limpiar conversación", use_container_width=True):
        st.session_state.pop("prevencion_v12_messages", None)
        st.rerun()

if not _enabled():
    st.warning(
        "La versión V12 está deshabilitada para el público. "
        "El acceso debe configurarse solo en un entorno privado y controlado. "
        "La variable de habilitación no sustituye la autenticación."
    )
    st.stop()

BASE = _base_dir()
if not (BASE / "backend_v12" / "chatbot_v12.py").is_file():
    st.error("No se encontró backend_v12 en la carpeta configurada de la aplicación.")
    st.stop()
if not (BASE / "chroma_db_v12").is_dir():
    st.error("No se encontró chroma_db_v12. Configura su ubicación privada antes de habilitar el chatbot.")
    st.stop()


@st.cache_resource(show_spinner="Cargando el recuperador documental...")
def _load_chatbot(base: str):
    from backend_v12.rag_v12 import RecuperadorV12
    from backend_v12.chatbot_v12 import ChatbotDocumentalV12

    retriever = RecuperadorV12(Path(base) / "chroma_db_v12")
    return ChatbotDocumentalV12(retriever)


try:
    chatbot = _load_chatbot(str(BASE))
except Exception:
    st.error(
        "No fue posible cargar el recuperador V12. "
        "Comprueba las dependencias, la colección y los archivos del backend."
    )
    st.stop()

if "prevencion_v12_messages" not in st.session_state:
    st.session_state.prevencion_v12_messages = []


for msg in st.session_state.prevencion_v12_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Fuentes documentales"):
                for src in msg["sources"]:
                    st.write(src)

if not st.session_state.prevencion_v12_messages:
    st.markdown("**Preguntas para comenzar**")
    sugerencias = [
        "¿Cómo pueden las mujeres fortalecer su autonomía económica?",
        "¿Qué señales permiten reconocer la violencia psicológica?",
        "¿Qué políticas públicas apoyan los derechos de las mujeres en Cali?",
    ]
    for idx, pregunta_sugerida in enumerate(sugerencias):
        if st.button(pregunta_sugerida, key=f"sugerencia_{idx}", use_container_width=True):
            st.session_state.prevencion_v12_pending = pregunta_sugerida
            st.rerun()

pregunta = st.chat_input("Escribe tu pregunta", max_chars=600)
pregunta_pendiente = st.session_state.pop("prevencion_v12_pending", None)
if pregunta_pendiente:
    pregunta = pregunta_pendiente

if pregunta and pregunta.strip():
    pregunta = pregunta.strip()
    st.session_state.prevencion_v12_messages.append(
        {"role": "user", "content": pregunta}
    )
    with st.chat_message("user"):
        st.markdown(pregunta)
    with st.chat_message("assistant"):
        with st.spinner("Buscando evidencia documental..."):
            try:
                resultado = chatbot.responder(pregunta)
            except Exception:
                st.error("No se pudo completar esta consulta. Revisa el backend V12.")
                st.stop()
        # Mostrar los extractos con saltos de línea, sin interpretación como HTML.
        st.markdown(resultado.respuesta.replace("\n", "  \n"))
        fuentes = list(dict.fromkeys(ev.cita for ev in resultado.evidencias))
        if fuentes:
            with st.expander("Fuentes documentales"):
                for fuente in fuentes:
                    st.write(fuente)
        st.caption(f"Estado técnico: {resultado.estado}")
        st.session_state.prevencion_v12_messages.append(
            {"role": "assistant", "content": resultado.respuesta, "sources": fuentes}
        )
