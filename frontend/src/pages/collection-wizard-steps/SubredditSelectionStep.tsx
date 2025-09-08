/**
 * Subreddit Selection Step Component
 * Step 1: Subreddit selection interface
 */

import React, { useState, useRef, useEffect } from 'react';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { SubredditSuggestions } from '@/components/collections/SubredditSuggestions';
import { validateSubredditName } from '@/utils/collectionWizardValidation';
import type { CollectionWizardFormData } from '@/hooks/useCollectionWizardState';

export interface SubredditSelectionStepProps {
  /** Current form data */
  formData: CollectionWizardFormData;
  /** Function to update form data */
  updateFormData: (updates: Partial<CollectionWizardFormData>) => void;
  /** Validation errors */
  errors: Record<string, string>;
}

// Popular subreddits for suggestions
const POPULAR_SUBREDDITS = [
  'AskReddit', 'funny', 'gaming', 'aww', 'Music', 'pics', 'science', 'worldnews',
  'videos', 'todayilearned', 'movies', 'news', 'technology', 'sports', 'television',
  'books', 'food', 'DIY', 'LifeProTips', 'explainlikeimfive', 'Showerthoughts',
  'mildlyinteresting', 'GetMotivated', 'personalfinance', 'Fitness', 'relationships',
  'space', 'programming', 'MachineLearning', 'datascience', 'investing', 'stocks',
  'apple', 'Android', 'iPhone', 'Tesla', 'bitcoin', 'ethereum', 'cryptocurrency'
];

export const SubredditSelectionStep: React.FC<SubredditSelectionStepProps> = ({
  formData,
  updateFormData,
  errors
}) => {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
  const [inputError, setInputError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const maxSubreddits = 10;

  // Filter suggestions based on input
  useEffect(() => {
    if (inputValue.length > 0) {
      const filtered = POPULAR_SUBREDDITS
        .filter(subreddit => 
          subreddit.toLowerCase().includes(inputValue.toLowerCase()) &&
          !formData.subreddits.some(selected => 
            selected.toLowerCase() === subreddit.toLowerCase()
          )
        )
        .slice(0, 8); // Limit to 8 suggestions
      setFilteredSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setShowSuggestions(false);
      setFilteredSuggestions([]);
    }
  }, [inputValue, formData.subreddits]);

  // Add subreddit
  const addSubreddit = (subredditName: string) => {
    const validation = validateSubredditName(subredditName);
    if (validation) {
      setInputError(validation);
      return;
    }

    // Check for duplicates (case insensitive)
    if (formData.subreddits.some(existing => 
        existing.toLowerCase() === subredditName.toLowerCase())) {
      setInputError('Subreddit already added');
      return;
    }

    if (formData.subreddits.length >= maxSubreddits) {
      setInputError(`Maximum ${maxSubreddits} subreddits allowed`);
      return;
    }

    // Clean the name (remove r/ prefix if present)
    const cleanName = subredditName.startsWith('r/') 
      ? subredditName.slice(2) 
      : subredditName;

    updateFormData({ subreddits: [...formData.subreddits, cleanName] });
    setInputValue('');
    setInputError('');
    setShowSuggestions(false);
    
    // Focus back to input
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  // Remove subreddit
  const removeSubreddit = (indexToRemove: number) => {
    const newSelection = formData.subreddits.filter((_, index) => index !== indexToRemove);
    updateFormData({ subreddits: newSelection });
    setInputError('');
  };

  // Handle input submission
  const handleInputSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      addSubreddit(inputValue.trim());
    }
  };

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
    setInputError('');
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion: string) => {
    addSubreddit(suggestion);
  };

  // Handle input key events
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setShowSuggestions(false);
    } else if (e.key === 'ArrowDown' && filteredSuggestions.length > 0) {
      e.preventDefault();
      // Focus first suggestion (could be enhanced with full keyboard navigation)
    }
  };

  return (
    <div className="space-y-6">
      {/* Step Introduction */}
      <div>
        <h3 className="font-subsection text-text-primary mb-2">
          Select Target Subreddits
        </h3>
        <p className="font-body text-text-secondary">
          Choose 1-{maxSubreddits} subreddits to collect data from. You can add them one by one or select from popular suggestions.
        </p>
      </div>

      {/* Input Section */}
      <div className="relative">
        <form onSubmit={handleInputSubmit}>
          <Input
            ref={inputRef}
            label="Add Subreddit"
            placeholder="Enter subreddit name (e.g., 'technology' or 'r/technology')"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowSuggestions(filteredSuggestions.length > 0)}
            error={inputError}
            helpText={`${formData.subreddits.length}/${maxSubreddits} subreddits selected`}
            fullWidth
            className="mx-1"
          />
          <div className="flex justify-end mt-1">
            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={!inputValue.trim() || formData.subreddits.length >= maxSubreddits}
              className="text-accent hover:text-blue-700"
            >
              ADD
            </Button>
          </div>
        </form>

        {/* Suggestions Dropdown */}
        {showSuggestions && (
          <div className="absolute top-full left-0 right-0 z-10 mt-1 bg-content border border-border-secondary rounded-default shadow-card max-h-48 overflow-y-auto">
            {filteredSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                className="w-full px-3 py-2 text-left font-body text-text-primary hover:bg-hover-blue transition-colors duration-150"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                r/{suggestion}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selected Subreddits */}
      {formData.subreddits.length > 0 && (
        <div>
          <h4 className="font-subsection text-text-primary mb-3">
            Selected Subreddits ({formData.subreddits.length})
          </h4>
          <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-3 bg-panel border border-border-primary rounded-default">
            {formData.subreddits.map((subreddit, index) => (
              <span
                key={`${subreddit}-${index}`}
                className="inline-flex items-center px-3 py-1 bg-content border border-border-secondary rounded-full font-small text-text-primary"
              >
                r/{subreddit}
                <button
                  onClick={() => removeSubreddit(index)}
                  className="ml-2 text-text-tertiary hover:text-danger transition-colors duration-150"
                  aria-label={`Remove r/${subreddit}`}
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* AI Subreddit Suggestions */}
      {formData.subreddits.length < maxSubreddits && (
        <SubredditSuggestions
          onSubredditAdd={addSubreddit}
          isDisabled={formData.subreddits.length >= maxSubreddits}
          selectedSubreddits={formData.subreddits}
        />
      )}

      {/* Global Error Display */}
      {errors.subreddits && (
        <div className="p-3 bg-red-50 border border-danger rounded-input">
          <p className="font-body text-danger">{errors.subreddits}</p>
        </div>
      )}
    </div>
  );
};

export default SubredditSelectionStep;