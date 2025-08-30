import React, { useState } from 'react';

const PromptInput: React.FC<{ onSubmit: (prompt: string) => void }> = ({ onSubmit }) => {
    const [prompt, setPrompt] = useState('');

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        if (prompt.trim()) {
            onSubmit(prompt);
            setPrompt('');
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <label htmlFor="prompt">Enter your text prompt:</label>
            <input
                type="text"
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                required
            />
            <button type="submit">Submit</button>
        </form>
    );
};

export default PromptInput;