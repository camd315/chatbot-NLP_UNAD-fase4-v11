
"""Streamlit – Ejercicio 3 / UNAD Fase 4.

Prototipo académico orientado a la autonomía femenina,
la prevención de violencias y la orientación institucional
en Santiago de Cali.

Despliegue público con demostración RAG controlada.
"""

import streamlit as st

from config import SETTINGS
from backend.chatbot import Chatbot, Session
from backend.rag import V11Retriever


# ============================================================
# 1. CONFIGURACIÓN GENERAL DE LA INTERFAZ
# ============================================================

st.set_page_config(
    page_title="Autonomía femenina y prevención de violencias · UNAD",
    page_icon="💬",
    layout="centered"
)

st.title("Asistente de autonomía femenina y prevención de violencias")

st.caption(
    "Prototipo académico de inteligencia artificial | "
    "UNAD · Natural Language Processing · Fase 4"
)


# ============================================================
# 2. PRESENTACIÓN Y PROPÓSITO DEL CHATBOT
# ============================================================

st.markdown("""
### Bienvenida al asistente

Este chatbot es un prototipo académico de inteligencia artificial
desarrollado en el marco del curso **Natural Language Processing**
de la Universidad Nacional Abierta y a Distancia (UNAD).

Su propósito es contribuir al fortalecimiento de la autonomía
femenina, la prevención de violencias de género y el acceso
a información sobre derechos y servicios institucionales
de orientación disponibles en **Santiago de Cali**.

Está concebido principalmente para mujeres mayores de 18 años
interesadas en acceder a información educativa y preventiva.
""")


# ============================================================
# 3. EJES TEMÁTICOS DEL PROYECTO
# ============================================================

with st.expander(
    "Conoce los tres ejes temáticos del proyecto",
    expanded=True
):

    st.markdown("""
    **1. Autonomía femenina**

    Información educativa sobre:

    - Autoconocimiento y autoestima.
    - Límites personales.
    - Toma de decisiones.
    - Relaciones saludables.

    **2. Prevención de violencias**

    Información general sobre:

    - Conceptos de violencia de género.
    - Manifestaciones de violencia.
    - Señales generales de control y manipulación.
    - Reconocimiento de conductas abusivas.

    **3. Orientación institucional**

    Información sobre:

    - Derechos de las mujeres.
    - Servicios institucionales de orientación.
    - Entidades y canales oficiales.
    - Rutas de orientación disponibles en Santiago de Cali.

    **Importante:** estos ejes corresponden al alcance previsto
    del proyecto. La disponibilidad de respuestas depende
    de las fuentes documentales habilitadas.
    """)


# ============================================================
# 4. INSTRUCCIONES PARA UTILIZAR EL CHATBOT
# ============================================================

with st.expander(
    "¿Cómo utilizar el chatbot?",
    expanded=True
):

    st.markdown("""
    **Instrucciones de uso**

    1. Escribe una pregunta en el cuadro de conversación
       ubicado en la parte inferior de la pantalla.
    2. Presiona **Enter** para enviar la consulta.
    3. Lee la respuesta proporcionada por el asistente.
    4. Cuando exista información documental disponible,
       revisa la fuente indicada.
    5. Puedes formular nuevas preguntas dentro
       de la misma conversación.
    6. Selecciona **Nueva conversación** para comenzar
       una interacción diferente.

    **Privacidad**

    Evita incluir nombres completos, documentos de identidad,
    direcciones, teléfonos o relatos íntimos en tus consultas.
    """)


# ============================================================
# 5. ESTADO ACTUAL DE LA DEMOSTRACIÓN
# ============================================================

with st.expander(
    "Estado de la versión pública y sus limitaciones",
    expanded=False
):

    st.markdown("""
    **Funcionalidades actualmente disponibles**

    Esta versión pública permite comprobar:

    - El funcionamiento de la interfaz conversacional.
    - La recuperación semántica mediante E5 y ChromaDB.
    - La identificación de fuentes educativas recuperadas.
    - El control de respuestas sin información suficiente.
    - Determinadas reglas preventivas de orientación.
    - La gestión temporal de memoria conversacional.

    **Alcance documental actual**

    La demostración utiliza ocho fichas educativas originales
    sobre tecnologías de inteligencia artificial y funcionamiento
    del prototipo.

    Estas fichas permiten evaluar el componente tecnológico,
    pero **no sustituyen la base documental especializada**
    sobre autonomía femenina, prevención de violencias
    y orientación institucional.

    **Componentes todavía no habilitados públicamente**

    - Base documental especializada V11.
    - Generación abierta de respuestas mediante Qwen.
    - Consulta en tiempo real de servicios institucionales.

    **Limitaciones del chatbot**

    El asistente no realiza diagnósticos psicológicos,
    asesoría jurídica personalizada, clasificación individual
    del riesgo, denuncias automáticas ni atención de emergencias.

    Las respuestas pueden presentar errores y deben contrastarse
    con fuentes oficiales o profesionales especializados
    cuando corresponda.

    El sistema no contacta automáticamente a instituciones
    ni autoridades.
    """)


