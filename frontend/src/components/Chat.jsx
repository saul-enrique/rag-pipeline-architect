// frontend/src/components/Chat.jsx
import React, { useState } from 'react';
import axios from 'axios';

// El Chat necesita saber la configuración actual del pipeline, que recibe como 'prop'.
const Chat = ({ onSaveExperiment, currentConfig }) => {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

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
      // --- ¡ESTA ES LA PARTE CLAVE Y CORREGIDA! ---
      // Creamos el cuerpo de la petición con la estructura anidada que espera el backend.
      const requestBody = {
        question: query,
        config: currentConfig, // Enviamos el objeto de configuración completo.
      };

      // Enviamos el requestBody a la API.
      const response = await axios.post('http://127.0.0.1:8000/rag/query', requestBody);
      // ---------------------------------------------

      setResult({
        question: query,
        llm_answer: response.data.llm_answer,
        retrieved_chunks: response.data.retrieved_chunks,
      });
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Ocurrió un error al hacer la consulta.';
      if (typeof errorMessage === 'string') {
        setError(errorMessage);
      } else {
        setError(JSON.stringify(errorMessage));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <h2>2. Chatea con tu Documento</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text" value={query} onChange={(e) => setQuery(e.target.value)}
          placeholder="Escribe tu pregunta aquí..." style={{ width: '70%' }}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Pensando...' : 'Preguntar'}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}
      
      {result && (
        <div className="results-container">
          <button onClick={() => onSaveExperiment(result)} className="save-button">
            Guardar Experimento
          </button>
          <h3>Respuesta del Asistente:</h3>
          <p className="llm-answer">{result.llm_answer}</p>
          <hr />
          <h4>Contexto Utilizado (Chunks Recuperados):</h4>
          <div className="chunks-container">
            {result.retrieved_chunks.map((chunk, index) => (
              <div key={index} className="chunk">
                <p><strong>Chunk {index + 1} (Página: {chunk.metadata.page + 1})</strong></p>
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
