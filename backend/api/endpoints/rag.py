# backend/api/endpoints/rag.py
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path

# Creamos un 'router' para nuestros endpoints.
# Es como una mini-aplicación FastAPI que podemos incluir en la principal.
router = APIRouter()

# Definimos la ruta base donde se guardarán los documentos.
# Usamos Path para manejar rutas de forma más segura y compatible entre OS.
# OJO: Esta ruta es relativa a la raíz del proyecto.
SOURCE_DOCS_PATH = Path("data_storage/source_documents")

@router.post("/upload", status_code=201)
def upload_document(file: UploadFile = File(...)):
    """
    Endpoint para subir un archivo. Por ahora, solo acepta PDFs.
    """
    # Asegurarnos de que el directorio de destino existe.
    SOURCE_DOCS_PATH.mkdir(parents=True, exist_ok=True)

    # Validar que el archivo es un PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")

    # Definir la ruta completa donde se guardará el archivo.
    file_path = SOURCE_DOCS_PATH / file.filename
    
    try:
        # Guardar el archivo en el disco.
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "message": "Archivo subido con éxito.",
            "filename": file.filename,
            "path": str(file_path)
        }
    except Exception as e:
        # Si algo sale mal, lanzamos un error del servidor.
        raise HTTPException(status_code=500, detail=f"No se pudo guardar el archivo: {e}")
