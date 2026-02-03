/**
 * VideoFeed Component - Fixed Responsive Layout
 * Maintains consistent size regardless of log expansion
 */

import React, { useRef, useEffect, useState } from 'react';
import { Camera } from 'lucide-react';

interface VideoFeedProps {
  onFrameCapture: (base64: string) => void;
  isMonitoring: boolean;
}

export const VideoFeed: React.FC<VideoFeedProps> = ({ onFrameCapture, isMonitoring }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const [error, setError] = useState<string | null>(null);
  const [streamActive, setStreamActive] = useState(false);

  /* ------------------- Camera Setup ------------------- */
  useEffect(() => {
    let stream: MediaStream | null = null;

    const startCamera = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            facingMode: 'user', 
            width: { ideal: 1280 }, 
            height: { ideal: 720 } 
          }
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setStreamActive(true);
          setError(null);
        }
      } catch (err) {
        console.error("Camera error:", err);
        setError("Could not access camera. Ensure permissions are granted.");
        setStreamActive(false);
      }
    };

    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  /* ------------------- Frame Capture ------------------- */
  useEffect(() => {
    if (!isMonitoring || !streamActive) return;

    const intervalId = window.setInterval(() => {
      if (videoRef.current && canvasRef.current) {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        if (ctx && video.readyState === 4) {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          
          try {
            const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
            onFrameCapture(dataUrl);
          } catch (err) {
            console.error('Frame capture error:', err);
          }
        }
      }
    }, 4000);

    return () => window.clearInterval(intervalId);
  }, [isMonitoring, streamActive, onFrameCapture]);

  /* ------------------- Render ------------------- */
  return (
    <div 
      ref={containerRef}
      className="relative w-full h-full bg-black rounded-lg overflow-hidden border border-slate-700 shadow-2xl"
      style={{
        // Fixed aspect ratio to prevent resizing
        aspectRatio: '16/9',
        maxHeight: '100%'
      }}
    >
      {error ? (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-red-500 font-mono text-xs sm:text-sm p-4 text-center">
          <Camera className="mb-2 w-8 h-8 sm:w-12 sm:h-12" />
          <span className="font-bold tracking-widest">{error}</span>
        </div>
      ) : (
        <>
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            muted 
            className="absolute inset-0 w-full h-full object-cover opacity-80 grayscale-[10%]"
          />
          <canvas ref={canvasRef} className="hidden" />

          {/* ---------------- HUD Overlay ---------------- */}
          <div className="absolute inset-0 pointer-events-none">

            {/* Corner Brackets */}
            <div className="absolute top-2 left-2 w-6 h-6 sm:w-8 sm:h-8 border-t-2 border-l-2 border-purple-400 opacity-50" />
            <div className="absolute top-2 right-2 w-6 h-6 sm:w-8 sm:h-8 border-t-2 border-r-2 border-purple-400 opacity-50" />
            <div className="absolute bottom-2 left-2 w-6 h-6 sm:w-8 sm:h-8 border-b-2 border-l-2 border-purple-400 opacity-50" />
            <div className="absolute bottom-2 right-2 w-6 h-6 sm:w-8 sm:h-8 border-b-2 border-r-2 border-purple-400 opacity-50" />

            {/* Center Reticle */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
              <div className={`w-8 h-8 sm:w-12 sm:h-12 border border-purple-400 rounded-full flex items-center justify-center transition-all duration-300 ${
                isMonitoring ? 'scale-100 opacity-80' : 'scale-50 opacity-20'
              }`}>
                <div className="w-1 h-1 bg-red-500 rounded-full animate-pulse"></div>
              </div>
            </div>

            {/* Scan Line */}
            {isMonitoring && (
              <div 
                className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-400/10 to-transparent"
                style={{
                  animation: 'scan 3s linear infinite'
                }}
              />
            )}

            {/* Status Indicators */}
            <div className="absolute top-2 left-10 sm:left-12 bg-black/50 backdrop-blur px-2 py-1 rounded border border-gray-700">
              <div className="flex items-center gap-1.5 sm:gap-2">
                <div className={`w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full ${
                  isMonitoring ? 'bg-red-500 animate-pulse' : 'bg-gray-500'
                }`} />
                <span className="font-mono text-[10px] sm:text-xs text-white tracking-widest uppercase">
                  {isMonitoring ? 'CORTEX // ACTIVE' : 'CORTEX // STANDBY'}
                </span>
              </div>
            </div>

            <div className="absolute bottom-2 right-10 sm:right-12 font-mono text-[10px] sm:text-xs text-purple-400 opacity-70">
              CAM_01 // 720p // 30FPS
            </div>

          </div>
        </>
      )}

      {/* Custom scan animation */}
      <style>{`
        @keyframes scan {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(100%); }
        }
      `}</style>
    </div>
  );
};
