/**
 * Terminal Button Component
 * Sharp, monospace button with terminal aesthetics
 */

import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button variant - simplified terminal variants */
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning';
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  /** Whether button spans full width */
  fullWidth?: boolean;
  /** Whether the button is in a loading state */
  loading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className = '', 
    variant = 'secondary', 
    size = 'md', 
    fullWidth = false,
    loading = false,
    disabled,
    children,
    ...props 
  }, ref) => {
    const isDisabled = disabled || loading;

    // Terminal variant classes
    const variantClasses = {
      primary: 'bg-accent text-white border-accent font-bold',
      secondary: 'bg-content text-text-secondary border-border hover:bg-hover-panel hover:border-border-dark',
      danger: 'bg-danger text-white border-danger font-bold',
      success: 'bg-success text-black border-success font-bold',
      warning: 'bg-warning text-black border-warning font-bold'
    };

    // Terminal size classes - dense spacing
    const sizeClasses = {
      sm: 'px-1.5 py-1 text-caption',
      md: 'px-2 py-1 text-body',
      lg: 'px-3 py-1.5 text-large'
    };

    const buttonClasses = [
      // Base terminal button styles
      'terminal-btn',
      'inline-flex items-center justify-center',
      'border transition-all duration-100',
      'font-terminal uppercase tracking-terminal-wide',
      'cursor-pointer select-none',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-accent',
      // Variant and size
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
        {/* Terminal loading indicator - simple spinning character */}
        {loading && (
          <span className="animate-terminal-spin mr-1" aria-hidden="true">
            /
          </span>
        )}

        {/* Button content */}
        <span className={loading ? 'opacity-75' : ''}>
          {children}
        </span>
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;