/**
 * Terminal Modal Component
 * Sharp, database-style dialog windows with terminal aesthetics
 */

import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import Button from './Button';

export interface ModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Function to call when modal should close */
  onClose: () => void;
  /** Modal title */
  title?: string;
  /** Modal content */
  children: React.ReactNode;
  /** Modal size - terminal sizes */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  /** Whether clicking overlay closes modal */
  closeOnOverlayClick?: boolean;
  /** Whether escape key closes modal */
  closeOnEscape?: boolean;
  /** Whether to show close button */
  showCloseButton?: boolean;
  /** Whether close actions are disabled */
  closeDisabled?: boolean;
  /** Additional CSS classes for modal content */
  className?: string;
  /** Additional CSS classes for overlay */
  overlayClassName?: string;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  closeOnOverlayClick = true,
  closeOnEscape = true,
  showCloseButton = true,
  closeDisabled = false,
  className = '',
  overlayClassName = ''
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  // Terminal size classes - more compact
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg', 
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-none mx-4'
  };

  // Handle escape key
  useEffect(() => {
    if (!isOpen || !closeOnEscape || closeDisabled) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape, closeDisabled, onClose]);

  // Focus management
  useEffect(() => {
    if (isOpen) {
      // Store previously focused element
      previousActiveElement.current = document.activeElement as HTMLElement;
      
      // Focus modal when opened
      if (modalRef.current) {
        modalRef.current.focus();
      }
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden';
    } else {
      // Restore focus to previously focused element
      if (previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
      
      // Restore body scroll
      document.body.style.overflow = 'unset';
    }

    // Cleanup on unmount
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  // Handle overlay click
  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (closeOnOverlayClick && !closeDisabled && event.target === event.currentTarget) {
      onClose();
    }
  };

  // Don't render if not open
  if (!isOpen) return null;

  const modalContent = (
    <div
      className={`fixed inset-0 z-modal flex items-center justify-center p-4 ${overlayClassName}`}
      onClick={handleOverlayClick}
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.4)' }} // Darker overlay for terminal feel
    >
      <div
        ref={modalRef}
        className={`
          terminal-panel bg-content w-full
          ${sizeClasses[size]}
          ${className}
          transform transition-all duration-100 ease-out
          animate-terminal-fade
        `}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
      >
        {/* Terminal Header */}
        {(title || showCloseButton) && (
          <div className="terminal-panel-header flex items-center justify-between">
            {title && (
              <h2 id="modal-title" className="font-large text-text-primary text-command">
                {title.toUpperCase()}
              </h2>
            )}
            
            {showCloseButton && (
              <Button
                variant="secondary"
                size="sm"
                onClick={closeDisabled ? undefined : onClose}
                disabled={closeDisabled}
                className={`text-text-secondary ${
                  closeDisabled 
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'hover:text-text-primary'
                }`}
                aria-label="Close dialog"
              >
                X
              </Button>
            )}
          </div>
        )}

        {/* Content */}
        <div className="terminal-panel-content">
          {children}
        </div>
      </div>
    </div>
  );

  // Render modal in portal
  return createPortal(modalContent, document.body);
};

// Terminal Modal sub-components
export const ModalHeader: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`pb-1.5 border-b border-border ${className}`}>
    {children}
  </div>
);

export const ModalBody: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`py-1.5 ${className}`}>
    {children}
  </div>
);

export const ModalFooter: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => (
  <div className={`pt-1.5 border-t border-border flex items-center justify-end space-x-1.5 ${className}`}>
    {children}
  </div>
);

// Terminal confirmation modal
export interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'primary';
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'CONFIRM',
  cancelText = 'CANCEL',
  variant = 'primary'
}) => {
  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  // Terminal status symbols
  const variantSymbols = {
    danger: '[!]',
    warning: '[?]',
    primary: '[i]'
  };

  const variantColors = {
    danger: 'text-danger',
    warning: 'text-warning',
    primary: 'text-accent'
  };

  const buttonVariants = {
    danger: 'danger' as const,
    warning: 'warning' as const,
    primary: 'primary' as const
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
    >
      <div className="text-center font-terminal">
        {/* Terminal status indicator */}
        <div className="mb-2">
          <span className={`font-header ${variantColors[variant]}`}>
            {variantSymbols[variant]}
          </span>
        </div>
        
        <p className="font-body text-text-secondary mb-4 leading-terminal-relaxed">
          {message.toUpperCase()}
        </p>
        
        <div className="flex space-x-1.5 justify-center">
          <Button
            variant="secondary"
            onClick={onClose}
          >
            {cancelText}
          </Button>
          <Button
            variant={buttonVariants[variant]}
            onClick={handleConfirm}
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default Modal;