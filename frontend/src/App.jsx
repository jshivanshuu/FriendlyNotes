import React, { useState } from 'react';
import UploadSection from './components/UploadSection';
import LearningDashboard from './components/LearningDashboard';

function App() {
  const [learningData, setLearningData] = useState(null);

  const handleUploadSuccess = (data) => {
    setLearningData(data);
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>FriendlyNotes</h1>
        <p>Turn any PDF into structured notes, formulas, and practice questions in seconds.</p>
      </header>

      <main>
        {!learningData ? (
          <UploadSection onUploadSuccess={handleUploadSuccess} />
        ) : (
          <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <h2 style={{ color: 'var(--accent-color)' }}>Your Learning Materials</h2>
              <button 
                className="btn" 
                style={{ background: 'transparent', border: '1px solid var(--accent-color)', color: 'var(--accent-color)' }}
                onClick={() => setLearningData(null)}
              >
                Upload Another PDF
              </button>
            </div>
            <LearningDashboard data={learningData} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
