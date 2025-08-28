/**
 * Subreddit Suggestions Component
 * AI-powered subreddit suggestions for collection creation
 */

import React, { useState } from 'react';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { useAIStatus } from '@/hooks/useApi';
import { api } from '@/api/client';

interface SubredditSuggestionsProps {
  /** Callback when user wants to add a subreddit */
  onSubredditAdd: (subreddit: string) => void;
  /** Whether the component is disabled */
  isDisabled?: boolean;
  /** Currently selected subreddits (to filter out duplicates) */
  selectedSubreddits: string[];
}

export const SubredditSuggestions: React.FC<SubredditSuggestionsProps> = ({
  onSubredditAdd,
  isDisabled = false,
  selectedSubreddits
}) => {
  const { data: aiStatus } = useAIStatus();
  const [researchDescription, setResearchDescription] = useState('');
  const [isGeneratingSubreddits, setIsGeneratingSubreddits] = useState(false);
  const [suggestedSubreddits, setSuggestedSubreddits] = useState<string[]>([]);
  const [aiError, setAiError] = useState<string | null>(null);

  const handleGenerateSubreddits = async () => {
    if (!researchDescription.trim()) {
      setAiError('Please enter a research description to get subreddit suggestions');
      return;
    }

    setIsGeneratingSubreddits(true);
    setAiError(null);

    try {
      const response = await api.suggestSubreddits({
        research_description: researchDescription,
        max_subreddits: 10
      });

      // Filter out already selected subreddits
      const newSuggestions = response.subreddits.filter(
        subreddit => !selectedSubreddits.some(selected => 
          selected.toLowerCase() === subreddit.toLowerCase()
        )
      );

      setSuggestedSubreddits(newSuggestions);

    } catch (error) {
      setAiError('Failed to generate subreddit suggestions. Please try again.');
      console.error('AI subreddit suggestion error:', error);
    } finally {
      setIsGeneratingSubreddits(false);
    }
  };

  const handleAddSubreddit = (subreddit: string) => {
    onSubredditAdd(subreddit);
    // Remove from suggestions after adding
    setSuggestedSubreddits(prev => prev.filter(s => s !== subreddit));
  };

  const isAIAvailable = aiStatus?.ai_available && aiStatus?.features?.keyword_suggestion;

  if (!isAIAvailable) {
    return null; // Don't show anything if AI is not available
  }

  return (
    <div>
      <h4 className="font-subsection text-text-primary mb-3">
        AI Subreddit Suggestions
      </h4>
      
      <div className="mb-4 p-4 bg-panel rounded-input border border-border-primary">
        <div className="mb-3">
          <p className="font-body text-text-secondary mb-3">
            Describe what you want to research and get AI-powered subreddit suggestions.
          </p>
          
          {aiError && (
            <div className="mb-3 p-2 bg-red-50 border border-danger rounded-input">
              <p className="font-body text-danger text-sm">{aiError}</p>
            </div>
          )}
        </div>
        
        <div className="flex items-start space-x-3">
          <div className="flex-1">
            <Input
              type="text"
              value={researchDescription}
              onChange={(e) => setResearchDescription(e.target.value)}
              placeholder="e.g., Electric vehicle charging problems and infrastructure issues"
              disabled={isDisabled || isGeneratingSubreddits}
              fullWidth
            />
          </div>
          
          <Button
            variant="secondary"
            onClick={handleGenerateSubreddits}
            disabled={!researchDescription.trim() || isDisabled || isGeneratingSubreddits}
            loading={isGeneratingSubreddits}
          >
            {isGeneratingSubreddits ? 'GENERATING...' : 'SUGGEST'}
          </Button>
        </div>
      </div>

      {/* Suggested Subreddits */}
      {suggestedSubreddits.length > 0 && (
        <div className="mb-4">
          <h5 className="font-subsection text-text-primary mb-3">
            Suggested Communities
          </h5>
          <div className="flex flex-wrap gap-2">
            {suggestedSubreddits.map((subreddit) => (
              <button
                key={subreddit}
                onClick={() => handleAddSubreddit(subreddit)}
                disabled={isDisabled}
                className="px-3 py-1 text-sm bg-hover-blue text-accent border border-accent rounded-full hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150"
              >
                r/{subreddit}
              </button>
            ))}
          </div>
          <p className="mt-2 font-small text-text-tertiary">
            Click to add suggested subreddits to your collection
          </p>
        </div>
      )}
    </div>
  );
};

export default SubredditSuggestions;