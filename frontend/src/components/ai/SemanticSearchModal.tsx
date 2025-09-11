/**
 * Semantic Search Modal Component
 * Redesigned to be wider and shorter with horizontal layout
 */

import React, { useState, useEffect, useRef } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';

interface SemanticSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  searchType: string;
  projectId: string;
  indexingStatus?: any; // Add indexing status prop
  isIndexingInProgress?: boolean; // Add indexing progress prop
}

const SemanticSearchModal: React.FC<SemanticSearchModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  searchType,
  projectId,
  indexingStatus,
  isIndexingInProgress
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [indexingStarted, setIndexingStarted] = useState(false);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const isCloudSearch = searchType === 'cloud_semantic';

  // Reset modal state whenever it opens or closes
  useEffect(() => {
    if (isOpen) {
      // Reset state when modal opens
      setIsGenerating(false);
      setError(null);
      setIndexingStarted(false);
    } else {
      // Clean up polling when modal closes
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    }
  }, [isOpen]);

  // Monitor indexing progress and close modal when complete
  useEffect(() => {
    if (indexingStarted && !isIndexingInProgress && isOpen) {
      // Indexing completed, close modal after a brief delay
      setTimeout(() => {
        setIsGenerating(false);
        setIndexingStarted(false);
        onClose();
      }, 500);
    }
  }, [indexingStarted, isIndexingInProgress, isOpen, onClose]);

  const handleConfirm = async () => {
    setIsGenerating(true);
    setError(null);
    
    try {
      await onConfirm();
      // Mark that indexing has started
      setIndexingStarted(true);
      // Don't close modal or reset loading state - wait for indexing to complete
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start indexing');
      setIsGenerating(false);
      setIndexingStarted(false);
    }
  };

  const handleClose = () => {
    // Prevent closing during generation or if indexing has started
    if (isGenerating || indexingStarted) return;
    setError(null);
    setIndexingStarted(false);
    onClose();
  };

  // Clean up polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Enable Semantic Search"
      size="xl"
      closeDisabled={isGenerating || indexingStarted}
    >
      <div className="space-y-4">
        {/* Brief Introduction */}
        <div className="text-center">
          <p className="font-body text-text-secondary leading-relaxed">
            Semantic search understands the <strong>meaning</strong> behind your questions, finding relevant 
            discussions even when they don't contain your exact words.
          </p>
        </div>

        {/* Two-Column Comparison */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Local Semantic Search */}
          <div className={`p-4 rounded-input border-2 transition-all ${
            !isCloudSearch 
              ? 'border-accent bg-hover-blue' 
              : 'border-border-primary bg-panel'
          }`}>
            <div className="flex items-start mb-3">
              <div className="flex-shrink-0 mr-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  !isCloudSearch ? 'bg-accent text-white' : 'bg-border-primary text-text-tertiary'
                }`}>
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
              <div>
                <h4 className="font-subsection text-text-primary mb-1">
                  Local Semantic Search
                </h4>
                <div className="text-sm text-success font-medium mb-2">
                  ✓ Free & Private
                </div>
              </div>
            </div>
            
            <div className="text-sm text-text-secondary space-y-2">
              <p>Runs entirely on your machine using open-source models. No data sent externally.</p>
              <div className="space-y-1">
                <div><strong>Cost:</strong> $0.00</div>
                <div><strong>Privacy:</strong> Complete</div>
                <div><strong>Quality:</strong> Good semantic understanding</div>
              </div>
            </div>
          </div>

          {/* Cloud Semantic Search */}
          <div className={`p-4 rounded-input border-2 transition-all ${
            isCloudSearch 
              ? 'border-accent bg-hover-blue' 
              : 'border-border-primary bg-panel'
          }`}>
            <div className="flex items-start mb-3">
              <div className="flex-shrink-0 mr-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  isCloudSearch ? 'bg-accent text-white' : 'bg-border-primary text-text-tertiary'
                }`}>
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5 2a1 1 0 011 1v1h1a1 1 0 010 2H6v1a1 1 0 01-2 0V6H3a1 1 0 010-2h1V3a1 1 0 011-1zm0 10a1 1 0 011 1v1h1a1 1 0 110 2H6v1a1 1 0 11-2 0v-1H3a1 1 0 110-2h1v-1a1 1 0 011-1zM12 2a1 1 0 01.967.744L14.146 7.2 17.5 9.134a1 1 0 010 1.732L14.146 12.8l-1.179 4.456a1 1 0 01-1.934 0L9.854 12.8 6.5 10.866a1 1 0 010-1.732L9.854 7.2l1.179-4.456A1 1 0 0112 2z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
              <div>
                <h4 className="font-subsection text-text-primary mb-1">
                  Cloud Semantic Search
                </h4>
                <div className="text-sm text-yellow-600 font-medium mb-2">
                  ⚠ API Usage Cost
                </div>
              </div>
            </div>
            
            <div className="text-sm text-text-secondary space-y-2">
              <p>Advanced search using OpenAI's embedding API with higher accuracy.</p>
              <div className="space-y-1">
                <div><strong>Cost:</strong> $0.01 - $0.20 estimated</div>
                <div><strong>Privacy:</strong> Data sent to OpenAI</div>
                <div><strong>Quality:</strong> Excellent semantic understanding</div>
              </div>
            </div>
          </div>
        </div>

        {/* Compact Setup Requirements */}
        <div className="bg-panel p-3 rounded-input border border-border-primary">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-4">
              <div>
                <span className="text-text-secondary">Processing time:</span>
                <span className="text-text-primary ml-1">1-10 minutes</span>
              </div>
              <div>
                <span className="text-text-secondary">Setup:</span>
                <span className="text-text-primary ml-1">One-time process</span>
              </div>
            </div>
            <div className="text-text-primary font-medium">
              {isCloudSearch ? 'Estimated: $0.01 - $0.20' : 'Completely Free'}
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-danger p-3 rounded-input">
            <div className="flex items-start">
              <svg className="h-5 w-5 text-danger mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div>
                <h5 className="font-medium text-danger mb-1">Setup Failed</h5>
                <p className="text-sm text-danger">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-2 border-t border-border-primary">
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={isGenerating}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleConfirm}
            loading={isGenerating}
            disabled={isGenerating}
          >
            {isGenerating 
              ? (indexingStarted ? 'Generating Embeddings...' : 'Generating Embeddings...') 
              : `Enable ${isCloudSearch ? 'Cloud' : 'Local'} Semantic`
            }
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default SemanticSearchModal;