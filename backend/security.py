"""Prioridad de seguridad V11: se conserva el módulo preventivo original."""
from .seguridad_v11_original import respuesta_preventiva_v11

REVIEW_MESSAGE = (
    "No puedo confirmar una respuesta segura y verificada para esta consulta. "
    "Si existe riesgo inmediato en Colombia, comunícate con el 123 si es seguro hacerlo; "
    "para orientación sobre violencias de género, 155. "
    "Esta aplicación no contacta autoridades ni reemplaza servicios humanos."
)

def evaluate(text):
    """Reglas originales V11; *no* sustituye las 32 referencias semánticas V10."""
    return respuesta_preventiva_v11(text)
