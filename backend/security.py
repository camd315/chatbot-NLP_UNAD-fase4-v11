"""Capa preventiva V11: emergencias directas y orientación sobre terceras personas.

Conserva las reglas del módulo seguridad_v11_original y agrega detección
contextual sin utilizar LLM ni recuperar documentos.
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

RESPUESTA_TERCERA_PERSONA = (
    "Si una persona cercana está viviendo violencia, escucha sin juzgar, "
    "evita confrontar al agresor y pregúntale cómo puedes apoyarla sin aumentar su riesgo. "
    "En Colombia puede solicitar orientación sobre violencias de género en la línea 155. "
    "Si hay peligro inmediato, llama al 123 cuando sea seguro hacerlo. "
    "Este chatbot no contacta automáticamente a las autoridades."
)

RESPUESTA_TERCERA_PERSONA_URGENTE = (
    "Si tu familiar o conocida está en peligro inmediato, prioriza su seguridad "
    "y la tuya. No confrontes al agresor ni te expongas. "
    "En Colombia, puedes llamar al 123 si es seguro hacerlo; "
    "para orientación sobre violencias de género, 155. "
    "Este chatbot no contacta automáticamente a las autoridades."
)

# Las expresiones se evalúan sobre texto minúsculo y sin tildes.
CONSULTA_ABSTRACTA = re.compile(
    r"^(?:que (?:es|significa)|define|explica|cual es la definicion|"
    r"como funciona|escribe (?:un|una)|redacta (?:un|una)|"
    r"dame (?:un|una) ejemplo)\b"
)
RIESGO_DIRECTO = re.compile(
    r"\b(?:estoy siendo (?:golpead[ao]|agredid[ao]|atacad[ao]|amenazad[ao])|"
    r"(?:me|nos) (?:estan|esta) (?:golpeando|agrediendo|atacando|amenazando)|"
    r"(?:mi pareja|mi esposo|mi novio|mi ex) me (?:golpea|agrede|amenaza))\b"
)
NEGACION_DIRECTA = re.compile(
    r"\b(?:no estoy siendo|no me estan|no me esta)\s+"
    r"(?:golpead[ao]|agredid[ao]|atacad[ao]|amenazad[ao]|"
    r"golpeando|agrediendo|atacando|amenazando)\b"
)
TERCERA_PERSONA = re.compile(
    r"\b(?:mi hermana|mi hermano|mi madre|mi mama|mi hija|mi hijo|"
    r"mi amiga|mi amigo|mi vecina|mi vecino|mi familiar|"
    r"una mujer|la mujer|esta mujer|una persona|ella)\b"
)
RIESGO_TERCERO = re.compile(
    r"\b(?:esta siendo|estan siendo|es) (?:golpead[ao]|agredid[ao]|"
    r"amenazad[ao]|maltratad[ao])\b|"
    r"\b(?:la|lo) estan (?:golpeando|agrediendo|amenazando)\b|"
    r"\b(?:sufre|vive|esta viviendo) (?:violencia|maltrato)\b|"
    r"\b(?:violencia psicologica|violencia fisica|violencia sexual|"
    r"maltrato|amenaza de muerte|la quieren matar)\b"
)
URGENCIA_ACTUAL = re.compile(
    r"\b(?:ahora mismo|en este momento|esta en peligro inmediato|"
    r"corre peligro inmediato|la quieren matar ahora|"
    r"su vida esta en peligro|necesita ayuda urgente)\b"
)

def _resultado(ruta, clasificacion, respuesta, regla):
    return {
        "ruta": ruta,
        "clasificacion": clasificacion,
        "respuesta": respuesta,
        "qwen_ejecutado": False,
        "rag_ejecutado": False,
        "embeddings_ejecutados": False,
        "regla": regla,
    }


def evaluate(text):
    """Clasifica primero el riesgo; no ejecuta recuperación ni modelos."""
    normalizado = normalizar_alerta_v11(text)
    
    # Detección de expresiones breves de violencia.
    # Evitar alertas por preguntas conceptuales o negaciones.
    if normalizado and not CONSULTA_ABSTRACTA.search(normalizado):

        negacion = re.search(
            r"\b(?:no|ya no|nunca)\s+"
            r"(?:me pegan|me pega|le pegan|le pega)\b",
            normalizado
        )

        if not negacion:

            # Violencia hacia una tercera persona.
            tercero = re.search(
                r"\b(?:le pegan|le pega|golpean|agreden|"
                r"maltratan)\s+a\s+(?:mi|una|la)\s+"
                r"(?:hermana|madre|mama|hija|amiga|"
                r"prima|tia|vecina|pareja)\b",
                normalizado
            )

            if tercero:
                if re.search(
                    r"\b(?:ahora mismo|en este momento|"
                    r"peligro inmediato)\b",
                    normalizado
                ):
                    return {
                        "ruta": "SEGURIDAD_INMEDIATA_189",
                        "respuesta": RESPUESTA_ALERTA_INMEDIATA_V11,
                        "clasificacion": "posible_urgencia",
                        "qwen_ejecutado": False,
                        "rag_ejecutado": False,
                    }

                return {
                    "ruta": "ORIENTACION_PREVENTIVA_V11",
                    "respuesta": None,
                    "clasificacion": "orientacion_terceros",
                    "qwen_ejecutado": False,
                    "rag_ejecutado": False,
                }

            # Violencia expresada en primera persona.
            if re.search(
                r"\b(?:me pegan|me pega|me golpean|"
                r"me golpea|me agreden|me agrede|"
                r"me maltratan|me maltrata)\b",
                normalizado
            ):
                return {
                    "ruta": "SEGURIDAD_INMEDIATA_189",
                    "respuesta": RESPUESTA_ALERTA_INMEDIATA_V11,
                    "clasificacion": "posible_urgencia",
                    "qwen_ejecutado": False,
                    "rag_ejecutado": False,
                }

    if not normalizado:
        return respuesta_preventiva_v11(text)

    # Evita alertas por preguntas puramente definicionales.
    abstracta = bool(CONSULTA_ABSTRACTA.search(normalizado))

    # Una agresión expresada en primera persona prevalece aunque se mencione
    # a un familiar en el resto del mensaje.
    if (not abstracta and RIESGO_DIRECTO.search(normalizado)
            and not NEGACION_DIRECTA.search(normalizado)):
        return _resultado(
            "SEGURIDAD_INMEDIATA_189", "posible_urgencia",
            RESPUESTA_ALERTA_INMEDIATA_V11, "riesgo_directo_v11_ext"
        )

    # Preguntas concretas sobre otra persona: respuesta de apoyo adecuada;
    # no suponer que quien consulta es la víctima.
    if (not abstracta and TERCERA_PERSONA.search(normalizado)
            and RIESGO_TERCERO.search(normalizado)):
        if URGENCIA_ACTUAL.search(normalizado):
            return _resultado(
                "SEGURIDAD_INMEDIATA_189", "posible_urgencia_tercero",
                RESPUESTA_TERCERA_PERSONA_URGENTE,
                "riesgo_inmediato_tercera_persona_v11_ext"
            )
        return _resultado(
            "ORIENTACION_PREVENTIVA_V11", "orientacion_tercera_persona",
            RESPUESTA_TERCERA_PERSONA,
            "orientacion_tercera_persona_v11_ext"
        )

    # Mantener el resto de los criterios conservadores originales.
    return respuesta_preventiva_v11(text)
