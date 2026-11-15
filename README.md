# Chatbot NLP UNAD · Fase 4 · adaptación controlada V11

## Procedencia y límites

Adaptación de la entrega del Ejercicio 2. Se conserva el archivo de reglas preventivas V11,
el control de abstención, el ensamblaje jurídico validado y la restricción de publicación
de borradores Qwen. **No se afirma equivalencia funcional completa**: las 32 referencias
semánticas se recuperaban del notebook V10, que NO está en el ZIP suministrado.
Las respuestas automáticas abiertas están expresamente deshabilitadas.

## Ejecutar localmente

1. Crear entorno Python 3.11 (recomendado), activar y ejecutar `pip install -r requirements.txt`.
2. Iniciar con `streamlit run app.py`.
3. Sin corpus autorizado, la aplicación responde a alertas V11 y se abstiene de consultas documentales.
4. Para ensayar con un corpus **auditado y autorizado para publicación**, copiar la estructura completa
   de ChromaDB V11 a `data/chroma_db/` (archivo `chroma.sqlite3` y carpeta del índice),
   y establecer `AUTHORIZED_PUBLIC_CORPUS=true` en el entorno del proceso.
5. Verificar los 173 registros, el modelo de embeddings y el rendimiento del servidor.

### Publicación en Streamlit Community Cloud

Subir a GitHub solamente archivos de código revisados, sin `data/`, `.env`, PDFs ni notebooks.
Elegir rama `main`, archivo `app.py` y desplegar. Por defecto el corpus no está disponible;
para disponer de RAG público se requiere primero una base redactada, verificada y autorizada,
y decidir una distribución segura. **No publique el ZIP original de ChromaDB.**

## Arquitectura

Streamlit → controlador seguro → módulo de urgencias V11 → rutas documentales exactas
→ (si se autoriza) E5 + ChromaDB V11 → comprobación de evidencia → respuesta.
Qwen está desactivado deliberadamente: no se publica texto experimental no validado.

## Ensayos

`python -m unittest discover -s tests -v`

## Advertencias

Sistema académico, no servicio de emergencias. Teléfonos y normas pueden cambiar. No guardar
preguntas personales en registros. El almacenamiento de historial en la pantalla es por sesión;
las consultas de emergencia no se retienen intencionadamente.

## Requisitos UNAD aún pendientes

Verificar control semántico completo con referencias V10, auditoría documental, despliegue real,
10 tareas de prueba, retroalimentación de usuarios, análisis de 3 problemas sistemáticos e informe APA.
