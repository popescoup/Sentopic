/**
 * Input Component
 * Professional input fields with sophisticated styling and validation
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
    /** Input size variant */
    size?: 'sm' | 'md' | 'lg';
    /** Whether the input spans full width */
    fullWidth?: boolean;
    /** Icon to display before input text */
    startIcon?: React.ReactNode;
    /** Icon to display after input text */
    endIcon?: React.ReactNode;
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
    startIcon,
    endIcon,
    className = '',
    id,
    ...props
  }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const isError = hasError || !!error;

    // Size classes
    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-3 py-2 text-body',
      lg: 'px-4 py-3 text-base'
    };

    // Base input classes
    const baseInputClasses = [
      'border rounded-input transition-all duration-150',
      'focus:outline-none focus:ring-2 focus:ring-offset-1',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'placeholder:text-text-tertiary',
      sizeClasses[size],
      fullWidth ? 'w-full' : ''
    ];

    // Conditional classes based on state
    const stateClasses = isError
      ? [
          'border-danger bg-red-50',
          'focus:border-danger focus:ring-danger'
        ]
      : [
          'border-border-secondary bg-content',
          'hover:border-border-emphasis',
          'focus:border-accent focus:ring-accent'
        ];

    const inputClasses = [...baseInputClasses, ...stateClasses, className]
      .filter(Boolean)
      .join(' ');

    // Wrapper classes for icons
    const hasIcons = startIcon || endIcon;
    const wrapperClasses = hasIcons
      ? 'relative flex items-center'
      : '';

    const inputElement = (
      <input
        ref={ref}
        id={inputId}
        className={inputClasses}
        {...props}
      />
    );

    const inputWithIcons = hasIcons ? (
      <div className={`${wrapperClasses} ${fullWidth ? 'w-full' : ''}`}>
        {startIcon && (
          <div className="absolute left-3 flex items-center pointer-events-none text-text-tertiary">
            {startIcon}
          </div>
        )}
        
        <input
          ref={ref}
          id={inputId}
          className={`${inputClasses} ${startIcon ? 'pl-10' : ''} ${endIcon ? 'pr-10' : ''}`}
          {...props}
        />
        
        {endIcon && (
          <div className="absolute right-3 flex items-center pointer-events-none text-text-tertiary">
            {endIcon}
          </div>
        )}
      </div>
    ) : inputElement;

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {/* Label */}
        {label && (
          <label
            htmlFor={inputId}
            className="block font-medium text-text-primary mb-2"
          >
            {label}
          </label>
        )}

        {/* Input */}
        {inputWithIcons}

        {/* Error message */}
        {error && (
          <p className="mt-1 text-sm text-danger">
            {error}
          </p>
        )}

        {/* Help text */}
        {helpText && !error && (
          <p className="mt-1 text-sm text-text-tertiary">
            {helpText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

// Textarea component with similar styling
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

    // Resize classes
    const resizeClasses = {
      none: 'resize-none',
      vertical: 'resize-y',
      horizontal: 'resize-x',
      both: 'resize'
    };

    // Base textarea classes
    const baseClasses = [
      'px-3 py-2 text-body border rounded-input transition-all duration-150',
      'focus:outline-none focus:ring-2 focus:ring-offset-1',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'placeholder:text-text-tertiary',
      resizeClasses[resize],
      fullWidth ? 'w-full' : ''
    ];

    // Conditional classes based on state
    const stateClasses = isError
      ? [
          'border-danger bg-red-50',
          'focus:border-danger focus:ring-danger'
        ]
      : [
          'border-border-secondary bg-content',
          'hover:border-border-emphasis',
          'focus:border-accent focus:ring-accent'
        ];

    const textareaClasses = [...baseClasses, ...stateClasses, className]
      .filter(Boolean)
      .join(' ');

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {/* Label */}
        {label && (
          <label
            htmlFor={textareaId}
            className="block font-medium text-text-primary mb-2"
          >
            {label}
          </label>
        )}

        {/* Textarea */}
        <textarea
          ref={ref}
          id={textareaId}
          className={textareaClasses}
          {...props}
        />

        {/* Error message */}
        {error && (
          <p className="mt-1 text-sm text-danger">
            {error}
          </p>
        )}

        {/* Help text */}
        {helpText && !error && (
          <p className="mt-1 text-sm text-text-tertiary">
            {helpText}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export default Input;