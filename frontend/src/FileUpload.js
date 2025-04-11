import React, { useState } from 'react';

function FileUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [summary, setSummary] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile); // 'file' must match FastAPI's param name

    try {
      const response = await fetch("http://localhost:5000/transcribe", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText);
      }

      const data = await response.json();
      setTranscription(data.transcription);
      setSummary(data.summary);
    } catch (err) {
      console.error("Error uploading file:", err);
      alert("Upload failed. See console for details.");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <input type="file" onChange={handleFileChange} accept=".mp3,.wav,.m4a" />
      <br /><br />
      <button onClick={handleUpload}>Upload & Summarize</button>
      <br /><br />
      {transcription && (
        <>
          <h2>Transcription:</h2>
          <p>{transcription}</p>
        </>
      )}
      {summary && (
        <>
          <h2>Summary:</h2>
          <p>{summary}</p>
        </>
      )}
    </div>
  );
}

export default FileUpload;
