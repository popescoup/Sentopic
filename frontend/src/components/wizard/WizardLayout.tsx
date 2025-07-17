/**
 * Wizard Layout Component
 * Reusable wizard shell providing consistent layout and navigation
 */

import React from 'react';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import ProgressIndicator from './ProgressIndicator';

export interface WizardStep {
  id: number;
  title: string;
  description: string;
  component?: React.ComponentType<any>;
}

export interface WizardLayoutProps {
  /** Array of step configurations */
  steps: WizardStep[];
  /** Current active step */
  currentStep: number;
  /** Whether user can navigate backwards */
  canGoBack: boolean;
  /** Whether user can navigate forwards */
  canGoNext: boolean;
  /** Whether form is submitting */
  isSubmitting?: boolean;
  /** Text for the next/submit button */
  submitText?: string;
  /** Step content */
  children: React.ReactNode;
  /** Step click handler */
  onStepClick?: (step: number) => void;
  /** Previous button handler */
  onPrevious: () => void;
  /** Next button handler */
  onNext: () => void;
  /** Cancel button handler */
  onCancel: () => void;
  /** Additional CSS classes */
  className?: string;
}

export const WizardLayout: React.FC<WizardLayoutProps> = ({
  steps,
  currentStep,
  canGoBack,
  canGoNext,
  isSubmitting = false,
  submitText = 'Next',
  children,
  onStepClick,
  onPrevious,
  onNext,
  onCancel,
  className = ''
}) => {
  const currentStepConfig = steps.find(step => step.id === currentStep);
  const isLastStep = currentStep === steps.length;

  return (
    <div className={`w-full ${className}`}>
      {/* Progress Indicator */}
      <div className="mb-8">
        <ProgressIndicator
          steps={steps}
          currentStep={currentStep}
          onStepClick={onStepClick}
        />
      </div>

      {/* Main Content Card */}
      <Card className="mb-6">
        {/* Step Header */}
        <div className="border-b border-border-primary pb-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-section-header text-text-primary mb-2">
                {currentStepConfig?.title}
              </h2>
              <p className="font-body text-text-secondary">
                {currentStepConfig?.description}
              </p>
            </div>
            <div className="text-right">
              <span className="font-small text-text-tertiary">
                Step {currentStep} of {steps.length}
              </span>
            </div>
          </div>
        </div>

        {/* Step Content */}
        <div className="min-h-[400px]">
          {children}
        </div>
      </Card>

      {/* Navigation Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {/* Cancel Button */}
          <Button
            variant="ghost"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>

          {/* Previous Button */}
          <Button
            variant="secondary"
            onClick={onPrevious}
            disabled={!canGoBack || isSubmitting}
          >
            ← Previous
          </Button>
        </div>

        <div className="flex items-center space-x-3">
          {/* Progress Text */}
          <span className="font-body text-text-tertiary">
            {currentStep} of {steps.length}
          </span>

          {/* Next/Submit Button */}
          <Button
            variant="primary"
            onClick={onNext}
            disabled={!canGoNext || isSubmitting}
            loading={isSubmitting}
          >
            {isLastStep ? (submitText || 'Create Project') : 'Next →'}
          </Button>
        </div>
      </div>

      {/* Step Completion Status */}
      <div className="mt-4 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          {steps.map((step, index) => {
            const isComplete = step.id < currentStep;
            const isCurrent = step.id === currentStep;
            
            return (
              <div
                key={step.id}
                className={`w-2 h-2 rounded-full transition-all duration-200 ${
                  isComplete
                    ? 'bg-success'
                    : isCurrent
                    ? 'bg-accent'
                    : 'bg-border-secondary'
                }`}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default WizardLayout;