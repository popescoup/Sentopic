/**
 * Progress Indicator Component
 * Professional step progress visualization for wizards
 */

import React from 'react';
import type { WizardStep } from './WizardLayout';

export interface ProgressIndicatorProps {
  /** Array of steps */
  steps: WizardStep[];
  /** Current active step */
  currentStep: number;
  /** Step click handler - if provided, steps become clickable */
  onStepClick?: (step: number) => void;
  /** Show step descriptions */
  showDescriptions?: boolean;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Additional CSS classes */
  className?: string;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  steps,
  currentStep,
  onStepClick,
  showDescriptions = false,
  size = 'md',
  className = ''
}) => {
  const getStepStatus = (stepId: number) => {
    return {
      isComplete: stepId < currentStep,
      isCurrent: stepId === currentStep,
      isFuture: stepId > currentStep,
      isAccessible: stepId <= currentStep,
    };
  };

  const sizeClasses = {
    sm: {
      container: 'py-4',
      circle: 'w-8 h-8 text-sm',
      connector: 'h-0.5',
      title: 'text-sm',
      description: 'text-xs',
    },
    md: {
      container: 'py-6',
      circle: 'w-10 h-10 text-base',
      connector: 'h-0.5',
      title: 'text-base',
      description: 'text-sm',
    },
    lg: {
      container: 'py-8',
      circle: 'w-12 h-12 text-lg',
      connector: 'h-1',
      title: 'text-lg',
      description: 'text-base',
    },
  };

  const classes = sizeClasses[size];

  return (
    <div className={`w-full ${classes.container} ${className}`}>
      {/* Desktop Layout */}
      <div className="hidden md:block">
      <div className="flex items-start justify-between relative">
          {/* Background connector line */}
          <div className="absolute inset-0 flex items-center z-0">
            <div className="w-full">
              <div className={`${classes.connector} bg-border-secondary`} />
            </div>
          </div>

          {/* Step indicators */}
          {steps.map((step, index) => {
            const status = getStepStatus(step.id);
            const isClickable = onStepClick && status.isAccessible;

            return (
              <div
                key={step.id}
                className="relative flex flex-col items-center"
              >
                {/* Step Circle */}
                <button
                  onClick={() => isClickable && onStepClick(step.id)}
                  disabled={!isClickable}
                  className={`
                    relative flex items-center justify-center font-semibold
                    ${classes.circle} rounded-full border-2 transition-all duration-200
                    ${status.isComplete
                      ? 'bg-success border-success text-white shadow-sm'
                      : status.isCurrent
                      ? 'bg-accent border-accent text-white shadow-sm'
                      : 'bg-content border-border-secondary text-text-tertiary'
                    }
                    ${isClickable 
                      ? 'hover:scale-105 cursor-pointer focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2'
                      : 'cursor-default'
                    }
                  `}
                >
                  {status.isComplete ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span>{step.id}</span>
                  )}
                </button>

                {/* Step Label */}
                <div className="mt-3 text-center max-w-[120px]">
                  <div className={`
                    font-medium ${classes.title}
                    ${status.isCurrent ? 'text-text-primary' : 'text-text-secondary'}
                  `}>
                    {step.title}
                  </div>
                  {showDescriptions && (
                    <div className={`
                      mt-1 ${classes.description} text-text-tertiary
                    `}>
                      {step.description}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Mobile Layout */}
      <div className="block md:hidden">
        <div className="flex items-center space-x-4">
          {/* Current Step Circle */}
          <div className={`
            flex items-center justify-center font-semibold
            ${classes.circle} rounded-full border-2 bg-accent border-accent text-white
          `}>
            {currentStep}
          </div>

          {/* Step Info */}
          <div className="flex-1 min-w-0">
            <div className={`font-medium ${classes.title} text-text-primary`}>
              {steps.find(s => s.id === currentStep)?.title}
            </div>
            <div className={`${classes.description} text-text-secondary`}>
              Step {currentStep} of {steps.length}
            </div>
          </div>

          {/* Progress Bar */}
          <div className="flex-1 min-w-0">
            <div className="w-full bg-border-secondary rounded-full h-2">
              <div 
                className="bg-accent h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentStep / steps.length) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressIndicator;