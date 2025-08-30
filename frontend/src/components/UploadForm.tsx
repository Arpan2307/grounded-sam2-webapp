import React, { useState } from 'react';

const UploadForm = () => {
    const [videoFile, setVideoFile] = useState(null);
    const [textPrompt, setTextPrompt] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [outputVideoUrl, setOutputVideoUrl] = useState('');

    const handleFileChange = (event) => {
        setVideoFile(event.target.files[0]);
    };

    const handlePromptChange = (event) => {
        setTextPrompt(event.target.value);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!videoFile || !textPrompt) {
            alert('Please upload a video file and enter a text prompt.');
            return;
        }

        setIsLoading(true);
        const formData = new FormData();
        formData.append('video', videoFile);
        formData.append('prompt', textPrompt);

        try {
            const response = await fetch('/api/tracking', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Failed to process video');
            }

            const data = await response.json();
            setOutputVideoUrl(data.outputVideoUrl);
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while processing the video.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <h2>Upload Video for Object Detection</h2>
            <form onSubmit={handleSubmit}>
                <input type="file" accept="video/*" onChange={handleFileChange} required />
                <input type="text" placeholder="Enter text prompt" value={textPrompt} onChange={handlePromptChange} required />
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Processing...' : 'Submit'}
                </button>
            </form>
            {outputVideoUrl && (
                <div>
                    <h3>Processed Video:</h3>
                    <video controls>
                        <source src={outputVideoUrl} type="video/mp4" />
                        Your browser does not support the video tag.
                    </video>
                </div>
            )}
        </div>
    );
};

export default UploadForm;