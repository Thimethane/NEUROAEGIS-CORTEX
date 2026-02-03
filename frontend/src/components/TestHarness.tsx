/**
 * Test Harness Component
 * Interactive testing interface for development
 * Add to App.tsx with: import { TestHarness } from './components/TestHarness';
 */

import React, { useState } from 'react';
import { testConnection } from '../services/geminiService';
import { Play, CheckCircle, XCircle, Loader } from 'lucide-react';

export const TestHarness: React.FC = () => {
  const [tests, setTests] = useState({
    geminiConnection: { status: 'pending', message: '' },
    cameraAccess: { status: 'pending', message: '' },
    frameCapture: { status: 'pending', message: '' },
    analysis: { status: 'pending', message: '' }
  });

  const [running, setRunning] = useState(false);

  const runTest = async (testName: string, testFn: () => Promise<any>) => {
    setTests(prev => ({
      ...prev,
      [testName]: { status: 'running', message: 'Testing...' }
    }));

    try {
      const result = await testFn();
      setTests(prev => ({
        ...prev,
        [testName]: {
          status: 'success',
          message: result || 'Test passed'
        }
      }));
    } catch (error) {
      setTests(prev => ({
        ...prev,
        [testName]: {
          status: 'failed',
          message: String(error)
        }
      }));
    }
  };

  const runAllTests = async () => {
    setRunning(true);

    // Test 1: Gemini Connection
    await runTest('geminiConnection', async () => {
      const success = await testConnection();
      if (!success) throw new Error('Connection failed');
      return 'Connected successfully';
    });

    await new Promise(resolve => setTimeout(resolve, 500));

    // Test 2: Camera Access
    await runTest('cameraAccess', async () => {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true
      });
      stream.getTracks().forEach(track => track.stop());
      return 'Camera accessible';
    });

    await new Promise(resolve => setTimeout(resolve, 500));

    // Test 3: Frame Capture
    await runTest('frameCapture', async () => {
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true
      });
      
      video.srcObject = stream;
      await video.play();
      
      canvas.width = 640;
      canvas.height = 480;
      const ctx = canvas.getContext('2d');
      ctx?.drawImage(video, 0, 0, 640, 480);
      
      const base64 = canvas.toDataURL('image/jpeg');
      
      stream.getTracks().forEach(track => track.stop());
      
      if (!base64.startsWith('data:image/jpeg')) {
        throw new Error('Invalid frame format');
      }
      
      return `Frame captured (${(base64.length / 1024).toFixed(1)}KB)`;
    });

    setRunning(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'failed':
        return <XCircle className="text-red-500" size={20} />;
      case 'running':
        return <Loader className="text-blue-500 animate-spin" size={20} />;
      default:
        return <div className="w-5 h-5 border-2 border-gray-600 rounded-full" />;
    }
  };

  return (
    <div className="fixed bottom-4 right-4 bg-gray-900 border border-gray-700 rounded-lg p-4 shadow-2xl z-50 w-96">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-bold">System Tests</h3>
        <button
          onClick={runAllTests}
          disabled={running}
          className="flex items-center gap-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded text-sm"
        >
          <Play size={14} />
          {running ? 'Running...' : 'Run All'}
        </button>
      </div>

      <div className="space-y-3">
        {Object.entries(tests).map(([name, test]) => (
          <div
            key={name}
            className="flex items-start gap-3 p-2 bg-gray-800 rounded"
          >
            {getStatusIcon(test.status)}
            <div className="flex-1 min-w-0">
              <div className="text-white text-sm font-medium">
                {name.replace(/([A-Z])/g, ' $1').trim()}
              </div>
              <div className="text-gray-400 text-xs truncate">
                {test.message || 'Not run'}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-700">
        <div className="text-xs text-gray-500">
          Press F12 to view detailed logs
        </div>
      </div>
    </div>
  );
};
