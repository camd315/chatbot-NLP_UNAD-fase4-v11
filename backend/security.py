
"""Capa preventiva V11 ampliada para el ejercicio 3.

Conserva las reglas originales, detecta declaraciones
directas e indirectas de violencia y distingue consultas
educativas de posibles solicitudes de apoyo.

No realiza diagnósticos ni evaluaciones individuales del riesgo.
"""

import re

from .seguridad_v11_original import (
    respuesta_preventiva_v11,
    normalizar_alerta_v11,
    RESPUESTA_ALERTA_INMEDIATA_V11,
)


REVIEW_MESSAGE = (
    "No puedo confirmar una respuesta segura y verificada "
    "para esta consulta. Si existe riesgo inmediato en Colombia, "
    "comunícate con el 123 si es seguro hacerlo; para orientación "
    "sobre violencias de género, 155. Esta aplicación no contacta "
    "autoridades ni reemplaza servicios humanos."
)


RESPUESTA_ORIENTACION_PREVENTIVA = (
    "Si esta situación está ocurriendo realmente, es importante "
    "priorizar la seguridad de la persona afectada. "
    "No necesitas compartir nombres ni detalles personales.\n\n"
    "¿La persona está en peligro ahora o necesita ayuda inmediata?\n\n"
    "Si existe peligro inmediato en Colombia, pueden llamar al "
    "**123**, siempre que sea seguro hacerlo.\n\n"
    "Para orientación sobre violencias de género está la "
    "**línea 155**.\n\n"
    "Si no es seguro llamar, pueden buscar apoyo de una persona "
    "de confianza, siempre que hacerlo no aumente el riesgo.\n\n"
    "Este asistente ofrece orientación preventiva general. "
    "No realiza diagnósticos ni contacta automáticamente "
    "a las autoridades."
)


RESPUESTA_SEGUIMIENTO = (
    "Si buscas ayuda por una situación de violencia, "
    "en Colombia puedes acudir a estos canales:\n\n"
    "- **123:** emergencias, si existe peligro inmediato.\n"
    "- **155:** orientación sobre violencias de género.\n\n"
    "Puedes buscar apoyo de una persona de confianza "
    "si hacerlo es seguro.\n\n"
    "No es necesario compartir información personal con este "
    "chatbot. La aplicación no realiza llamadas ni denuncias "
    "automáticas y no sustituye los servicios especializados."
)


# Referencias a terceras personas.
AFECTADA = re.compile(
    r"\b(?:una mujer|la mujer|esta mujer|mi amiga|una amiga|"
    r"mi hermana|mi madre|mi hija|mi vecina|una persona|"
    r"la victima|alguien|ella)\b"
)


# Riesgos contextuales ya contemplados en la extensión previa.
RIESGO_TERCEROS = re.compile(
    r"\b(?:situacion(?:es)? de violencia|"
    r"violencia (?:fisica|sexual|de genero)|"
    r"siendo (?:golpead[ao]|agredid[ao]|amenazad[ao])|"
    r"la estan (?:golpeando|agrediendo|amenazando)|"
    r"la quieren matar|esta en peligro|corre peligro|"
    r"riesgo inmediato|amenaza de muerte|maltrato)\b"
)


AYUDA_APREMIANTE = re.compile(
    r"\b(?:necesita(?:n)?|requiere(?:n)?|pide(?:n)?|"
    r"busca(?:n)?) "
    r"(?:ayuda|auxilio|proteccion|apoyo)"
    r"(?: (?:urgente|inmediata|ahora|ya))?\b|"
    r"\b(?:urgente|urgencia|inmediato|inmediata|"
    r"ahora mismo)\b|"
    r"\b(?:a donde (?:puede|debe) acudir|"
    r"como (?:la|le) (?:ayudo|ayudamos)|"
    r"como (?:puedo|podemos) ayudarla|"
    r"a quien (?:puede|debe) llamar)\b"
)


# Detección directa de violencia física en curso.
# Por prevención, estas expresiones se consideran
# posibles situaciones urgentes, no emergencias confirmadas.
VIOLENCIA_DIRECTA = re.compile(
    r"\b(?:estoy siendo (?:golpead[ao]|agredid[ao])|"
    r"me (?:estan|esta) (?:golpeando|agrediendo)|"
    r"me (?:golpean|agreden))\b"
)


