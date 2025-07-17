/**
 * Collections Step Component
 * Step 3: Data source selection interface
 */

import React from 'react';
import CollectionSelector from '@/components/projects/CollectionSelector';
import type { WizardFormData } from '@/hooks/useWizardState';

export interface CollectionsStepProps {
  /** Current form data */
  formData: WizardFormData;
  /** Function to update form data */
  updateFormData: (updates: Partial<WizardFormData>) => void;
  /** Validation errors */
  errors: Record<string, string>;
}

export const CollectionsStep: React.FC<CollectionsStepProps> = ({
  formData,
  updateFormData,
  errors
}) => {
  const handleCollectionChange = (selectedCollections: string[]) => {
    updateFormData({ selectedCollections });
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Step Introduction */}
      <div className="mb-8">
        <h3 className="font-subsection text-text-primary mb-3">
          Choose Data Collections
        </h3>
        <p className="font-body text-text-secondary">
          Select the Reddit data collections you want to analyze. Each collection represents 
          posts and comments from a specific subreddit, gathered with specific parameters.
        </p>
      </div>

      {/* Collection Selector */}
      <CollectionSelector
        selectedCollections={formData.selectedCollections}
        onSelectionChange={handleCollectionChange}
        error={errors.collections}
      />

      {/* Analysis Preview */}
      {formData.selectedCollections.length > 0 && (
        <div className="mt-8 p-4 bg-panel rounded-input border border-border-primary">
          <h4 className="font-subsection text-text-primary mb-3">
            Analysis Preview
          </h4>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h5 className="font-body text-text-primary mb-2 font-medium">
                What will be analyzed:
              </h5>
              <ul className="space-y-1 text-sm text-text-secondary">
                <li>• Posts and comments from {formData.selectedCollections.length} collection{formData.selectedCollections.length !== 1 ? 's' : ''}</li>
                <li>• Text content matching your {formData.keywords.length} keyword{formData.keywords.length !== 1 ? 's' : ''}</li>
                <li>• Sentiment patterns around each keyword</li>
                <li>• Co-occurrence relationships between keywords</li>
              </ul>
            </div>
            
            <div>
              <h5 className="font-body text-text-primary mb-2 font-medium">
                You'll get insights about:
              </h5>
              <ul className="space-y-1 text-sm text-text-secondary">
                <li>• Overall sentiment trends</li>
                <li>• Most discussed topics</li>
                <li>• Keyword relationships and patterns</li>
                <li>• Representative discussion examples</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Data Quality Guidelines */}
      <div className="mt-6 p-4 bg-panel rounded-input border border-border-primary">
        <h4 className="font-subsection text-text-primary mb-3">
          Choosing the Right Collections
        </h4>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <h5 className="font-body text-text-primary mb-2 font-medium">
              ✅ Good collection choices:
            </h5>
            <ul className="space-y-1 text-sm text-text-secondary">
              <li>• Collections relevant to your research question</li>
              <li>• Subreddits where your keywords likely appear</li>
              <li>• Recent collections with substantial data</li>
              <li>• Multiple subreddits for broader perspective</li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-body text-text-primary mb-2 font-medium">
              ⚠️ Consider carefully:
            </h5>
            <ul className="space-y-1 text-sm text-text-secondary">
              <li>• Very large collections may slow analysis</li>
              <li>• Unrelated subreddits may dilute insights</li>
              <li>• Too many collections may overwhelm results</li>
              <li>• Very small collections may lack sufficient data</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Collection Types Guide */}
      <div className="mt-6 p-4 bg-panel rounded-input border border-border-primary">
        <h4 className="font-subsection text-text-primary mb-3">
          Understanding Collection Types
        </h4>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="p-3 bg-content rounded-input border border-border-secondary">
            <h5 className="font-body text-text-primary mb-2 font-medium">
              Hot Posts
            </h5>
            <p className="font-small text-text-secondary">
              Currently trending discussions with high engagement
            </p>
          </div>
          
          <div className="p-3 bg-content rounded-input border border-border-secondary">
            <h5 className="font-body text-text-primary mb-2 font-medium">
              Top Posts
            </h5>
            <p className="font-small text-text-secondary">
              Highest-scoring posts from specific time periods
            </p>
          </div>
          
          <div className="p-3 bg-content rounded-input border border-border-secondary">
            <h5 className="font-body text-text-primary mb-2 font-medium">
              New Posts
            </h5>
            <p className="font-small text-text-secondary">
              Recently submitted content, regardless of score
            </p>
          </div>
          
          <div className="p-3 bg-content rounded-input border border-border-secondary">
            <h5 className="font-body text-text-primary mb-2 font-medium">
              Controversial
            </h5>
            <p className="font-small text-text-secondary">
              Posts with high engagement but mixed voting
            </p>
          </div>
        </div>
      </div>

      {/* Requirements */}
      <div className="mt-6 p-4 bg-hover-blue rounded-input border border-accent">
        <h4 className="font-subsection text-text-primary mb-2">
          Requirements for Next Step:
        </h4>
        <ul className="space-y-1 text-sm text-text-secondary">
          <li>• At least 1 collection must be selected</li>
          <li>• Only completed collections are available</li>
          <li>• Selected collections should be relevant to your research</li>
          <li>• Consider the time period and sorting method of each collection</li>
        </ul>
      </div>
    </div>
  );
};

export default CollectionsStep;