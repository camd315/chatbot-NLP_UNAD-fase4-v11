# Chatbot NLP UNAD – Fase 4 V11 / Despliegue controlado

Esta versión es una **demostración pública académica** con recuperación semántica real mediante
`intfloat/multilingual-e5-small` (384 dimensiones) y ChromaDB en memoria. Las ocho fichas de
`data/demo/` son contenido educativo original redactado para el prototipo; **NO** son los 173
fragmentos originales del ejercicio 2, ni representan documentos institucionales.

## Alcance
- Reglas preventivas originales V11 más corrección contextual de consultas en tercera persona.
- Prioridad de posible urgencia, reinicio de metadatos de memoria y abstención ante falta de evidencia.
- Búsqueda vectorial E5 + ChromaDB, con respuestas extractivas y citas de fichas didácticas.
- Qwen **no se ejecuta ni publica**. El cuaderno V11 había reportado generación experimental,
  no un servicio listo para producción. El clasificador semántico V10 completo tampoco se reproduce.
- La modalidad documental V11 original se mantiene bloqueada hasta que se verifique el permiso
  de redistribución de cada fuente y el corpus se instale fuera de un repositorio público.

## Despliegue
Ver `DEPLOY.md`. Ejecutar `python -m unittest discover -s tests -v` para pruebas del controlador.
La descarga inicial del modelo E5 depende de acceso de red y recursos disponibles en Streamlit.

## Consultas recomendadas
`¿Qué es RAG?`, `¿Qué es un embedding?`, `¿Para qué sirve ChromaDB?`,
`¿Cómo se evalúa un chatbot?`, `¿Qué es la violencia psicológica?` (abstención),
`Mi hermana está siendo golpeada y necesita ayuda urgente` (control preventivo).

## Privacidad
No registrar ni subir preguntas de personas reales. No publicar datos, claves, archivos
originales, el ZIP del ejercicio 2 ni la base de 173 fragmentos sin autorización verificable.
