/**
 * useEvidence Hook
 * Manages evidence upload/download functionality
 * Handles frontend storage and backend integration
 */

import { useState, useEffect, useCallback } from 'react';
import { STORAGE_KEYS, FEATURES } from '../constants';

interface ProcessedFile {
  id: string;
  name: string;
  type: string;
  size: number;
  data: string;
  thumbnail?: string;
  timestamp: number;
  processed: boolean;
}

interface EvidenceStore {
  files: ProcessedFile[];
  incidents: {
    [incidentId: string]: {
      files: string[]; // file IDs
      timestamp: number;
    };
  };
}

export const useEvidence = () => {
  const [showEvidencePanel, setShowEvidencePanel] = useState<'upload' | 'download' | null>(null);
  const [evidenceStore, setEvidenceStore] = useState<EvidenceStore>({
    files: [],
    incidents: {}
  });

  /**
   * Load evidence from localStorage on mount
   */
  useEffect(() => {
    if (FEATURES.ENABLE_PERSISTENCE) {
      try {
        const stored = localStorage.getItem('aegisai_evidence_v3');
        if (stored) {
          setEvidenceStore(JSON.parse(stored));
        }
      } catch (error) {
        console.error('Failed to load evidence store:', error);
      }
    }
  }, []);

  /**
   * Save evidence to localStorage
   */
  const saveEvidenceStore = useCallback((store: EvidenceStore) => {
    if (FEATURES.ENABLE_PERSISTENCE) {
      try {
        localStorage.setItem(
          'aegisai_evidence_v3',
          JSON.stringify(store)
        );
        setEvidenceStore(store);
      } catch (error) {
        console.error('Failed to save evidence store:', error);
      }
    }
  }, []);

  /**
   * Toggle evidence panel
   */
  const toggleEvidencePanel = useCallback((mode: 'upload' | 'download' | null) => {
    setShowEvidencePanel(mode);
  }, []);

  /**
   * Upload evidence files
   * Process and store on frontend, optionally sync with backend
   */
  const uploadEvidence = useCallback(async (files: ProcessedFile[]) => {
    const newStore = { ...evidenceStore };
    
    // Add files to store
    newStore.files = [...newStore.files, ...files];
    
    // Save to frontend storage
    saveEvidenceStore(newStore);

    // If backend is enabled, send metadata (not full files)
    if (FEATURES.ENABLE_BACKEND_API) {
      try {
        const metadata = files.map(f => ({
          id: f.id,
          name: f.name,
          type: f.type,
          size: f.size,
          timestamp: f.timestamp
        }));

        // Send metadata to backend
        await fetch('/api/evidence/metadata', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ files: metadata })
        });
        
        console.log('Evidence metadata synced with backend');
      } catch (error) {
        console.warn('Failed to sync evidence metadata with backend:', error);
        // Continue anyway - frontend storage is primary
      }
    }

    console.log(`✅ Uploaded ${files.length} evidence file(s)`);
  }, [evidenceStore, saveEvidenceStore]);

  /**
   * Associate evidence with incident
   */
  const linkEvidenceToIncident = useCallback((incidentId: string, fileIds: string[]) => {
    const newStore = { ...evidenceStore };
    
    newStore.incidents[incidentId] = {
      files: fileIds,
      timestamp: Date.now()
    };
    
    saveEvidenceStore(newStore);
  }, [evidenceStore, saveEvidenceStore]);

  /**
   * Download evidence for selected incidents
   */
  const downloadEvidence = useCallback((incidentIds: string[]) => {
    const filesToDownload: ProcessedFile[] = [];

    // Collect all files for selected incidents
    incidentIds.forEach(incidentId => {
      const incident = evidenceStore.incidents[incidentId];
      if (incident) {
        incident.files.forEach(fileId => {
          const file = evidenceStore.files.find(f => f.id === fileId);
          if (file) {
            filesToDownload.push(file);
          }
        });
      }
    });

    // Download each file
    filesToDownload.forEach(file => {
      const link = document.createElement('a');
      link.href = `data:${file.type};base64,${file.data}`;
      link.download = file.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });

    console.log(`✅ Downloaded ${filesToDownload.length} evidence file(s)`);
  }, [evidenceStore]);

  /**
   * Store frame snapshot as evidence
   */
  const saveFrameSnapshot = useCallback((base64Image: string, incidentId: string) => {
    const file: ProcessedFile = {
      id: `snapshot_${incidentId}_${Date.now()}`,
      name: `incident_${incidentId}_snapshot.jpg`,
      type: 'image/jpeg',
      size: base64Image.length,
      data: base64Image.includes(',') ? base64Image.split(',')[1] : base64Image,
      timestamp: Date.now(),
      processed: true
    };

    const newStore = { ...evidenceStore };
    newStore.files.push(file);
    
    // Link to incident
    if (!newStore.incidents[incidentId]) {
      newStore.incidents[incidentId] = { files: [], timestamp: Date.now() };
    }
    newStore.incidents[incidentId].files.push(file.id);

    saveEvidenceStore(newStore);
    
    console.log(`✅ Saved snapshot for incident ${incidentId}`);
  }, [evidenceStore, saveEvidenceStore]);

  /**
   * Get evidence count
   */
  const evidenceCount = evidenceStore.files.length;

  /**
   * Get incidents with evidence
   */
  const getIncidentsWithEvidence = useCallback(() => {
    return Object.keys(evidenceStore.incidents).filter(
      id => evidenceStore.incidents[id].files.length > 0
    );
  }, [evidenceStore]);

  /**
   * Clear old evidence (older than 30 days)
   */
  const cleanupOldEvidence = useCallback(() => {
    const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
    const newStore = { ...evidenceStore };
    
    // Remove old files
    newStore.files = newStore.files.filter(f => f.timestamp > thirtyDaysAgo);
    
    // Remove old incident associations
    Object.keys(newStore.incidents).forEach(id => {
      if (newStore.incidents[id].timestamp < thirtyDaysAgo) {
        delete newStore.incidents[id];
      }
    });

    saveEvidenceStore(newStore);
    console.log('🧹 Cleaned up old evidence');
  }, [evidenceStore, saveEvidenceStore]);

  /**
   * Export evidence store as JSON
   */
  const exportEvidenceStore = useCallback(() => {
    const dataStr = JSON.stringify(evidenceStore, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `aegisai_evidence_${new Date().toISOString()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    console.log('✅ Exported evidence store');
  }, [evidenceStore]);

  return {
    showEvidencePanel,
    toggleEvidencePanel,
    uploadEvidence,
    downloadEvidence,
    saveFrameSnapshot,
    linkEvidenceToIncident,
    evidenceCount,
    getIncidentsWithEvidence,
    cleanupOldEvidence,
    exportEvidenceStore
  };
};
