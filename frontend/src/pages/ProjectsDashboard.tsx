/**
 * Projects Dashboard Page
 * Main landing page showing all user projects with full API integration
 * 
 * Phase 2.1: Complete functional implementation with real data
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import { LoadingState } from '@/components/layout/LoadingSpinner';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { ConfirmModal } from '@/components/ui/Modal';
import { useProjects, useDeleteProject } from '@/hooks/useApi';
import { getErrorMessage } from '@/api/client';
import type { ProjectResponse } from '@/types/api';

const ProjectsDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: projectsData, isLoading, error, refetch } = useProjects();
  const deleteProjectMutation = useDeleteProject();
  
  // State for delete confirmation modal
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    project: ProjectResponse | null;
  }>({
    isOpen: false,
    project: null
  });

  // Handle navigation to project workspace
  const handleViewProject = (projectId: string) => {
    navigate(`/project/${projectId}`);
  };

  // Handle navigation to project creation
  const handleCreateProject = () => {
    navigate('/projects/new');
  };

  // Handle delete project flow
  const handleDeleteProject = (project: ProjectResponse) => {
    setDeleteModal({
      isOpen: true,
      project
    });
  };

  const confirmDeleteProject = async () => {
    if (!deleteModal.project) return;

    try {
      await deleteProjectMutation.mutateAsync(deleteModal.project.id);
      setDeleteModal({ isOpen: false, project: null });
    } catch (error) {
      console.error('Failed to delete project:', error);
      // Error is handled by the mutation's onError callback
    }
  };

  const closeDeleteModal = () => {
    setDeleteModal({ isOpen: false, project: null });
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    if (diffDays <= 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  // Loading state
  if (isLoading) {
    return (
      <MainLayout title="Projects Dashboard">
        <div className="mb-8">
          <h1 className="font-page-title text-text-primary mb-3">
            Research Projects
          </h1>
          <p className="font-body text-text-secondary max-w-2xl">
            Create and manage your Reddit research investigations. Each project combines 
            keywords, data collections, and AI-powered insights to help you understand 
            discussions and sentiment patterns.
          </p>
        </div>
        
        <LoadingState 
          title="Loading Projects..."
          description="Fetching your research projects from the server."
        />
      </MainLayout>
    );
  }

  // Error state
  if (error) {
    return (
      <MainLayout title="Projects Dashboard">
        <div className="mb-8">
          <h1 className="font-page-title text-text-primary mb-3">
            Research Projects
          </h1>
          <p className="font-body text-text-secondary max-w-2xl">
            Create and manage your Reddit research investigations.
          </p>
        </div>

        <Card className="text-center py-12">
          <div className="text-danger mb-4">
            <svg
              className="h-12 w-12 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          
          <h3 className="font-subsection text-text-primary mb-2">
            Failed to Load Projects
          </h3>
          
          <p className="font-body text-text-secondary mb-6 max-w-md mx-auto">
            {getErrorMessage(error)}
          </p>
          
          <div className="flex justify-center space-x-3">
            <Button variant="primary" onClick={() => refetch()}>
              Try Again
            </Button>
            <Button variant="secondary" onClick={handleCreateProject}>
              Create New Project
            </Button>
          </div>
        </Card>
      </MainLayout>
    );
  }

  const projects = projectsData?.projects || [];

  // Empty state
  if (projects.length === 0) {
    return (
      <MainLayout title="Projects Dashboard">
        <div className="mb-8">
          <h1 className="font-page-title text-text-primary mb-3">
            Research Projects
          </h1>
          <p className="font-body text-text-secondary max-w-2xl">
            Create and manage your Reddit research investigations. Each project combines 
            keywords, data collections, and AI-powered insights to help you understand 
            discussions and sentiment patterns.
          </p>
        </div>

        <Card className="text-center py-16">
          <div className="text-accent mb-6">
            <svg
              className="h-16 w-16 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          
          <h2 className="font-section-header text-text-primary mb-3">
            Create Your First Project
          </h2>
          
          <p className="font-body text-text-secondary mb-8 max-w-lg mx-auto">
            Get started by creating your first research project. Define your research question, 
            select keywords, choose data sources, and let our AI-powered analytics reveal 
            insights from Reddit discussions.
          </p>
          
          <Button
            variant="primary"
            size="lg"
            onClick={handleCreateProject}
            className="font-semibold"
          >
            Create First Project
          </Button>
          
          <div className="mt-8 pt-6 border-t border-border-primary">
            <p className="font-small text-text-tertiary">
              Need data first? Visit the{' '}
              <button
                onClick={() => navigate('/collections')}
                className="text-accent hover:underline"
              >
                Collection Manager
              </button>
              {' '}to gather Reddit data.
            </p>
          </div>
        </Card>
      </MainLayout>
    );
  }

  // Projects grid view
  return (
    <MainLayout title="Projects Dashboard">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <h1 className="font-page-title text-text-primary">
            Research Projects
          </h1>
          <Button
            variant="primary"
            onClick={handleCreateProject}
            startIcon={
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            }
          >
            New Project
          </Button>
        </div>
        <p className="font-body text-text-secondary max-w-2xl">
          Create and manage your Reddit research investigations. Each project combines 
          keywords, data collections, and AI-powered insights to help you understand 
          discussions and sentiment patterns.
        </p>
      </div>

      {/* Projects Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* New Project Card */}
        <Card 
          clickable
          hover
          className="border-2 border-dashed border-border-secondary bg-panel text-center py-8"
          onClick={handleCreateProject}
        >
          <div className="text-accent mb-4">
            <svg
              className="h-12 w-12 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
          </div>
          <h3 className="font-subsection text-text-primary mb-2">
            New Project
          </h3>
          <p className="font-body text-text-secondary">
            Start a new research investigation
          </p>
        </Card>

        {/* Existing Project Cards */}
        {projects.map((project) => {
          return (
            <Card
              key={project.id}
              hover
              className="cursor-pointer relative group"
              onClick={() => handleViewProject(project.id)}
            >
              {/* Project Content */}
              <div className="mb-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-subsection text-text-primary mb-1 flex-1 mr-3">
                    {project.name}
                  </h3>
                  {/* Delete button moved to top right */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteProject(project);
                    }}
                    className="text-text-secondary hover:text-danger -mr-2 -mt-1"
                    aria-label="Delete project"
                  >
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </Button>
                </div>
                <p className="font-small text-text-tertiary">
                  Created {formatDate(project.created_at)} • {project.collections_metadata.map(c => `r/${c.subreddit}`).join(', ')}
                </p>
              </div>
              
              {/* AI Summary Preview */}
              {project.summary && (
                <p className="font-body text-text-secondary mb-4 line-clamp-2">
                  {project.summary.summary_preview}
                </p>
              )}
              
              {/* Project Stats */}
              <div className="flex items-center justify-between text-small mb-4">
                <div className="flex space-x-4">
                  <span className="text-text-tertiary">
                    <span className="font-technical">{project.stats.total_mentions.toLocaleString()}</span> mentions
                  </span>
                  <span className={project.stats.avg_sentiment >= 0 ? 'text-success' : 'text-danger'}>
                    <span className="font-technical">
                      {project.stats.avg_sentiment >= 0 ? '+' : ''}{project.stats.avg_sentiment.toFixed(2)}
                    </span> sentiment
                  </span>
                </div>
              </div>

              {/* Keywords Preview */}
              <div className="mb-4">
                <div className="flex flex-wrap gap-1">
                  {project.keywords.slice(0, 3).map((keyword, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-panel text-text-secondary font-small rounded-input text-xs"
                    >
                      {keyword}
                    </span>
                  ))}
                  {project.keywords.length > 3 && (
                    <span className="px-2 py-1 bg-panel text-text-tertiary font-small rounded-input text-xs">
                      +{project.keywords.length - 3} more
                    </span>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleViewProject(project.id);
                  }}
                >
                  View Results
                </Button>
              </div>

              {/* Loading Overlay for Delete */}
              {deleteProjectMutation.isPending && deleteModal.project?.id === project.id && (
                <div className="absolute inset-0 bg-content bg-opacity-75 flex items-center justify-center rounded-default">
                  <div className="flex items-center space-x-2">
                    <svg className="animate-spin h-4 w-4 text-accent" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="font-small text-text-secondary">Deleting...</span>
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteModal.isOpen}
        onClose={closeDeleteModal}
        onConfirm={confirmDeleteProject}
        title="Delete Project"
        message={
          deleteModal.project
            ? `Are you sure you want to delete "${deleteModal.project.name}"? This will permanently remove all analysis results, chat sessions, and project data. This action cannot be undone.`
            : ''
        }
        confirmText="Delete Project"
        cancelText="Cancel"
        variant="danger"
      />

      {/* Stats Footer */}
      <div className="mt-12 bg-panel rounded-default p-6 border border-border-primary">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-subsection text-text-primary mb-1">
              Project Overview
            </h3>
            <p className="font-body text-text-secondary">
              {projects.length} {projects.length === 1 ? 'project' : 'projects'} total
            </p>
          </div>
          
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={() => navigate('/collections')}
            >
              Manage Collections
            </Button>
            <Button
              variant="primary"
              onClick={handleCreateProject}
            >
              New Project
            </Button>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default ProjectsDashboard;