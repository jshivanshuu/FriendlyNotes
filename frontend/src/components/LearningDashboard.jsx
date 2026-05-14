import React, { useState } from 'react';

const LearningDashboard = ({ data }) => {
  const [activeTab, setActiveTab] = useState('notes');

  if (!data || !data.topics) return null;

  return (
    <div className="dashboard glass-panel">
      <div className="tabs">
        <button 
          className={`tab-btn ${activeTab === 'notes' ? 'active' : ''}`}
          onClick={() => setActiveTab('notes')}
        >
          📝 Notes
        </button>
        <button 
          className={`tab-btn ${activeTab === 'formulas' ? 'active' : ''}`}
          onClick={() => setActiveTab('formulas')}
        >
          📐 Formulas
        </button>
        <button 
          className={`tab-btn ${activeTab === 'questions' ? 'active' : ''}`}
          onClick={() => setActiveTab('questions')}
        >
          ❓ Practice Questions
        </button>
      </div>

      <div className="content-area">
        {data.topics.map((topic, index) => (
          <div key={index} className="topic-card">
            <h2>{topic.title}</h2>
            
            {activeTab === 'notes' && (
              <ul className="notes-list">
                {topic.notes && topic.notes.length > 0 ? (
                  topic.notes.map((note, i) => (
                    <li key={i}>{note}</li>
                  ))
                ) : (
                  <p style={{ color: '#94a3b8' }}>No specific notes for this topic.</p>
                )}
              </ul>
            )}

            {activeTab === 'formulas' && (
              <div className="formulas-container">
                {topic.formulas && topic.formulas.length > 0 ? (
                  topic.formulas.map((formula, i) => (
                    <div key={i} className="formula-card">
                      <h3>{formula.name}</h3>
                      <div className="formula-math">{formula.equation}</div>
                      <p style={{ color: '#cbd5e1' }}>{formula.description}</p>
                    </div>
                  ))
                ) : (
                  <p style={{ color: '#94a3b8' }}>No specific formulas for this topic.</p>
                )}
              </div>
            )}

            {activeTab === 'questions' && (
              <div className="questions-container">
                {topic.questions && topic.questions.length > 0 ? (
                  topic.questions.map((q, i) => (
                    <div key={i} className="question-card">
                      <div className="question-text">Q: {q.question}</div>
                      <div className="answer-text"><strong>A:</strong> {q.answer}</div>
                    </div>
                  ))
                ) : (
                  <p style={{ color: '#94a3b8' }}>No practice questions available for this topic.</p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LearningDashboard;
