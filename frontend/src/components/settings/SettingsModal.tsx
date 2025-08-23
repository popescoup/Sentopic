/**
 * Settings Modal Component
 * Main settings interface with tab navigation
 */

import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import ConfigurationTab from './ConfigurationTab';
import AdvancedTab from './AdvancedTab';
import { useSettingsForm } from '@/hooks/useSettings';

interface SettingsModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Function to call when modal should close */
  onClose: () => void;
}

type TabType = 'configuration' | 'advanced';

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose
}) => {
  // Tab state
  const [activeTab, setActiveTab] = useState<TabType>('configuration');
  
  // Settings form hook
  const { configStatus, statusLoading } = useSettingsForm();

  const handleOperationComplete = () => {
    // Could add a toast notification here
    console.log('Settings operation completed successfully');
  };

  const tabs: { id: TabType; label: string; description: string }[] = [
    {
      id: 'configuration',
      label: 'Configuration',
      description: 'Reddit API and LLM settings'
    },
    {
      id: 'advanced',
      label: 'Advanced',
      description: 'Data management and system options'
    }
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Application Settings"
      size="full"
      className="max-h-[85vh] overflow-hidden"
    >
      <div className="h-[70vh] flex flex-col">
        {/* Tab Navigation */}
        <div className="border-b border-border-primary mb-6">
          <div className="flex space-x-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors duration-150 ${
                  activeTab === tab.id
                    ? 'border-accent text-accent'
                    : 'border-transparent text-text-secondary hover:text-text-primary hover:border-border-secondary'
                }`}
              >
                <div>
                  <div>{tab.label}</div>
                  <div className="text-xs text-text-tertiary mt-1">
                    {tab.description}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto">
          {statusLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin h-8 w-8 border-2 border-accent border-t-transparent rounded-full mx-auto mb-4" />
                <p className="text-text-secondary">Loading configuration status...</p>
              </div>
            </div>
          ) : (
            <>
              {activeTab === 'configuration' && (
                <ConfigurationTab
                  configStatus={configStatus}
                  statusLoading={statusLoading}
                  onSave={handleOperationComplete}
                />
              )}

              {activeTab === 'advanced' && (
                <AdvancedTab
                  onOperationComplete={handleOperationComplete}
                />
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-border-primary flex justify-between items-center">
          <div className="text-sm text-text-tertiary">
            Configuration changes take effect immediately
          </div>
          <Button
            variant="secondary"
            onClick={onClose}
          >
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default SettingsModal;