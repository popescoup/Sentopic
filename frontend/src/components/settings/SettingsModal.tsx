/**
 * Settings Modal Component
 * Main settings interface with tab navigation
 */

import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import ConfigurationTab from './ConfigurationTab';
import { useSettingsForm } from '@/hooks/useSettings';

interface SettingsModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Function to call when modal should close */
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
    isOpen,
    onClose
  }) => {
    // Settings form hook
    const { configStatus, statusLoading } = useSettingsForm();
  
    const handleOperationComplete = () => {
      // Could add a toast notification here
      console.log('Settings operation completed successfully');
    };
  
    return (
        <Modal
        isOpen={isOpen}
        onClose={onClose}
        title="Application Settings"
        size="xl"
        className="max-h-[90vh]"
      >
        <div className="h-[70vh] flex flex-col">
          {/* Content */}
          <div className="flex-1 overflow-y-auto">
            {statusLoading ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <div className="animate-spin h-8 w-8 border-2 border-accent border-t-transparent rounded-full mx-auto mb-4" />
                  <p className="text-text-secondary">Loading configuration status...</p>
                </div>
              </div>
            ) : (
              <ConfigurationTab
                configStatus={configStatus}
                statusLoading={statusLoading}
                onSave={handleOperationComplete}
                onOperationComplete={handleOperationComplete}
              />
            )}
          </div>
        </div>
      </Modal>
    );
};

export default SettingsModal;