// frontend/src/components/FileUpload.jsx

import React, { useState } from 'react'; // ¡LA CORRECCIÓN ESTÁ AQUÍ!
import axios from 'axios';

const FileUpload = () => {
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

    setIsLoading(true);
    setMessage('');
    setError('');

    try {
      const response = await axios.post('http://127.0.0.1:8000/rag/upload_and_process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMessage(response.data.message || 'Archivo procesado con éxito');
      setFile(null); // Limpiar el input después de subir
    } catch (err) {
      setError(err.response?.data?.detail || 'Ocurrió un error al subir el archivo.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <h2>1. Cargar Documento PDF</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".pdf" onChange={handleFileChange} />
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
