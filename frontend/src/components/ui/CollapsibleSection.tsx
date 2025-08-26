/**
 * Collapsible Section Component
 * Reusable component for expandable content sections
 */

import React, { useState } from 'react';
import Button from './Button';

interface CollapsibleSectionProps {
  /** Section title */
  title: string;
  /** Section content */
  children: React.ReactNode;
  /** Whether section starts expanded */
  defaultExpanded?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Icon to display when collapsed */
  collapsedIcon?: React.ReactNode;
  /** Icon to display when expanded */
  expandedIcon?: React.ReactNode;
}

export const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  title,
  children,
  defaultExpanded = false,
  className = '',
  collapsedIcon,
  expandedIcon
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const defaultCollapsedIcon = (
    <svg className="h-4 w-4 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  );

  const defaultExpandedIcon = (
    <svg className="h-4 w-4 transition-transform duration-200 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  );

  return (
    <div className={`border border-border-primary rounded-default bg-content ${className}`}>
      <Button
        variant="ghost"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-panel transition-colors duration-150"
        aria-expanded={isExpanded}
        aria-controls={`section-${title.replace(/\s+/g, '-').toLowerCase()}`}
      >
        <span className="font-subsection text-text-primary">{title}</span>
        <span className="text-text-secondary flex-shrink-0 ml-2">
          {isExpanded 
            ? (expandedIcon || defaultExpandedIcon)
            : (collapsedIcon || defaultCollapsedIcon)
          }
        </span>
      </Button>
      
      <div
        id={`section-${title.replace(/\s+/g, '-').toLowerCase()}`}
        className={`overflow-hidden transition-all duration-300 ease-out ${
          isExpanded ? 'max-h-none opacity-100' : 'max-h-0 opacity-0'
        }`}
        style={{
          maxHeight: isExpanded ? 'none' : '0',
        }}
      >
        <div className="p-4 pt-2 border-t border-border-primary">
          <div className="prose prose-sm max-w-none">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CollapsibleSection;