/**
 * Projects Dashboard Page
 * Landing page showing all user projects
 * 
 * Phase 1: Placeholder with professional styling
 * Phase 2: Full implementation with project cards and creation flow
 */

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';

const ProjectsDashboard: React.FC = () => {
  return (
    <MainLayout title="Projects Dashboard">
      {/* Page Header */}
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

      {/* Phase 1 Placeholder Content */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* New Project Card Placeholder */}
        <Card 
          clickable
          hover
          className="border-2 border-dashed border-border-secondary bg-panel text-center py-8"
          onClick={() => alert('Project creation wizard will be implemented in Phase 2')}
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

        {/* Example Project Cards (for visual reference) */}
        <Card hover className="cursor-pointer">
          <div className="mb-4">
            <h3 className="font-subsection text-text-primary mb-1">
              iPhone Battery Analysis
            </h3>
            <p className="font-small text-text-tertiary">
              Created 2 days ago • r/iphone, r/apple
            </p>
          </div>
          
          <p className="font-body text-text-secondary mb-4 line-clamp-2">
            Analysis reveals significant user frustration with battery performance, 
            particularly around charging speeds and drain patterns during intensive usage.
          </p>
          
          <div className="flex items-center justify-between text-small">
            <div className="flex space-x-4">
              <span className="text-text-tertiary">
                <span className="font-technical">1,247</span> mentions
              </span>
              <span className="text-danger">
                <span className="font-technical">-0.23</span> sentiment
              </span>
            </div>
            <span className="text-success font-medium">
              Completed
            </span>
          </div>
        </Card>

        <Card hover className="cursor-pointer">
          <div className="mb-4">
            <h3 className="font-subsection text-text-primary mb-1">
              EV Charging Infrastructure
            </h3>
            <p className="font-small text-text-tertiary">
              Created 1 week ago • r/electricvehicles, r/teslamotors
            </p>
          </div>
          
          <p className="font-body text-text-secondary mb-4 line-clamp-2">
            Mixed sentiment around charging network expansion with positive trends 
            for home installation but concerns about public infrastructure reliability.
          </p>
          
          <div className="flex items-center justify-between text-small">
            <div className="flex space-x-4">
              <span className="text-text-tertiary">
                <span className="font-technical">892</span> mentions
              </span>
              <span className="text-success">
                <span className="font-technical">+0.15</span> sentiment
              </span>
            </div>
            <span className="text-success font-medium">
              Completed
            </span>
          </div>
        </Card>
      </div>

      {/* Phase Information */}
      <div className="mt-12 bg-panel rounded-default p-6 border border-border-primary">
        <h2 className="font-section-header text-text-primary mb-3">
          Phase 1 Implementation Status
        </h2>
        
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              ✅ Completed
            </h3>
            <ul className="font-body text-text-secondary space-y-1">
              <li>• Professional design system</li>
              <li>• Type-safe API integration</li>
              <li>• Layout and navigation structure</li>
              <li>• ASCII branding implementation</li>
              <li>• Error handling and loading states</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              🚧 Next Phase (Phase 2)
            </h3>
            <ul className="font-body text-text-secondary space-y-1">
              <li>• Project creation wizard</li>
              <li>• Real project data integration</li>
              <li>• Analysis progress tracking</li>
              <li>• AI keyword suggestions</li>
              <li>• Collection selection interface</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-6 pt-4 border-t border-border-primary">
          <Button
            variant="outline"
            onClick={() => window.open('/api/health', '_blank')}
            className="mr-3"
          >
            Test Backend Connection
          </Button>
          <Button
            variant="ghost"
            onClick={() => alert('Backend health check will show actual API status')}
          >
            View API Status
          </Button>
        </div>
      </div>
    </MainLayout>
  );
};

export default ProjectsDashboard;