/**
 * Analysis Progress Hook
 * Manages fake progress simulation for analysis screen
 * 
 * Phase 2.3: Realistic progress timing with background completion polling
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysisStatus } from '@/hooks/useApi';

export type AnalysisPhase = 'collections' | 'summary' | 'complete';

export interface AnalysisProgressState {
  progress: number;
  phase: AnalysisPhase;
  currentCollection: number;
  isComplete: boolean;
  statusMessage: string;
}

export const useAnalysisProgress = (
  projectId: string,
  collectionCount: number,
  generateSummary: boolean
): AnalysisProgressState => {
  const navigate = useNavigate();
  
  // Progress state
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState<AnalysisPhase>('collections');
  const [currentCollection, setCurrentCollection] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  
  // Background polling to check for actual completion
  const { data: analysisStatus } = useAnalysisStatus(projectId, true);
  
  // Generate status message based on current state
  const getStatusMessage = useCallback((currentPhase: AnalysisPhase, collectionNum: number): string => {
    switch (currentPhase) {
      case 'collections':
        return `Analyzing Reddit discussions in collection ${collectionNum}...`;
      case 'summary':
        return 'Generating AI-powered insights and summary...';
      case 'complete':
        return 'Analysis complete! Preparing your results...';
      default:
        return 'Starting analysis...';
    }
  }, []);
  
  const statusMessage = getStatusMessage(phase, currentCollection);
  
  // Main progress simulation effect
  useEffect(() => {
    let timeouts: NodeJS.Timeout[] = [];
    
    // Ensure we have valid collection count
    const validCollectionCount = Math.max(1, collectionCount);
    
    if (generateSummary) {
      // WITH SUMMARY: Phase 1 (0% → 80%) + Phase 2 (80% → 98%)
      
      // Phase 1: Collection analysis (fast progression to 80%)
      const collectionStep = 80 / validCollectionCount;
      
      for (let i = 0; i < validCollectionCount; i++) {
        const timeout = setTimeout(() => {
          const newProgress = (i + 1) * collectionStep;
          setProgress(newProgress);
          setCurrentCollection(i + 1);
          
          // Switch to summary phase after last collection
          if (i === validCollectionCount - 1) {
            setPhase('summary');
          }
        }, i * 150); // 0.15 seconds per collection
        
        timeouts.push(timeout);
      }
      
      // Phase 2: Summary generation (slow progression 80% → 98%)
      const summaryStartTime = validCollectionCount * 150;
      
      for (let i = 81; i <= 98; i++) {
        const timeout = setTimeout(() => {
          setProgress(i);
        }, summaryStartTime + (i - 80) * 1300); // 1 second per percent
        
        timeouts.push(timeout);
      }
      
    } else {
      // WITHOUT SUMMARY: Stop at (n-1)/n collections
      
      const collectionStep = 100 / validCollectionCount;
      const maxCollections = Math.max(1, validCollectionCount - 1);
      
      for (let i = 0; i < maxCollections; i++) {
        const timeout = setTimeout(() => {
          const newProgress = (i + 1) * collectionStep;
          setProgress(newProgress);
          setCurrentCollection(i + 1);
        }, i * 150); // 0.15 seconds per collection
        
        timeouts.push(timeout);
      }
      
      // For single collection case, still show some progression
      if (validCollectionCount === 1) {
        const timeout = setTimeout(() => {
          setProgress(90); // Stop at 90% for single collection
          setCurrentCollection(1);
        }, 150);
        timeouts.push(timeout);
      }
    }
    
    // Cleanup function
    return () => {
      timeouts.forEach(timeout => clearTimeout(timeout));
    };
  }, [collectionCount, generateSummary]);
  
  // Handle actual analysis completion
  useEffect(() => {
    if (analysisStatus?.status === 'completed') {
      // Jump to 100% and mark as complete
      setProgress(100);
      setPhase('complete');
      setIsComplete(true);
      
      // Redirect to project workspace after a brief delay
      const redirectTimeout = setTimeout(() => {
        navigate(`/project/${projectId}`);
      }, 1500); // 1.5 second delay to show completion
      
      return () => clearTimeout(redirectTimeout);
    }
  }, [analysisStatus?.status, projectId, navigate]);
  
  // Handle analysis failure
  useEffect(() => {
    if (analysisStatus?.status === 'failed') {
      // On failure, navigate to project page to show error state
      navigate(`/project/${projectId}`);
    }
  }, [analysisStatus?.status, projectId, navigate]);
  
  return {
    progress,
    phase,
    currentCollection,
    isComplete,
    statusMessage,
  };
};