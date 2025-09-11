/**
 * Connection Test Component
 * Reusable component for testing API connections with real-time status
 */

import React from 'react';
import Button from '@/components/ui/Button';
import { InlineSpinner } from '@/components/layout/LoadingSpinner';

interface ConnectionTestProps {
    /** Label for the connection test */
    label: string;
    /** Whether the connection is configured */
    isConfigured: boolean;
    /** Current connection status */
    isConnected: boolean;
    /** Error message if connection failed */
    error?: string;
    /** Whether a test is currently running */
    isTesting: boolean;
    /** Function to trigger connection test */
    onTest: () => void;
    /** Additional CSS classes */
    className?: string;
    /** Whether to show the individual test button */
    showTestButton?: boolean;
  }

  export const ConnectionTest: React.FC<ConnectionTestProps> = ({
    label,
    isConfigured,
    isConnected,
    error,
    isTesting,
    onTest,
    className = '',
    showTestButton = true
  }) => {
  // Determine status indicator
  const getStatusIndicator = () => {
    if (isTesting) {
      return (
        <div className="flex items-center space-x-2 text-text-secondary">
          <InlineSpinner size="sm" />
          <span className="font-small">Testing...</span>
        </div>
      );
    }
    
    if (!isConfigured) {
      return (
        <div className="flex items-center space-x-2 text-text-tertiary">
          <div className="h-2 w-2 rounded-full bg-border-secondary" />
          <span className="font-small">Not configured</span>
        </div>
      );
    }
    
    if (isConnected) {
      return (
        <div className="flex items-center space-x-2 text-success">
          <div className="h-2 w-2 rounded-full bg-success" />
          <span className="font-small">Connected</span>
        </div>
      );
    }
    
    return (
      <div className="flex items-center space-x-2 text-danger">
        <div className="h-2 w-2 rounded-full bg-danger" />
        <span className="font-small">Connection failed</span>
      </div>
    );
  };

  return (
    <div className={`bg-panel border border-border-primary rounded-default p-4 ${className}`}>
      <div className={`flex items-center ${showTestButton ? 'justify-between' : 'justify-start'} mb-3`}>
        <div className="flex items-center space-x-3">
          <h4 className="font-medium text-text-primary">{label}</h4>
          {getStatusIndicator()}
        </div>
        
        {showTestButton && (
          <Button
          variant="secondary"
          size="sm"
          onClick={onTest}
          loading={isTesting}
          disabled={!isConfigured || isTesting}
        >
          Test Connection
        </Button>
        )}
      </div>
      
      {/* Error message display */}
      {error && !isTesting && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-input">
          <p className="font-small text-danger">{error}</p>
        </div>
      )}
      
      {/* Success message for connected state */}
      {isConnected && !error && !isTesting && (
        <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded-input">
          <p className="font-small text-success">Connection successful</p>
        </div>
      )}
    </div>
  );
};

export default ConnectionTest;