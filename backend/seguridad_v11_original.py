import re
import unicodedata

PATRONES_ALERTA_DIRECTA_V11 = ['\\bauxilio\\b',
 '\\bsocorro\\b',
 '\\bsos\\b',
 '\\bestoy en peligro\\b',
 '\\bmi vida (?:esta|corre) (?:en )?peligro\\b',
 '\\bme estan golpeando\\b',
 '\\bme esta golpeando\\b',
 '\\bme estan agrediendo\\b',
 '\\bme esta agrediendo\\b',
 '\\bme quieren matar\\b',
 '\\bme amenaza(?:n)? con matarme\\b',
 '\\bme esta(?:n)? amenazando\\b',
 '\\btengo miedo de que me maten\\b',
 '\\bnecesito ayuda urgente\\b',
 '\\bnecesito ayuda ahora\\b',
 '\\bnecesito ayuda ya\\b',
 '\\bayudenme\\b',
 '\\bllam(?:a|en|e) (?:a )?la policia\\b',
 '\\bnecesito (?:a )?la policia\\b',
 '\\bllam(?:a|en|e) (?:al )?123\\b',
 '^es una emergencia$',
 '\\bestoy en una emergencia\\b',
 '\\btengo una emergencia\\b',
 '\\bestoy siendo atacad[ao]\\b',
 '\\bme estan persiguiendo\\b']

PATRONES_SOLICITUD_V11 = ['\\b(?:necesito|requiero|pido) ayuda\\b',
 '\\b(?:por favor )?ayudame\\b',
 '\\b(?:necesito|requiero) (?:una )?ambulancia\\b',
 '\\b(?:necesito|requiero) (?:a )?la policia\\b',
 '\\b(?:llamen|llama|llame) (?:a )?(?:una ambulancia|emergencias)\\b']

PATRONES_INFORMATIVOS_189 = ['que (?:es|significa) (?:una? )?(?:emergencia|auxilio|ayuda)',
 'cual es la funcion de la policia',
 'que hace la policia',
 'como funciona la linea (?:123|155)',
 'cual es el numero de (?:la )?policia',
 'que hacer ante una emergencia',
 'como solicitar ayuda institucional']

PALABRAS_ALERTA_AISLADAS_V11 = ['123', '155', 'auxilio', 'ayuda', 'emergencia', 'policia', 'socorro', 'sos']

PATRONES_NEGACION_SEGURA_190 = ['no estoy en peligro',
 'ya no estoy en peligro',
 'no necesito ayuda urgente',
 'no me estan golpeando']

PATRONES_INFORMATIVOS_EXTRA_190 = ['que significa pedir auxilio']

PATRONES_RIESGO_INDIRECTO_190 = ['\\b(?:mi esposo|mi pareja|mi marido|mi novio|mi '
 'ex)\\s+(?:dice|dijo|amenaza)\\s+que\\s+me\\s+va\\s+a\\s+matar\\b',
 '\\bme\\s+(?:encerraron|encerraron aqui|tienen '
 'encerrada)\\s+y\\s+no\\s+puedo\\s+salir\\b',
 '\\bme\\s+(?:esta|estan)\\s+siguiendo\\s+y\\s+tengo\\s+miedo\\b',
 '\\bme\\s+(?:tiene|tienen)\\s+encerrad[ao]\\b',
 '\\b(?:me|nos)\\s+(?:secuestraron|retuvieron)\\s+(?:contra mi voluntad|y no puedo '
 'salir)\\b']

PATRONES_RIESGO_190_3 = ['\\b(?:mi pareja|mi esposo|mi marido|mi novio|mi '
 'ex)\\s+(?:dijo|dice)\\s+que\\s+me\\s+mataria\\b',
 '\\bme\\s+encerro\\s+en\\s+(?:la\\s+)?casa\\s+y\\s+no\\s+me\\s+deja\\s+salir\\b',
 '\\balguien\\s+me\\s+persigue\\s+y\\s+tengo\\s+(?:mucho\\s+)?miedo\\b',
 '\\bnecesito\\s+que\\s+venga\\s+la\\s+policia(?:\\s+ahora)?\\b']

PATRONES_REFERENCIA_190_3 = ['nunca dije auxilio',
 'en un libro aparece la palabra auxilio',
 'que quiere decir la palabra socorro']

