import React, { useState } from 'react';
import '../src/App.css'; // Import the CSS file for styling

function FileUpload({onResult}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);  // new state for loader
  const [processingTime, setProcessingTime] = useState(0);

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

    setLoading(true); // show loader when request starts

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
      setProcessingTime(data.processing_time); // Get processing time from response
      onResult(data.summary, data.transcription);  // Send summary + transcription to App

    } catch (err) {
      console.error("Error uploading file:", err);
      alert("Upload failed. See console for details.");
    } finally {
      setLoading(false); // hide loader after everything finishes
    }
  };

  return (
    <div className="app-container">
      <h1>🎧 Podcast Summarizer</h1>
  
      <div className="file-upload-wrapper">
  <label htmlFor="file-upload" className="custom-file-upload">
    📁 Choose Audio File
  </label>
  <input
    id="file-upload"
    type="file"
    onChange={handleFileChange}
    accept=".mp3,.wav,.m4a"
  />
  {selectedFile && <span className="file-name">{selectedFile.name}</span>}
</div>


      <br />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Upload & Summarize"}
      </button>
  
      {loading && <div className="loader"></div>}
  
      {transcription && (
  <>
    <h2>Transcription:</h2>
    <pre className="text-box">{transcription}</pre>
  </>
)}
{summary && (
  <>
    <h2>Summary:</h2>
    <pre className="text-box">{summary}</pre>
  </>
)}

  
  {processingTime > 0 && (
  <>
    <h2>Processed in:</h2>
    <p>{processingTime}</p>
  </>
)}

  
      <footer>
        Made with ❤️ using React and FastAPI
      </footer>
    </div>
  );
  
  
}

export default FileUpload;
