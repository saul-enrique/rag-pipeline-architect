// frontend/src/components/FileUpload.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const [embeddingModels, setEmbeddingModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');

  // Este 'useEffect' se ejecuta una sola vez cuando el componente se carga.
  // Su propósito es llamar a nuestra API para obtener la lista de modelos.
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/rag/supported_embedding_models');
        setEmbeddingModels(response.data);
        if (response.data.length > 0) {
          setSelectedModel(response.data[0]); // Seleccionamos el primer modelo por defecto
        }
      } catch (err) {
        setError('Error: No se pudo conectar con la API para cargar los modelos.');
      }
    };
    fetchModels();
  }, []); // El array vacío asegura que se ejecute solo al montar el componente.

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
    formData.append('embedding_model', selectedModel);

    setIsLoading(true);
    setMessage('');
    setError('');

    try {
      const response = await axios.post('http://127.0.0.1:8000/rag/upload_and_process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMessage(response.data.message);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ocurrió un error al procesar el archivo.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <h2>1. Configurar Pipeline y Cargar Documento</h2>
      <form onSubmit={handleSubmit}>
        <div className="config-item">
          <label htmlFor="model-select">Modelo de Embedding:</label>
          <select 
            id="model-select" 
            value={selectedModel} 
            onChange={(e) => setSelectedModel(e.target.value)}
            disabled={embeddingModels.length === 0}
          >
            {embeddingModels.map(model => (
              <option key={model} value={model}>{model}</option>
            ))}
          </select>
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
