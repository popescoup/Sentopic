/**
 * App Header Component
 * Professional header with ASCII logo, navigation, and settings
 */

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import ASCIILogo from '@/components/branding/ASCIILogo';
import Button from '@/components/ui/Button';
import SettingsModal from '@/components/settings/SettingsModal';
import HelpModal from '@/components/modals/HelpModal';

interface AppHeaderProps {
  /** Additional CSS classes */
  className?: string;
}

export const AppHeader: React.FC<AppHeaderProps> = ({ className = '' }) => {
  const location = useLocation();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  // Determine if we're on collection manager page
  const isCollectionManager = location.pathname.startsWith('/collections');

  return (
    <header className={`bg-gradient-header border-b border-border-primary relative z-header ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo Section */}
          <div className="flex items-center">
            <ASCIILogo 
              showSubtitle={true}
              clickable={true}
              className="mr-6"
            />
          </div>

          {/* Navigation Section */}
          <div className="flex items-center space-x-4">
            {/* Collection Manager Link */}
            <Link
              to="/collections"
              className={`px-3 py-2 rounded-input text-sm font-medium transition-colors duration-150 ${
                isCollectionManager
                  ? 'bg-accent text-white'
                  : 'text-text-secondary hover:text-text-primary hover:bg-hover-blue'
              }`}
            >
              Collection Manager
            </Link>

            {/* Divider */}
            <div className="h-4 w-px bg-border-secondary" />

            {/* Settings Menu */}
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsSettingsOpen(true)}
                className="text-text-secondary hover:text-text-primary"
                aria-label="Open settings"
              >
                ⚙️ Settings
              </Button>
            </div>

            {/* Help Menu */}
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsHelpOpen(true)}
                className="text-text-secondary hover:text-text-primary"
                aria-label="Open help"
              >
                ? Help
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      <SettingsModal 
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />

      {/* Help Modal */}
      <HelpModal 
        isOpen={isHelpOpen}
        onClose={() => setIsHelpOpen(false)}
      />
    </header>
  );
};

export default AppHeader;