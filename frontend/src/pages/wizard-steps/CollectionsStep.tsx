/**
 * Collections Step Component
 * Step 3: Data source selection interface
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CollectionSelector from '@/components/projects/CollectionSelector';
import { ConfirmModal } from '@/components/ui/Modal';
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
  const navigate = useNavigate();
  const [showNavigationWarning, setShowNavigationWarning] = useState(false);

  const handleCollectionChange = (selectedCollections: string[]) => {
    updateFormData({ selectedCollections });
  };

  const handleManageCollectionsClick = () => {
    setShowNavigationWarning(true);
  };

  const handleConfirmNavigation = () => {
    setShowNavigationWarning(false);
    navigate('/collections');
  };

  const handleCancelNavigation = () => {
    setShowNavigationWarning(false);
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Step Introduction */}
      <div className="mb-8">
        <p className="font-body text-text-secondary">
          Each collection contains posts and comments from a specific subreddit with different sorting methods and time periods.
        </p>
      </div>

      {/* Collection Selector */}
      <CollectionSelector
        selectedCollections={formData.selectedCollections}
        onSelectionChange={handleCollectionChange}
        error={errors.collections}
        onManageCollectionsClick={handleManageCollectionsClick}
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
      {/* Navigation Warning Modal */}
      <ConfirmModal
        isOpen={showNavigationWarning}
        onClose={handleCancelNavigation}
        onConfirm={handleConfirmNavigation}
        title="Leave Project Setup?"
        message="Navigating to the Collection Manager will abandon your current project setup. All progress will be lost and you'll need to start over. Are you sure you want to continue?"
        confirmText="Yes, Go to Collections"
        cancelText="Stay in Setup"
        variant="warning"
      />
    </div>
  );
};

export default CollectionsStep;