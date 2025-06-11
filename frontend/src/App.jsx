// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload.jsx';
import Chat from './components/Chat.jsx';
import ComparisonDashboard from './components/ComparisonDashboard.jsx';
import axios from 'axios';
import './App.css';

function App() {
  // --- CORRECCIÓN CLAVE: Usamos snake_case para que coincida con el backend ---
  const [pipelineConfig, setPipelineConfig] = useState({
    embedding_model: '',
    chunk_size: 1000,
    chunk_overlap: 200,
  });
  // --------------------------------------------------------------------

  const [supportedModels, setSupportedModels] = useState([]);
  const [savedExperiments, setSavedExperiments] = useState([]);
  const [isConfigReady, setIsConfigReady] = useState(false);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/rag/supported_embedding_models');
        const models = response.data;
        setSupportedModels(models);
        if (models.length > 0) {
          // --- CORRECCIÓN CLAVE: Usamos snake_case al actualizar ---
          setPipelineConfig(prev => ({ ...prev, embedding_model: models[0] }));
          setIsConfigReady(true);
        }
      } catch (err) {
        console.error("Error al cargar los modelos de embedding", err);
      }
    };
    fetchModels();
  }, []);

  const handleSaveExperiment = (experimentData) => {
    const newExperiment = {
      id: new Date().getTime(),
      config: pipelineConfig,
      ...experimentData,
    };
    setSavedExperiments(prev => [...prev, newExperiment]);
  };

  return (
    <div className="App">
      <h1>RAG Pipeline Architect</h1>
      <div className="main-layout">
        <div className="config-and-chat-panel">
          {isConfigReady ? (
            <>
              <FileUpload
                pipelineConfig={pipelineConfig}
                setPipelineConfig={setPipelineConfig}
                supportedModels={supportedModels}
              />
              <Chat 
                onSaveExperiment={handleSaveExperiment} 
                currentConfig={pipelineConfig} 
              />
            </>
          ) : (
            <p>Cargando configuración desde la API...</p>
          )}
        </div>
        <div className="dashboard-panel">
          <ComparisonDashboard experiments={savedExperiments} />
        </div>
      </div>
    </div>
  );
}

export default App;
