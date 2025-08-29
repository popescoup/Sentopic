/**
 * Terminal Collapsible Section Component
 * Sharp, database-style expandable sections with terminal aesthetics
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
}

export const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  title,
  children,
  defaultExpanded = false,
  className = ''
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className={`bg-content border border-border ${className}`}>
      <Button
        variant="secondary"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between bg-panel text-left hover:bg-hover-panel transition-colors duration-100 border-0"
        aria-expanded={isExpanded}
        aria-controls={`section-${title.replace(/\s+/g, '-').toLowerCase()}`}
      >
        <span className="font-large text-text-primary tracking-terminal-wide font-bold">{title.toUpperCase()}</span>
        <span className="text-text-secondary flex-shrink-0 ml-2 font-terminal tracking-terminal-wide">
          {isExpanded ? '[-]' : '[+]'}
        </span>
      </Button>
      
      <div
        id={`section-${title.replace(/\s+/g, '-').toLowerCase()}`}
        className={`overflow-hidden transition-all duration-100 ease-out ${
          isExpanded ? 'max-h-none opacity-100' : 'max-h-0 opacity-0'
        }`}
        style={{
          maxHeight: isExpanded ? 'none' : '0',
        }}
      >
        <div className="border-t border-border p-2 font-terminal">
          {children}
        </div>
      </div>
    </div>
  );
};

export default CollapsibleSection;