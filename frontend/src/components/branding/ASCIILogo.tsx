/**
 * ASCII Logo Component
 * Implements the modular geometric logo design from specifications
 */

import React from 'react';
import { Link } from 'react-router-dom';

interface ASCIILogoProps {
  /** Whether to show the full logo with subtitle */
  showSubtitle?: boolean;
  /** Whether the logo should be clickable (navigation to dashboard) */
  clickable?: boolean;
  /** Additional CSS classes */
  className?: string;
}

export const ASCIILogo: React.FC<ASCIILogoProps> = ({ 
  showSubtitle = true, 
  clickable = true,
  className = ''
}) => {
  const logoContent = (
    <div className={`font-mono select-none ${className}`}>
      <div 
        className="text-text-secondary hover:text-text-primary transition-colors duration-150"
        style={{
          fontSize: '11px',
          lineHeight: '1.0',
          letterSpacing: '0'
        }}
      >
        {/* Modular Geometric ASCII Logo */}
        <div className="whitespace-pre">
{`┌─┐┌─┐┌┐┌┌┬┐┌─┐┌─┐┬┌─┐
└─┐├┤ │││ │ │ │├─┘││  
└─┘└─┘┘└┘ ┴ └─┘┴  ┴└─┘`}
        </div>
        
        {/* Subtitle - only show on desktop/tablet */}
        {showSubtitle && (
          <div className="hidden sm:block mt-1 text-[9px] tracking-wider text-text-tertiary">
            REDDIT ANALYTICS
          </div>
        )}
        
        {/* Mobile text fallback */}
        {showSubtitle && (
          <div className="block sm:hidden text-sm font-sans font-semibold text-text-secondary">
            SENTOPIC
          </div>
        )}
      </div>
    </div>
  );

  if (clickable) {
    return (
      <Link 
        to="/" 
        className="block focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 rounded-sm"
        aria-label="Return to Projects Dashboard"
      >
        {logoContent}
      </Link>
    );
  }

  return logoContent;
};

export default ASCIILogo;