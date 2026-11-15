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

# ===============================


# ============================================================
# DIAGNOSTICO PRIVADO DE CHROMADB V11
# No habilita respuestas documentales al publico.
# ============================================================

if st.secrets.get("V11_DIAGNOSTIC_ENABLED", False):

    @st.cache_resource(show_spinner=False)
    def verificar_chromadb_v11():
        try:
            from pathlib import Path
            import chromadb

            from backend.private_db import preparar_base_privada
            from backend.rag import V11Retriever

            print(
                "V11_DIAG: Iniciando prueba privada",
                flush=True
            )

            ruta = preparar_base_privada(
                token=st.secrets["GITHUB_PRIVATE_TOKEN"],
                repo=st.secrets["GITHUB_PRIVATE_REPO"],
                branch=st.secrets["GITHUB_PRIVATE_BRANCH"],
                destino=SETTINGS.chroma_path
            )

            ruta = Path(ruta)

            if not (ruta / "chroma.sqlite3").is_file():
                raise RuntimeError("SQLite no encontrado")

            indices = list(ruta.glob("*/header.bin"))

            if not indices:
                raise RuntimeError("Indice vectorial no encontrado")

            print(
                "V11_DIAG: Descarga y archivos OK",
                flush=True
            )

            cliente = chromadb.PersistentClient(
                path=str(ruta)
            )

            colecciones = cliente.list_collections()

            if len(colecciones) != 1:
                raise RuntimeError(
                    "Se esperaba una sola coleccion"
                )

            coleccion = cliente.get_collection(
                name=colecciones[0].name
            )

            cantidad = coleccion.count()

            print(
                f"V11_DIAG: Fragmentos={cantidad}",
                flush=True
            )

            if cantidad != 173:
                raise RuntimeError(
                    "Cantidad de fragmentos incorrecta"
                )

            recuperador = V11Retriever(db_path=ruta)

            resultados = recuperador.retrieve(
                "¿Qué derechos reconoce la Ley 1257 de 2008?",
                k=4
            )

            if not resultados:
                raise RuntimeError(
                    "La consulta vectorial no devolvio resultados"
                )

            print(
                "V11_DIAG: Recuperacion vectorial OK",
                flush=True
            )

            print(
                "V11_DIAG: VALIDACION EXITOSA",
                flush=True
            )

            # No se devuelven fragmentos ni documentos.
            return True

        except Exception as exc:
            print(
                "V11_DIAG: ERROR "
                + type(exc).__name__,
                flush=True
            )
            return False

    verificar_chromadb_v11()

# ============================================================
# FIN DEL DIAGNOSTICO PRIVADO
# ============================================================

# ===================


# ============================================================
# PRUEBA PRIVADA TEMPORAL DEL FLUJO COMPLETO V11
# No muestra documentos ni respuestas en la interfaz.
# ============================================================

if st.secrets.get("V11_PRIVATE_FLOW_TEST", False):

    @st.cache_resource(show_spinner=False)
    def probar_flujo_completo_v11():
        try:
            from backend.private_db import preparar_base_privada
            from backend.rag import V11Retriever
            from backend.chatbot import Chatbot, Session

            print(
                "V11_FLOW: INICIO PRUEBA PRIVADA",
                flush=True
            )

            # 1. Preparar base privada.
            ruta = preparar_base_privada(
                token=st.secrets["GITHUB_PRIVATE_TOKEN"],
                repo=st.secrets["GITHUB_PRIVATE_REPO"],
                branch=st.secrets["GITHUB_PRIVATE_BRANCH"],
                destino=SETTINGS.chroma_path
            )

            # 2. Inicializar recuperador real.
            recuperador = V11Retriever(db_path=ruta)

            cantidad = recuperador.collection.count()

            print(
                f"V11_FLOW: FRAGMENTOS={cantidad}",
                flush=True
            )

            if cantidad != 173:
                raise RuntimeError(
                    "Cantidad documental inesperada"
                )

            # 3. Instanciar chatbot sin demo técnica.
            asistente = Chatbot(
                retriever=recuperador,
                demo_retriever=None
            )

            preguntas = [
                (
                    "LEY_1257",
                    "¿Qué derechos reconoce la Ley 1257 "
                    "de 2008 a las mujeres?"
                ),
                (
                    "TIPOS_VIOLENCIA",
                    "¿Qué tipos de violencia contra "
                    "las mujeres existen?"
                ),
                (
                    "ORIENTACION_CALI",
                    "¿Dónde puedo recibir orientación "
                    "institucional en Cali?"
                )
            ]

            fallos = 0

            # 4. Ejecutar flujo Chatbot -> RAG.
            for nombre, pregunta in preguntas:

                # Sesión independiente por consulta.
                sesion = Session()

                resultado = asistente.reply(
                    pregunta,
                    sesion
                )

                ruta_respuesta = resultado.get(
                    "route", "SIN_RUTA"
                )

                respuesta = resultado.get(
                    "answer", ""
                )

                qwen = resultado.get(
                    "qwen_executed", False
                )

                # Solo metadatos, nunca texto documental.
                respuesta_disponible = bool(
                    str(respuesta).strip()
                )

                rutas_validas = {
                    "RAG_V11_PRIVADO_EXTRACTIVO",
                    "DOCUMENTAL_CONTROLADA",
                    "DOCUMENTAL_JURIDICA"
                }

                correcto = (
                    ruta_respuesta in rutas_validas
                    and respuesta_disponible
                    and qwen is False
                )

                if not correcto:
                    fallos += 1

                print(
                    "V11_FLOW: "
                    f"{nombre} | "
                    f"RUTA={ruta_respuesta} | "
                    f"RESPUESTA={'SI' if respuesta_disponible else 'NO'} | "
                    f"QWEN={qwen} | "
                    f"ESTADO={'OK' if correcto else 'REVISAR'}",
                    flush=True
                )

            if fallos == 0:
                print(
                    "V11_FLOW: VALIDACION FUNCIONAL EXITOSA",
                    flush=True
                )
            else:
                print(
                    f"V11_FLOW: PRUEBAS_PENDIENTES={fallos}",
                    flush=True
                )

            # No devolver respuestas ni fragmentos.
            return fallos == 0

        except Exception as exc:
            print(
                "V11_FLOW: ERROR="
                + type(exc).__name__,
                flush=True
            )
            return False

    probar_flujo_completo_v11()

