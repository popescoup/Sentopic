/**
 * Terminal Input Component
 * Sharp, monospace form fields with terminal aesthetics
 */

import React from 'react';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Input label */
  label?: string;
  /** Error message to display */
  error?: string;
  /** Help text to display below input */
  helpText?: string;
  /** Whether the input is in an error state */
  hasError?: boolean;
  /** Input size variant - terminal sizes */
  size?: 'sm' | 'md' | 'lg';
  /** Whether the input spans full width */
  fullWidth?: boolean;
  /** Additional CSS classes */
  className?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({
    label,
    error,
    helpText,
    hasError,
    size = 'md',
    fullWidth = false,
    className = '',
    id,
    ...props
  }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const isError = hasError || !!error;

    // Terminal size classes - dense spacing
    const sizeClasses = {
      sm: 'px-1.5 py-1 text-body',     // 12px (was 10px)
      md: 'px-2 py-1 text-large',      // 14px (was 12px)
      lg: 'px-2 py-1.5 text-title'     // 16px (was 14px)
    };

    // Base terminal input classes
    const baseInputClasses = [
      'terminal-input',
      'border transition-all duration-100',
      'focus:outline-none focus:ring-2 focus:ring-offset-1',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'placeholder:text-text-tertiary placeholder:uppercase',
      'font-terminal',
      sizeClasses[size],
      fullWidth ? 'w-full' : ''
    ];

    // State-based classes
    const stateClasses = isError
      ? [
          'border-danger bg-red-50',
          'focus:border-danger focus:ring-danger'
        ]
      : [
          'border-border bg-content',
          'hover:border-border-dark',
          'focus:border-accent focus:ring-accent'
        ];

    const inputClasses = [...baseInputClasses, ...stateClasses, className]
      .filter(Boolean)
      .join(' ');

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {/* Terminal label */}
        {label && (
          <label
            htmlFor={inputId}
            className="block font-small text-text-primary mb-1 font-bold tracking-terminal-wide"
          >
            {label.toUpperCase()}
          </label>
        )}

        {/* Input field */}
        <input
          ref={ref}
          id={inputId}
          className={inputClasses}
          {...props}
        />

        {/* Error message - terminal style */}
        {error && (
          <p className="mt-1 font-caption text-danger font-bold tracking-terminal-wide">
            ERROR: {error.toUpperCase()}
          </p>
        )}

        {/* Help text - terminal style */}
        {helpText && !error && (
          <p className="mt-1 font-caption text-text-tertiary tracking-terminal-wide">
            {helpText.toUpperCase()}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

// Terminal Textarea component
export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helpText?: string;
  hasError?: boolean;
  fullWidth?: boolean;
  resize?: 'none' | 'vertical' | 'horizontal' | 'both';
  className?: string;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({
    label,
    error,
    helpText,
    hasError,
    fullWidth = false,
    resize = 'vertical',
    className = '',
    id,
    ...props
  }, ref) => {
    const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;
    const isError = hasError || !!error;

    // Terminal resize classes
    const resizeClasses = {
      none: 'resize-none',
      vertical: 'resize-y',
      horizontal: 'resize-x',
      both: 'resize'
    };

    // Base terminal textarea classes
    const baseClasses = [
      'terminal-input',
      'px-2 py-1 text-body border transition-all duration-100',
      'focus:outline-none focus:ring-2 focus:ring-offset-1',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'placeholder:text-text-tertiary placeholder:uppercase',
      'font-terminal',
      resizeClasses[resize],
      fullWidth ? 'w-full' : ''
    ];

    // State-based classes
    const stateClasses = isError
      ? [
          'border-danger bg-red-50',
          'focus:border-danger focus:ring-danger'
        ]
      : [
          'border-border bg-content',
          'hover:border-border-dark',
          'focus:border-accent focus:ring-accent'
        ];

    const textareaClasses = [...baseClasses, ...stateClasses, className]
      .filter(Boolean)
      .join(' ');

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {/* Terminal label */}
        {label && (
          <label
            htmlFor={textareaId}
            className="block font-small text-text-primary mb-1 font-bold tracking-terminal-wide"
          >
            {label.toUpperCase()}
          </label>
        )}

        {/* Textarea field */}
        <textarea
          ref={ref}
          id={textareaId}
          className={textareaClasses}
          {...props}
        />

        {/* Error message - terminal style */}
        {error && (
          <p className="mt-1 font-caption text-danger font-bold tracking-terminal-wide">
            ERROR: {error.toUpperCase()}
          </p>
        )}

        {/* Help text - terminal style */}
        {helpText && !error && (
          <p className="mt-1 font-caption text-text-tertiary tracking-terminal-wide">
            {helpText.toUpperCase()}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export default Input;