RESPUESTA_ALERTA_INMEDIATA_V11 = ('Si estás en peligro inmediato en Cali o en otra ciudad de Colombia, busca un lugar '
 'seguro si puedes hacerlo sin aumentar el riesgo.\n'
 '\n'
 '• Emergencias: 123.\n'
 '• Orientación sobre violencias de género: 155.\n'
 '\n'
 'Si no puedes llamar de forma segura, intenta pedir apoyo a una persona de confianza.\n'
 '\n'
 'Este chatbot no contacta automáticamente a las autoridades ni sustituye la atención de '
 'los servicios de emergencia.')



def normalizar_alerta_v11(texto):
    if not isinstance(texto, str):
        return ""

    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    return re.sub(r"\s+", " ", texto)


def evaluar_alerta_inmediata_v11(pregunta):

    texto = normalizar_alerta_v11(pregunta)

    if not texto:
        return {
            "alerta": False,
            "tipo": "entrada_vacia",
            "regla": None
        }

    limpio = re.sub(
        r"^[^\w]+|[^\w]+$", "", texto
    ).strip()

    # A. Patrones adicionales de riesgo.
    for patron in PATRONES_RIESGO_190_3:
        if re.search(patron, limpio):
            return {
                "alerta": True,
                "tipo": "alerta_inmediata",
                "regla": patron
            }

    # B. Referencias informativas exactas.
    for patron in PATRONES_REFERENCIA_190_3:
        if re.fullmatch(patron, limpio):
            return {
                "alerta": False,
                "tipo": "referencia_no_urgente",
                "regla": None
            }

    # C. Negaciones exactas.
    for patron in PATRONES_NEGACION_SEGURA_190:
        if re.fullmatch(patron, limpio):
            return {
                "alerta": False,
                "tipo": "negacion_explicita",
                "regla": None
            }

    # D. Preguntas conceptuales adicionales.
    for patron in PATRONES_INFORMATIVOS_EXTRA_190:
        if re.fullmatch(patron, limpio):
            return {
                "alerta": False,
                "tipo": "consulta_informativa",
                "regla": None
            }

    # E. Amenazas indirectas.
    for patron in PATRONES_RIESGO_INDIRECTO_190:
        if re.search(patron, limpio):
            return {
                "alerta": True,
                "tipo": "alerta_inmediata",
                "regla": patron
            }

    # F. Palabras aisladas.
    if limpio in PALABRAS_ALERTA_AISLADAS_V11:
        return {
            "alerta": True,
            "tipo": "alerta_inmediata",
            "regla": "palabra_aislada"
        }

    # G. Alertas explícitas y solicitudes directas.
    patrones = (
        PATRONES_ALERTA_DIRECTA_V11
        + PATRONES_SOLICITUD_V11
    )

    for patron in patrones:

        if patron in (
            r"\bauxilio\b",
            r"\bsocorro\b",
            r"\bsos\b"
        ):
            continue

        if re.search(patron, limpio):
            return {
                "alerta": True,
                "tipo": "alerta_inmediata",
                "regla": patron
            }

    # H. Consultas informativas completas.
    for patron in PATRONES_INFORMATIVOS_189:
        if re.fullmatch(patron, limpio):
            return {
                "alerta": False,
                "tipo": "consulta_informativa",
                "regla": None
            }

    # I. Auxilio explícito restante.
    for palabra in ("auxilio", "socorro", "sos"):
        if re.search(r"\b" + palabra + r"\b", limpio):
            return {
                "alerta": True,
                "tipo": "alerta_inmediata",
                "regla": "auxilio_explicito"
            }

    return {
        "alerta": False,
        "tipo": "evaluacion_posterior",
        "regla": None
    }


def respuesta_preventiva_v11(pregunta):

    resultado = evaluar_alerta_inmediata_v11(
        pregunta
    )

    if resultado["alerta"]:
        return {
            "ruta": "SEGURIDAD_INMEDIATA_189",
            "clasificacion": "posible_urgencia",
            "respuesta": RESPUESTA_ALERTA_INMEDIATA_V11,
            "qwen_ejecutado": False,
            "rag_ejecutado": False,
            "embeddings_ejecutados": False,
            "regla": resultado["regla"]
        }

    return {
        "ruta": "CONTINUAR_CLASIFICACION",
        "clasificacion": resultado["tipo"],
        "respuesta": None,
        "qwen_ejecutado": False,
        "rag_ejecutado": False,
        "embeddings_ejecutados": False,
        "regla": None
    }
