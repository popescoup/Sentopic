/**
 * AI Question Modal Component
 * Full-screen modal version of the AI chat interface
 * Provides expanded space for rich AI conversations and responses
 */

import React from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import SearchTypeSelector from './SearchTypeSelector';
import MessageList from './MessageList';
import SemanticSearchModal from './SemanticSearchModal';
import { useSearchType } from '@/hooks/useSearchType';
import type { ChatMessageCreate } from '@/types/api';

// Extract the search type for consistency
type SearchType = NonNullable<ChatMessageCreate['search_type']>;

interface AIQuestionModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Function to call when modal should close */
  onClose: () => void;
  /** Project ID for the chat session */
  projectId: string;
  /** Current session ID */
  sessionId: string | null;
  /** Chat messages */
  messages: Array<{
    id: number;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    response?: any;
    searchType?: string;
  }>;
  /** Whether chat is loading */
  isLoading: boolean;
  /** Error message if any */
  error: string | null;
  /** Function to send a question */
  sendQuestion: (question: string, searchType: SearchType) => Promise<void>;
}

const AIQuestionModal: React.FC<AIQuestionModalProps> = ({
  isOpen,
  onClose,
  projectId,
  sessionId,
  messages,
  isLoading,
  error,
  sendQuestion
}) => {
  const [question, setQuestion] = React.useState('');
  const [showSemanticModal, setShowSemanticModal] = React.useState(false);
  const [pendingSearchType, setPendingSearchType] = React.useState<SearchType | null>(null);

  // Use the same search type hook as the sidebar
  const {
    searchType,
    setSearchType,
    indexingStatus,
    startIndexing,
    isIndexingRequired,
    isIndexingInProgress
  } = useSearchType(projectId);

  // Handle question submission
  const handleSubmitQuestion = async () => {
    if (!question.trim() || isLoading) return;

    try {
      await sendQuestion(question, searchType);
      setQuestion(''); // Clear input after successful submission
    } catch (error) {
      console.error('Failed to send question:', error);
    }
  };

  // Handle search type change
  const handleSearchTypeChange = (newSearchType: SearchType) => {
    // Check if semantic search requires indexing
    if ((newSearchType === 'local_semantic' || newSearchType === 'cloud_semantic') && 
        isIndexingRequired(newSearchType)) {
      setPendingSearchType(newSearchType);
      setShowSemanticModal(true);
    } else {
      setSearchType(newSearchType);
    }
  };

  // Handle semantic search modal confirmation
  const handleSemanticConfirm = async (searchType: SearchType) => {
    try {
      await startIndexing(searchType === 'cloud_semantic' ? 'openai' : 'local');
      setSearchType(searchType);
      setPendingSearchType(null);
    } catch (error) {
      console.error('Failed to start indexing:', error);
    }
  };

  // Handle semantic search modal cancel
  const handleSemanticCancel = () => {
    setShowSemanticModal(false);
    setPendingSearchType(null);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmitQuestion();
    }
  };

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        title=""
        size="xl"
        className="max-w-6xl"
        showCloseButton={false}
      >
        <div className="flex flex-col h-[80vh]">
          {/* Custom Header with Search Type Selector */}
          <div className="flex items-center justify-between pb-4 border-b border-border-primary">
            <div className="flex items-center space-x-4">
              <h2 className="font-section-header text-text-primary">
                AI Assistant
              </h2>
              <div className="flex items-center text-small text-text-tertiary">
                <div className={`w-2 h-2 rounded-full mr-2 ${
                  isLoading ? 'bg-accent animate-pulse' : 
                  error ? 'bg-danger' : 'bg-success'
                }`}></div>
                {isLoading ? 'Analyzing question' : 
                 error ? 'Error' : 'Ready'}
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Search Type Selector */}
              <div className="min-w-80">
                <SearchTypeSelector
                  selectedType={searchType}
                  onTypeChange={handleSearchTypeChange}
                  indexingStatus={indexingStatus}
                  isIndexingInProgress={isIndexingInProgress}
                />
              </div>

              {/* Close Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="text-text-secondary hover:text-text-primary"
                aria-label="Close modal"
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </Button>
            </div>
          </div>

          {/* Chat Content Area */}
          <div className="flex-1 flex flex-col overflow-hidden pt-4">
            {/* Message History */}
            <div className="flex-1 overflow-y-auto mb-4 pr-2 min-h-0">
              <MessageList messages={messages} isLoading={isLoading} />
            </div>

            {/* Question Input Area */}
            <div className="flex-shrink-0 space-y-3 border-t border-border-primary pt-4">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about your analysis..."
                disabled={isLoading}
                className="w-full min-h-[3rem] max-h-32 px-3 py-2 text-sm border border-border-secondary rounded-input bg-content text-text-primary placeholder-text-tertiary resize-none overflow-hidden focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent focus:ring-opacity-20 transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  height: 'auto',
                  minHeight: '3rem'
                }}
                ref={(textarea) => {
                  if (textarea) {
                    // Auto-resize functionality
                    textarea.style.height = 'auto';
                    textarea.style.height = Math.min(textarea.scrollHeight, 128) + 'px';
                  }
                }}
              />
              
              <div className="flex items-center justify-between">
                <p className="text-xs text-text-tertiary">
                  *Each question is analyzed independently
                </p>
                
                <Button
                  onClick={handleSubmitQuestion}
                  disabled={!question.trim() || isLoading}
                  loading={isLoading}
                  variant="primary"
                  size="sm"
                >
                  Ask Question
                </Button>
              </div>

              {/* Error Display */}
              {error && (
                <div className="p-3 bg-red-50 border border-danger rounded-input">
                  <p className="text-sm text-danger">
                    {error}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </Modal>

      {/* Semantic Search Modal */}
      <SemanticSearchModal
        isOpen={showSemanticModal}
        onClose={handleSemanticCancel}
        onConfirm={() => handleSemanticConfirm(pendingSearchType!)}
        searchType={pendingSearchType || 'local_semantic'}
        projectId={projectId}
        indexingStatus={indexingStatus}
        isIndexingInProgress={isIndexingInProgress}
      />
    </>
  );
};

export default AIQuestionModal;