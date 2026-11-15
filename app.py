
"""Interfaz Streamlit – UNAD NLP Fase 4.

Prototipo académico de autonomía femenina,
prevención de violencias y orientación institucional
en Santiago de Cali.

Despliegue con recuperación documental controlada.
"""

import streamlit as st

from config import SETTINGS
from backend.chatbot import Chatbot, Session
from backend.rag import V11Retriever


# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Autonomía femenina y prevención de violencias",
    page_icon="💜",
    layout="centered"
)


# ============================================================
# 2. PRESENTACIÓN PRINCIPAL
# ============================================================

st.title(
    "Asistente de autonomía femenina "
    "y prevención de violencias"
)

st.caption(
    "Prototipo educativo y preventivo | "
    "UNAD · Santiago de Cali"
)

st.markdown("""
### Bienvenida

Este espacio ha sido diseñado como un prototipo académico
de inteligencia artificial para facilitar el acceso
a información educativa y preventiva.

Su propósito es contribuir al fortalecimiento de la
**autonomía femenina**, la **prevención de violencias
de género** y el conocimiento de los **derechos y
servicios institucionales de orientación en Santiago de Cali**.

Está dirigido principalmente a mujeres mayores de 18 años
y a personas interesadas en estos temas desde una
perspectiva educativa y comunitaria.
""")


# ============================================================
# 3. ALCANCE DEL PROYECTO: TRES EJES TEMÁTICOS
# ============================================================

st.markdown("### Nuestros ejes de orientación")

with st.container(border=True):

    st.markdown("#### 🌷 Autonomía femenina")

    st.write(
        "Promover conocimientos relacionados con "
        "el autoconocimiento, la autoestima, "
        "los límites personales, la toma de decisiones "
        "y las relaciones saludables."
    )

with st.container(border=True):

    st.markdown("#### 🛡️ Prevención de violencias")

    st.write(
        "Facilitar información educativa para comprender "
        "los conceptos, manifestaciones y señales generales "
        "de violencia de género, incluyendo conductas "
        "de control, manipulación y aislamiento."
    )

with st.container(border=True):

    st.markdown("#### 🏛️ Orientación institucional")

    st.write(
        "Facilitar el conocimiento de derechos, "
        "entidades, servicios y rutas oficiales "
        "de orientación disponibles en Santiago de Cali, "
        "mediante información pública verificable."
    )


# ============================================================
# 4. INSTRUCCIONES DE USO
# ============================================================

with st.expander(
    "¿Cómo utilizar el asistente?",
    expanded=False
):

    st.markdown("""
    Puedes escribir tu consulta en el cuadro
    de conversación ubicado en la parte inferior.

    El asistente procesará tu mensaje y ofrecerá
    información según las funcionalidades
    y fuentes que estén disponibles.

    Cuando una respuesta esté respaldada por una
    fuente documental, se mostrará su referencia.

    Si no existe información validada, el sistema
    te indicará que no dispone de una respuesta.

    **Privacidad y protección de datos**

    Evita compartir nombres completos,
    documentos de identidad, direcciones,
    teléfonos o relatos personales íntimos.

    Puedes seleccionar **Nueva conversación**
    para reiniciar la interacción.
    """)


# ============================================================
# 5. ALCANCE Y LIMITACIONES DE LA VERSIÓN ACTUAL
# ============================================================

with st.expander(
    "Alcance y limitaciones de esta versión",
    expanded=False
):

    st.markdown("""
    **Objetivo del proyecto**

    Desarrollar un chatbot educativo y preventivo
    sobre autonomía femenina, prevención de
    violencias y orientación institucional.

    **Estado actual**

    Esta versión pública se encuentra en etapa
    de demostración y validación tecnológica.

    Actualmente permite:

    - Utilizar una interfaz conversacional.
    - Probar la recuperación documental mediante
      un conjunto limitado de fichas educativas
      técnicas de demostración.
    - Aplicar determinadas reglas de orientación
      preventiva ante consultas sensibles.
    - Reconocer cuando no existe información
      documental suficiente.
    - Gestionar temporalmente el contexto
      de algunas interacciones.

    **Funcionalidades aún no habilitadas**

    - Recuperación completa del corpus especializado
      sobre los tres ejes del proyecto.
    - Generación abierta mediante Qwen.
    - Consulta de servicios institucionales
      actualizados en tiempo real.

    Las fichas de demostración actuales son de
    carácter técnico y no sustituyen el contenido
    educativo especializado del proyecto.

    **Límites de atención**

    El sistema no realiza diagnósticos psicológicos,
    asesoría jurídica personalizada, clasificación
    individual del riesgo, denuncias automáticas
    ni atención de emergencias.

    Tampoco contacta automáticamente a profesionales
    o autoridades.

    Sus respuestas deben contrastarse con fuentes
    oficiales cuando corresponda.
    """)


