# backend/api/endpoints/rag.py

import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from pathlib import Path

# Importamos solo lo que necesitamos del motor
from backend.core.engine import (
    process_and_store_embeddings, 
    get_rag_chain, 
    SUPPORTED_EMBEDDING_MODELS
)

# --- CONSTANTE DEFINIDA LOCALMENTE ---
# Definimos la ruta aquí, ya que es una responsabilidad de la API.
SOURCE_DOCS_PATH = Path("data_storage/source_documents")

router = APIRouter()

# --- Modelos Pydantic ---
class PipelineConfig(BaseModel):
    embedding_model: str
    chunk_size: int
    chunk_overlap: int

class QueryRequest(BaseModel):
    question: str
    config: PipelineConfig

class UploadResponse(BaseModel):
    message: str
    filename: str
    config: PipelineConfig

class Chunk(BaseModel):
    content: str
    metadata: dict

class QueryResponse(BaseModel):
    llm_answer: str
    retrieved_chunks: list[Chunk]

# --- Endpoints ---
@router.get("/supported_embedding_models", response_model=list[str])
def get_supported_embedding_models():
    return SUPPORTED_EMBEDDING_MODELS

@router.post("/upload_and_process", response_model=UploadResponse)
def upload_and_process_document(
    chunk_size: int = Form(default=1000),
    chunk_overlap: int = Form(default=200),
    embedding_model: str = Form(default=SUPPORTED_EMBEDDING_MODELS[0]),
    file: UploadFile = File(...)
):
    if embedding_model not in SUPPORTED_EMBEDDING_MODELS:
        raise HTTPException(status_code=400, detail="Modelo no soportado.")

    config = PipelineConfig(embedding_model=embedding_model, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # Usamos la constante local SOURCE_DOCS_PATH
    SOURCE_DOCS_PATH.mkdir(parents=True, exist_ok=True)

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Formato de archivo inválido. Solo se aceptan PDF.")

    file_path = SOURCE_DOCS_PATH / file.filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {e}")

    try:
        process_and_store_embeddings(file_path=str(file_path), config=config.model_dump())
        return UploadResponse(message="Archivo procesado.", filename=file.filename, config=config)
    except Exception as e:
        # Devolvemos el mensaje de error real para facilitar la depuración
        raise HTTPException(status_code=500, detail=f"Error durante el procesamiento: {str(e)}")

@router.post("/query", response_model=QueryResponse)
def query_document(request: QueryRequest):
    rag_chain, retriever = get_rag_chain(config=request.config.model_dump())
    
    if rag_chain is None:
        raise HTTPException(status_code=404, detail="Índice para esta configuración no encontrado. Procese un documento con esta configuración primero.")
        
    try:
        llm_answer = rag_chain.invoke(request.question)
        retrieved_docs = retriever.invoke(request.question)
        retrieved_chunks = [Chunk(content=doc.page_content, metadata=doc.metadata) for doc in retrieved_docs]
        return QueryResponse(llm_answer=llm_answer, retrieved_chunks=retrieved_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en consulta: {str(e)}")
