/**
 * Terminal Card/Panel Component
 * Sharp, database-style panels with terminal aesthetics
 */

import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Whether the card should have hover effects */
  hover?: boolean;
  /** Whether the card is clickable */
  clickable?: boolean;
  /** Card variant styling - simplified for terminal */
  variant?: 'default' | 'panel' | 'data';
  /** Card padding size - terminal density */
  padding?: 'none' | 'sm' | 'md';
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
    // Terminal card variants
    const variantClasses = {
      default: 'terminal-panel bg-content',
      panel: 'bg-panel border-border-dark',
      data: 'bg-content border-border' // For data tables
    };

    // Terminal padding - dense spacing
    const paddingClasses = {
      none: '',
      sm: 'p-1.5',
      md: 'p-2'
    };

    // Interactive classes
    const interactiveClasses = [];
    
    if (hover || clickable) {
      interactiveClasses.push('terminal-hover-lift');
    }
    
    if (clickable) {
      interactiveClasses.push(
        'cursor-pointer',
        'focus:outline-none',
        'focus:ring-2',
        'focus:ring-accent'
      );
    }

    const allClasses = [
      'terminal-border',
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

// Terminal Panel sub-components
export const CardHeader: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`terminal-panel-header ${className}`}>
    {children}
  </div>
);

export const CardTitle: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <h3 className={`font-large text-text-primary text-command ${className}`}>
    {children}
  </h3>
);

export const CardDescription: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <p className={`font-small text-text-secondary mt-1 ${className}`}>
    {children}
  </p>
);

export const CardContent: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`terminal-panel-content ${className}`}>
    {children}
  </div>
);

export const CardFooter: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`pt-1.5 mt-1.5 border-t border-border flex items-center justify-between ${className}`}>
    {children}
  </div>
);

// Terminal Insight Card - Updated for ASCII aesthetic
export const InsightCard: React.FC<{
  title: string;
  value: string | number;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
  onClick?: () => void;
  className?: string;
  isArrowCard?: boolean;
}> = ({ 
  title, 
  value, 
  description, 
  trend, 
  onClick,
  className = '',
  isArrowCard = false
}) => {
  const trendColors = {
    up: 'text-success',
    down: 'text-danger',
    neutral: 'text-text-tertiary'
  };

  // Terminal trend symbols
  const trendSymbols = {
    up: '↗',
    down: '↘',
    neutral: '→'
  };

  return (
    <Card 
      clickable={!!onClick}
      hover={!!onClick}
      onClick={onClick}
      padding="sm"
      className={className}
    >
      {/* Terminal title */}
      <div className="mb-1.5">
        <h4 className="font-caption text-text-secondary tracking-terminal-widest">
          {title.toUpperCase()}
        </h4>
      </div>

      {/* Primary value - terminal styling */}
      <div className="mb-1">
        {isArrowCard ? (
          <div className="flex items-center">
            <span 
              className={`text-4xl font-bold font-terminal tracking-tight ${
                trend ? trendColors[trend] : 'text-text-primary'
              }`}
              style={{ fontSize: '32px', lineHeight: '1' }}
            >
              {value}
            </span>
          </div>
        ) : (
          <span 
            className="text-xl font-bold text-text-primary font-terminal tracking-tight"
            style={{ fontSize: '20px', letterSpacing: '-0.01em' }}
          >
            {typeof value === 'number' ? value.toLocaleString() : value}
          </span>
        )}
      </div>

      {/* Description */}
      {description && (
        <div className="mb-1">
          <p className="font-small text-text-secondary leading-terminal">
            {description.toUpperCase()}
          </p>
        </div>
      )}

      {/* Terminal trend display */}
      {!isArrowCard && trend && (
        <div className="flex items-center justify-start">
          <div className={`font-caption ${trendColors[trend]} flex items-center`}>
            <span className="mr-1">{trendSymbols[trend]}</span>
            <span className="text-command">TREND</span>
          </div>
        </div>
      )}

      {/* Click indicator - terminal style */}
      {onClick && (
        <div className="mt-1.5 pt-1 border-t border-border">
          <span className="font-caption text-accent text-command">
          {">"} VIEW_DETAILS
          </span>
        </div>
      )}
    </Card>
  );
};

export default Card;