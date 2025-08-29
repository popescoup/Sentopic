/**
 * App Header Component
 * Terminal-style header with ASCII logo and tab navigation
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

  // Determine current page for tab highlighting
  const isCollectionManager = location.pathname.startsWith('/collections');

  return (
    <header className={className}>
      {/* Top Header Bar - Logo and Actions */}
      <div className="bg-panel">
        <div className="max-w-7xl mx-auto terminal-spacing">
          <div className="flex items-center justify-between" style={{ minHeight: '48px' }}>
            {/* Logo Section */}
            <div className="flex items-center">
              <ASCIILogo 
                showSubtitle={true}
                clickable={true}
              />
            </div>

            {/* Settings and Help - Right Side */}
            <div className="flex items-center space-x-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setIsSettingsOpen(true)}
                className="font-caption"
                aria-label="Open settings"
              >
                SETTINGS
              </Button>

              <Button
                variant="secondary"
                size="sm"
                onClick={() => setIsHelpOpen(true)}
                className="font-caption"
                aria-label="Open help"
              >
                HELP
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation Bar */}
      <div className="bg-panel border-t border-b border-border">
        <div className="flex">
          {/* Projects Tab - Half Width */}
          <Link
            to="/"
            className={`flex-1 px-4 py-2 font-caption border-r border-border transition-colors duration-100 text-center ${
              !isCollectionManager
                ? 'bg-background text-text-primary font-bold border-b-0'
                : 'text-text-secondary hover:text-text-primary hover:bg-hover-panel'
            }`}
            style={{
              marginBottom: !isCollectionManager ? '-1px' : '0'
            }}
          >
            PROJECTS
          </Link>

          {/* Collections Tab - Half Width */}
          <Link
            to="/collections"
            className={`flex-1 px-4 py-2 font-caption transition-colors duration-100 text-center ${
              isCollectionManager
                ? 'bg-background text-text-primary font-bold border-b-0'
                : 'text-text-secondary hover:text-text-primary hover:bg-hover-panel'
            }`}
            style={{
              marginBottom: isCollectionManager ? '-1px' : '0'
            }}
          >
            COLLECTIONS
          </Link>
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