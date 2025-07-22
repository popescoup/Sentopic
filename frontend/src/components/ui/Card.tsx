/**
 * Card Component
 * Professional card component with sophisticated styling and variants
 */

import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Whether the card should have hover effects */
  hover?: boolean;
  /** Whether the card is clickable */
  clickable?: boolean;
  /** Card variant styling */
  variant?: 'default' | 'outlined' | 'elevated' | 'panel';
  /** Card padding size */
  padding?: 'none' | 'sm' | 'md' | 'lg';
  /** Additional CSS classes */
  className?: string;
  /** Card content */
  children: React.ReactNode;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ 
    hover = false,
    clickable = false,
    variant = 'default',
    padding = 'md',
    className = '',
    children,
    onClick,
    ...props 
  }, ref) => {
    // Base card classes
    const baseClasses = 'rounded-default transition-all duration-150';
    
    // Variant classes
    const variantClasses = {
      default: 'bg-content border border-border-primary shadow-card',
      outlined: 'bg-content border border-border-secondary',
      elevated: 'bg-content border border-border-primary shadow-card-hover',
      panel: 'bg-panel border border-border-primary'
    };

    // Padding classes
    const paddingClasses = {
      none: '',
      sm: 'p-3',
      md: 'p-4',
      lg: 'p-6'
    };

    // Hover and clickable classes
    const interactiveClasses = [];
    
    if (hover || clickable) {
      interactiveClasses.push('hover-lift');
    }
    
    if (clickable) {
      interactiveClasses.push(
        'cursor-pointer',
        'focus:outline-none',
        'focus:ring-2',
        'focus:ring-accent',
        'focus:ring-offset-2'
      );
    }

    const allClasses = [
      baseClasses,
      variantClasses[variant],
      paddingClasses[padding],
      ...interactiveClasses,
      className
    ].filter(Boolean).join(' ');

    const handleClick = (event: React.MouseEvent<HTMLDivElement>) => {
      if (clickable && onClick) {
        onClick(event);
      }
    };

    const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
      if (clickable && onClick && (event.key === 'Enter' || event.key === ' ')) {
        event.preventDefault();
        onClick(event as any);
      }
    };

    return (
      <div
        ref={ref}
        className={allClasses}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        tabIndex={clickable ? 0 : undefined}
        role={clickable ? 'button' : undefined}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

// Card sub-components for structured content
export const CardHeader: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`pb-3 border-b border-border-primary ${className}`}>
    {children}
  </div>
);

export const CardTitle: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <h3 className={`font-subsection text-text-primary ${className}`}>
    {children}
  </h3>
);

export const CardDescription: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <p className={`font-body text-text-secondary mt-1 ${className}`}>
    {children}
  </p>
);

export const CardContent: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`pt-3 ${className}`}>
    {children}
  </div>
);

export const CardFooter: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`pt-3 mt-3 border-t border-border-primary flex items-center justify-between ${className}`}>
    {children}
  </div>
);

// Insight Card
export const InsightCard: React.FC<{
  title: string;
  value: string | number;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  onClick?: () => void;
  className?: string;
  isArrowCard?: boolean; // New prop for arrow-based cards
}> = ({ 
  title, 
  value, 
  description, 
  trend, 
  trendValue, 
  onClick,
  className = '',
  isArrowCard = false
}) => {
  const trendColors = {
    up: 'text-success',
    down: 'text-danger',
    neutral: 'text-text-tertiary'
  };

  const trendIcons = {
    up: '↗',
    down: '↘',
    neutral: '→'
  };

  return (
    <Card 
      clickable={!!onClick}
      hover={!!onClick}
      onClick={onClick}
      className={className}
    >
      {/* Card header with title */}
      <div className="mb-3">
        <h4 className="font-small uppercase text-text-secondary tracking-wider">
          {title}
        </h4>
      </div>

      {/* Primary value - either number or arrow */}
      <div className="mb-2">
        {isArrowCard ? (
          <div className="flex items-center">
            <span 
              className={`text-4xl font-semibold tracking-tight ${
                trend ? trendColors[trend] : 'text-text-primary'
              }`}
              style={{ fontSize: '48px', lineHeight: '1' }}
            >
              {value}
            </span>
          </div>
        ) : (
          <span 
            className="text-2xl font-semibold text-text-primary tracking-tight"
            style={{ fontSize: '28px', letterSpacing: '-0.01em' }}
          >
            {typeof value === 'number' ? value.toLocaleString() : value}
          </span>
        )}
      </div>

      {/* Description */}
      <div className="mb-2">
        {description && (
          <p className="font-body text-text-secondary leading-relaxed">
            {description}
          </p>
        )}
      </div>

      {/* Legacy trend display (for backwards compatibility) */}
      {!isArrowCard && trend && trendValue && (
        <div className="flex items-center justify-between">
          <div className={`font-small ${trendColors[trend]} flex items-center`}>
            <span className="mr-1">{trendIcons[trend]}</span>
            {trendValue}
          </div>
        </div>
      )}

      {/* Click indicator */}
      {onClick && (
        <div className="mt-3 pt-2 border-t border-border-primary">
          <span className="font-small text-accent">
            Click to explore →
          </span>
        </div>
      )}
    </Card>
  );
};

export default Card;