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

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_LLM_MODEL = "llama3"

def process_and_store_embeddings(file_path: str, embedding_model: str = DEFAULT_EMBEDDING_MODEL):
    """Orquesta la carga, división y almacenamiento de un documento."""
    print(f"INFO: Procesando {file_path} con el modelo de embedding {embedding_model}.")
    
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    if not docs:
        print("ERROR: No se pudo cargar el documento.")
        return False
    
    # ---- LÍNEA CORREGIDA ----
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    # -------------------------
    chunks = text_splitter.split_documents(docs)
    
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model, model_kwargs={'device': 'cpu'})
    
    # Asegurarse de que el directorio existe antes de usarlo
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_STORE_PATH
    )
    print("INFO: Índice vectorial creado/actualizado con éxito.")
    return True

def get_rag_chain(llm_model: str = DEFAULT_LLM_MODEL, k_chunks: int = 3):
    """Prepara y devuelve una cadena RAG lista para ser invocada."""
    if not os.path.exists(VECTOR_STORE_PATH):
        return None, None
        
    embeddings = HuggingFaceEmbeddings(model_name=DEFAULT_EMBEDDING_MODEL, model_kwargs={'device': 'cpu'})
    vector_store = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={'k': k_chunks})
    
    template = """
    Eres un asistente que responde preguntas basándose únicamente en el contexto proporcionado.
    Contexto: {context}
    Pregunta: {question}
    Respuesta:
    """
    prompt = PromptTemplate.from_template(template)
    llm = Ollama(model=llm_model)

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain, retriever
