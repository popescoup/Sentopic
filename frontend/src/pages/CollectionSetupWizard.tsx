/**
 * Collection Setup Wizard Page
 * Comprehensive 4-step guided wizard for collection creation
 */

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import WizardLayout from '@/components/wizard/WizardLayout';
import SubredditSelectionStep from '@/pages/collection-wizard-steps/SubredditSelectionStep';
import ParametersStep from '@/pages/collection-wizard-steps/ParametersStep';
import ReviewStep from '@/pages/collection-wizard-steps/ReviewStep';
import ProgressStep from '@/pages/collection-wizard-steps/ProgressStep';
import { useCollectionWizardState } from '@/hooks/useCollectionWizardState';
import { useCreateCollections } from '@/hooks/useApi';
import { validateCollectionStep } from '@/utils/collectionWizardValidation';
import { getErrorMessage } from '@/api/client';
import Card from '@/components/ui/Card';

const CollectionSetupWizard: React.FC = () => {
  const navigate = useNavigate();
  const createCollectionsMutation = useCreateCollections();

  const {
    currentStep,
    formData,
    updateFormData,
    goToStep,
    canGoBack,
    canGoNext,
    isStepComplete,
    resetWizard
  } = useCollectionWizardState();

  // Step configuration
  const steps = [
    {
      id: 1,
      title: 'Select Subreddits',
      component: SubredditSelectionStep,
      description: 'Choose target communities'
    },
    {
      id: 2,
      title: 'Configure Parameters',
      component: ParametersStep,
      description: 'Set collection parameters'
    },
    {
      id: 3,
      title: 'Review & Confirm',
      component: ReviewStep,
      description: 'Review your settings'
    },
    {
      id: 4,
      title: 'Collection Progress',
      component: ProgressStep,
      description: 'Monitor collection progress'
    }
  ];

  const currentStepConfig = steps.find(step => step.id === currentStep);
  const CurrentStepComponent = currentStepConfig?.component;

  // Navigation handlers
  const handlePrevious = () => {
    if (canGoBack && currentStep !== 4) { // Disable back during progress
      goToStep(currentStep - 1);
    }
  };

  const handleNext = async () => {
    // Validate current step
    const validation = validateCollectionStep(currentStep, formData);
    if (!validation.isValid) {
      console.error('Validation failed:', validation.errors);
      return;
    }

    if (currentStep < steps.length) {
      if (currentStep === 3) {
        // Starting collection process - go to progress step and start collection
        goToStep(4);
        await handleStartCollection();
      } else {
        goToStep(currentStep + 1);
      }
    }
  };

  const handleCancel = () => {
    if (currentStep === 4) {
      // During progress, don't allow cancel
      return;
    }
    resetWizard();
    navigate('/collections');
  };

  // Collection submission
  const handleStartCollection = async () => {
    try {
      const collectionRequest = {
        subreddits: formData.subreddits,
        collection_params: formData.parameters
      };

      await createCollectionsMutation.mutateAsync(collectionRequest);
    } catch (error) {
      console.error('Failed to start collection:', error);
      // Error will be handled by the progress step component
    }
  };

  // Handle collection completion (called from ProgressStep)
  const handleCollectionComplete = () => {
    // Navigate back to collections manager after brief delay
    setTimeout(() => {
      navigate('/collections');
    }, 2000);
  };

  // Loading state
  const isSubmitting = createCollectionsMutation.isPending;

  return (
    <MainLayout title="Create New Collection">
      {/* Breadcrumb Navigation */}
      <div className="mb-6">
        <nav className="flex items-center space-x-2 font-body text-text-secondary">
          <Link 
            to="/collections" 
            className="hover:text-text-primary transition-colors duration-150"
          >
            Collections
          </Link>
          <span>→</span>
          <span className="text-text-primary">New Collection</span>
        </nav>
      </div>
  
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="font-page-title text-text-primary mb-3">
          Create New Collection
        </h1>
        <p className="font-body text-text-secondary max-w-2xl">
          Set up a new Reddit data collection by selecting target subreddits and configuring 
          collection parameters. This will gather posts and comments for use in your analysis projects.
        </p>
      </div>
  
      {/* Wizard Container */}
      <div className="max-w-4xl mx-auto">
        <WizardLayout
          steps={steps}
          currentStep={currentStep}
          onStepClick={currentStep !== 4 ? goToStep : undefined} // Disable step navigation during progress
          canGoBack={canGoBack && currentStep !== 4} // Disable back during progress
          canGoNext={canGoNext && isStepComplete(currentStep)}
          onPrevious={handlePrevious}
          onNext={handleNext}
          onCancel={currentStep !== 4 ? handleCancel : undefined} // No cancel during progress
          isSubmitting={isSubmitting}
          submitText={currentStep === 3 ? 'Start Collection' : 'Next'}
        >
          {/* Step Content */}
          {CurrentStepComponent && (
            <CurrentStepComponent
              formData={formData}
              updateFormData={updateFormData}
              errors={validateCollectionStep(currentStep, formData).errors}
              onComplete={currentStep === 4 ? handleCollectionComplete : undefined}
              createCollectionsMutation={currentStep === 4 ? createCollectionsMutation : undefined}
            />
          )}
        </WizardLayout>
      </div>
  
      {/* Error Display */}
      {createCollectionsMutation.error && currentStep !== 4 && (
        <div className="mt-6 max-w-4xl mx-auto">
          <Card className="border-danger bg-red-50">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-danger" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="font-subsection text-danger">
                  Collection Creation Failed
                </h3>
                <p className="font-body text-text-secondary mt-1">
                  {getErrorMessage(createCollectionsMutation.error) || 'An unexpected error occurred'}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </MainLayout>
  );
};

export default CollectionSetupWizard;