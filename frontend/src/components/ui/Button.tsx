/**
 * Terminal Button Component
 * Sharp, monospace button with terminal aesthetics
 */

import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button variant - simplified terminal variants */
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'orange';
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

    // Terminal variant classes with hover effects
    const variantClasses = {
      primary: 'bg-accent text-white border-accent font-bold hover:bg-blue-700 hover:border-blue-700 hover:-translate-y-0.5 transition-all duration-100',
      secondary: 'bg-content text-text-secondary border-border hover:bg-hover-panel hover:border-border-dark hover:-translate-y-0.5 transition-all duration-100',
      danger: 'bg-danger text-white border-danger font-bold hover:bg-red-700 hover:border-red-700 hover:-translate-y-0.5 transition-all duration-100',
      success: 'bg-success text-black border-success font-bold hover:bg-green-400 hover:border-green-400 hover:-translate-y-0.5 transition-all duration-100',
      warning: 'bg-warning text-black border-warning font-bold hover:bg-yellow-500 hover:border-yellow-500 hover:-translate-y-0.5 transition-all duration-100',
      orange: 'bg-orange-500 text-white border-orange-500 font-bold hover:bg-orange-600 hover:border-orange-600 hover:-translate-y-0.5 transition-all duration-100'
    };

    // Terminal size classes - dense spacing
    const sizeClasses = {
      sm: 'px-3 py-2 text-small',
      md: 'px-4 py-2.5 text-body',
      lg: 'px-6 py-3 text-large'
    };

    const buttonClasses = [
      // Base terminal button styles
      'inline-flex items-center justify-center',
      'border transition-all duration-100',
      'font-terminal uppercase tracking-terminal-wide',
      'cursor-pointer select-none',
      'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0',
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