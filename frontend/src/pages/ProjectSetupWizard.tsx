/**
 * Project Setup Wizard Page
 * Guided project creation flow
 * 
 * Phase 2.1: Placeholder implementation
 * Phase 2.2: Full multi-step wizard with form validation
 */

import React from 'react';
import { Link } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';

const ProjectSetupWizard: React.FC = () => {
  return (
    <MainLayout title="Create New Project">
      {/* Breadcrumb Navigation */}
      <div className="mb-6">
        <nav className="flex items-center space-x-2 font-body text-text-secondary">
          <Link 
            to="/" 
            className="hover:text-text-primary transition-colors duration-150"
          >
            Projects
          </Link>
          <span>→</span>
          <span className="text-text-primary">New Project</span>
        </nav>
      </div>

      {/* Page Header */}
      <div className="mb-8">
        <h1 className="font-page-title text-text-primary mb-3">
          Create New Project
        </h1>
        <p className="font-body text-text-secondary max-w-2xl">
          Set up a new research project to analyze Reddit discussions. Define your research 
          question, select keywords, and choose data collections to uncover insights.
        </p>
      </div>

      {/* Placeholder Content */}
      <Card className="max-w-2xl mx-auto text-center py-16">
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
              d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
            />
          </svg>
        </div>
        
        <h2 className="font-section-header text-text-primary mb-3">
          Project Setup Wizard
        </h2>
        
        <p className="font-body text-text-secondary mb-8 max-w-lg mx-auto">
          The comprehensive project creation wizard will be implemented in Phase 2.2. 
          This will include research question input, AI keyword suggestions, collection 
          selection, and analysis configuration.
        </p>
        
        {/* Planned Features Preview */}
        <div className="bg-panel rounded-default p-6 mb-8 text-left">
          <h3 className="font-subsection text-text-primary mb-4 text-center">
            Coming in Phase 2.2:
          </h3>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">
                ✨ Smart Setup Process
              </h4>
              <ul className="font-body text-text-secondary space-y-1 text-sm">
                <li>• Multi-step guided wizard</li>
                <li>• Research question input</li>
                <li>• AI-powered keyword suggestions</li>
                <li>• Form validation and error handling</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">
                🔧 Configuration Options
              </h4>
              <ul className="font-body text-text-secondary space-y-1 text-sm">
                <li>• Collection selection interface</li>
                <li>• Analysis settings configuration</li>
                <li>• Partial matching options</li>
                <li>• AI summary preferences</li>
              </ul>
            </div>
          </div>
        </div>
        
        {/* Navigation */}
          <div className="flex justify-center space-x-3">
            <Link
              to="/"
              className="inline-flex items-center px-4 py-2 bg-panel text-text-primary border border-border-primary rounded-default hover:bg-gray-100 hover:border-border-secondary transition-colors duration-150 font-medium"
            >
              ← Back to Projects
            </Link>
            <Link
              to="/collections"
              className="inline-flex items-center px-4 py-2 bg-transparent text-accent border border-accent rounded-default hover:bg-hover-blue transition-colors duration-150 font-medium"
            >
              Manage Collections
            </Link>
          </div>
      </Card>

      {/* Development Info */}
      <div className="mt-12 bg-panel rounded-default p-6 border border-border-primary max-w-4xl mx-auto">
        <h2 className="font-section-header text-text-primary mb-3">
          Phase 2.2 Implementation Plan
        </h2>
        
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              Setup Wizard Features
            </h3>
            <ul className="font-body text-text-secondary space-y-1">
              <li>• Step 1: Research question input with validation</li>
              <li>• Step 2: Keywords with AI suggestions and manual editing</li>
              <li>• Step 3: Collection selection from available data</li>
              <li>• Step 4: Analysis configuration and preferences</li>
              <li>• Progress indicator and step navigation</li>
              <li>• Real-time form validation and error handling</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              Backend Integration
            </h3>
            <ul className="font-body text-text-secondary space-y-1">
              <li>• GET /collections for data source selection</li>
              <li>• POST /ai/keywords/suggest for AI assistance</li>
              <li>• POST /projects for project creation</li>
              <li>• POST /projects/&#123;id&#125;/analysis/start for analysis</li>
              <li>• Real-time validation and error handling</li>
              <li>• Navigation to progress screen after creation</li>
            </ul>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default ProjectSetupWizard;