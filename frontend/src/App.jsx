// frontend/src/App.jsx
import React from 'react';
// Añadimos las extensiones .jsx para ser explícitos
import FileUpload from './components/FileUpload.jsx';
import Chat from './components/Chat.jsx';
import './App.css';

function App() {
  return (
    <div className="App">
      <h1>RAG Pipeline Architect</h1>
      <FileUpload />
      <Chat />
    </div>
  );
}

export default App;
