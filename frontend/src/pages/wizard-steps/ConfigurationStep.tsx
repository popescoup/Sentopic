/**
 * Configuration Step Component
 * Step 4: Analysis configuration and final review
 */

import React from 'react';
import { useCollections } from '@/hooks/useApi';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';
import type { WizardFormData } from '@/hooks/useWizardState';

export interface ConfigurationStepProps {
  /** Current form data */
  formData: WizardFormData;
  /** Function to update form data */
  updateFormData: (updates: Partial<WizardFormData>) => void;
  /** Validation errors */
  errors: Record<string, string>;
}

export const ConfigurationStep: React.FC<ConfigurationStepProps> = ({
  formData,
  updateFormData,
  errors
}) => {
  const { data: collectionsData } = useCollections();
  const collections = collectionsData?.collections || [];

  const handleProjectNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    updateFormData({ projectName: event.target.value });
  };

  const handlePartialMatchingChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    updateFormData({ partialMatching: event.target.checked });
  };

  const handleContextWindowChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    updateFormData({ contextWindow: parseInt(event.target.value) || 150 });
  };

  const handleGenerateSummaryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    updateFormData({ generateSummary: event.target.checked });
  };

  // Get selected collections data
  const selectedCollections = collections.filter(c => 
    formData.selectedCollections.includes(c.id)
  );

  // Calculate estimated analysis scope
  const totalPosts = selectedCollections.reduce((sum, c) => sum + c.posts_collected, 0);
  const totalComments = selectedCollections.reduce((sum, c) => sum + c.comments_collected, 0);
  const estimatedDuration = Math.ceil((totalPosts + totalComments) / 1000); // rough estimate

  return (
    <div className="max-w-4xl mx-auto">
      {/* Step Introduction */}
      <div className="mb-8">
        <h3 className="font-subsection text-text-primary mb-3">
          Configure Analysis Settings
        </h3>
        <p className="font-body text-text-secondary">
          Review your selections and configure analysis parameters before creating your project.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Configuration Settings */}
        <div className="space-y-6">
          {/* Project Name */}
          <Card>
            <h4 className="font-subsection text-text-primary mb-4">
              Project Settings
            </h4>
            
            <div className="space-y-4">
              <Input
                label="Project Name"
                value={formData.projectName}
                onChange={handleProjectNameChange}
                placeholder="Enter a descriptive project name"
                error={errors.projectName}
                helpText="This will help you identify the project later"
                fullWidth
              />
            </div>
          </Card>

          {/* Analysis Parameters */}
          <Card>
            <h4 className="font-subsection text-text-primary mb-4">
              Analysis Parameters
            </h4>
            
            <div className="space-y-4">
              {/* Partial Matching */}
              <div>
                <label className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    checked={formData.partialMatching}
                    onChange={handlePartialMatchingChange}
                    className="mt-1 rounded border-border-secondary focus:border-accent focus:ring-accent"
                  />
                  <div>
                    <div className="font-medium text-text-primary">
                      Partial Keyword Matching
                    </div>
                    <div className="font-body text-text-secondary text-sm">
                      Find keywords as parts of larger words (e.g., "program" matches "programming")
                    </div>
                  </div>
                </label>
              </div>

              {/* Context Window */}
              <div>
                <label className="block font-medium text-text-primary mb-2">
                  Context Window: {formData.contextWindow} words
                </label>
                <input
                  type="range"
                  min="50"
                  max="500"
                  step="25"
                  value={formData.contextWindow}
                  onChange={handleContextWindowChange}
                  className="w-full h-2 bg-border-secondary rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-text-tertiary mt-1">
                  <span>50 words</span>
                  <span>500 words</span>
                </div>
                <div className="font-body text-text-secondary text-sm mt-1">
                  Amount of surrounding text to include with each keyword match
                </div>
              </div>

              {/* AI Summary */}
              <div>
                <label className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    checked={formData.generateSummary}
                    onChange={handleGenerateSummaryChange}
                    className="mt-1 rounded border-border-secondary focus:border-accent focus:ring-accent"
                  />
                  <div>
                    <div className="font-medium text-text-primary">
                      Generate AI Summary
                    </div>
                    <div className="font-body text-text-secondary text-sm">
                      Create an AI-powered summary of key findings and insights
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </Card>
        </div>

        {/* Review Summary */}
        <div className="space-y-6">
          {/* Project Summary */}
          <Card>
            <h4 className="font-subsection text-text-primary mb-4">
              Project Summary
            </h4>
            
            <div className="space-y-4">
              {/* Research Question */}
              <div>
                <h5 className="font-body text-text-primary mb-1 font-medium">
                  Research Question:
                </h5>
                <p className="font-body text-text-secondary">
                  {formData.researchQuestion || 'No research question specified'}
                </p>
              </div>

              {/* Keywords */}
              <div>
                <h5 className="font-body text-text-primary mb-1 font-medium">
                  Keywords ({formData.keywords.length}):
                </h5>
                <div className="flex flex-wrap gap-1">
                  {formData.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-hover-blue text-accent text-sm rounded"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>

              {/* Collections */}
              <div>
                <h5 className="font-body text-text-primary mb-1 font-medium">
                  Collections ({selectedCollections.length}):
                </h5>
                <div className="space-y-1">
                  {selectedCollections.map((collection) => (
                    <div key={collection.id} className="flex items-center justify-between text-sm">
                      <span className="text-text-secondary">
                        r/{collection.subreddit}
                      </span>
                      <span className="text-text-tertiary">
                        {collection.posts_collected + collection.comments_collected} items
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>

          {/* Analysis Scope */}
          <Card>
            <h4 className="font-subsection text-text-primary mb-4">
              Analysis Scope
            </h4>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="font-body text-text-secondary">Total Posts:</span>
                <span className="font-technical text-text-primary">
                  {totalPosts.toLocaleString()}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="font-body text-text-secondary">Total Comments:</span>
                <span className="font-technical text-text-primary">
                  {totalComments.toLocaleString()}
                </span>
              </div>
              
              <div className="flex justify-between items-center border-t border-border-primary pt-3">
                <span className="font-body text-text-primary font-medium">Total Items:</span>
                <span className="font-technical text-text-primary font-medium">
                  {(totalPosts + totalComments).toLocaleString()}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="font-body text-text-secondary">Est. Duration:</span>
                <span className="font-technical text-text-tertiary">
                  ~{estimatedDuration} minute{estimatedDuration !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Analysis Process Preview */}
      <div className="mt-8 p-4 bg-panel rounded-input border border-border-primary">
        <h4 className="font-subsection text-text-primary mb-3">
          What happens next?
        </h4>
        <div className="grid gap-4 md:grid-cols-4">
          <div className="text-center">
            <div className="w-8 h-8 bg-accent text-white rounded-full flex items-center justify-center mx-auto mb-2">
              1
            </div>
            <h5 className="font-body text-text-primary font-medium mb-1">
              Create Project
            </h5>
            <p className="font-small text-text-secondary">
              Project saved with your settings
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-8 h-8 bg-accent text-white rounded-full flex items-center justify-center mx-auto mb-2">
              2
            </div>
            <h5 className="font-body text-text-primary font-medium mb-1">
              Start Analysis
            </h5>
            <p className="font-small text-text-secondary">
              Begin processing your data
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-8 h-8 bg-accent text-white rounded-full flex items-center justify-center mx-auto mb-2">
              3
            </div>
            <h5 className="font-body text-text-primary font-medium mb-1">
              Track Progress
            </h5>
            <p className="font-small text-text-secondary">
              Monitor analysis progress
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-8 h-8 bg-success text-white rounded-full flex items-center justify-center mx-auto mb-2">
              ✓
            </div>
            <h5 className="font-body text-text-primary font-medium mb-1">
              View Results
            </h5>
            <p className="font-small text-text-secondary">
              Explore insights and findings
            </p>
          </div>
        </div>
      </div>

      {/* Requirements */}
      <div className="mt-6 p-4 bg-hover-blue rounded-input border border-accent">
        <h4 className="font-subsection text-text-primary mb-2">
          Ready to Create Project:
        </h4>
        <ul className="space-y-1 text-sm text-text-secondary">
          <li>• Project name: {formData.projectName || 'Required'}</li>
          <li>• {formData.keywords.length} keywords selected</li>
          <li>• {selectedCollections.length} collections selected</li>
          <li>• Analysis parameters configured</li>
        </ul>
      </div>
    </div>
  );
};

export default ConfigurationStep;