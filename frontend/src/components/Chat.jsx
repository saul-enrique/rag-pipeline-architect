// frontend/src/components/Chat.jsx
import React, { useState } from 'react';
import axios from 'axios';

const Chat = () => {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleQueryChange = (event) => {
    setQuery(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!query.trim()) {
      setError('Por favor, introduce una pregunta.');
      return;
    }

    setIsLoading(true);
    setResult(null);
    setError('');

    try {
      const response = await axios.post('http://127.0.0.1:8000/rag/query', {
        question: query,
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ocurrió un error al hacer la consulta.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <h2>2. Chatea con tu Documento</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={handleQueryChange}
          placeholder="Escribe tu pregunta aquí..."
          style={{ width: '70%' }} // Añadimos un poco de estilo inline
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Pensando...' : 'Preguntar'}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}
      
      {result && (
        <div className="results-container">
          <h3>Respuesta del Asistente:</h3>
          <p className="llm-answer">{result.llm_answer}</p>
          
          <hr />

          <h4>Contexto Utilizado (Chunks Recuperados):</h4>
          <div className="chunks-container">
            {result.retrieved_chunks.map((chunk, index) => (
              <div key={index} className="chunk">
                <p><strong>Chunk {index + 1} (Fuente: {chunk.metadata.source}, Página: {chunk.metadata.page + 1})</strong></p>
                <small>{chunk.content}</small>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;
