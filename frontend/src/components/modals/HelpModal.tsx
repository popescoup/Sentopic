/**
 * Help Modal Component
 * Comprehensive help documentation with search functionality
 */

import React from 'react';
import Modal from '@/components/ui/Modal';
import HelpContent from './HelpContent';

interface HelpModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Function to call when modal should close */
  onClose: () => void;
}

export const HelpModal: React.FC<HelpModalProps> = ({
  isOpen,
  onClose,
}) => {
  return (
    <Modal
  isOpen={isOpen}
  onClose={onClose}
  title="Help & Documentation"
  size="xl"
  className="max-h-[85vh]"
>
  <div className="h-[60vh] overflow-hidden">
        {/* Scrollable Content Area */}
        <div className="h-full overflow-y-auto px-2 pt-2 pb-0">
          <HelpContent />
        </div>
      </div>
    </Modal>
  );
};

export default HelpModal;