/**
 * AI Question Panel Component
 * Main Q&A interface for project analysis exploration
 */

import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { useQASession } from '@/hooks/useQASession';
import { useSearchType } from '@/hooks/useSearchType';
import { useAIStatus } from '@/hooks/useApi';
import SearchTypeSelector from './SearchTypeSelector';
import SemanticSearchModal from './SemanticSearchModal';
import MessageList from './MessageList';
import type { ChatMessageCreate } from '@/types/api';

// Extract the search type for consistency
type SearchType = NonNullable<ChatMessageCreate['search_type']>;

interface AIQuestionPanelProps {
  projectId: string;
}

const AIQuestionPanel: React.FC<AIQuestionPanelProps> = ({ projectId }) => {
  const [question, setQuestion] = useState('');
  const [showSemanticModal, setShowSemanticModal] = useState(false);
  const [pendingSearchType, setPendingSearchType] = useState<SearchType | null>(null); // Updated type

  // Hooks
  const { data: aiStatus } = useAIStatus();
  const {
    sessionId,
    messages,
    isLoading,
    error,
    sendQuestion,
    initializeSession
  } = useQASession(projectId);
  
  const {
    searchType,
    setSearchType,
    indexingStatus,
    startIndexing,
    isIndexingRequired,
    isIndexingInProgress
  } = useSearchType(projectId);

  // Initialize session on mount
  useEffect(() => {
    if (aiStatus?.ai_available) {
      initializeSession();
    }
  }, [aiStatus?.ai_available, initializeSession]);

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
  const handleSearchTypeChange = (newSearchType: SearchType) => { // Updated type
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
      // Don't close modal here - let the modal handle its own closing
      setPendingSearchType(null);
    } catch (error) {
      console.error('Failed to start indexing:', error);
      // Modal will handle error display
    }
  };

  // Handle semantic search modal cancel
  const handleSemanticCancel = () => {
    setShowSemanticModal(false);
    setPendingSearchType(null);
    // Keep current search type
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmitQuestion();
    }
    // Allow Shift+Enter for new lines (default behavior)
  };

  // Check if AI is available
  if (!aiStatus?.ai_available) {
    return (
      <Card className="bg-gradient-subtle">
        <div className="mb-4">
          <h3 className="font-section-header text-text-primary mb-2">
            AI Assistant
          </h3>
          <div className="flex items-center text-small text-text-tertiary">
            <div className="w-2 h-2 bg-text-tertiary rounded-full mr-2"></div>
            Unavailable
          </div>
        </div>
        
        <div className="mb-4 p-3 bg-content rounded-input border border-border-primary">
          <p className="font-body text-text-secondary text-sm">
            AI features are not available. Please check the AI configuration 
            in settings or contact your administrator.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <>
      <Card className="bg-gradient-subtle">
        <div className="mb-4">
          <h3 className="font-section-header text-text-primary mb-2">
            AI Assistant
          </h3>
          <div className="flex items-center text-small text-text-tertiary">
            <div className={`w-2 h-2 rounded-full mr-2 ${
              isLoading ? 'bg-accent animate-pulse' : 
              error ? 'bg-danger' : 'bg-success'
            }`}></div>
            {isLoading ? 'Analyzing question' : 
             error ? 'Error' : 'Ready'}
          </div>
        </div>

        {/* Search Type Selector */}
        <div className="mb-4">
          <SearchTypeSelector
            selectedType={searchType}
            onTypeChange={handleSearchTypeChange}
            indexingStatus={indexingStatus}
            isIndexingInProgress={isIndexingInProgress}
          />
        </div>

        {/* Message History */}
        <div className="mb-4 max-h-80 overflow-y-auto">
          <MessageList messages={messages} isLoading={isLoading} />
        </div>

        {/* Question Input */}
        <div className="space-y-3">
        <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your analysis..."
            disabled={isLoading}
            className="w-full min-h-[2.5rem] max-h-32 px-3 py-2 text-sm border border-border-secondary rounded-input bg-content text-text-primary placeholder-text-tertiary resize-none overflow-hidden focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent focus:ring-opacity-20 transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
                height: 'auto',
                minHeight: '2.5rem'
            }}
            ref={(textarea) => {
                if (textarea) {
                // Auto-resize functionality
                textarea.style.height = 'auto';
                textarea.style.height = Math.min(textarea.scrollHeight, 128) + 'px'; // 128px = max-h-32
                }
            }}
            />
          
          <Button
            onClick={handleSubmitQuestion}
            disabled={!question.trim() || isLoading}
            loading={isLoading}
            variant="primary"
            fullWidth
          >
            Ask Question
          </Button>

          <p className="text-xs text-text-tertiary text-center">
            *Each question is analyzed independently
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-3 p-3 bg-red-50 border border-danger rounded-input">
            <p className="text-sm text-danger">
              {error}
            </p>
          </div>
        )}
      </Card>

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

export default AIQuestionPanel;