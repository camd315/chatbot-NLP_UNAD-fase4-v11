# Pasos de despliegue controlado
1. Revisar todos los archivos del paquete y comprobar que no hay secretos ni datos privados.
2. En GitHub, abrir el repositorio creado, rama main, y subir `app.py`, `config.py`,
   carpeta `backend`, `requirements.txt`, `.gitignore`, `.streamlit` y `README.md`.
3. No subir `data/`, ZIP originales, PDFs, registros con conversaciones ni notebooks.
4. En Streamlit: New app → From GitHub → repo → `main` → `app.py` → Deploy.
5. Confirmar que aparece el aviso «Corpus público no autorizado».
6. Ejecutar pruebas de urgencia y de abstención; documentar las capturas y resultados.
7. Solamente después de auditar y autorizar un corpus depurado, estudiar despliegue RAG.
