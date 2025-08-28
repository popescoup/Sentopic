/**
 * Collection Creation Modal
 * Multi-step wizard for creating new Reddit data collections
 */

import React, { useState, useEffect } from 'react';
import { Modal, ModalHeader, ModalBody } from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { SubredditSelector } from './SubredditSelector';
import { CollectionParametersForm } from './CollectionParametersForm';
import { CollectionProgress } from './CollectionProgress';
import { useCreateCollections, useCollectionBatchStatus } from '@/hooks/useApi';
import type { CollectionParams } from '@/types/api';

interface CollectionCreationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

type WizardStep = 'subreddits' | 'parameters' | 'review' | 'progress';

interface FormData {
  subreddits: string[];
  parameters: CollectionParams;
}

const defaultParameters: CollectionParams = {
  sort_method: 'hot',
  time_period: undefined,
  posts_count: 50,
  root_comments: 10,
  replies_per_root: 3,
  min_upvotes: 1
};

export const CollectionCreationModal: React.FC<CollectionCreationModalProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  // State management
  const [currentStep, setCurrentStep] = useState<WizardStep>('subreddits');
  const [formData, setFormData] = useState<FormData>({
    subreddits: [],
    parameters: defaultParameters
  });
  const [batchId, setBatchId] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // API hooks
  const createCollectionsMutation = useCreateCollections();
  const { data: batchStatus, isLoading: isLoadingStatus } = useCollectionBatchStatus(
    batchId || '',
    currentStep === 'progress' && !!batchId
  );

  // Reset state when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setCurrentStep('subreddits');
      setFormData({
        subreddits: [],
        parameters: defaultParameters
      });
      setBatchId(null);
      setErrors({});
    }
  }, [isOpen]);

  // Handle batch completion
  useEffect(() => {
    if (batchStatus && batchStatus.status === 'completed' && onSuccess) {
      // Small delay to show completion state
      const timer = setTimeout(() => {
        onSuccess();
        onClose();
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [batchStatus, onSuccess, onClose]);

  // Step navigation
  const goToStep = (step: WizardStep) => {
    setCurrentStep(step);
    setErrors({});
  };

  const goToNextStep = () => {
    switch (currentStep) {
      case 'subreddits':
        if (validateSubreddits()) {
          goToStep('parameters');
        }
        break;
      case 'parameters':
        if (validateParameters()) {
          goToStep('review');
        }
        break;
      case 'review':
        handleStartCollection();
        break;
    }
  };

  const goToPreviousStep = () => {
    switch (currentStep) {
      case 'parameters':
        goToStep('subreddits');
        break;
      case 'review':
        goToStep('parameters');
        break;
    }
  };

  // Validation
  const validateSubreddits = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (formData.subreddits.length === 0) {
      newErrors.subreddits = 'At least one subreddit is required';
    } else if (formData.subreddits.length > 10) {
      newErrors.subreddits = 'Maximum 10 subreddits allowed';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateParameters = (): boolean => {
    const newErrors: Record<string, string> = {};
    const params = formData.parameters;

    if (params.posts_count < 1 || params.posts_count > 1000) {
      newErrors.posts_count = 'Posts count must be between 1 and 1000';
    }

    if (params.root_comments < 0 || params.root_comments > 100) {
      newErrors.root_comments = 'Root comments must be between 0 and 100';
    }

    if (params.replies_per_root < 0 || params.replies_per_root > 50) {
      newErrors.replies_per_root = 'Replies per root must be between 0 and 50';
    }

    if (params.min_upvotes < 0) {
      newErrors.min_upvotes = 'Minimum upvotes cannot be negative';
    }

    if (['top', 'controversial'].includes(params.sort_method) && !params.time_period) {
      newErrors.time_period = 'Time period is required for top/controversial sorts';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle input submission
  const handleStartCollection = async () => {
    // Go to progress step immediately - don't wait for backend
    goToStep('progress');
    
    // Start the collection request but don't await it
    createCollectionsMutation.mutate(
      {
        subreddits: formData.subreddits,
        collection_params: formData.parameters
      },
      {
        onSuccess: (result) => {
          // When we eventually get the batch ID, set it
          console.log('Collection started successfully, batch ID:', result.batch_id);
          setBatchId(result.batch_id);
        },
        onError: (error) => {
          // Type-safe error handling
          const errorMessage = error instanceof Error ? error.message : 'Failed to start collection';
          
          // If it's a timeout, we assume collection is still running
          if (errorMessage.includes('timeout')) {
            console.log('Request timed out but collection likely still running');
            // Generate a temporary batch ID for simulation purposes
            setBatchId('temp-' + Date.now());
          } else {
            console.error('Failed to start collection:', error);
            setErrors({
              submit: errorMessage
            });
            // Go back to review step on real errors
            goToStep('review');
          }
        }
      }
    );
  };

  // Update form data
  const updateSubreddits = (subreddits: string[]) => {
    setFormData(prev => ({ ...prev, subreddits }));
    setErrors(prev => ({ ...prev, subreddits: '' }));
  };

  const updateParameters = (parameters: CollectionParams) => {
    setFormData(prev => ({ ...prev, parameters }));
    setErrors({});
  };

  // Step content rendering
  const renderStepContent = () => {
    switch (currentStep) {
      case 'subreddits':
        return (
          <SubredditSelector
            selectedSubreddits={formData.subreddits}
            onSelectionChange={updateSubreddits}
            error={errors.subreddits}
          />
        );

      case 'parameters':
        return (
          <CollectionParametersForm
            parameters={formData.parameters}
            onParametersChange={updateParameters}
            errors={errors}
          />
        );

      case 'review':
        return (
          <div className="space-y-6">
            {/* Subreddits Review */}
            <div>
              <h4 className="font-subsection text-text-primary mb-3">
                Target Subreddits ({formData.subreddits.length})
              </h4>
              <div className="flex flex-wrap gap-2">
                {formData.subreddits.map(subreddit => (
                  <span
                    key={subreddit}
                    className="px-3 py-1 bg-hover-blue text-accent rounded-full font-small"
                  >
                    r/{subreddit}
                  </span>
                ))}
              </div>
            </div>

            {/* Parameters Review */}
            <div>
              <h4 className="font-subsection text-text-primary mb-3">
                Collection Parameters
              </h4>
              <div className="bg-panel border border-border-primary rounded-default p-4 space-y-2">
                <div className="flex justify-between">
                  <span className="font-body text-text-secondary">Sort Method:</span>
                  <span className="font-technical text-text-primary capitalize">
                    {formData.parameters.sort_method}
                    {formData.parameters.time_period && ` (${formData.parameters.time_period})`}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="font-body text-text-secondary">Posts per Subreddit:</span>
                  <span className="font-technical text-text-primary">
                    {formData.parameters.posts_count}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="font-body text-text-secondary">Root Comments per Post:</span>
                  <span className="font-technical text-text-primary">
                    {formData.parameters.root_comments}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="font-body text-text-secondary">Replies per Root Comment:</span>
                  <span className="font-technical text-text-primary">
                    {formData.parameters.replies_per_root}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="font-body text-text-secondary">Minimum Upvotes:</span>
                  <span className="font-technical text-text-primary">
                    {formData.parameters.min_upvotes}
                  </span>
                </div>
              </div>
            </div>

            {/* Estimated Stats */}
            <div>
            <h4 className="font-subsection text-text-primary mb-3">
                Estimated Collection Size
            </h4>
            <div className="bg-hover-blue border border-accent rounded-default p-4 space-y-2">
                <div className="flex justify-between">
                <span className="font-body text-text-secondary">Total Posts:</span>
                <span className="font-technical text-accent">
                    ~{formData.subreddits.length * formData.parameters.posts_count}
                </span>
                </div>
                <div className="flex justify-between">
                <span className="font-body text-text-secondary">Expected Comments:</span>
                <span className="font-technical text-accent">
                    ~{formData.subreddits.length * formData.parameters.posts_count * 
                    formData.parameters.root_comments * (1 + formData.parameters.replies_per_root)}
                </span>
                </div>
                <div className="flex justify-between">
  <span className="font-body text-text-secondary">Estimated Duration:</span>
  <span className="font-technical text-accent">
    {(() => {
      // Time coefficients (lower and upper bounds) in seconds per post for comment collection
      const timeCoefficients = {
        'new': { min: 0.6, max: 0.8 },
        'hot': { min: 2.4, max: 3.6 },
        'rising': { min: 2.4, max: 3.6 },
        'top': {
          'hour': { min: 0.7, max: 0.9 },
          'day': { min: 2.6, max: 3.8 },
          'week': { min: 3.0, max: 4.4 },
          'month': { min: 3.0, max: 4.4 },
          'year': { min: 3.3, max: 4.9 },
          'all': { min: 3.3, max: 4.9 }
        },
        'controversial': {
          'hour': { min: 0.6, max: 0.8 },
          'day': { min: 0.7, max: 1.0 },
          'week': { min: 1.0, max: 1.4 },
          'month': { min: 1.4, max: 2.1 },
          'year': { min: 1.9, max: 2.9 },
          'all': { min: 2.5, max: 3.7 }
        }
      };
      
      // Get the time coefficient range for comment collection
      let commentTimeRange: { min: number, max: number };
      if (['new', 'hot', 'rising'].includes(formData.parameters.sort_method)) {
        commentTimeRange = timeCoefficients[formData.parameters.sort_method as keyof typeof timeCoefficients] as { min: number, max: number };
      } else if (['top', 'controversial'].includes(formData.parameters.sort_method) && formData.parameters.time_period) {
        const methodCoeffs = timeCoefficients[formData.parameters.sort_method as 'top' | 'controversial'];
        commentTimeRange = methodCoeffs[formData.parameters.time_period as keyof typeof methodCoeffs] || { min: 3.3, max: 4.9 };
      } else {
        // Fallback for unknown combinations
        commentTimeRange = { min: 3.3, max: 4.9 };
      }
      
      // Calculate time range per subreddit in seconds
      const postCollectionTime = formData.parameters.posts_count / 100; // 1 second per 100 posts
      const commentCollectionTimeMin = formData.parameters.posts_count * commentTimeRange.min;
      const commentCollectionTimeMax = formData.parameters.posts_count * commentTimeRange.max;
      const totalTimePerSubredditMin = postCollectionTime + commentCollectionTimeMin;
      const totalTimePerSubredditMax = postCollectionTime + commentCollectionTimeMax;
      
      // Calculate total time range for all subreddits
      const totalTimeSecondsMin = formData.subreddits.length * totalTimePerSubredditMin;
      const totalTimeSecondsMax = formData.subreddits.length * totalTimePerSubredditMax;
      
      // Convert to minutes - use floor for min, ceil for max to preserve range
        const estimatedMinutesMin = Math.max(1, Math.floor(totalTimeSecondsMin / 60));
        const estimatedMinutesMax = Math.max(1, Math.ceil(totalTimeSecondsMax / 60));

        // Ensure we always have a range (if they're the same, add 1 to max)
        const finalMin = estimatedMinutesMin;
        const finalMax = estimatedMinutesMin === estimatedMinutesMax ? estimatedMinutesMax + 1 : estimatedMinutesMax;

        // Check if both estimates are under 1 minute
        const totalTimeMinutesMin = totalTimeSecondsMin / 60;
        const totalTimeMinutesMax = totalTimeSecondsMax / 60;

        if (totalTimeMinutesMax < 1) {
        return "< 1";
        }

        return `${finalMin} - ${finalMax}`;
    })()} minutes
  </span>
</div>
            </div>
            </div>

            {/* Submit Error */}
            {errors.submit && (
              <div className="p-3 bg-red-50 border border-danger rounded-input">
                <p className="font-body text-danger">{errors.submit}</p>
              </div>
            )}
          </div>
        );

        case 'progress':
            return (
              <CollectionProgress
                batchId={batchId!}
                batchStatus={batchStatus}
                isLoading={isLoadingStatus}
                subreddits={formData.subreddits}
                collectionParams={formData.parameters}
              />
            );

      default:
        return null;
    }
  };

  // Step indicator
  const steps = [
    { id: 'subreddits', label: 'Subreddits', step: 1 },
    { id: 'parameters', label: 'Parameters', step: 2 },
    { id: 'review', label: 'Review', step: 3 },
    { id: 'progress', label: 'Progress', step: 4 }
  ];

  const getCurrentStepIndex = () => steps.findIndex(step => step.id === currentStep);
  const canGoNext = () => {
    switch (currentStep) {
      case 'subreddits':
        return formData.subreddits.length > 0;
      case 'parameters':
        return true; // Validation happens on next click
      case 'review':
        return !createCollectionsMutation.isPending;
      case 'progress':
        return false;
      default:
        return false;
    }
  };

  const canGoPrevious = () => {
    return ['parameters', 'review'].includes(currentStep);
  };

  const getNextButtonText = () => {
    switch (currentStep) {
      case 'subreddits':
        return 'Configure Parameters';
      case 'parameters':
        return 'Review & Confirm';
      case 'review':
        return 'Start Collection';
      default:
        return 'Next';
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={currentStep === 'progress' ? () => {} : onClose}
      title="Create New Collection"
      size="lg"
      closeOnOverlayClick={currentStep !== 'progress'}
      showCloseButton={currentStep !== 'progress'}
    >
      {/* Step Indicator */}
      <div className="flex items-center justify-between mb-6">
        {steps.map((step, index) => {
          const isActive = step.id === currentStep;
          const isCompleted = getCurrentStepIndex() > index;
          const isAccessible = getCurrentStepIndex() >= index;

          return (
            <div key={step.id} className="flex items-center">
              <div
                className={`
                  flex items-center justify-center w-10 h-10 rounded-full text-sm font-medium transition-all duration-150
                  ${isActive 
                    ? 'bg-accent text-white' 
                    : isCompleted 
                      ? 'bg-success text-white'
                      : isAccessible
                        ? 'bg-border-secondary text-text-secondary hover:bg-border-emphasis cursor-pointer'
                        : 'bg-border-primary text-text-tertiary'
                  }
                `}
                onClick={() => isAccessible && currentStep !== 'progress' && goToStep(step.id as WizardStep)}
                >
                {isCompleted ? '✓' : step.step}
              </div>
              <span className={`ml-2 font-small ${isActive ? 'text-text-primary' : 'text-text-secondary'}`}>
                {step.label}
              </span>
              {index < steps.length - 1 && (
                <div className={`mx-4 h-px w-8 ${isCompleted ? 'bg-success' : 'bg-border-primary'}`} />
              )}
            </div>
          );
        })}
      </div>

      {/* Step Content */}
      <div className="max-h-[60vh] overflow-y-auto">
        {renderStepContent()}
      </div>

      {/* Footer Actions */}
      {currentStep !== 'progress' && (
        <div className="flex justify-between items-center pt-6 border-t border-border-primary mt-6">
          <div>
            {canGoPrevious() && (
              <Button
              variant="secondary"
              onClick={goToPreviousStep}
              disabled={createCollectionsMutation.isPending}
            >
              ← PREVIOUS
            </Button>
            )}
          </div>

          <div className="flex space-x-3">
            <Button
              variant="secondary"
              onClick={onClose}
              disabled={createCollectionsMutation.isPending}
            >
              Cancel
            </Button>
            {canGoNext() && (
              <Button
                variant="primary"
                onClick={goToNextStep}
                loading={createCollectionsMutation.isPending}
              >
                {getNextButtonText()}
              </Button>
            )}
          </div>
        </div>
      )}
    </Modal>
  );
};

export default CollectionCreationModal;