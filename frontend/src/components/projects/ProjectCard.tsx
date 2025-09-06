/**
 * ProjectCard Component
 * Reusable project card for displaying project information
 * 
 * Handles individual project interactions, status display, and navigation
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import type { ProjectResponse } from '@/types/api';

interface ProjectCardProps {
  /** Project data to display */
  project: ProjectResponse;
  /** Called when user wants to delete the project */
  onDelete: (project: ProjectResponse) => void;
  /** Whether the project is currently being deleted */
  isDeleting?: boolean;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onDelete,
  isDeleting = false
}) => {
  const navigate = useNavigate();

  // Handle navigation to project workspace
  const handleViewProject = () => {
    navigate(`/project/${project.id}`);
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

  return (
    <Card
      hover
      className="cursor-pointer relative group"
      onClick={handleViewProject}
    >
      {/* Project Header */}
      <div className="mb-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-subsection text-text-primary mb-1 flex-1 mr-3">
            {project.name}
          </h3>
          {/* Delete button moved to top right */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(project);
            }}
            className="text-text-secondary hover:text-danger -mr-0.3 -mt-1 font-terminal text-lg font-bold transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Delete project"
            disabled={isDeleting}
          >
            ×
          </button>
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
          variant="primary"
          size="sm"
          className="flex-1"
          onClick={(e) => {
            e.stopPropagation();
            handleViewProject();
          }}
        >
          View Results
        </Button>
      </div>

      {/* Loading Overlay for Delete */}
      {isDeleting && (
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
};

export default ProjectCard;