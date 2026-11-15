# Despliegue actualizado – ejercicio 3

## 1. Repositorio GitHub ya existente
`camd315/chatbot-NLP_UNAD-fase4-v11` (rama `main`).

## 2. Qué sustituir y qué agregar (subir solo el contenido de este ZIP)
**Actualizar**: `app.py`, `config.py`, `requirements.txt`, `.gitignore`, `README.md`,
`DEPLOY.md`, `backend/chatbot.py`, `backend/security.py`, `tests/test_control.py`.
**Agregar**: `backend/demo_rag.py`, `data/demo/documentos_academicos_originales.json`,
`tests/test_demo.py`.
**Conservar intactos**: `backend/seguridad_v11_original.py`,
`backend/validated.py`, `backend/rag.py` y `backend/__init__.py`.

En GitHub, reemplazar los archivos existentes y subir las carpetas nuevas manteniendo
su ruta. Evitar duplicar una carpeta raíz adicional.

## 3. Streamlit
Repositorio `camd315/chatbot-NLP_UNAD-fase4-v11`, rama `main`, archivo `app.py`.
No se requieren secretos. Python 3.11.
Variables (opcionales): `DEMO_RAG_ENABLED=true` y `AUTHORIZED_PUBLIC_CORPUS=false`.
Este último valor **debe permanecer en false** hasta verificar la redistribución.

## 4. Pruebas
- `¿Qué es RAG?` → `RAG_DEMO_EXTRACTIVO` y fuente `intro-rag`.
- `¿Qué es un embedding?` → `RAG_DEMO_EXTRACTIVO`.
- `¿Qué servicios de Casa Matria ...?` → `DOCUMENTACION_PENDIENTE` (sin corpus autorizado).
- `¿Qué es la violencia psicológica?` → no debe activar urgencia.
- `Mi hermana está siendo golpeada y necesita ayuda urgente` → `SEGURIDAD_INMEDIATA_189`.
- Después de urgencia, la memoria interna temática se limpia; historial visual no guarda el texto.

Si el modelo E5 no se carga por memoria o por red, Streamlit mostrará advertencia y seguirá
habilitado el módulo preventivo. Revisar Manage app → Logs, sin copiar credenciales.

## 5. Pendiente para completar la guía
La demostración no reemplaza el RAG del caso de uso real del ejercicio 2. Para activar
sus 173 fragmentos, completar la matriz de licencias y privacidad, instalar un corpus
con permisos fuera de GitHub público y volver a validar las respuestas. Tampoco
reemplaza la integración final de un LLM abierto ni la evaluación formal de 10 casos.
