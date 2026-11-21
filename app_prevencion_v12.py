"""Chatbot Prevención V12: interfaz Streamlit de evaluación privada.

No despliega contenido de forma pública. Requiere habilitación explícita para
pruebas locales. Reutiliza backend_v12 del Paso 28 y la colección existente.
"""
from __future__ import annotations

import os
import io
import shutil
import stat
import tempfile
import urllib.error
import urllib.request
import zipfile
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
    st.error("No se encontró backend_v12 en la carpeta de la aplicación.")
    st.stop()


def _chroma_privado() -> Path:
    """Obtiene una copia local de ChromaDB desde el repositorio privado.

    No modifica el repositorio remoto ni vuelve a generar embeddings.
    El ZIP descargado permanece en memoria; solo se extrae chroma_db_v12/.
    """
    repo = _config("CHATBOT_PREVENCION_PRIVATE_REPO").strip()
    token = _config("CHATBOT_PREVENCION_PRIVATE_TOKEN").strip()
    if not token or not repo:
        raise RuntimeError("Falta configurar el token o el repositorio privado")
    parts = repo.split("/")
    if len(parts) != 2 or not all(parts) or not all(
        all(c.isalnum() or c in "-_ ." for c in part) and " " not in part
        for part in parts
    ):
        raise RuntimeError("El identificador de repositorio no es válido")

    # Descarga privada del estado de la rama main de la base documental.
    url = f"https://api.github.com/repos/{repo}/zipball/main"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "chatbot-prevencion-v12-private",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        archive_bytes = response.read(100 * 1024 * 1024 + 1)
    if len(archive_bytes) > 100 * 1024 * 1024:
        raise RuntimeError("La base supera el máximo de descarga configurado")

    directory = Path(tempfile.mkdtemp(prefix="prevencion_v12_"))
    target = directory / "chroma_db_v12"
    target.mkdir()
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            entries = []
            for item in archive.infolist():
                # GitHub zipball agrega un directorio raíz con un sufijo de commit.
                components = Path(item.filename).parts
                if len(components) < 3 or components[1] != "chroma_db_v12":
                    continue
                parts_local = components[2:]
                if not parts_local or any(c in (".", "..", "") for c in parts_local):
                    raise RuntimeError("Ruta no válida en el paquete documental")
                if stat.S_ISLNK((item.external_attr >> 16) & 0xFFFF):
                    raise RuntimeError("El paquete contiene un enlace simbólico")
                if item.file_size > 100 * 1024 * 1024:
                    raise RuntimeError("Archivo de índice demasiado grande")
                entries.append((item, parts_local))
            if sum(item.file_size for item, _ in entries) > 200 * 1024 * 1024:
                raise RuntimeError("La base vectorial supera el límite de extracción")
            for item, relative in entries:
                destination = target.joinpath(*relative)
                if item.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(item) as source, destination.open("wb") as out:
                    shutil.copyfileobj(source, out)
        if not (target / "chroma.sqlite3").is_file():
            raise RuntimeError("No se encontró chroma.sqlite3 en la copia privada")
        if not any((target / folder).is_dir() for folder in os.listdir(target)
                   if folder != "chroma.sqlite3"):
            raise RuntimeError("No se encontró el directorio de índices vectoriales")
        return target
    except Exception:
        shutil.rmtree(directory, ignore_errors=True)
        raise


@st.cache_resource(show_spinner="Cargando el recuperador privado V12...")
def _load_chatbot():
    from backend_v12.rag_v12 import RecuperadorV12
    from backend_v12.chatbot_v12 import ChatbotDocumentalV12

    local_chroma = _chroma_privado()
    retriever = RecuperadorV12(local_chroma)
    return ChatbotDocumentalV12(retriever)


try:
    chatbot = _load_chatbot()
except Exception:
    # No mostrar excepciones de red, URLs privadas ni credenciales al usuario.
    st.error(
        "No fue posible abrir la base documental V12. "
        "Revisa el acceso al repositorio privado y las dependencias instaladas."
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
