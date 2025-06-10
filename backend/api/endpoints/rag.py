# backend/api/endpoints/rag.py

import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from pathlib import Path

# Importamos las funciones y constantes necesarias de nuestro motor
from backend.core.engine import (
    process_and_store_embeddings, 
    get_rag_chain, 
    SUPPORTED_EMBEDDING_MODELS, 
    SOURCE_DOCS_PATH
)

router = APIRouter()

# --- Modelos de Datos (Pydantic) para validar y documentar la API ---
class UploadResponse(BaseModel):
    message: str
    filename: str

class QueryRequest(BaseModel):
    question: str

class Chunk(BaseModel):
    content: str
    metadata: dict

class QueryResponse(BaseModel):
    llm_answer: str
    retrieved_chunks: list[Chunk]

# --- Endpoints de la API ---

@router.get("/supported_embedding_models", response_model=list[str])
def get_supported_embedding_models():
    """
    Devuelve la lista de modelos de embedding soportados por el backend.
    """
    return SUPPORTED_EMBEDDING_MODELS

@router.post("/upload_and_process", response_model=UploadResponse)
def upload_and_process_document(
    embedding_model: str = Form(default=SUPPORTED_EMBEDDING_MODELS[0]),
    file: UploadFile = File(...)
):
    """
    Sube un PDF y lo procesa usando el modelo de embedding especificado.
    """
    if embedding_model not in SUPPORTED_EMBEDDING_MODELS:
        raise HTTPException(status_code=400, detail="El modelo de embedding no es soportado.")

    source_path = Path(SOURCE_DOCS_PATH)
    source_path.mkdir(parents=True, exist_ok=True)

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Formato de archivo inválido. Solo se aceptan PDF.")

    file_path = source_path / file.filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {e}")

    try:
        if not process_and_store_embeddings(str(file_path), embedding_model=embedding_model):
            raise HTTPException(status_code=500, detail="El motor RAG no pudo procesar el documento.")
        
        return UploadResponse(
            message=f"Archivo procesado con éxito usando {embedding_model}.",
            filename=file.filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el procesamiento: {e}")

@router.post("/query", response_model=QueryResponse)
def query_document(request: QueryRequest):
    """
    Recibe una pregunta y devuelve la respuesta del LLM y los chunks recuperados.
    """
    rag_chain, retriever = get_rag_chain()
    
    if rag_chain is None:
        raise HTTPException(status_code=404, detail="Índice no encontrado. Por favor, suba y procese un documento primero.")
        
    try:
        llm_answer = rag_chain.invoke(request.question)
        retrieved_docs = retriever.invoke(request.question)
        retrieved_chunks = [
            Chunk(content=doc.page_content, metadata=doc.metadata) for doc in retrieved_docs
        ]
        
        return QueryResponse(
            llm_answer=llm_answer,
            retrieved_chunks=retrieved_chunks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la consulta con el LLM: {e}")
