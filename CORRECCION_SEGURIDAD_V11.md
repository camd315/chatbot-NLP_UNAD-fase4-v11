# Corrección del módulo preventivo – V11

## Incidente documentado
La consulta «Una mujer está viviendo una situación de violencia en Cali y necesita ayuda urgente. ¿A dónde puede acudir?» retornó `DOCUMENTACION_PENDIENTE` en Streamlit.

## Causa
Las expresiones en tercera persona y las peticiones indirectas de orientación no estaban suficientemente contempladas en las reglas preventivas originales.

## Cambios
- `backend/security.py`: llama primero a la implementación V11 original y, si no se activa, evalúa coincidencias conjuntas **persona afectada + riesgo + necesidad de ayuda**. No sobrescribe `seguridad_v11_original.py`.
- `tests/test_control.py`: amplía la batería a diez casos, incluyendo la incidencia, limpieza de memoria, no generación Qwen, preguntas conceptuales y negación.

## Límites
Clasificación por patrones, no por referencias semánticas V10. Una consulta ambigua puede ser un falso positivo o falso negativo; nunca reemplaza apoyo humano. Las llamadas 123 y 155 proceden del texto preventivo V11 original y sus condiciones vigentes deben corroborarse antes de cualquier uso real. No se introdujeron claves ni documentos.

## Probar
```bash
python -m unittest discover -s tests -v
```

## Actualización segura de GitHub
Reemplazar únicamente `backend/security.py` y `tests/test_control.py` en `main`; crear commit y comprobar el reinicio automático de Streamlit. No subir ChromaDB o archivos confidenciales.
