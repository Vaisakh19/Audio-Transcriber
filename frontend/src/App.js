import React, { useState } from 'react';
import FileUpload from './FileUpload';
import ResultDisplay from './ResultDisplay';
import './styles.css';

const App = () => {
  const [summary, setSummary] = useState('');
  const [transcript, setTranscript] = useState('');
  const [activeTab, setActiveTab] = useState('summary');

  return (
    <div className="app-container">
      <h1>Podcast Summarizer</h1>

      {/* Upload component with callback */}
      <FileUpload
        onResult={(s, t) => {
          setSummary(s);
          setTranscript(t);
        }}
      />

      {/* Show tab buttons only when summary or transcript is available */}
      {(summary || transcript) && (
        <div className="tabs">
          <button onClick={() => setActiveTab('summary')}>Summary</button>
          <button onClick={() => setActiveTab('transcript')}>Transcript</button>
        </div>
      )}

      {/* Display summary or transcript based on tab */}
      {activeTab === 'summary' && summary && <ResultDisplay summary={summary} />}
      {activeTab === 'transcript' && transcript && (
        <div className="result-box">
          <h2>Transcript</h2>
          <p>{transcript}</p>
        </div>
      )}
    </div>
  );
};

export default App;
