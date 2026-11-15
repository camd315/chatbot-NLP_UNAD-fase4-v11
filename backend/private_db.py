
"""Descarga privada de ChromaDB V11 desde GitHub.

Las credenciales se reciben desde Streamlit Secrets.
No se guardan tokens ni documentos en el repositorio público.
"""

from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile
import tempfile
import shutil


def preparar_base_privada(token, repo, branch, destino):
    destino = Path(destino)

    # Si la base ya está disponible, no descargar otra vez.
    if (destino / "chroma.sqlite3").is_file():
        return destino

    if not token or not repo:
        raise RuntimeError(
            "Falta configurar el token o repositorio privado."
        )

    url = (
        f"https://api.github.com/repos/{repo}/"
        f"zipball/{branch}"
    )

    solicitud = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "UNAD-NLP-V11"
        }
    )

    with urlopen(solicitud, timeout=60) as respuesta:
        contenido = respuesta.read()

    with zipfile.ZipFile(BytesIO(contenido)) as z:
        archivos = {}

        for miembro in z.infolist():
            if miembro.is_dir():
                continue

            partes = Path(miembro.filename).parts

            if "chroma_db" not in partes:
                continue

            indice = partes.index("chroma_db")
            relativa = Path(*partes[indice + 1:])

            # Evitar rutas externas o inesperadas.
            if not relativa.parts:
                continue
            if ".." in relativa.parts:
                continue

            if (
                relativa.name == "chroma.sqlite3"
                or relativa.suffix == ".bin"
            ):
                archivos[relativa] = miembro

        if not any(
            ruta.name == "chroma.sqlite3"
            for ruta in archivos
        ):
            raise RuntimeError(
                "El repositorio privado no contiene chroma.sqlite3."
            )

        with tempfile.TemporaryDirectory() as temporal:
            carpeta = Path(temporal) / "chroma_db"
            carpeta.mkdir()

            for relativa, miembro in archivos.items():
                salida = carpeta / relativa
                salida.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                with z.open(miembro) as origen:
                    with salida.open("wb") as destino_archivo:
                        shutil.copyfileobj(
                            origen,
                            destino_archivo
                        )

            destino.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            if destino.exists():
                shutil.rmtree(destino)

            shutil.copytree(carpeta, destino)

    return destino
