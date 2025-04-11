import React from 'react';
import './styles.css';

const ResultDisplay = ({ summary }) => {
  return (
    <div className="result-box">
      <h2>Summary</h2>
      <p>{summary}</p>
    </div>
  );
};

export default ResultDisplay;
