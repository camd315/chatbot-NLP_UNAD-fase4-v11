"""Respuestas educativas originales para uso público.

No reproduce los documentos de la colección privada V11 ni consulta servicios en vivo.
No sustituye la capa de seguridad de backend/security.py.
"""
import re
import unicodedata


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize('NFKD', texto.casefold())
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', texto).strip()


_RESPUESTAS = {
    'autonomia': (
        '**Fortalecer la autonomía y la autoestima** puede comenzar con acciones pequeñas y sostenibles:\n\n'
        '- Reconoce tus cualidades, intereses y logros sin compararte con otras personas.\n'
        '- Identifica qué decisiones son importantes para ti y qué información necesitas antes de tomarlas.\n'
        '- Practica expresar tus preferencias y establecer límites respetuosos.\n'
        '- Busca redes de confianza que escuchen tus decisiones sin imponerte las suyas.\n\n'
        'Una actividad sencilla es anotar una decisión que quieras tomar, dos opciones posibles y '
        'qué valores personales representa cada una. No tienes que resolverlo todo de inmediato.\n\n'
        '*Orientación educativa general; no equivale a acompañamiento psicológico personalizado.*'
    ),
    'violencia': (
        '**La violencia contra las mujeres puede adoptar distintas formas**, entre ellas:\n\n'
        '- **Física:** golpes, empujones u otras agresiones al cuerpo.\n'
        '- **Psicológica:** amenazas, humillaciones, intimidación, aislamiento o control persistente.\n'
        '- **Sexual:** actos o presiones sexuales sin consentimiento libre.\n'
        '- **Económica o patrimonial:** limitar injustificadamente el acceso a recursos o controlar, '
        'retener o destruir bienes con fines de dominación.\n\n'
        'Las manifestaciones pueden coexistir. Reconocerlas ayuda a buscar orientación, '
        'pero esta explicación no determina por sí sola una situación jurídica individual. '
        'Si existe peligro inmediato en Colombia, la línea de emergencias es **123**; '
        'para orientación sobre violencias de género existe la **155**.\n\n'
        '*Información educativa preventiva; no reemplaza atención profesional.*'
    ),
    'institucional': (
        '**Orientación institucional en Cali:** puedes buscar información y acompañamiento '
        'en los servicios municipales de atención a mujeres, como **Casa Matria**, '
        'y consultar las rutas de atención de la Alcaldía de Santiago de Cali.\n\n'
        'En Colombia, la línea **155** ofrece orientación sobre violencias de género; '
        'ante una emergencia inmediata puedes comunicarte al **123** si es seguro hacerlo.\n\n'
        'No puedo confirmar desde esta versión los horarios, direcciones o números locales '
        'actualizados. Verifica esos datos en los canales oficiales antes de desplazarte.\n\n'
        '*Este chatbot no realiza denuncias ni contacta autoridades.*'
    ),
    'derechos': (
        '**La Ley 1257 de 2008 de Colombia** establece medidas de sensibilización, '
        'prevención y sanción frente a formas de violencia y discriminación contra las mujeres. '
        'Su enfoque comprende la protección de la dignidad, la integridad, la libertad '
        'y el derecho a una vida libre de violencias.\n\n'
        'Según la situación, una mujer puede solicitar orientación institucional y '
        'acceder a mecanismos de protección previstos por el ordenamiento jurídico. '
        'Las medidas concretas dependen de los hechos y de la autoridad competente.\n\n'
        'Para una interpretación jurídica o verificación de vigencia, consulta el texto '
        'oficial de la norma y recibe orientación de la entidad correspondiente.\n\n'
        '*Resumen educativo original; no constituye asesoría jurídica individual.*'
    ),
}


def respuesta_publica(pregunta: str):
    """Devuelve (tema, respuesta) o None, sin acceso a ChromaDB."""
    q = _normalizar(pregunta)
    if len(q) < 12:
        return None
    # Priorizar preguntas jurídicas explícitas frente a coincidencias generales.
    if '1257' in q or ('derechos' in q and ('mujer' in q or 'violencia' in q)):
        return 'DERECHOS_EDUCATIVOS', _RESPUESTAS['derechos']
    if any(t in q for t in ('casa matria', 'orientacion institucional', 'donde puedo recibir orientacion', 'donde puedo pedir ayuda en cali', 'a donde acudir en cali')):
        return 'ORIENTACION_INSTITUCIONAL_EDUCATIVA', _RESPUESTAS['institucional']
    if any(t in q for t in ('autoestima', 'autoconocimiento', 'autonomia', 'tomar decisiones', 'tomar una decision', 'limites personales', 'confianza en mi misma')):
        return 'AUTONOMIA_EDUCATIVA', _RESPUESTAS['autonomia']
    if any(t in q for t in ('tipos de violencia', 'violencia psicologica', 'senales de violencia', 'violencia contra las mujeres', 'violencia economica', 'violencia fisica', 'violencia de genero')):
        return 'PREVENCION_VIOLENCIAS_EDUCATIVA', _RESPUESTAS['violencia']
    return None
