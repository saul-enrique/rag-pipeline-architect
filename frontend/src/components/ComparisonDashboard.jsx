// frontend/src/components/ComparisonDashboard.jsx
import React from 'react';

const ExperimentCard = ({ experiment }) => (
  <div className="experiment-card">
    <h4>Experimento #{experiment.id}</h4>
    <div className="experiment-config">
      <strong>Configuración:</strong>
      <ul>
        <li>Modelo: {experiment.config.embeddingModel}</li>
        <li>Tamaño Chunk: {experiment.config.chunkSize}</li>
        <li>Solapamiento: {experiment.config.chunkOverlap}</li>
      </ul>
    </div>
    <div className="experiment-query">
      <strong>Pregunta:</strong>
      <p>{experiment.question}</p>
    </div>
    <div className="experiment-answer">
      <strong>Respuesta:</strong>
      <p>{experiment.llm_answer}</p>
    </div>
  </div>
);

const ComparisonDashboard = ({ experiments }) => {
  return (
    <div className="dashboard-container">
      <h2>Dashboard de Comparación</h2>
      {experiments.length === 0 ? (
        <p>No hay experimentos guardados. Realiza una consulta y guárdala para empezar a comparar.</p>
      ) : (
        <div className="experiments-grid">
          {experiments.map(exp => (
            <ExperimentCard key={exp.id} experiment={exp} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ComparisonDashboard;