# Declaraciones breves sobre terceras personas.
# "herma" se admite como variante incompleta de "hermana".
VIOLENCIA_TERCERA_PERSONA = re.compile(
    r"\b(?:mi (?:hermana|herma|amiga|madre|hija|vecina)|"
    r"una mujer|la mujer|ella)\s+"
    r"(?:es|esta siendo|esta)\s+"
    r"(?:golpead[ao]|agredid[ao])\b|"
    r"\b(?:mi (?:hermana|herma|amiga|madre|hija|vecina)|"
    r"una mujer|ella)\s+"
    r"(?:la estan golpeando|recibe golpes)\b"
)


# Preguntas breves que pueden continuar una conversación
# donde ya se comunicó una situación de violencia.
PREGUNTA_SEGUIMIENTO = re.compile(
    r"\b(?:donde puedo llamar|a donde puedo llamar|"
    r"a quien puedo llamar|donde llamo|"
    r"que numero debo marcar|"
    r"a donde puedo acudir|donde busco ayuda|"
    r"como consigo ayuda|donde pido ayuda|"
    r"me puedes dar un telefono)\b"
)


# Consultas definicionales, hipotéticas o de ejemplos.
CONSULTA_ABSTRACTA = re.compile(
    r"^(?:que (?:es|significa)|define|explica|"
    r"cual es la definicion|como funciona|"
    r"escribe (?:un|una)|redacta (?:un|una)|"
    r"dame (?:un|una) ejemplo|"
    r"pon (?:un|una) ejemplo|"
    r"imagina|supongamos|"
    r"en un ejemplo|si mi hermana)\b"
)


# Negaciones frecuentes para reducir falsas alertas.
NEGACION_VIOLENCIA = re.compile(
    r"\b(?:no|ya no|nunca)\s+"
    r"(?:es|esta|esta siendo|estoy siendo|"
    r"me estan|me esta)\s+"
    r"(?:golpead[ao]|agredid[ao]|"
    r"golpeando|agrediendo)\b|"
    r"\bno me (?:golpean|agreden)\b"
)


def _respuesta(ruta, clasificacion, mensaje, regla):
    """Construye un resultado preventivo compatible con V11."""
    return {
        "ruta": ruta,
        "clasificacion": clasificacion,
        "respuesta": mensaje,
        "qwen_ejecutado": False,
        "rag_ejecutado": False,
        "embeddings_ejecutados": False,
        "regla": regla,
    }


def es_pregunta_seguimiento(texto):
    """Identifica solicitudes breves de canales de ayuda."""
    normalizado = normalizar_alerta_v11(texto)
    return bool(PREGUNTA_SEGUIMIENTO.search(normalizado))


def evaluate(text):
    """Evalúa primero las reglas originales y luego las ampliadas.

    Las expresiones de violencia reciben orientación preventiva
    sin depender de la base documental ni de Qwen.
    """

    # 1. Se conserva la prioridad de las alertas V11 originales.
    original = respuesta_preventiva_v11(text)

    if original["ruta"] == "SEGURIDAD_INMEDIATA_189":
        return original

    normalizado = normalizar_alerta_v11(text)

    if not normalizado:
        return original

    # 2. Evitar falsas alertas en consultas conceptuales.
    if CONSULTA_ABSTRACTA.search(normalizado):
        return original

    # 3. Evitar alertas por negaciones expresas.
    if NEGACION_VIOLENCIA.search(normalizado):
        return original

    # 4. Declaración directa de agresión en curso.
    if VIOLENCIA_DIRECTA.search(normalizado):
        return _respuesta(
            "SEGURIDAD_INMEDIATA_189",
            "posible_urgencia",
            RESPUESTA_ALERTA_INMEDIATA_V11,
            "violencia_directa_v11_ext",
        )

    # 5. Urgencia contextual en tercera persona.
    if (
        AFECTADA.search(normalizado)
        and RIESGO_TERCEROS.search(normalizado)
        and AYUDA_APREMIANTE.search(normalizado)
    ):
        return _respuesta(
            "SEGURIDAD_INMEDIATA_189",
            "posible_urgencia",
            RESPUESTA_ALERTA_INMEDIATA_V11,
            "riesgo_tercera_persona_contextual_v11_ext",
        )

    # 6. Declaración de violencia contra una tercera persona
    # sin petición expresa de ayuda inmediata.
    if VIOLENCIA_TERCERA_PERSONA.search(normalizado):
        return _respuesta(
            "ORIENTACION_PREVENTIVA_V11",
            "violencia_reportada",
            RESPUESTA_ORIENTACION_PREVENTIVA,
            "violencia_reportada_contextual_v11_ext",
        )

    # 7. Sin indicios suficientes, continuar con el flujo normal.
    return original
