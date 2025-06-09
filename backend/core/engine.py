# backend/core/engine.py

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Nuevas importaciones para este átomo
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# --- CONSTANTES ---
# Define el nombre del modelo de embedding que usaremos.
# 'all-MiniLM-L6-v2' es un excelente modelo para empezar: es rápido y de buena calidad.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Define la carpeta donde guardaremos la base de datos vectorial.
# La crearemos dentro de data_storage, pero recuerda que está en .gitignore.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VECTOR_STORE_PATH = os.path.join(project_root, "data_storage", "vector_store")


def process_document(file_path: str):
    """Carga un documento PDF y lo divide en chunks."""
    if not os.path.exists(file_path):
        print(f"Error: El archivo no se encuentra en la ruta: {file_path}")
        return None

    print(f"Cargando el documento: {file_path}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    if not documents:
        print("No se pudo cargar ningún documento.")
        return None

    print(f"Documento cargado. {len(documents)} página(s) encontradas.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Documento dividido en {len(chunks)} chunks.")

    return chunks

def create_vector_store(chunks, embedding_model_name: str, path: str):
    """
    Crea una base de datos vectorial a partir de los chunks del documento.
    """
    if not chunks:
        print("No hay chunks para procesar.")
        return None
    
    print("Creando el modelo de embeddings...")
    # 1. Inicializar el modelo de embeddings desde HuggingFace.
    # La primera vez que se ejecute, descargará el modelo.
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        model_kwargs={'device': 'cpu'} # Forzamos el uso de CPU
    )
    
    print(f"Modelo de embeddings '{embedding_model_name}' cargado.")
    
    print("Creando y guardando la base de datos vectorial en ChromaDB...")
    # 2. Crear la base de datos vectorial y guardarla en disco.
    vector_store = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory=path
    )
    
    print("¡Base de datos vectorial creada con éxito!")
    print(f"Ubicación: {path}")
    return vector_store


# --- Bloque para probar los átomos de forma aislada ---
if __name__ == '__main__':
    test_pdf_path = os.path.join(project_root, "data_storage", "source_documents", "sample.pdf")
    
    # Átomo 1.1
    document_chunks = process_document(test_pdf_path)
    
    if document_chunks:
        # Átomo 1.2
        vector_store = create_vector_store(
            chunks=document_chunks,
            embedding_model_name=EMBEDDING_MODEL_NAME,
            path=VECTOR_STORE_PATH
        )
        
        # Pequeña prueba para ver si funciona
        if vector_store:
            print("\n--- Realizando una búsqueda de prueba ---")
            query = "colisión inelástica"
            # Usamos la búsqueda por similitud del objeto que acabamos de crear
            results = vector_store.similarity_search(query, k=2)
            
            print(f"Resultados para la consulta: '{query}'")
            for doc in results:
                print("-" * 50)
                print(f"Contenido: {doc.page_content[:250]}...")
                print(f"Fuente: {doc.metadata.get('source', 'N/A')}, Página: {doc.metadata.get('page', 'N/A')}")
