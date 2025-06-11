// frontend/src/components/FileUpload.jsx
import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = ({ pipelineConfig, setPipelineConfig, supportedModels }) => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setMessage('');
    setError('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Por favor, selecciona un archivo.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    // Enviamos los datos con los nombres correctos (snake_case)
    formData.append('embedding_model', pipelineConfig.embedding_model);
    formData.append('chunk_size', pipelineConfig.chunk_size);
    formData.append('chunk_overlap', pipelineConfig.chunk_overlap);

    setIsLoading(true);
    setMessage('');
    setError('');

    try {
      const response = await axios.post('http://127.0.0.1:8000/rag/upload_and_process', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const config = response.data.config;
      setMessage(`Éxito! Modelo: ${config.embedding_model}, Tamaño Chunk: ${config.chunk_size}, Solapamiento: ${config.chunk_overlap}.`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ocurrió un error al procesar el archivo.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfigChange = (e) => {
    const { name, value } = e.target;
    setPipelineConfig(prev => ({
      ...prev,
      [name]: value // El 'name' del input ya es snake_case
    }));
  };

  return (
    <div className="file-upload-container">
      <h2>1. Configurar Pipeline y Cargar Documento</h2>
      <form onSubmit={handleSubmit}>
        {/* --- CORRECCIÓN CLAVE: name y value usan snake_case --- */}
        <div className="config-item">
          <label htmlFor="embedding_model">Modelo de Embedding:</label>
          <select id="embedding_model" name="embedding_model" value={pipelineConfig.embedding_model} onChange={handleConfigChange}>
            {supportedModels.map(model => (<option key={model} value={model}>{model}</option>))}
          </select>
        </div>
        <div className="config-item">
          <label htmlFor="chunk_size">Tamaño de Chunk:</label>
          <input id="chunk_size" name="chunk_size" type="number" value={pipelineConfig.chunk_size} onChange={handleConfigChange} />
        </div>
        <div className="config-item">
          <label htmlFor="chunk_overlap">Solapamiento:</label>
          <input id="chunk_overlap" name="chunk_overlap" type="number" value={pipelineConfig.chunk_overlap} onChange={handleConfigChange} />
        </div>
        <div className="config-item">
          <label htmlFor="file-input">Archivo PDF:</label>
          <input id="file-input" type="file" accept=".pdf" onChange={handleFileChange} />
        </div>
        <button type="submit" disabled={isLoading || !file}>
          {isLoading ? 'Procesando...' : 'Subir y Procesar'}
        </button>
      </form>
      {message && <p className="success-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default FileUpload;
