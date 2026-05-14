import React, { useState, useRef } from 'react';

const UploadSection = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (selectedFile) => {
    setError('');
    if (selectedFile.type !== 'application/pdf') {
      setError('Please upload a PDF file.');
      setFile(null);
      return;
    }
    setFile(selectedFile);
  };

  const uploadFile = async () => {
    if (!file) return;

    setIsUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Upload failed');
      }

      const data = await response.json();
      onUploadSuccess(data);
    } catch (err) {
      setError(err.message || 'An error occurred during upload.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="glass-panel">
        <h2 style={{ marginBottom: '1rem' }}>Upload Your Notes</h2>
        <p style={{ color: '#94a3b8', marginBottom: '2rem' }}>
          Upload your PDF notes and let AI generate study materials for your exam.
        </p>

        <div 
          className={`dropzone ${isDragging ? 'active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m3.75 9v6m3-3H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
          
          {file ? (
            <div style={{ color: 'var(--success-color)', fontWeight: '600' }}>
              Selected: {file.name}
            </div>
          ) : (
            <div>
              <span style={{ color: 'var(--accent-color)' }}>Click to upload</span> or drag and drop<br/>
              <span style={{ fontSize: '0.9rem', color: '#64748b' }}>PDF files only</span>
            </div>
          )}
          
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept="application/pdf"
            style={{ display: 'none' }} 
          />
        </div>

        {error && <div style={{ color: '#ef4444', marginTop: '1rem' }}>{error}</div>}

        <div style={{ marginTop: '2rem' }}>
          <button 
            className="btn" 
            onClick={uploadFile} 
            disabled={!file || isUploading}
            style={{ width: '100%' }}
          >
            {isUploading ? 'Generating Materials (this may take a minute)...' : 'Generate Study Materials'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadSection;
