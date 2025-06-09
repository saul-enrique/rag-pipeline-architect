# backend/core/engine.py

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def process_document(file_path: str):
    """
    Carga un documento PDF y lo divide en chunks.
    """
    if not os.path.exists(file_path):
        print(f"Error: El archivo no se encuentra en la ruta: {file_path}")
        return None

    print(f"Cargando el documento: {file_path}")
    # 1. Cargar el documento
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    if not documents:
        print("No se pudo cargar ningún documento.")
        return None

    print(f"Documento cargado. {len(documents)} página(s) encontradas.")

    # 2. Dividir el texto en chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Número de caracteres por chunk
        chunk_overlap=200,   # Caracteres de solapamiento para mantener contexto
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Documento dividido en {len(chunks)} chunks.")

    return chunks

# --- Bloque para probar este átomo de forma aislada ---
if __name__ == '__main__':
    # Nos aseguramos de que la ruta sea correcta relativa a la raíz del proyecto
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    test_pdf_path = os.path.join(project_root, "data_storage", "source_documents", "sample.pdf")
    
    document_chunks = process_document(test_pdf_path)

    if document_chunks:
        print("\n--- Ejemplo de un Chunk ---")
        print(document_chunks[0].page_content)
        print("\n--- Metadatos del Chunk ---")
        print(document_chunks[0].metadata)
