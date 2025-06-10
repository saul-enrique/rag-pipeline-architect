# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Importar middleware
from backend.api.endpoints import rag

app = FastAPI(
    title="RAG Pipeline Architect API",
    description="API para diseñar, probar y comparar pipelines RAG.",
    version="0.1.0"
)

# --- Configuración de CORS ---
# Lista de orígenes que tienen permiso para hacer peticiones.
origins = [
    "http://localhost:5173", # La dirección de nuestro frontend de React
    "http://localhost:5174", # A veces Vite usa otro puerto
    # Añade aquí la URL de tu aplicación cuando la despliegues
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"], # Permitir todos los headers
)
# ---------------------------

@app.get("/", tags=["General"])
def read_root():
    return {"message": "Bienvenido a la API del RAG Pipeline Architect"}

app.include_router(rag.router, prefix="/rag", tags=["RAG Pipeline"])
