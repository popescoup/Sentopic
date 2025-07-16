/**
 * Loading Spinner Component
 * Professional loading animations with different variants
 */

import React from 'react';

interface LoadingSpinnerProps {
  /** Size of the spinner */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Loading message to display */
  message?: string;
  /** Whether to center the spinner */
  centered?: boolean;
  /** Whether to show as a full-page overlay */
  overlay?: boolean;
  /** Additional CSS classes */
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  message,
  centered = false,
  overlay = false,
  className = ''
}) => {
  // Size classes for spinner
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12'
  };

  // Text size classes
  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl'
  };

  const spinnerElement = (
    <div className={`flex items-center justify-center ${centered ? 'h-full' : ''} ${className}`}>
      <div className="flex flex-col items-center">
        {/* Spinner */}
        <svg
          className={`animate-spin text-accent ${sizeClasses[size]}`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          aria-label="Loading"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>

        {/* Loading message */}
        {message && (
          <p className={`mt-3 text-text-secondary ${textSizeClasses[size]} animate-pulse`}>
            {message}
          </p>
        )}
      </div>
    </div>
  );

  // Overlay variant
  if (overlay) {
    return (
      <div className="fixed inset-0 bg-background bg-opacity-75 backdrop-blur-sm flex items-center justify-center z-modal">
        <div className="bg-content rounded-default p-6 shadow-modal">
          {spinnerElement}
        </div>
      </div>
    );
  }

  return spinnerElement;
};

// Simple inline spinner for buttons and small spaces
export const InlineSpinner: React.FC<{
  size?: 'sm' | 'md';
  className?: string;
}> = ({ size = 'sm', className = '' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5'
  };

  return (
    <svg
      className={`animate-spin ${sizeClasses[size]} ${className}`}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-label="Loading"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
};

// Professional loading state for entire page sections
export const LoadingState: React.FC<{
  title?: string;
  description?: string;
  className?: string;
}> = ({ 
  title = 'Loading...', 
  description = 'Please wait while we fetch your data.',
  className = ''
}) => {
  return (
    <div className={`flex flex-col items-center justify-center py-12 ${className}`}>
      <LoadingSpinner size="lg" />
      <div className="mt-6 text-center">
        <h3 className="font-subsection text-text-primary mb-2">
          {title}
        </h3>
        <p className="font-body text-text-secondary max-w-sm">
          {description}
        </p>
      </div>
    </div>
  );
};

export default LoadingSpinner;