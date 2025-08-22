/**
 * Subreddit Selector Component
 * Interface for selecting target subreddits for collection
 */

import React, { useState, useRef, useEffect } from 'react';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { SubredditSuggestions } from './SubredditSuggestions';

interface SubredditSelectorProps {
  selectedSubreddits: string[];
  onSelectionChange: (subreddits: string[]) => void;
  error?: string;
  maxSubreddits?: number;
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

export const SubredditSelector: React.FC<SubredditSelectorProps> = ({
  selectedSubreddits,
  onSelectionChange,
  error,
  maxSubreddits = 10
}) => {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
  const [inputError, setInputError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Filter suggestions based on input
  useEffect(() => {
    if (inputValue.length > 0) {
      const filtered = POPULAR_SUBREDDITS
        .filter(subreddit => 
          subreddit.toLowerCase().includes(inputValue.toLowerCase()) &&
          !selectedSubreddits.some(selected => 
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
  }, [inputValue, selectedSubreddits]);

  // Validate subreddit name
  const validateSubredditName = (name: string): string | null => {
    if (!name.trim()) {
      return 'Subreddit name cannot be empty';
    }

    // Remove r/ prefix if present
    const cleanName = name.startsWith('r/') ? name.slice(2) : name;

    if (cleanName.length < 1) {
      return 'Subreddit name is too short';
    }

    if (cleanName.length > 21) {
      return 'Subreddit name is too long (max 21 characters)';
    }

    // Basic format validation (letters, numbers, underscores, hyphens)
    if (!/^[a-zA-Z0-9_-]+$/.test(cleanName)) {
      return 'Subreddit name contains invalid characters';
    }

    // Check for duplicates (case insensitive)
    if (selectedSubreddits.some(existing => 
        existing.toLowerCase() === cleanName.toLowerCase())) {
      return 'Subreddit already added';
    }

    return null;
  };

  // Add subreddit
  const addSubreddit = (subredditName: string) => {
    const validation = validateSubredditName(subredditName);
    if (validation) {
      setInputError(validation);
      return;
    }

    if (selectedSubreddits.length >= maxSubreddits) {
      setInputError(`Maximum ${maxSubreddits} subreddits allowed`);
      return;
    }

    // Clean the name (remove r/ prefix if present)
    const cleanName = subredditName.startsWith('r/') 
      ? subredditName.slice(2) 
      : subredditName;

    onSelectionChange([...selectedSubreddits, cleanName]);
    setInputValue('');
    setInputError('');
    setShowSuggestions(false);
    
    // Focus back to input
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  // Remove subreddit
  const removeSubreddit = (indexToRemove: number) => {
    const newSelection = selectedSubreddits.filter((_, index) => index !== indexToRemove);
    onSelectionChange(newSelection);
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
      {/* Header */}
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
            helpText={`${selectedSubreddits.length}/${maxSubreddits} subreddits selected`}
            endIcon={
              <Button
                type="submit"
                variant="ghost"
                size="sm"
                disabled={!inputValue.trim() || selectedSubreddits.length >= maxSubreddits}
                className="text-accent hover:text-blue-700"
              >
                Add
              </Button>
            }
            fullWidth
            className="mx-1"
          />
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
      {selectedSubreddits.length > 0 && (
        <div>
          <h4 className="font-subsection text-text-primary mb-3">
            Selected Subreddits ({selectedSubreddits.length})
          </h4>
          <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-3 bg-panel border border-border-primary rounded-default">
            {selectedSubreddits.map((subreddit, index) => (
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
      {selectedSubreddits.length < maxSubreddits && (
        <SubredditSuggestions
          onSubredditAdd={addSubreddit}
          isDisabled={selectedSubreddits.length >= maxSubreddits}
          selectedSubreddits={selectedSubreddits}
        />
      )}

      {/* Global Error Display */}
      {error && (
        <div className="p-3 bg-red-50 border border-danger rounded-input">
          <p className="font-body text-danger">{error}</p>
        </div>
      )}
    </div>
  );
};

export default SubredditSelector;