# backend/core/engine.py

import os
import shutil
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from pathlib import Path

# --- CONSTANTES ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASE_VECTOR_STORE_PATH = PROJECT_ROOT / "data_storage" / "vector_stores" # Cambiamos a un directorio base

SUPPORTED_EMBEDDING_MODELS = [
    "all-MiniLM-L6-v2",
    "BAAI/bge-base-en-v1.5",
    "BAAI/bge-small-en-v1.5"
]

DEFAULT_LLM_MODEL = "llama3"

# --- NUEVA FUNCIÓN HELPER ---
def get_vector_store_path(config: dict) -> str:
    """Genera una ruta única para el índice basada en la configuración."""
    model_name_slug = config['embedding_model'].replace('/', '_') # Reemplaza '/' para nombres de carpeta válidos
    dir_name = f"{model_name_slug}_chunk-{config['chunk_size']}_overlap-{config['chunk_overlap']}"
    return str(BASE_VECTOR_STORE_PATH / dir_name)

# --- FUNCIÓN DE PROCESAMIENTO MODIFICADA ---
def process_and_store_embeddings(
    file_path: str,
    config: dict
):
    """Orquesta la carga, división y almacenamiento usando una ruta de índice dinámica."""
    embedding_model = config['embedding_model']
    chunk_size = config['chunk_size']
    chunk_overlap = config['chunk_overlap']

    if embedding_model not in SUPPORTED_EMBEDDING_MODELS:
        return False

    vector_store_path = get_vector_store_path(config)
    print(f"INFO: Usando ruta de índice: {vector_store_path}")

    # Si la carpeta del índice ya existe, la eliminamos para reconstruirla.
    if os.path.exists(vector_store_path):
        print("INFO: Índice existente encontrado. Reconstruyendo...")
        shutil.rmtree(vector_store_path)

    # ... (el resto de la lógica de procesamiento no cambia) ...
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model, model_kwargs={'device': 'cpu'})
    
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=vector_store_path
    )
    print("INFO: Índice vectorial creado con éxito.")
    return True

# --- FUNCIÓN DE CONSULTA MODIFICADA ---
def get_rag_chain(config: dict, llm_model: str = DEFAULT_LLM_MODEL, k_chunks: int = 3):
    """Prepara la cadena RAG usando la ruta de índice correcta."""
    vector_store_path = get_vector_store_path(config)
    
    if not os.path.exists(vector_store_path):
        return None, None
        
    embeddings = HuggingFaceEmbeddings(model_name=config['embedding_model'], model_kwargs={'device': 'cpu'})
    vector_store = Chroma(persist_directory=vector_store_path, embedding_function=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={'k': k_chunks})
    
    template = "Eres un asistente que responde preguntas basándose únicamente en el contexto proporcionado.\nContexto: {context}\nPregunta: {question}\nRespuesta:"
    prompt = PromptTemplate.from_template(template)
    llm = Ollama(model=llm_model)
    rag_chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser())
    
    return rag_chain, retriever
