import React, { useState, useEffect } from 'react';

interface Task {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  result_video_url?: string;
  error?: string;
}

const App: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [fileId, setFileId] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [textPrompt, setTextPrompt] = useState<string>('cat');
  const [task, setTask] = useState<Task | null>(null);
  const [error, setError] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1>Grounded SAM-2 Video Tracker</h1>
        <p>Upload a video, describe the object you want to track, and get an annotated video with object tracking</p>
      </header>

      <div style={{ marginBottom: '30px' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px' }}>
          {['Upload Video', 'Set Detection Prompt', 'Process Video', 'Download Result'].map((step, index) => (
            <div
              key={step}
              style={{
                padding: '10px 20px',
                margin: '0 10px',
                backgroundColor: index <= activeStep ? '#1976d2' : '#f5f5f5',
                color: index <= activeStep ? 'white' : 'black',
                borderRadius: '5px',
                fontSize: '14px'
              }}
            >
              {step}
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div style={{ 
          backgroundColor: '#ffebee', 
          color: '#c62828', 
          padding: '15px', 
          marginBottom: '20px',
          borderRadius: '5px',
          border: '1px solid #ffcdd2'
        }}>
          {error}
        </div>
      )}

      {/* Step 0: File Upload */}
      {activeStep === 0 && (
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              border: '2px dashed #ccc',
              borderRadius: '10px',
              padding: '60px 20px',
              marginBottom: '20px',
              cursor: 'pointer',
              transition: 'border-color 0.3s'
            }}
            onDragOver={(e) => {
              e.preventDefault();
              e.currentTarget.style.borderColor = '#1976d2';
            }}
            onDragLeave={(e) => {
              e.currentTarget.style.borderColor = '#ccc';
            }}
            onDrop={(e) => {
              e.preventDefault();
              e.currentTarget.style.borderColor = '#ccc';
              const files = e.dataTransfer.files;
              if (files.length > 0) {
                handleFileUpload(files[0]);
              }
            }}
            onClick={() => {
              const input = document.createElement('input');
              input.type = 'file';
              input.accept = 'video/*';
              input.onchange = (e) => {
                const file = (e.target as HTMLInputElement).files?.[0];
                if (file) handleFileUpload(file);
              };
              input.click();
            }}
          >
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>📁</div>
            <h3>Drop your video file here or click to browse</h3>
            <p>Supported formats: MP4, AVI, MOV, MKV, WEBM (Max: 100MB)</p>
          </div>
        </div>
      )}

      {/* Step 1: Prompt Input */}
      {activeStep === 1 && (
        <div>
          <div style={{ 
            backgroundColor: '#e8f5e8', 
            color: '#2e7d32', 
            padding: '15px', 
            marginBottom: '20px',
            borderRadius: '5px',
            border: '1px solid #c8e6c9'
          }}>
            Video "{fileName}" uploaded successfully!
          </div>
          
          <div style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h3>Describe the object you want to track:</h3>
            <input
              type="text"
              value={textPrompt}
              onChange={(e) => setTextPrompt(e.target.value)}
              placeholder="e.g., cat, person, car, dog"
              style={{
                width: '100%',
                padding: '15px',
                fontSize: '16px',
                border: '1px solid #ddd',
                borderRadius: '5px',
                marginBottom: '20px'
              }}
            />
            <button
              onClick={handleStartTracking}
              disabled={!textPrompt.trim() || isProcessing}
              style={{
                width: '100%',
                padding: '15px',
                fontSize: '16px',
                backgroundColor: '#1976d2',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
                opacity: (!textPrompt.trim() || isProcessing) ? 0.6 : 1
              }}
            >
              {isProcessing ? 'Starting...' : 'Start Tracking'}
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Processing */}
      {activeStep === 2 && (
        <div style={{ textAlign: 'center' }}>
          <h3>Processing Video...</h3>
          <div style={{ marginBottom: '20px' }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>⚙️</div>
            {task?.message && <p>{task.message}</p>}
            {task?.progress !== undefined && (
              <div style={{ width: '100%', maxWidth: '400px', margin: '0 auto' }}>
                <div style={{
                  width: '100%',
                  height: '20px',
                  backgroundColor: '#f0f0f0',
                  borderRadius: '10px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    height: '100%',
                    width: `${task.progress}%`,
                    backgroundColor: '#1976d2',
                    transition: 'width 0.3s ease'
                  }}></div>
                </div>
                <p>{Math.round(task.progress || 0)}% completed</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Step 3: Results */}
      {activeStep === 3 && task?.status === 'completed' && (
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            backgroundColor: '#e8f5e8', 
            color: '#2e7d32', 
            padding: '15px', 
            marginBottom: '20px',
            borderRadius: '5px',
            border: '1px solid #c8e6c9'
          }}>
            Video processing completed successfully!
          </div>

          <div style={{ marginBottom: '20px' }}>
            <video 
              controls 
              style={{ 
                width: '100%', 
                maxWidth: '800px', 
                height: 'auto',
                borderRadius: '10px'
              }}
            >
              <source src={`/api/download/${task.task_id}`} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <a
              href={`/api/download/${task.task_id}`}
              download={`tracked_video_${task.task_id}.mp4`}
              style={{
                display: 'inline-block',
                padding: '15px 30px',
                backgroundColor: '#1976d2',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '5px',
                marginRight: '10px'
              }}
            >
              Download Video
            </a>
            <button
              onClick={handleReset}
              style={{
                padding: '15px 30px',
                backgroundColor: '#666',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              Process Another Video
            </button>
          </div>
        </div>
      )}
    </div>
  );

  async function handleFileUpload(file: File) {
    try {
      setError('');
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setFileId(data.file_id);
      setFileName(data.filename || file.name);
      setActiveStep(1);
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    }
  }

  async function handleStartTracking() {
    if (!fileId || !textPrompt.trim()) {
      setError('Please upload a video and enter a detection prompt');
      return;
    }

    try {
      setError('');
      setIsProcessing(true);
      setActiveStep(2);

      const formData = new FormData();
      formData.append('file_id', fileId);
      formData.append('text_prompt', textPrompt);
      formData.append('prompt_type', 'box');
      formData.append('box_threshold', '0.35');
      formData.append('text_threshold', '0.25');

      const response = await fetch('/api/track', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTask({
        task_id: data.task_id,
        status: data.status,
      });

      // Start polling for updates
      pollTaskStatus(data.task_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start tracking');
      setIsProcessing(false);
      setActiveStep(1);
    }
  }

  async function pollTaskStatus(taskId: string) {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/status/${taskId}`);
        if (response.ok) {
          const updatedTask = await response.json();
          setTask(updatedTask);

          if (updatedTask.status === 'completed') {
            setActiveStep(3);
            setIsProcessing(false);
            clearInterval(pollInterval);
          } else if (updatedTask.status === 'failed') {
            setError(updatedTask.error || 'Processing failed');
            setIsProcessing(false);
            clearInterval(pollInterval);
          }
        }
      } catch (err) {
        console.error('Failed to fetch task status:', err);
      }
    }, 2000);

    // Clean up interval after 10 minutes
    setTimeout(() => clearInterval(pollInterval), 600000);
  }

  function handleReset() {
    setActiveStep(0);
    setFileId(null);
    setFileName('');
    setTextPrompt('cat');
    setTask(null);
    setError('');
    setIsProcessing(false);
  }
};

export default App;