# ============================================================
# FIN DE PRUEBA PRIVADA TEMPORAL
# ============================================================



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

with st.expander("¿Cómo utilizar el asistente?", expanded=False):
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

with st.expander("Alcance y limitaciones de esta versión", expanded=False):
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
# 6. CARGA DEL CORPUS ESPECIALIZADO V11 (PRIVADO)
# ============================================================

@st.cache_resource(show_spinner=False)
def load_original():
    # Deshabilitado por defecto para evitar exponer los
    # documentos privados en el chatbot público.
    if not st.secrets.get("V11_ENABLED", False):
        return (
            None,
            "Base documental V11 preparada, "
            "pendiente de habilitación."
        )

    # Se mantiene además la autorización original del proyecto.
    if not SETTINGS.authorized_corpus:
        return (
            None,
            "Corpus especializado pendiente de autorización "
            "para uso público."
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
            "(verificación de fragmentos a cargo del recuperador)."
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
        return (None, "Demostración documental deshabilitada.")

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
        with st.spinner("Preparando el asistente..."):
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

with st.expander("Información técnica del prototipo", expanded=False):
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

if st.button("Nueva conversación", use_container_width=False):
    st.session_state.chat_session.reset()
    st.session_state.messages = []
    st.rerun()

# ========================================================

# ============================================================
# PREGUNTAS SUGERIDAS PARA ORIENTAR A LAS PERSONAS
# ============================================================

st.markdown("### ¿No sabes por dónde empezar?")
st.write(
    "Selecciona una pregunta de tu interés o escribe "
    "tu propia consulta en el espacio de conversación."
)

preguntas_sugeridas = {
    "🌷 Autonomía femenina": [
        "¿Cómo puedo fortalecer mi autoestima?",
        "¿Cómo puedo tomar decisiones con mayor seguridad?",
        "¿Qué es el autoconocimiento y cómo puedo desarrollarlo?"
    ],
    "🛡️ Prevención de violencias": [
        "¿Cuáles son las señales de violencia psicológica?",
        "¿Qué tipos de violencia contra las mujeres existen?",
        "¿Cómo puedo identificar la violencia económica?"
    ],
    "🏛️ Orientación institucional": [
        "¿Dónde puedo recibir orientación institucional en Cali?",
        "¿Qué derechos reconoce la Ley 1257 de 2008 a las mujeres?",
        "¿Qué es Casa Matria y dónde puedo recibir orientación en Cali?"
    ]
}

with st.expander("💬 Explorar preguntas sugeridas", expanded=True):
    pestanas = st.tabs(list(preguntas_sugeridas.keys()))

    for indice, (categoria, preguntas) in enumerate(
        preguntas_sugeridas.items()
    ):
        with pestanas[indice]:
            for numero, pregunta in enumerate(preguntas):
                if st.button(
                    pregunta,
                    key=f"sugerida_{indice}_{numero}",
                    use_container_width=True
                ):
                    st.session_state["pregunta_sugerida"] = pregunta

# ============================================================
# FIN DE PREGUNTAS SUGERIDAS
# ============================================================


# ============================================================
# 11. VISUALIZACIÓN DEL HISTORIAL
# ============================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================================================
# 12. INTERACCIÓN CON EL ASISTENTE
# ============================================================

question = st.chat_input("Escribe aquí tu consulta...")

if question:
    with st.chat_message("user"):
        st.markdown(question)

    result = Chatbot(original, demo).reply(
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
        st.caption("Clasificación: " + result["route"])

    if not sensitive:
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"]
        })
