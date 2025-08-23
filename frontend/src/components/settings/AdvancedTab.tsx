/**
 * Advanced Tab Component
 * Data management and advanced configuration options
 */

import React, { useState } from 'react';
import Button from '@/components/ui/Button';
import { ConfirmModal } from '@/components/ui/Modal';
import { useClearAllData, useResetConfiguration } from '@/hooks/useSettings';

interface AdvancedTabProps {
  /** Function to call when operations are completed */
  onOperationComplete?: () => void;
}

export const AdvancedTab: React.FC<AdvancedTabProps> = ({
  onOperationComplete
}) => {
  // Modal state
  const [showClearDataModal, setShowClearDataModal] = useState(false);
  const [showResetConfigModal, setShowResetConfigModal] = useState(false);

  // Mutation hooks
  const clearDataMutation = useClearAllData();
  const resetConfigMutation = useResetConfiguration();

  const handleClearAllData = async () => {
    try {
      await clearDataMutation.mutateAsync();
      setShowClearDataModal(false);
      onOperationComplete?.();
    } catch (error) {
      // Error handling is managed by the mutation
      console.error('Failed to clear data:', error);
    }
  };

  const handleResetConfiguration = async () => {
    try {
      await resetConfigMutation.mutateAsync();
      setShowResetConfigModal(false);
      onOperationComplete?.();
    } catch (error) {
      // Error handling is managed by the mutation
      console.error('Failed to reset configuration:', error);
    }
  };

  return (
    <div className="space-y-8">
      {/* Data Management Section */}
      <section>
        <div className="mb-4">
          <h3 className="font-subsection text-text-primary mb-2">Data Management</h3>
          <p className="font-body text-text-secondary">
            Manage your application data and reset options. These operations cannot be undone.
          </p>
        </div>

        <div className="space-y-4">
          {/* Clear All Data */}
          <div className="bg-content border border-border-primary rounded-default p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1 mr-4">
                <h4 className="font-medium text-text-primary mb-2">Clear All Data</h4>
                <p className="font-body text-text-secondary mb-2">
                  Permanently delete all projects, analysis sessions, Reddit collections, chat history, 
                  and AI summaries from the application.
                </p>
                <p className="font-small text-danger">
                  ⚠️ This will delete all your research data and cannot be undone.
                </p>
              </div>
              <Button
                variant="danger"
                onClick={() => setShowClearDataModal(true)}
                disabled={clearDataMutation.isPending}
              >
                Clear All Data
              </Button>
            </div>

            {/* Success/Error Messages */}
            {clearDataMutation.isSuccess && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-input">
                <p className="font-small text-success">
                  All application data has been cleared successfully.
                </p>
              </div>
            )}
            {clearDataMutation.isError && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-input">
                <p className="font-small text-danger">
                  Failed to clear data: {clearDataMutation.error?.message}
                </p>
              </div>
            )}
          </div>

          {/* Reset Configuration */}
          <div className="bg-content border border-border-primary rounded-default p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1 mr-4">
                <h4 className="font-medium text-text-primary mb-2">Reset Configuration</h4>
                <p className="font-body text-text-secondary mb-2">
                  Reset all configuration settings to their default values. This will clear all API keys 
                  and restore the application to its initial state.
                </p>
                <p className="font-small text-warning">
                  ⚠️ You will need to reconfigure your API keys after this operation.
                </p>
              </div>
              <Button
                variant="secondary"
                onClick={() => setShowResetConfigModal(true)}
                disabled={resetConfigMutation.isPending}
              >
                Reset Settings
              </Button>
            </div>

            {/* Success/Error Messages */}
            {resetConfigMutation.isSuccess && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-input">
                <p className="font-small text-success">
                  Configuration has been reset to defaults successfully.
                </p>
              </div>
            )}
            {resetConfigMutation.isError && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-input">
                <p className="font-small text-danger">
                  Failed to reset configuration: {resetConfigMutation.error?.message}
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* System Information */}
      <section>
        <div className="mb-4">
          <h3 className="font-subsection text-text-primary mb-2">System Information</h3>
          <p className="font-body text-text-secondary">
            Information about your Sentopic installation and configuration.
          </p>
        </div>

        <div className="bg-panel border border-border-primary rounded-default p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-text-secondary">Application:</span>
              <span className="ml-2 text-text-primary font-mono">Sentopic v1.0</span>
            </div>
            <div>
              <span className="font-medium text-text-secondary">Database:</span>
              <span className="ml-2 text-text-primary font-mono">SQLite</span>
            </div>
            <div>
              <span className="font-medium text-text-secondary">Configuration:</span>
              <span className="ml-2 text-text-primary font-mono">config.json</span>
            </div>
            <div>
              <span className="font-medium text-text-secondary">Storage:</span>
              <span className="ml-2 text-text-primary font-mono">Local filesystem</span>
            </div>
          </div>
        </div>
      </section>

      {/* Clear Data Confirmation Modal */}
      <ConfirmModal
        isOpen={showClearDataModal}
        onClose={() => setShowClearDataModal(false)}
        onConfirm={handleClearAllData}
        title="Clear All Data"
        message="Are you sure you want to delete all projects, collections, chat history, and analysis data? This action cannot be undone."
        confirmText="Delete All Data"
        cancelText="Cancel"
        variant="danger"
      />

      {/* Reset Configuration Confirmation Modal */}
      <ConfirmModal
        isOpen={showResetConfigModal}
        onClose={() => setShowResetConfigModal(false)}
        onConfirm={handleResetConfiguration}
        title="Reset Configuration"
        message="Are you sure you want to reset all settings to defaults? This will clear all your API keys and configuration. A backup will be created automatically."
        confirmText="Reset Settings"
        cancelText="Cancel"
        variant="warning"
      />
    </div>
  );
};

export default AdvancedTab;