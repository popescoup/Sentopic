/**
 * Loading Spinner Component
 * Terminal-style loading animations with ASCII aesthetic
 */

import React, { useState, useEffect } from 'react';

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
  // Terminal spinner animation frames
  const [frameIndex, setFrameIndex] = useState(0);
  const spinFrames = ['/', '-', '\\', '|'];
  
  useEffect(() => {
    const interval = setInterval(() => {
      setFrameIndex((prev) => (prev + 1) % spinFrames.length);
    }, 150);
    
    return () => clearInterval(interval);
  }, []);

  // Size classes for terminal spinner
  const sizeClasses = {
    sm: 'text-small',
    md: 'text-body',
    lg: 'text-large',
    xl: 'text-title'
  };

  // Text size classes
  const textSizeClasses = {
    sm: 'font-small',
    md: 'font-body',
    lg: 'font-large',
    xl: 'font-title'
  };

  const spinnerElement = (
    <div className={`flex items-center justify-center font-terminal ${centered ? 'h-full' : ''} ${className}`}>
      <div className="flex flex-col items-center">
        {/* Terminal ASCII Spinner */}
        <div className={`text-accent ${sizeClasses[size]} font-bold`}>
          [{spinFrames[frameIndex]}]
        </div>

        {/* Loading message - terminal style */}
        {message && (
          <div className={`mt-2 text-text-secondary ${textSizeClasses[size]} tracking-terminal-wide`}>
            {message.toUpperCase()}
          </div>
        )}
      </div>
    </div>
  );

  // Overlay variant - terminal panel style
  if (overlay) {
    return (
      <div className="fixed inset-0 bg-background bg-opacity-75 flex items-center justify-center z-modal">
        <div className="terminal-panel bg-content p-4">
          {spinnerElement}
        </div>
      </div>
    );
  }

  return spinnerElement;
};

// Terminal inline spinner for buttons
export const InlineSpinner: React.FC<{
  size?: 'sm' | 'md';
  className?: string;
}> = ({ size = 'sm', className = '' }) => {
  const [frameIndex, setFrameIndex] = useState(0);
  const spinFrames = ['/', '-', '\\', '|'];
  
  useEffect(() => {
    const interval = setInterval(() => {
      setFrameIndex((prev) => (prev + 1) % spinFrames.length);
    }, 150);
    
    return () => clearInterval(interval);
  }, []);

  const sizeClasses = {
    sm: 'font-small',
    md: 'font-body'
  };

  return (
    <span className={`font-terminal text-accent ${sizeClasses[size]} ${className}`}>
      {spinFrames[frameIndex]}
    </span>
  );
};

// Terminal loading state for page sections
export const LoadingState: React.FC<{
  title?: string;
  description?: string;
  className?: string;
}> = ({ 
  title = 'LOADING', 
  description = 'PROCESSING DATA...',
  className = ''
}) => {
  return (
    <div className={`flex flex-col items-center justify-center py-12 font-terminal ${className}`}>
      <LoadingSpinner size="lg" />
      <div className="mt-4 text-center">
        <h3 className="font-large text-text-primary mb-2 tracking-terminal-widest">
          {title.toUpperCase()}
        </h3>
        <p className="font-body text-text-secondary max-w-sm tracking-terminal-wide">
          {description.toUpperCase()}
        </p>
      </div>
    </div>
  );
};

// Terminal progress bar component
export const TerminalProgress: React.FC<{
  progress: number; // 0-100
  width?: number; // character width
  className?: string;
}> = ({ progress, width = 20, className = '' }) => {
  const filled = Math.round((progress / 100) * width);
  const empty = width - filled;
  
  return (
    <div className={`font-terminal text-accent ${className}`}>
      [{'='.repeat(filled)}{' '.repeat(empty)}] {progress.toFixed(0)}%
    </div>
  );
};

export default LoadingSpinner;