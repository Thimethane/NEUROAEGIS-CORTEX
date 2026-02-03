/**
 * Evidence Manager Component
 * Handles upload and download of evidence files
 * All processing happens on frontend before backend interaction
 */

import React, { useState, useRef } from 'react';
import { 
  X, Upload, Download, FileImage, File, CheckCircle, 
  AlertCircle, Loader, Trash2, Eye 
} from 'lucide-react';
import type { SecurityEvent } from '../types';

interface EvidenceManagerProps {
  mode: 'upload' | 'download' | null;
  onClose: () => void;
  onUpload: (files: ProcessedFile[]) => Promise<void>;
  onDownload: (incidentIds: string[]) => void;
  incidents: SecurityEvent[];
}

interface ProcessedFile {
  id: string;
  name: string;
  type: string;
  size: number;
  data: string; // base64
  thumbnail?: string;
  timestamp: number;
  processed: boolean;
}

export const EvidenceManager: React.FC<EvidenceManagerProps> = ({
  mode,
  onClose,
  onUpload,
  onDownload,
  incidents
}) => {
  const [files, setFiles] = useState<ProcessedFile[]>([]);
  const [selectedIncidents, setSelectedIncidents] = useState<Set<string>>(new Set());
  const [processing, setProcessing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  /**
   * Process uploaded files on frontend
   * Clean and prepare data before sending to backend
   */
  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files;
    if (!selectedFiles || selectedFiles.length === 0) return;

    setProcessing(true);
    const processedFiles: ProcessedFile[] = [];

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      
      try {
        // Process each file
        const processed = await processFile(file);
        processedFiles.push(processed);
      } catch (error) {
        console.error(`Failed to process ${file.name}:`, error);
      }
    }

    setFiles(prev => [...prev, ...processedFiles]);
    setProcessing(false);
    
    // Clear input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /**
   * Process individual file
   * Convert to base64, generate thumbnail, validate
   */
  const processFile = (file: File): Promise<ProcessedFile> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = async (e) => {
        try {
          const data = e.target?.result as string;
          
          // Clean base64 data
          const cleanData = data.includes(',') ? data.split(',')[1] : data;
          
          // Generate thumbnail for images
          let thumbnail: string | undefined;
          if (file.type.startsWith('image/')) {
            thumbnail = await generateThumbnail(data);
          }

          // Validate file size (max 10MB)
          if (file.size > 10 * 1024 * 1024) {
            reject(new Error('File too large (max 10MB)'));
            return;
          }

          resolve({
            id: `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            name: file.name,
            type: file.type,
            size: file.size,
            data: cleanData,
            thumbnail,
            timestamp: Date.now(),
            processed: true
          });
        } catch (error) {
          reject(error);
        }
      };

      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsDataURL(file);
    });
  };

  /**
   * Generate thumbnail for images
   */
  const generateThumbnail = (dataUrl: string): Promise<string> => {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Thumbnail size
        const maxWidth = 100;
        const maxHeight = 100;
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > maxWidth) {
            height *= maxWidth / width;
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width *= maxHeight / height;
            height = maxHeight;
          }
        }

        canvas.width = width;
        canvas.height = height;
        ctx?.drawImage(img, 0, 0, width, height);
        
        resolve(canvas.toDataURL('image/jpeg', 0.7));
      };
      img.src = dataUrl;
    });
  };

  /**
   * Handle upload to backend
   */
  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploadStatus('uploading');
    try {
      await onUpload(files);
      setUploadStatus('success');
      setTimeout(() => {
        setUploadStatus('idle');
        setFiles([]);
        onClose();
      }, 2000);
    } catch (error) {
      setUploadStatus('error');
      setTimeout(() => setUploadStatus('idle'), 3000);
    }
  };

  /**
   * Handle download from frontend storage
   */
  const handleDownload = () => {
    if (selectedIncidents.size === 0) {
      alert('Please select incidents to download');
      return;
    }

    onDownload(Array.from(selectedIncidents));
    onClose();
  };

  /**
   * Toggle incident selection
   */
  const toggleIncident = (incidentId: string) => {
    setSelectedIncidents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(incidentId)) {
        newSet.delete(incidentId);
      } else {
        newSet.add(incidentId);
      }
      return newSet;
    });
  };

  /**
   * Remove file from upload queue
   */
  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  /**
   * Format file size
   */
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-aegis-panel border border-slate-700 rounded-lg w-full max-w-4xl max-h-[80vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          <div className="flex items-center gap-3">
            {mode === 'upload' ? (
              <Upload className="text-blue-400" size={24} />
            ) : (
              <Download className="text-green-400" size={24} />
            )}
            <div>
              <h2 className="text-lg font-bold text-white">
                {mode === 'upload' ? 'Upload Evidence' : 'Download Evidence'}
              </h2>
              <p className="text-xs text-slate-400">
                {mode === 'upload' 
                  ? 'Add images, documents, or other evidence files'
                  : 'Select incidents to download evidence'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-800 rounded transition-colors"
          >
            <X className="text-slate-400" size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {mode === 'upload' ? (
            <UploadContent
              files={files}
              processing={processing}
              uploadStatus={uploadStatus}
              fileInputRef={fileInputRef}
              onFileSelect={handleFileSelect}
              onRemoveFile={removeFile}
              formatFileSize={formatFileSize}
            />
          ) : (
            <DownloadContent
              incidents={incidents}
              selectedIncidents={selectedIncidents}
              onToggleIncident={toggleIncident}
            />
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-700 flex justify-between items-center">
          <div className="text-sm text-slate-400">
            {mode === 'upload' 
              ? `${files.length} file(s) ready to upload`
              : `${selectedIncidents.size} incident(s) selected`
            }
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={mode === 'upload' ? handleUpload : handleDownload}
              disabled={
                (mode === 'upload' && (files.length === 0 || uploadStatus === 'uploading')) ||
                (mode === 'download' && selectedIncidents.size === 0)
              }
              className={`px-4 py-2 rounded transition-colors font-medium ${
                mode === 'upload'
                  ? 'bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700'
                  : 'bg-green-600 hover:bg-green-700 disabled:bg-slate-700'
              } text-white disabled:cursor-not-allowed`}
            >
              {uploadStatus === 'uploading' ? (
                <span className="flex items-center gap-2">
                  <Loader className="animate-spin" size={16} />
                  Uploading...
                </span>
              ) : uploadStatus === 'success' ? (
                <span className="flex items-center gap-2">
                  <CheckCircle size={16} />
                  Success!
                </span>
              ) : uploadStatus === 'error' ? (
                <span className="flex items-center gap-2">
                  <AlertCircle size={16} />
                  Failed
                </span>
              ) : (
                mode === 'upload' ? 'Upload Files' : 'Download Selected'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Upload Content Component
 */
const UploadContent: React.FC<{
  files: ProcessedFile[];
  processing: boolean;
  uploadStatus: string;
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onRemoveFile: (id: string) => void;
  formatFileSize: (bytes: number) => string;
}> = ({ files, processing, uploadStatus, fileInputRef, onFileSelect, onRemoveFile, formatFileSize }) => (
  <div className="space-y-4">
    {/* Drop Zone */}
    <div
      className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer"
      onClick={() => fileInputRef.current?.click()}
    >
      <Upload className="mx-auto text-slate-500 mb-3" size={48} />
      <p className="text-slate-300 mb-2">
        Click to upload or drag and drop
      </p>
      <p className="text-sm text-slate-500">
        Images, PDFs, or documents (max 10MB each)
      </p>
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,.pdf,.doc,.docx,.txt"
        onChange={onFileSelect}
        className="hidden"
      />
    </div>

    {/* Processing Indicator */}
    {processing && (
      <div className="flex items-center justify-center gap-2 text-blue-400">
        <Loader className="animate-spin" size={20} />
        <span>Processing files...</span>
      </div>
    )}

    {/* Files List */}
    {files.length > 0 && (
      <div className="space-y-2">
        <h3 className="text-sm font-medium text-slate-400">Files to Upload:</h3>
        {files.map(file => (
          <div
            key={file.id}
            className="flex items-center gap-3 p-3 bg-slate-800 rounded border border-slate-700"
          >
            {file.thumbnail ? (
              <img
                src={file.thumbnail}
                alt={file.name}
                className="w-12 h-12 object-cover rounded"
              />
            ) : (
              <div className="w-12 h-12 bg-slate-700 rounded flex items-center justify-center">
                <File size={24} className="text-slate-500" />
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white truncate">{file.name}</p>
              <p className="text-xs text-slate-500">
                {formatFileSize(file.size)} • {file.type}
              </p>
            </div>
            <CheckCircle className="text-green-500" size={20} />
            <button
              onClick={() => onRemoveFile(file.id)}
              className="p-1 hover:bg-slate-700 rounded transition-colors"
            >
              <Trash2 className="text-red-400" size={16} />
            </button>
          </div>
        ))}
      </div>
    )}
  </div>
);

/**
 * Download Content Component
 */
const DownloadContent: React.FC<{
  incidents: SecurityEvent[];
  selectedIncidents: Set<string>;
  onToggleIncident: (id: string) => void;
}> = ({ incidents, selectedIncidents, onToggleIncident }) => (
  <div className="space-y-2">
    {incidents.length === 0 ? (
      <div className="text-center py-12 text-slate-500">
        <FileImage size={48} className="mx-auto mb-3 opacity-50" />
        <p>No incidents with evidence available</p>
      </div>
    ) : (
      <>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-slate-400">
            Available Incidents ({incidents.length}):
          </h3>
          <button
            onClick={() => {
              if (selectedIncidents.size === incidents.length) {
                incidents.forEach(i => onToggleIncident(i.id));
              } else {
                incidents.forEach(i => {
                  if (!selectedIncidents.has(i.id)) {
                    onToggleIncident(i.id);
                  }
                });
              }
            }}
            className="text-xs text-blue-400 hover:text-blue-300"
          >
            {selectedIncidents.size === incidents.length ? 'Deselect All' : 'Select All'}
          </button>
        </div>
        {incidents.map(incident => (
          <div
            key={incident.id}
            onClick={() => onToggleIncident(incident.id)}
            className={`p-3 rounded border cursor-pointer transition-all ${
              selectedIncidents.has(incident.id)
                ? 'bg-blue-900/30 border-blue-500'
                : 'bg-slate-800 border-slate-700 hover:border-slate-600'
            }`}
          >
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={selectedIncidents.has(incident.id)}
                onChange={() => {}}
                className="w-4 h-4"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-sm font-medium ${
                    incident.severity === 'high' ? 'text-red-400' :
                    incident.severity === 'medium' ? 'text-orange-400' :
                    'text-blue-400'
                  }`}>
                    {incident.type.toUpperCase()}
                  </span>
                  <span className="text-xs text-slate-500">
                    {new Date(incident.timestamp).toLocaleString()}
                  </span>
                </div>
                <p className="text-xs text-slate-400 line-clamp-2">
                  {incident.reasoning}
                </p>
              </div>
              {incident.snapshot && (
                <Eye className="text-slate-500" size={16} />
              )}
            </div>
          </div>
        ))}
      </>
    )}
  </div>
);
