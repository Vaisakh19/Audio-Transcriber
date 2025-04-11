import React, { useState } from 'react';
import FileUpload from './FileUpload';
import ResultDisplay from './ResultDisplay';
import './styles.css';

const App = () => {
  const [summary, setSummary] = useState('');

  return (
    <div className="app-container">
      <h1>Podcast Summarizer</h1>
      <FileUpload onResult={setSummary} />
      {summary && <ResultDisplay summary={summary} />}
    </div>
  );
};

export default App;
