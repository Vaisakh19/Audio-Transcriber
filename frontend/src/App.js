import React, { useState } from 'react';
import FileUpload from './FileUpload';
//import ResultDisplay from './ResultDisplay';
import './styles.css';

const App = () => {
  const [setSummary] = useState('');
  const [setTranscript] = useState('');
  //const [activeTab, setActiveTab] = useState('summary');

  return (
    <div className="app-container">

      {/* Upload component with callback */}
      <FileUpload
        onResult={(s, t) => {
          setSummary(s);
          setTranscript(t);
        }}
      />
    </div>
  );
};

export default App;
