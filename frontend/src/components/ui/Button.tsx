/**
 * Button Component
 * Professional button with sophisticated styling and variants
 */

import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  /** Whether button spans full width */
  fullWidth?: boolean;
  /** Whether the button is in a loading state */
  loading?: boolean;
  /** Icon to display before the button text */
  startIcon?: React.ReactNode;
  /** Icon to display after the button text */
  endIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className = '', 
    variant = 'primary', 
    size = 'md', 
    fullWidth = false,
    loading = false,
    startIcon,
    endIcon,
    disabled,
    children,
    ...props 
  }, ref) => {
    const isDisabled = disabled || loading;

    // Variant classes
    const variantClasses = {
      primary: 'bg-accent text-white border border-accent hover:bg-blue-700 hover:border-blue-700 focus:ring-accent active:bg-blue-800',
      secondary: 'bg-panel text-text-primary border border-border-primary hover:bg-gray-100 hover:border-border-secondary focus:ring-border-emphasis active:bg-gray-200',
      outline: 'bg-transparent text-accent border border-accent hover:bg-hover-blue focus:ring-accent active:bg-blue-50',
      ghost: 'bg-transparent text-text-secondary border border-transparent hover:bg-hover-blue hover:text-text-primary focus:ring-border-emphasis active:bg-gray-100',
      danger: 'bg-danger text-white border border-danger hover:bg-red-700 hover:border-red-700 focus:ring-danger active:bg-red-800',
      success: 'bg-success text-white border border-success hover:bg-green-700 hover:border-green-700 focus:ring-success active:bg-green-800'
    };

    // Size classes
    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm rounded-input',
      md: 'px-4 py-2 text-body rounded-default',
      lg: 'px-5 py-3 text-base rounded-default'
    };

    const buttonClasses = [
      'inline-flex items-center justify-center font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
      variantClasses[variant],
      sizeClasses[size],
      fullWidth ? 'w-full' : '',
      className
    ].filter(Boolean).join(' ');

    return (
      <button
        className={buttonClasses}
        ref={ref}
        disabled={isDisabled}
        {...props}
      >
        {/* Loading spinner */}
        {loading && (
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
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
        )}

        {/* Start icon */}
        {!loading && startIcon && (
          <span className="mr-2 -ml-1 flex-shrink-0">
            {startIcon}
          </span>
        )}

        {/* Button content */}
        <span className="truncate">
          {children}
        </span>

        {/* End icon */}
        {!loading && endIcon && (
          <span className="ml-2 -mr-1 flex-shrink-0">
            {endIcon}
          </span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;