/**
 * ASCII Logo Component
 * Terminal-style ASCII logo with sharp monospace aesthetic
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
    <div className={`font-terminal select-none ${className}`}>
      <div 
        className="text-text-primary hover:text-accent transition-colors duration-100"
        style={{
          fontSize: '10px',
          lineHeight: '1.1',
          letterSpacing: '0'
        }}
      >
        {/* ASCII Logo - Clean SENTOPIC */}
        <div className="whitespace-pre font-terminal">
{`                               
  _  _   _  _/_  _    _   .  _ 
_\  /_' / / /   /_/  /_/ /  /_ 
                    /          `}
        </div>
        
        {/* Subtitle - terminal style */}
        {showSubtitle && (
          <div className="hidden sm:block mt-1 font-caption text-text-tertiary tracking-terminal-widest">
            REDDIT ANALYTICS
          </div>
        )}
        
        {/* Mobile text fallback - also terminal style */}
        {showSubtitle && (
          <div className="block sm:hidden font-large text-text-primary tracking-terminal-wide">
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
        className="block focus:outline-none focus:ring-2 focus:ring-accent"
        aria-label="Return to Projects Dashboard"
      >
        {logoContent}
      </Link>
    );
  }

  return logoContent;
};

export default ASCIILogo;