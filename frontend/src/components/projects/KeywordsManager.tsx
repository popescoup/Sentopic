/**
 * Keywords Manager Component
 * Tag-style keyword management component with validation
 */

import React, { useState, useRef } from 'react';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { isValidKeyword, sanitizeKeyword } from '@/utils/wizardValidation';

export interface KeywordsManagerProps {
  /** Current keywords array */
  keywords: string[];
  /** Callback when keywords change */
  onKeywordsChange: (keywords: string[]) => void;
  /** Maximum number of keywords allowed */
  maxKeywords?: number;
  /** Whether the component is disabled */
  disabled?: boolean;
  /** Error message to display */
  error?: string;
  /** Placeholder text for input */
  placeholder?: string;
  /** Additional CSS classes */
  className?: string;
}

export const KeywordsManager: React.FC<KeywordsManagerProps> = ({
  keywords,
  onKeywordsChange,
  maxKeywords = 20,
  disabled = false,
  error,
  placeholder = "Enter a keyword and press Enter",
  className = ''
}) => {
  const [inputValue, setInputValue] = useState('');
  const [inputError, setInputError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Add keyword
  const addKeyword = () => {
    const trimmedValue = inputValue.trim();
    
    if (!trimmedValue) {
      setInputError('Please enter a keyword');
      return;
    }

    if (!isValidKeyword(trimmedValue)) {
      setInputError('Keyword must be between 1-50 characters');
      return;
    }

    const sanitizedKeyword = sanitizeKeyword(trimmedValue);
    
    // Check for duplicates
    if (keywords.some(k => sanitizeKeyword(k) === sanitizedKeyword)) {
      setInputError('This keyword already exists');
      return;
    }

    // Check max keywords
    if (keywords.length >= maxKeywords) {
      setInputError(`Maximum ${maxKeywords} keywords allowed`);
      return;
    }

    // Add keyword
    onKeywordsChange([...keywords, trimmedValue]);
    setInputValue('');
    setInputError('');
    
    // Focus back to input
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Remove keyword
  const removeKeyword = (indexToRemove: number) => {
    onKeywordsChange(keywords.filter((_, index) => index !== indexToRemove));
  };

  // Handle input key events
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      addKeyword();
    } else if (event.key === 'Backspace' && !inputValue && keywords.length > 0) {
      // Remove last keyword if input is empty and backspace is pressed
      removeKeyword(keywords.length - 1);
    }
  };

  // Handle input change
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
    if (inputError) {
      setInputError('');
    }
  };

  // Clear all keywords
  const clearAllKeywords = () => {
    onKeywordsChange([]);
  };

  return (
    <div className={className}>
      {/* Keywords Display */}
      {keywords.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="font-body text-text-secondary">
              Keywords ({keywords.length}/{maxKeywords})
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearAllKeywords}
              disabled={disabled}
              className="text-text-tertiary hover:text-danger"
            >
              Clear all
            </Button>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {keywords.map((keyword, index) => (
              <div
                key={index}
                className="inline-flex items-center bg-hover-blue border border-accent rounded-input px-3 py-1 text-sm"
              >
                <span className="text-text-primary">{keyword}</span>
                <button
                  type="button"
                  onClick={() => removeKeyword(index)}
                  disabled={disabled}
                  className="ml-2 text-text-tertiary hover:text-danger transition-colors duration-150 disabled:opacity-50"
                  aria-label={`Remove keyword: ${keyword}`}
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input Section */}
      <div className="flex items-start space-x-3">
        <div className="flex-1">
          <Input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || keywords.length >= maxKeywords}
            error={inputError || error}
            fullWidth
          />
        </div>
        
        <Button
          variant="secondary"
          onClick={addKeyword}
          disabled={disabled || !inputValue.trim() || keywords.length >= maxKeywords}
        >
          Add
        </Button>
      </div>

      {/* Helper Text */}
      <div className="mt-2 flex items-center justify-between">
        <div className="font-body text-text-tertiary text-sm">
          {keywords.length === 0 
            ? 'Press Enter or click Add to add keywords'
            : `${keywords.length} keyword${keywords.length !== 1 ? 's' : ''} added`
          }
        </div>
        
        {keywords.length >= maxKeywords && (
          <div className="font-body text-warning text-sm">
            Maximum keywords reached
          </div>
        )}
      </div>

      {/* Keyboard Shortcuts Help */}
      <div className="mt-3 p-3 bg-panel rounded-input border border-border-primary">
        <h4 className="font-subsection text-text-primary mb-2">Keyboard Shortcuts:</h4>
        <div className="space-y-1 text-sm text-text-secondary">
          <div>• <kbd className="px-1 py-0.5 bg-border-secondary rounded text-xs">Enter</kbd> - Add keyword</div>
          <div>• <kbd className="px-1 py-0.5 bg-border-secondary rounded text-xs">Backspace</kbd> - Remove last keyword (when input is empty)</div>
        </div>
      </div>

      {/* Usage Guidelines */}
      <div className="mt-3 p-3 bg-panel rounded-input border border-border-primary">
        <h4 className="font-subsection text-text-primary mb-2">Guidelines:</h4>
        <ul className="space-y-1 text-sm text-text-secondary">
          <li>• Use specific, relevant terms related to your research</li>
          <li>• Avoid very common words (the, and, or, etc.)</li>
          <li>• Consider synonyms and related terms</li>
          <li>• Keywords are case-insensitive</li>
          <li>• Maximum {maxKeywords} keywords per project</li>
        </ul>
      </div>
    </div>
  );
};

export default KeywordsManager;