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
import LoadingSpinner from '@/components/layout/LoadingSpinner';
import { DashboardHeader, SystemStats, ManagementControls, type SortOption } from '@/components/dashboard';
import { useDashboardSort } from '@/hooks/useDashboardSort';

const ProjectsDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: projectsData, isLoading, error, refetch } = useProjects();
  const deleteProjectMutation = useDeleteProject();
  
  // State for delete confirmation modal
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    project: ProjectResponse | null;
    projects?: ProjectResponse[] | null;
  }>({
    isOpen: false,
    project: null,
    projects: null
  });

  // State for bulk selection
  const [selectedProjects, setSelectedProjects] = useState<Set<string>>(new Set());

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
      project,
      projects: null
    });
  };

  const confirmDeleteProject = async () => {
    if (!deleteModal.project && !deleteModal.projects) return;

    try {
      if (deleteModal.projects) {
        // Bulk delete
        for (const project of deleteModal.projects) {
          await deleteProjectMutation.mutateAsync(project.id);
        }
        setSelectedProjects(new Set()); // Clear selection
      } else if (deleteModal.project) {
        // Single delete
        await deleteProjectMutation.mutateAsync(deleteModal.project.id);
      }
      
      setDeleteModal({ isOpen: false, project: null, projects: null });
    } catch (error) {
      console.error('Failed to delete project(s):', error);
    }
  };

  // Handle bulk selection
  const handleSelectProject = (projectId: string, isSelected: boolean) => {
    const newSelected = new Set(selectedProjects);
    if (isSelected) {
      newSelected.add(projectId);
    } else {
      newSelected.delete(projectId);
    }
    setSelectedProjects(newSelected);
  };

  const handleSelectAll = (isSelected: boolean) => {
    if (isSelected) {
      const allIds = new Set(projects.map(p => p.id));
      setSelectedProjects(allIds);
    } else {
      setSelectedProjects(new Set());
    }
  };

  const handleBulkDelete = () => {
    if (selectedProjects.size === 0) return;
    
    const projectsToDelete = projects.filter(p => selectedProjects.has(p.id));
    setDeleteModal({
      isOpen: true,
      project: null,
      projects: projectsToDelete
    });
  };

  const closeDeleteModal = () => {
    setDeleteModal({ isOpen: false, project: null, projects: null });
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

  const projects = projectsData?.projects || [];

  // Sort functionality
  const { sortedItems: sortedProjects, handleSort, getCurrentSortValue } = useDashboardSort(
    projects,
    'date',
    'desc'
  );

  // Sort options for projects
  const projectSortOptions: SortOption[] = [
    { value: 'name-asc', label: 'NAME (A-Z)' },
    { value: 'name-desc', label: 'NAME (Z-A)' },
    { value: 'date-desc', label: 'NEWEST FIRST' },
    { value: 'date-asc', label: 'OLDEST FIRST' },
    { value: 'mentions-desc', label: 'MOST MENTIONS' },
    { value: 'sentiment-desc', label: 'HIGHEST SENTIMENT' },
  ];

  // Calculate stats
  const totalMentions = projects.reduce((sum, project) => sum + project.stats.total_mentions, 0);
  const uniqueCollections = new Set(
    projects.flatMap(project => project.collections_metadata.map(c => c.subreddit))
  ).size;

  const dashboardStats = [
    { value: projects.length, label: 'Total Projects' },
    { value: totalMentions.toLocaleString(), label: 'Total Mentions' },
    { value: uniqueCollections, label: 'Collections Used' },
  ];

  // Loading state
  if (isLoading) {
    return (
      <MainLayout title="Projects Dashboard">
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" message="Loading Projects..." />
        </div>
      </MainLayout>
    );
  }

  // Error state
  if (error) {
    return (
      <MainLayout title="Projects Dashboard">
        <div className="dashboard-spacing">
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
                TRY AGAIN
              </Button>
              <Button variant="secondary" onClick={handleCreateProject}>
                CREATE NEW PROJECT
              </Button>
            </div>
          </Card>
        </div>
      </MainLayout>
    );
  }

  // Empty state
  if (projects.length === 0) {
    return (
      <MainLayout title="Projects Dashboard">
        <div className="dashboard-spacing">
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
            >
              CREATE FIRST PROJECT
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
        </div>
      </MainLayout>
    );
  }

  // Projects dashboard with new hierarchy
  return (
    <MainLayout title="Projects Dashboard" className="dashboard-spacing">
      {/* Level 1: Page Header */}
      <DashboardHeader 
        title="Projects Dashboard"
        subtitle="Research Project Management Interface"
      />

      {/* Level 2: Management Controls with Stats */}
      <ManagementControls
        title="Project Management"
        selectedCount={selectedProjects.size}
        totalCount={projects.length}
        sortOptions={projectSortOptions}
        currentSort={getCurrentSortValue()}
        onSelectAll={() => handleSelectAll(true)}
        onDeselectAll={() => handleSelectAll(false)}
        onSort={handleSort}
        onBulkDelete={handleBulkDelete}
        isAllSelected={selectedProjects.size === projects.length && projects.length > 0}
        stats={dashboardStats}
      />

      {/* Level 4: Projects Grid */}
      <div className="dashboard-level-4">
        <h4 className="font-large text-text-primary mb-4">
          Project Collection
        </h4>
        <div className="projects-grid">
          {/* New Project Card - Terminal Style */}
          <div 
            className="bg-content border-2 border-dashed border-border text-center cursor-pointer hover:border-border-dark hover:bg-panel transition-all duration-100 flex flex-col items-center justify-center font-terminal"
            style={{ minHeight: '155px', padding: '20px' }}
            onClick={handleCreateProject}
          >
            <div className="font-title text-text-tertiary mb-2">
              [+]
            </div>
            <div className="font-body text-text-primary mb-1 tracking-terminal-wide">
              NEW PROJECT
            </div>
            <div className="font-caption text-text-secondary tracking-terminal-wide">
              START NEW RESEARCH
            </div>
          </div>

          {/* Existing Project Cards */}
          {sortedProjects.map((project) => {
            const isSelected = selectedProjects.has(project.id);
            
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
                    <div className="flex items-center space-x-3 flex-1">
                      <div 
                        className="h-4 w-4 border border-border-secondary bg-content cursor-pointer flex items-center justify-center"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectProject(project.id, !isSelected);
                        }}
                      >
                        {isSelected && (
                          <div className="h-2 w-2 bg-accent"></div>
                        )}
                      </div>
                      <h3 className="font-subsection text-text-primary mb-1 flex-1">
                        {project.name}
                      </h3>
                    </div>
                    {/* Delete button moved to top right */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteProject(project);
                      }}
                      className="text-text-secondary hover:text-danger -mr-0.3 -mt-1 font-terminal text-lg font-bold transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                      aria-label="Delete project"
                      disabled={deleteProjectMutation.isPending && deleteModal.project?.id === project.id}
                    >
                      ×
                    </button>
                  </div>
                  <p className="font-small text-text-tertiary">
                    Created {formatDate(project.created_at)} • {project.collections_metadata.map(c => `r/${c.subreddit}`).join(', ')}
                  </p>
                </div>
                
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
                    variant="primary"
                    size="sm"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewProject(project.id);
                    }}
                  >
                    VIEW RESULTS
                  </Button>
                </div>

                {/* Loading Overlay for Delete */}
                {deleteProjectMutation.isPending && deleteModal.project?.id === project.id && (
                  <div className="absolute inset-0 bg-content bg-opacity-75 flex items-center justify-center">
                    <LoadingSpinner size="sm" message="Deleting" />
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteModal.isOpen}
        onClose={closeDeleteModal}
        onConfirm={confirmDeleteProject}
        title="Delete Project"
        message={
          deleteModal.projects
            ? `Are you sure you want to delete ${deleteModal.projects.length} projects? This will permanently remove all analysis results, chat sessions, and project data for: ${deleteModal.projects.map(p => `"${p.name}"`).join(', ')}. This action cannot be undone.`
            : deleteModal.project
            ? `Are you sure you want to delete "${deleteModal.project.name}"? This will permanently remove all analysis results, chat sessions, and project data. This action cannot be undone.`
            : ''
        }
        confirmText={deleteModal.projects ? `Delete ${deleteModal.projects.length} Projects` : "Delete Project"}
        cancelText="Cancel"
        variant="danger"
      />
    </MainLayout>
  );
};

export default ProjectsDashboard;