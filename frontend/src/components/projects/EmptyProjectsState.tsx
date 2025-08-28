/**
 * EmptyProjectsState Component
 * Professional empty state for when user has no projects
 * 
 * Provides clear guidance and call-to-action for new users
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';

interface EmptyProjectsStateProps {
  /** Called when user wants to create their first project */
  onCreateProject?: () => void;
}

export const EmptyProjectsState: React.FC<EmptyProjectsStateProps> = ({ 
  onCreateProject 
}) => {
  const navigate = useNavigate();

  const handleCreateProject = () => {
    if (onCreateProject) {
      onCreateProject();
    } else {
      navigate('/projects/new');
    }
  };

  const handleGoToCollections = () => {
    navigate('/collections');
  };

  return (
    <Card className="text-center py-16">
      {/* Icon */}
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
      
      {/* Title */}
      <h2 className="font-section-header text-text-primary mb-3">
        Create Your First Project
      </h2>
      
      {/* Description */}
      <p className="font-body text-text-secondary mb-8 max-w-lg mx-auto">
        Get started by creating your first research project. Define your research question, 
        select keywords, choose data sources, and let our AI-powered analytics reveal 
        insights from Reddit discussions.
      </p>
      
      {/* Primary Action */}
      <Button
        variant="primary"
        size="lg"
        onClick={handleCreateProject}
        className="font-semibold mb-6"
      >
        + CREATE FIRST PROJECT
      </Button>
      
      {/* Getting Started Guide */}
      <div className="mb-8">
        <h3 className="font-subsection text-text-primary mb-4">
          How it works:
        </h3>
        <div className="grid gap-4 md:grid-cols-3 max-w-4xl mx-auto">
          <div className="text-center">
            <div className="w-12 h-12 bg-accent text-white rounded-full flex items-center justify-center mx-auto mb-3 font-semibold">
              1
            </div>
            <h4 className="font-subsection text-text-primary mb-2">Define Research</h4>
            <p className="font-small text-text-secondary">
              Set your research question and select relevant keywords
            </p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-accent text-white rounded-full flex items-center justify-center mx-auto mb-3 font-semibold">
              2
            </div>
            <h4 className="font-subsection text-text-primary mb-2">Choose Data</h4>
            <p className="font-small text-text-secondary">
              Select Reddit collections from relevant subreddits
            </p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-accent text-white rounded-full flex items-center justify-center mx-auto mb-3 font-semibold">
              3
            </div>
            <h4 className="font-subsection text-text-primary mb-2">Get Insights</h4>
            <p className="font-small text-text-secondary">
              AI analyzes discussions and surfaces key insights
            </p>
          </div>
        </div>
      </div>
      
      {/* Secondary Action */}
      <div className="pt-6 border-t border-border-primary">
        <p className="font-small text-text-tertiary mb-3">
          Need data first?
        </p>
        <Button
          variant="secondary"
          onClick={handleGoToCollections}
        >
          {">"} COLLECTION MANAGER
        </Button>
      </div>
    </Card>
  );
};

export default EmptyProjectsState;