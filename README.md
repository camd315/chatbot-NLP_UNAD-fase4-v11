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

## Configuración centralizada

El prototipo centraliza sus parámetros operativos en `config.py`, mediante la clase `Settings` y la instancia `SETTINGS`.

| Parámetro | Valor predeterminado | Función |
|---|---|---|
| `llm_model` | `Qwen/Qwen2.5-1.5B-Instruct` | Identifica el LLM del ejercicio 2; no se ejecuta en la demostración pública. |
| `llm_temperature` | `0.2` | Temperatura propuesta para futuras pruebas generativas. |
| `llm_max_new_tokens` | `256` | Límite propuesto de tokens generados. |
| `embedding_model` | `intfloat/multilingual-e5-small` | Modelo para representaciones semánticas. |
| `top_k` | `4` | Parámetro de recuperación para el backend original. |
| `demo_collection_name` | `demo_academica_original_v1` | Nombre de la colección del RAG educativo. |
| `demo_top_k` | `1` | Número predeterminado de fichas recuperadas. |
| `memory_limit` | `4` | Límite de contexto conversacional. |
| `authorized_corpus` | `False` | Impide utilizar el corpus original sin autorización. |
| `allow_generated_answers` | `False` | Mantiene deshabilitada la generación abierta en Streamlit. |

Los valores de configuración del LLM no implican que la generación esté activa. El sistema público usa recuperación extractiva sobre fichas educativas originales. Los parámetros generativos propuestos deben contrastarse con el notebook del ejercicio 2 antes de presentarse como valores experimentales.

Los parámetros configurables mediante variables de entorno se gestionan sin incluir credenciales ni información sensible en GitHub.
