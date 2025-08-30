import React from 'react';

const ProgressBar: React.FC<{ progress: number }> = ({ progress }) => {
    return (
        <div style={{ width: '100%', backgroundColor: '#e0e0df', borderRadius: '5px', overflow: 'hidden' }}>
            <div
                style={{
                    height: '10px',
                    width: `${progress}%`,
                    backgroundColor: progress < 100 ? '#3b5998' : '#4caf50',
                    transition: 'width 0.5s ease-in-out',
                }}
            />
        </div>
    );
};

export default ProgressBar;