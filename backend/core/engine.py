# backend/core/engine.py

import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
# ---- Importaciones actualizadas y corregidas ----
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM as Ollama # CORRECCIÓN AQUÍ
# ---------------------------------------------
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

# --- CONSTANTES ---
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VECTOR_STORE_PATH = os.path.join(project_root, "data_storage", "vector_store")
LLM_MODEL_NAME = "llama3"

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
        chunk_size=1000, overlap=200, length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Documento dividido en {len(chunks)} chunks.")
    return chunks

def create_vector_store(chunks, embedding_model_name: str, path: str):
    """Crea una base de datos vectorial a partir de los chunks del documento."""
    if not chunks:
        print("No hay chunks para procesar.")
        return None
    
    print("Creando el modelo de embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model_name, model_kwargs={'device': 'cpu'}
    )
    print(f"Modelo de embeddings '{embedding_model_name}' cargado.")
    
    print("Creando y guardando la base de datos vectorial en ChromaDB...")
    vector_store = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=path
    )
    
    print(f"¡Base de datos vectorial creada con éxito!")
    print(f"Ubicación: {path}")
    return vector_store

def query_rag_pipeline(query: str):
    """Ejecuta una consulta contra el pipeline RAG completo."""
    print("\n--- Iniciando Pipeline RAG para la consulta ---")
    print(f"Consulta: '{query}'")

    print("Cargando base de datos vectorial...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME, model_kwargs={'device': 'cpu'}
    )
    vector_store = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={'k': 3})
    
    print("Base de datos cargada. Creando prompt...")

    template = """
    Eres un asistente de inteligencia artificial. Tu tarea es responder la pregunta del usuario
    basándote únicamente en el siguiente contexto. Si la respuesta no se encuentra en el
    contexto, di "La información no se encuentra en el documento.". No inventes información.

    Contexto:
    {context}

    Pregunta:
    {question}

    Respuesta:
    """
    prompt = PromptTemplate.from_template(template)

    llm = Ollama(model=LLM_MODEL_NAME) # Gracias al alias, esta línea no cambia
    print(f"LLM '{LLM_MODEL_NAME}' inicializado.")

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("Ejecutando la cadena RAG...")
    response = rag_chain.invoke(query)
    
    print("\n--- Respuesta Final ---")
    print(response)

    retrieved_docs = retriever.invoke(query)
    print("\n--- Documentos Recuperados como Contexto ---")
    for i, doc in enumerate(retrieved_docs):
        print(f"Chunk {i+1}:")
        print(doc.page_content)
        print("-" * 20)

if __name__ == '__main__':
    rebuild_index_input = input("¿Deseas reconstruir el índice vectorial? (s/n): ").strip().lower()
    
    if rebuild_index_input == 's':
        test_pdf_path = os.path.join(project_root, "data_storage", "source_documents", "sample.pdf")
        document_chunks = process_document(test_pdf_path)
        if document_chunks:
            create_vector_store(
                chunks=document_chunks,
                embedding_model_name=EMBEDDING_MODEL_NAME,
                path=VECTOR_STORE_PATH
            )
    else:
        if not os.path.exists(VECTOR_STORE_PATH):
            print("El índice no existe. Por favor, ejecute el script con la opción 's' para crearlo primero.")
            exit()
        print("Omitiendo la reconstrucción del índice. Usando el existente.")
    
    while True:
        user_query = input("\nIntroduce tu pregunta (o 'salir' para terminar): ")
        if user_query.lower() == 'salir':
            break
        if not user_query.strip():
            print("Por favor, introduce una pregunta válida.")
            continue
        query_rag_pipeline(user_query)
