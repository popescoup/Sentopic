/**
 * Analysis Progress Page
 * Shows realistic progress simulation during project analysis
 * 
 * Phase 2.3: Analysis progress screen with fake progress bar
 */

import React from 'react';
import { useParams, Navigate, useLocation } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import Card from '@/components/ui/Card';
import { useAnalysisProgress } from '@/hooks/useAnalysisProgress';
import { useProject } from '@/hooks/useApi';

const AnalysisProgress: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const location = useLocation();
  
  // Redirect if no project ID
  if (!projectId) {
    return <Navigate to="/" replace />;
  }

  // Try to get project data from navigation state first
  const projectFromState = location.state?.projectData;
  const collectionCountFromState = location.state?.collectionCount;
  const generateSummaryFromState = location.state?.generateSummary;
  
  // Fallback to API call only if we don't have state data
  const { data: projectFromAPI, isLoading: projectLoading, error: projectError } = useProject(projectId, {
    enabled: !projectFromState // Only fetch if we don't have state data
  });
  
  // Use state data if available, otherwise use API data
  const project = projectFromState || projectFromAPI;
  const collectionCount = collectionCountFromState || project?.collections_metadata?.length || 1;
  const generateSummary = generateSummaryFromState ?? false;
  
  // Use progress hook with project-specific parameters
  const {
    progress,
    phase,
    currentCollection,
    isComplete,
    statusMessage
  } = useAnalysisProgress(
    projectId,
    collectionCount,
    generateSummary
  );

  // Only show loading if we're waiting for API and have no state data
  if (!projectFromState && projectLoading) {
    return (
      <MainLayout title="Starting Analysis...">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-accent mb-4"></div>
            <p className="font-body text-text-secondary">Loading project details...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Handle project error
  if (projectError || !project) {
    return (
      <MainLayout title="Analysis Error">
        <div className="max-w-2xl mx-auto mt-12">
          <Card className="border-danger bg-red-50">
            <div className="text-center py-8">
              <div className="mb-4">
                <svg className="h-12 w-12 text-danger mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="font-section-header text-danger mb-2">
                Unable to Start Analysis
              </h2>
              <p className="font-body text-text-secondary mb-6">
                There was an error loading the project details. Please try again.
              </p>
              <a
                href="/"
                className="inline-flex items-center px-4 py-2 bg-accent text-white rounded-default hover:bg-blue-700 transition-colors duration-150"
              >
                ← Return to Dashboard
              </a>
            </div>
          </Card>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout title="Analyzing Project">
      <div className="max-w-2xl mx-auto mt-12">
        {/* Progress Card */}
        <Card className="mb-6">
          <div className="text-center py-8">
            {/* Project Info */}
            <div className="mb-8">
              <h1 className="font-section-header text-text-primary mb-2">
                Analyzing "{project.name}"
              </h1>
              <p className="font-body text-text-secondary">
                Please wait while we analyze your Reddit data...
              </p>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="font-body text-text-secondary text-sm">Progress</span>
                <span className="font-technical text-text-primary text-sm">{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-border-secondary rounded-full h-3">
                <div 
                  className="bg-accent h-3 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Status Message */}
            <div className="mb-8">
              <p className="font-body text-text-primary mb-1 tracking-terminal-wide">
               {'>'} {statusMessage.toUpperCase()}
              </p>
              
              {/* Phase-specific details */}
              {phase === 'collections' && (
                <p className="font-body text-text-secondary text-sm tracking-terminal-wide">
                  PROCESSING COLLECTION {currentCollection} OF {project.collections_metadata.length}
                </p>
              )}
              
              {phase === 'summary' && (
                <p className="font-body text-text-secondary text-sm tracking-terminal-wide">
                  GENERATING AI-POWERED INSIGHTS AND SUMMARY
                </p>
              )}
              
              {phase === 'complete' && (
                <p className="font-body text-text-secondary text-sm tracking-terminal-wide">
                  REDIRECTING TO PROJECT WORKSPACE...
                </p>
              )}
            </div>

            {/* Analysis Details */}
            <div className="bg-panel p-4 border border-border">
              <div className="grid grid-cols-2 gap-4 text-sm font-terminal">
                <div>
                  <span className="font-body text-text-secondary tracking-terminal-wide">KEYWORDS:</span>
                  <span className="font-technical text-text-primary ml-2">
                    {project.keywords.length}
                  </span>
                </div>
                <div>
                  <span className="font-body text-text-secondary tracking-terminal-wide">COLLECTIONS:</span>
                  <span className="font-technical text-text-primary ml-2">
                    {project.collections_metadata.length}
                  </span>
                </div>
              </div>
            </div>

            {/* Loading Animation */}
            {!isComplete && (
              <div className="mt-6">
                <div className="inline-flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-accent rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-accent rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-accent rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                  <span className="font-body text-text-tertiary text-sm">Analyzing</span>
                </div>
              </div>
            )}
          </div>
        </Card>
      </div>
    </MainLayout>
  );
};

export default AnalysisProgress;