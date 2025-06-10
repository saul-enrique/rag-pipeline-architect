# backend/core/engine.py

import os
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
VECTOR_STORE_PATH = str(PROJECT_ROOT / "data_storage" / "vector_store")
SOURCE_DOCS_PATH = str(PROJECT_ROOT / "data_storage" / "source_documents")

SUPPORTED_EMBEDDING_MODELS = [
    "all-MiniLM-L6-v2",
    "BAAI/bge-base-en-v1.5",
    "BAAI/bge-small-en-v1.5"
]

DEFAULT_EMBEDDING_MODEL = SUPPORTED_EMBEDDING_MODELS[0]
DEFAULT_LLM_MODEL = "llama3"

# --- MODIFICAMOS LA FUNCIÓN DE PROCESAMIENTO ---
def process_and_store_embeddings(
    file_path: str,
    embedding_model: str,
    chunk_size: int,
    chunk_overlap: int
):
    """Orquesta la carga, división y almacenamiento usando la configuración proporcionada."""
    if embedding_model not in SUPPORTED_EMBEDDING_MODELS:
        print(f"ERROR: Modelo de embedding '{embedding_model}' no soportado.")
        return False
        
    print(f"INFO: Procesando {file_path} con la configuración:")
    print(f"  - Modelo Embedding: {embedding_model}")
    print(f"  - Tamaño de Chunk: {chunk_size}")
    print(f"  - Solapamiento: {chunk_overlap}")
    
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    if not docs:
        print("ERROR: No se pudo cargar el documento.")
        return False
    
    # Usamos los nuevos parámetros aquí
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(docs)
    print(f"INFO: Documento dividido en {len(chunks)} chunks.")
    
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model, model_kwargs={'device': 'cpu'})
    
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_STORE_PATH
    )
    print("INFO: Índice vectorial creado/actualizado con éxito.")
    return True

# --- (La función get_rag_chain no necesita cambios por ahora) ---
def get_rag_chain(llm_model: str = DEFAULT_LLM_MODEL, k_chunks: int = 3):
    """Prepara y devuelve una cadena RAG lista para ser invocada."""
    # ... (código existente sin cambios) ...
    if not os.path.exists(VECTOR_STORE_PATH):
        return None, None
    embeddings = HuggingFaceEmbeddings(model_name=DEFAULT_EMBEDDING_MODEL, model_kwargs={'device': 'cpu'})
    vector_store = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={'k': k_chunks})
    template = "Eres un asistente que responde preguntas basándose únicamente en el contexto proporcionado.\nContexto: {context}\nPregunta: {question}\nRespuesta:"
    prompt = PromptTemplate.from_template(template)
    llm = Ollama(model=llm_model)
    rag_chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser())
    return rag_chain, retriever
