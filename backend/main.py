# backend/main.py
from fastapi import FastAPI
# Importamos el router que acabamos de crear
from backend.api.endpoints import rag

app = FastAPI(
    title="RAG Pipeline Architect API",
    description="API para diseñar, probar y comparar pipelines RAG.",
    version="0.1.0"
)

@app.get("/", tags=["General"])
def read_root():
    return {"message": "Bienvenido a la API del RAG Pipeline Architect"}

# Incluimos el router de RAG en nuestra aplicación principal.
# Le ponemos un prefijo y una etiqueta para mantener todo organizado.
app.include_router(rag.router, prefix="/rag", tags=["RAG Pipeline"])
