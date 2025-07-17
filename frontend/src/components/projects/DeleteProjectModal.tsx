/**
 * DeleteProjectModal Component
 * Professional confirmation dialog for project deletion
 * 
 * Prevents accidental data loss with clear consequences explanation
 */

import React from 'react';
import { Modal, ModalBody, ModalFooter } from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import type { ProjectResponse } from '@/types/api';

interface DeleteProjectModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Project to be deleted */
  project: ProjectResponse | null;
  /** Called when user confirms deletion */
  onConfirm: () => void;
  /** Called when user cancels or closes modal */
  onClose: () => void;
  /** Whether deletion is in progress */
  isDeleting?: boolean;
}

export const DeleteProjectModal: React.FC<DeleteProjectModalProps> = ({
  isOpen,
  project,
  onConfirm,
  onClose,
  isDeleting = false
}) => {
  if (!project) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Delete Project"
      size="sm"
    >
      <ModalBody>
        <div className="text-center">
          {/* Warning Icon */}
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
            <svg
              className="h-6 w-6 text-danger"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          
          {/* Project Name */}
          <h3 className="font-subsection text-text-primary mb-2">
            Delete "{project.name}"?
          </h3>
          
          {/* Warning Message */}
          <p className="font-body text-text-secondary mb-6">
            This will permanently delete this project and all associated data. 
            This action cannot be undone.
          </p>
          
          {/* What Will Be Deleted */}
          <div className="bg-red-50 rounded-input p-4 mb-6 text-left">
            <h4 className="font-subsection text-text-primary mb-3">
              The following will be permanently deleted:
            </h4>
            <ul className="font-body text-text-secondary space-y-1">
              <li className="flex items-center">
                <svg className="h-4 w-4 text-danger mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                All analysis results and statistics
              </li>
              <li className="flex items-center">
                <svg className="h-4 w-4 text-danger mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                AI-generated summaries and insights
              </li>
              <li className="flex items-center">
                <svg className="h-4 w-4 text-danger mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                All chat sessions and conversations
              </li>
              <li className="flex items-center">
                <svg className="h-4 w-4 text-danger mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Project configuration and settings
              </li>
            </ul>
          </div>
          
          {/* Collection Safety Note */}
          <div className="bg-blue-50 rounded-input p-4 text-left">
            <div className="flex items-start">
              <svg className="h-5 w-5 text-accent mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h4 className="font-subsection text-text-primary mb-1">
                  Your data collections are safe
                </h4>
                <p className="font-small text-text-secondary">
                  The original Reddit data collections used in this project will remain intact 
                  and can be used in other projects.
                </p>
              </div>
            </div>
          </div>
        </div>
      </ModalBody>
      
      <ModalFooter>
        <Button
          variant="secondary"
          onClick={onClose}
          disabled={isDeleting}
        >
          Cancel
        </Button>
        <Button
          variant="danger"
          onClick={onConfirm}
          loading={isDeleting}
          disabled={isDeleting}
        >
          {isDeleting ? 'Deleting...' : 'Delete Project'}
        </Button>
      </ModalFooter>
    </Modal>
  );
};

export default DeleteProjectModal;