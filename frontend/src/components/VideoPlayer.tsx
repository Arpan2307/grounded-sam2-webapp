import React, { useEffect, useRef } from 'react';

interface VideoPlayerProps {
    videoSrc: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoSrc }) => {
    const videoRef = useRef<HTMLVideoElement | null>(null);

    useEffect(() => {
        if (videoRef.current) {
            videoRef.current.load();
        }
    }, [videoSrc]);

    return (
        <div>
            <video ref={videoRef} controls width="600">
                <source src={videoSrc} type="video/mp4" />
                Your browser does not support the video tag.
            </video>
        </div>
    );
};

export default VideoPlayer;