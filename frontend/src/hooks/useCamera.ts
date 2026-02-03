/**
 * useCamera Hook
 * Manages webcam access and frame capture
 */

import { useRef, useEffect, useState, useCallback } from 'react';

interface UseCameraOptions {
  onFrameCapture?: (base64: string) => void;
  captureInterval?: number;
  isActive?: boolean;
}

interface UseCameraReturn {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  error: string | null;
  streamActive: boolean;
  captureFrame: () => string | null;
  restartCamera: () => Promise<void>;
}

export const useCamera = ({
  onFrameCapture,
  captureInterval = 4000,
  isActive = false
}: UseCameraOptions = {}): UseCameraReturn => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  
  const [error, setError] = useState<string | null>(null);
  const [streamActive, setStreamActive] = useState(false);

  const captureFrame = useCallback((): string | null => {
    if (!videoRef.current || !canvasRef.current) return null;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (!ctx || video.readyState !== 4) return null;

    try {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      return canvas.toDataURL('image/jpeg', 0.8);
    } catch (err) {
      console.error('Frame capture error:', err);
      return null;
    }
  }, []);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setStreamActive(true);
        setError(null);
      }
    } catch (err) {
      console.error('Camera access error:', err);
      setError('Could not access camera. Ensure permissions are granted.');
      setStreamActive(false);
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
      setStreamActive(false);
    }
  }, []);

  const restartCamera = useCallback(async () => {
    stopCamera();
    await startCamera();
  }, [startCamera, stopCamera]);

  // Initialize camera on mount
  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, [startCamera, stopCamera]);

  // Auto-capture frames when active
  useEffect(() => {
    if (!isActive || !streamActive || !onFrameCapture) return;

    const intervalId = window.setInterval(() => {
      const frame = captureFrame();
      if (frame) {
        onFrameCapture(frame);
      }
    }, captureInterval);

    return () => window.clearInterval(intervalId);
  }, [isActive, streamActive, onFrameCapture, captureInterval, captureFrame]);

  return {
    videoRef,
    canvasRef,
    error,
    streamActive,
    captureFrame,
    restartCamera
  };
};
