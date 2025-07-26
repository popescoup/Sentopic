/**
 * Semantic Search Modal Component
 * Explains semantic search and handles embedding generation
 */

import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';

interface SemanticSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  searchType: string;
  projectId: string;
}

const SemanticSearchModal: React.FC<SemanticSearchModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  searchType,
  projectId
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isCloudSearch = searchType === 'cloud_semantic';

  const handleConfirm = async () => {
    setIsGenerating(true);
    setError(null);
    
    try {
      await onConfirm();
      // onConfirm should handle closing the modal on success
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start indexing');
      setIsGenerating(false);
    }
  };

  const handleClose = () => {
    if (isGenerating) return; // Prevent closing during generation
    setError(null);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Enable Semantic Search"
      size="md"
    >
      <div className="space-y-6">
        {/* Introduction */}
        <div>
          <h4 className="font-subsection text-text-primary mb-3">
            What is Semantic Search?
          </h4>
          <p className="font-body text-text-secondary mb-4 leading-relaxed">
            Semantic search understands the <strong>meaning</strong> behind your questions, 
            not just keywords. It can find relevant discussions even when they don't 
            contain your exact words.
          </p>
          
          <div className="bg-hover-blue p-4 rounded-input border border-border-primary">
            <h5 className="font-medium text-text-primary mb-2">Example:</h5>
            <div className="text-sm text-text-secondary space-y-1">
              <div><strong>Question:</strong> "What are users saying about battery performance?"</div>
              <div><strong>Finds:</strong> Discussions about "power drain", "charging issues", "battery life" even without using "battery performance"</div>
            </div>
          </div>
        </div>

        {/* Search Type Specific Information */}
        <div>
          <h4 className="font-subsection text-text-primary mb-3">
            {isCloudSearch ? 'Cloud Semantic Search' : 'Local Semantic Search'}
          </h4>
          
          {isCloudSearch ? (
            <div className="space-y-3">
              <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-input">
                <div className="flex items-start">
                  <svg className="h-5 w-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h5 className="font-medium text-yellow-800 mb-1">API Usage Cost</h5>
                    <p className="text-sm text-yellow-700">
                      Cloud semantic search uses OpenAI's embedding API. Based on your project size, 
                      this will cost approximately <strong>$0.10 - $2.00</strong> depending on the 
                      amount of content to process.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="text-sm text-text-secondary">
                <strong>Benefits:</strong> Higher quality semantic understanding, better accuracy for complex queries
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="bg-green-50 border border-green-200 p-4 rounded-input">
                <div className="flex items-start">
                  <svg className="h-5 w-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h5 className="font-medium text-green-800 mb-1">Free & Private</h5>
                    <p className="text-sm text-green-700">
                      Local semantic search runs entirely on your machine using open-source models. 
                      No data is sent to external services and there are no API costs.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="text-sm text-text-secondary">
                <strong>Benefits:</strong> Complete privacy, no ongoing costs, good semantic understanding
              </div>
            </div>
          )}
        </div>

        {/* Setup Requirements */}
        <div>
          <h4 className="font-subsection text-text-primary mb-3">
            Setup Required
          </h4>
          <p className="font-body text-text-secondary mb-3">
            To enable semantic search, we need to generate embeddings for your project content. 
            This is a one-time process that will take a few minutes.
          </p>
          
          <div className="bg-panel p-4 rounded-input border border-border-primary">
            <div className="text-sm space-y-2">
              <div className="flex justify-between">
                <span className="text-text-secondary">Processing time:</span>
                <span className="text-text-primary">2-5 minutes</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Content to process:</span>
                <span className="text-text-primary">All posts and comments in your analysis</span>
              </div>
              {isCloudSearch && (
                <div className="flex justify-between">
                  <span className="text-text-secondary">Estimated cost:</span>
                  <span className="text-text-primary">$0.10 - $2.00</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-danger p-4 rounded-input">
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
        <div className="flex justify-end space-x-3 pt-4 border-t border-border-primary">
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
            {isGenerating ? 'Generating Embeddings...' : 'Enable Semantic Search'}
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default SemanticSearchModal;