st.caption(
    "Este asistente es un prototipo académico en evaluación. "
    "No sustituye la atención profesional, la orientación "
    "jurídica personalizada ni los servicios de emergencia."
)


# ============================================================
# 6. CARGA DEL CORPUS ESPECIALIZADO V11
# ============================================================


@st.cache_resource(show_spinner=False)
def load_original():

    # No exponer automáticamente los documentos
    # en la aplicación pública.
    if not st.secrets.get("V11_ENABLED", False):
        return (
            None,
            "Base documental V11 preparada, "
            "pendiente de habilitación."
        )

    try:
        from backend.private_db import preparar_base_privada

        preparar_base_privada(
            token=st.secrets["GITHUB_PRIVATE_TOKEN"],
            repo=st.secrets["GITHUB_PRIVATE_REPO"],
            branch=st.secrets["GITHUB_PRIVATE_BRANCH"],
            destino=SETTINGS.chroma_path
        )

        recuperador = V11Retriever()

        return (
            recuperador,
            "Base documental V11 cargada correctamente "
            "(173 fragmentos)."
        )

    except Exception as exc:
        return (
            None,
            "No se pudo cargar la base documental V11: "
            + type(exc).__name__
        )




# ============================================================
# 7. CARGA DE LA DEMOSTRACIÓN RAG
# ============================================================

@st.cache_resource(show_spinner=False)
def load_demo():

    if not SETTINGS.demo_rag_enabled:

        return (
            None,
            "Demostración documental deshabilitada."
        )

    from backend.demo_rag import DemoRetriever

    return (
        DemoRetriever(),
        "Componente de recuperación documental "
        "de demostración disponible."
    )


# ============================================================
# 8. INICIALIZACIÓN DE COMPONENTES
# ============================================================

original, status = load_original()

demo = None

if SETTINGS.demo_rag_enabled:

    try:

        with st.spinner(
            "Preparando el asistente..."
        ):

            demo, demo_status = load_demo()

    except Exception as exc:

        st.warning(
            "No se pudo inicializar la recuperación "
            "documental de demostración: "
            + type(exc).__name__
        )


# ============================================================
# 9. ESTADO BREVE DE DISPONIBILIDAD
# ============================================================

with st.expander(
    "Información técnica del prototipo",
    expanded=False
):

    st.write(status)

    if demo is not None:
        st.write(
            "Recuperación documental de demostración: "
            "habilitada con ocho fichas educativas "
            "de contenido técnico."
        )
    else:
        st.write(
            "Recuperación documental de demostración: "
            "no disponible."
        )

    st.write(
        "La generación abierta mediante Qwen "
        "permanece deshabilitada."
    )


# ============================================================
# 10. MEMORIA CONVERSACIONAL
# ============================================================

if "chat_session" not in st.session_state:

    st.session_state.chat_session = Session()


if "messages" not in st.session_state:

    st.session_state.messages = []


if st.button(
    "Nueva conversación",
    use_container_width=False
):

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
# 12. INTERACCIÓN CON EL ASISTENTE
# ============================================================

question = st.chat_input(
    "Escribe aquí tu consulta..."
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

    # Las consultas sensibles no se conservan
    # en el historial visual de la conversación.
    sensitive = result["route"] in (
        "SEGURIDAD_INMEDIATA_189",
        "ORIENTACION_PREVENTIVA_V11"
    )

    if sensitive:

        st.session_state.messages = []

        # La limpieza de memoria y el indicador
        # temporal de seguimiento son gestionados
        # por backend/chatbot.py.

    else:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

    with st.chat_message("assistant"):

        st.markdown(result["answer"])

        # Ruta técnica visible en modo de demostración.
        st.caption(
            "Clasificación: " + result["route"]
        )

    if not sensitive:

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"]
        })
