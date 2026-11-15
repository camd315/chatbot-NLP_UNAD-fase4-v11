"""Extensión preventiva conservadora compatible con V11.

Las reglas V11 originales permanecen intactas. Esta capa añade reconocimiento
contextual de solicitudes de auxilio formuladas sobre terceras personas.
No se realizan llamadas externas ni se almacenan datos personales.
"""
import re
from .seguridad_v11_original import (
    respuesta_preventiva_v11,
    normalizar_alerta_v11,
    RESPUESTA_ALERTA_INMEDIATA_V11,
)

REVIEW_MESSAGE = (
    "No puedo confirmar una respuesta segura y verificada para esta consulta. "
    "Si existe riesgo inmediato en Colombia, comunícate con el 123 si es seguro hacerlo; "
    "para orientación sobre violencias de género, 155. "
    "Esta aplicación no contacta autoridades ni reemplaza servicios humanos."
)

# Un concepto aislado ("violencia", "urgencia") no es suficiente para alertar.
# Es necesario identificar a alguien afectado + evidencia contextual de riesgo.
AFECTADA = re.compile(
    r"\b(?:una mujer|la mujer|esta mujer|mi amiga|una amiga|mi hermana|mi madre|"
    r"mi hija|mi vecina|una persona|la victima|alguien|ella)\b"
)
RIESGO_TERCEROS = re.compile(
    r"\b(?:situacion(?:es)? de violencia|violencia (?:fisica|sexual|de genero)|"
    r"siendo (?:golpead[ao]|agredid[ao]|amenazad[ao])|la estan (?:golpeando|"
    r"agrediendo|amenazando)|la quieren matar|esta en peligro|corre peligro|"
    r"riesgo inmediato|amenaza de muerte|maltrato)\b"
)
AYUDA_APREMIANTE = re.compile(
    r"\b(?:necesita(?:n)?|requiere(?:n)?|pide(?:n)?|busca(?:n)?) "
    r"(?:ayuda|auxilio|proteccion|apoyo)(?: (?:urgente|inmediata|ahora|ya))?\b|"
    r"\b(?:urgente|urgencia|inmediato|inmediata|ahora mismo)\b|"
    r"\b(?:a donde (?:puede|debe) acudir|como (?:la|le) (?:ayudo|ayudamos)|"
    r"como (?:puedo|podemos) ayudarla|a quien (?:puede|debe) llamar)\b"
)
# Evita marcar como una urgencia actual las preguntas puramente definicionales.
CONSULTA_ABSTRACTA = re.compile(
    r"^(?:que (?:es|significa)|define|explica|cual es la definicion|"
    r"como funciona|escribe (?:un|una)|redacta (?:un|una)|"
    r"dame (?:un|una) ejemplo)\b"
)


def evaluate(text):
    """Reglas originales primero; alerta contextual adicional antes de RAG.

    La extensión es un tamiz de seguridad, no la clasificación semántica completa
    de V11 que dependía de las 32 referencias de V10.
    """
    original = respuesta_preventiva_v11(text)
    if original["ruta"] == "SEGURIDAD_INMEDIATA_189":
        return original
    normalizado = normalizar_alerta_v11(text)
    if (
        normalizado
        and not CONSULTA_ABSTRACTA.search(normalizado)
        and AFECTADA.search(normalizado)
        and RIESGO_TERCEROS.search(normalizado)
        and AYUDA_APREMIANTE.search(normalizado)
    ):
        return {
            "ruta": "SEGURIDAD_INMEDIATA_189",
            "clasificacion": "posible_urgencia",
            "respuesta": RESPUESTA_ALERTA_INMEDIATA_V11,
            "qwen_ejecutado": False,
            "rag_ejecutado": False,
            "embeddings_ejecutados": False,
            "regla": "riesgo_tercera_persona_contextual_v11_ext",
        }
    return original