# ============================================================
# 6. CONSULTAS DISPONIBLES PARA PROBAR EL PROTOTIPO
# ============================================================

with st.expander(
    "Preguntas sugeridas para evaluar esta demostración",
    expanded=False
):

    st.markdown("""
    Para comprobar la recuperación documental de esta
    versión pública puedes utilizar las siguientes preguntas:

    - ¿Qué es RAG?
    - ¿Qué es un embedding?
    - ¿Para qué sirve ChromaDB?
    - ¿Cómo se evalúa un chatbot?

    **Nota:** estas preguntas son pruebas técnicas del sistema.
    No representan los tres ejes temáticos finales del proyecto.

    Las consultas relacionadas con autonomía femenina,
    prevención de violencias y orientación institucional
    requieren el corpus especializado para ofrecer respuestas
    documentales completas y verificables.
    """)


st.info(
    "Este chatbot es un prototipo académico en evaluación. "
    "No reemplaza servicios profesionales, orientación jurídica "
    "ni atención de emergencias."
)


# ============================================================
# 7. CARGA DE LA BASE DOCUMENTAL ORIGINAL V11
# ============================================================

@st.cache_resource(show_spinner=False)
def load_original():

    if not SETTINGS.authorized_corpus:
        return (
            None,
            "Base documental especializada V11 no habilitada: "
            "pendientes las autorizaciones de publicación."
        )

    try:
        ret = V11Retriever()

        return (
            ret,
            "Corpus documental V11 autorizado cargado "
            "(173 fragmentos)."
        )

    except Exception as exc:

        return (
            None,
            "Corpus V11 no disponible: " + type(exc).__name__
        )


# ============================================================
# 8. CARGA DEL RAG EDUCATIVO DE DEMOSTRACIÓN
# ============================================================

@st.cache_resource(show_spinner=False)
def load_demo():

    if not SETTINGS.demo_rag_enabled:

        return (
            None,
            "Demostración RAG deshabilitada."
        )

    from backend.demo_rag import DemoRetriever

    return (
        DemoRetriever(),
        "Demostración educativa RAG activa "
        "(8 fichas originales)."
    )


# ============================================================
# 9. INICIALIZACIÓN DE LOS COMPONENTES
# ============================================================

original, status = load_original()

st.info(status)

demo = None

if SETTINGS.demo_rag_enabled:

    try:

        with st.spinner(
            "Cargando modelo de embeddings E5 "
            "para la demostración…"
        ):

            demo, demo_status = load_demo()

        st.success(demo_status)

    except Exception as exc:

        st.warning(
            "La demostración RAG no pudo cargarse: "
            + type(exc).__name__
        )

        st.caption(
            "Si es el primer inicio, revisa los registros "
            "de dependencias y descarga del modelo."
        )


# ============================================================
# 10. CONTROL DE SESIÓN Y MEMORIA CONVERSACIONAL
# ============================================================

if "chat_session" not in st.session_state:

    st.session_state.chat_session = Session()


if "messages" not in st.session_state:

    st.session_state.messages = []


if st.button("Nueva conversación"):

    st.session_state.chat_session.reset()

    st.session_state.messages = []

    st.rerun()


# ============================================================
# 11. VISUALIZACIÓN DEL HISTORIAL
# ============================================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])


# ============================================================
# 12. RECEPCIÓN Y PROCESAMIENTO DE CONSULTAS
# ============================================================

question = st.chat_input(
    "Escribe tu consulta"
)


if question:

    with st.chat_message("user"):

        st.markdown(question)

    result = Chatbot(
        original,
        demo
    ).reply(
        question,
        st.session_state.chat_session
    )

    # Tratar ambas rutas preventivas como conversaciones sensibles.
    # El historial visible se limpia y no conserva el relato.
    emergency = result["route"] in (
        "SEGURIDAD_INMEDIATA_189",
        "ORIENTACION_PREVENTIVA_V11",
    )

    # Frente a una urgencia se limpia el historial interno
    # y también el historial visible de la conversación.

    if emergency:

        st.session_state.messages = []

        st.session_state.chat_session.reset()

    else:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

    with st.chat_message("assistant"):

        st.markdown(result["answer"])

        st.caption(
            "Ruta: " + result["route"]
        )

    if not emergency:

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"]
            }
        )
