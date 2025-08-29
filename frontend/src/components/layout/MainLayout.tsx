/**
 * Main Layout Component
 * Provides consistent layout structure for all pages
 */

import React from 'react';
import AppHeader from './AppHeader';

interface MainLayoutProps {
  /** Page content */
  children: React.ReactNode;
  /** Optional page title for document head */
  title?: string;
  /** Whether to show the header */
  showHeader?: boolean;
  /** Maximum width constraint */
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  /** Additional CSS classes for the main content area */
  className?: string;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  title,
  showHeader = true,
  maxWidth = 'xl',
  className = ''
}) => {
  // Set document title if provided
  React.useEffect(() => {
    if (title) {
      document.title = `${title} - Sentopic`;
    } else {
      document.title = 'Sentopic - Reddit Analytics Tool';
    }
  }, [title]);

  // Max width classes
  const maxWidthClasses = {
    sm: 'max-w-2xl',
    md: 'max-w-4xl',
    lg: 'max-w-6xl',
    xl: 'max-w-7xl',
    '2xl': 'max-w-none',
    full: 'max-w-full'
  };

  return (
    <div className="min-h-screen bg-background font-terminal">
      {/* Header */}
      {showHeader && <AppHeader />}

      {/* Main Content */}
      <main className="flex-1">
        <div className={`${maxWidthClasses[maxWidth]} mx-auto terminal-spacing ${className}`}>
          {children}
        </div>
      </main>
    </div>
  );
};

export default MainLayout;