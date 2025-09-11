/**
 * Search Type Selector Component
 * Dropdown for selecting between keyword and semantic search types
 */

import React, { useState, useRef, useEffect } from 'react';
import type { ChatMessageCreate } from '@/types/api';
import { useOpenAIStatus } from '@/hooks/useOpenAIStatus';

// Extract the search type for consistency
type SearchType = NonNullable<ChatMessageCreate['search_type']>;

interface SearchTypeOption {
  value: SearchType; // Changed from string
  label: string;
  description: string;
  requiresIndexing?: boolean;
  disabled?: boolean;
  disabledReason?: string;
}

interface SearchTypeSelectorProps {
  selectedType: SearchType; // Changed from string
  onTypeChange: (type: SearchType) => void; // Changed from string
  indexingStatus: any;
  isIndexingInProgress: boolean;
}

const SearchTypeSelector: React.FC<SearchTypeSelectorProps> = ({
  selectedType,
  onTypeChange,
  indexingStatus,
  isIndexingInProgress
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { isOpenAIConfigured } = useOpenAIStatus();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Define search type options
  const searchOptions: SearchTypeOption[] = [
    {
      value: 'keyword',
      label: 'Keyword Search',
      description: 'Traditional keyword-based search through your analysis data'
    },
    {
      value: 'local_semantic',
      label: 'Semantic (Local)',
      description: 'AI-powered semantic search using local embeddings (free)',
      requiresIndexing: true,
      disabled: isIndexingInProgress,
      disabledReason: isIndexingInProgress ? 'Indexing in progress...' : undefined
    },
    {
      value: 'cloud_semantic',
      label: 'Semantic (Cloud)',
      description: isOpenAIConfigured 
        ? 'Advanced semantic search using OpenAI embeddings (paid)'
        : 'Configure OpenAI API key to enable cloud embeddings',
      requiresIndexing: true,
      disabled: !isOpenAIConfigured || isIndexingInProgress,
      disabledReason: !isOpenAIConfigured 
        ? 'OpenAI API key not configured' 
        : isIndexingInProgress ? 'Indexing in progress...' : undefined
    }
  ];

  // Get the currently selected option
  const selectedOption = searchOptions.find(option => option.value === selectedType) || searchOptions[0];

  // Handle option selection
  const handleSelect = (option: SearchTypeOption) => {
    if (option.disabled) return;
    
    setIsOpen(false);
    onTypeChange(option.value);
  };

  // Get status indicator for semantic options
  const getStatusIndicator = (option: SearchTypeOption) => {
    if (!option.requiresIndexing) return null;
    
    const isLocal = option.value === 'local_semantic';
    const status = isLocal ? 
      indexingStatus?.indexing_status?.local : 
      indexingStatus?.indexing_status?.cloud;
    
    if (isIndexingInProgress) {
      return (
        <span className="text-xs text-accent">
          Indexing...
        </span>
      );
    }
    
    if (status === 'complete') {
      return (
        <span className="text-xs text-success">
          ✓ Ready
        </span>
      );
    }
    
    return (
      <span className="text-xs text-text-tertiary">
        Setup required
      </span>
    );
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <label className="block font-medium text-text-primary mb-2 text-sm">
        Search Type
      </label>
      
      {/* Dropdown Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`
          w-full px-3 py-2 text-left bg-content border rounded-input
          transition-all duration-150 flex items-center justify-between
          ${isOpen ? 'border-accent ring-2 ring-accent ring-opacity-20' : 'border-border-secondary hover:border-border-emphasis'}
          focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent focus:ring-opacity-20
        `}
      >
        <div className="flex-1">
          <div className="font-medium text-text-primary text-sm">
            {selectedOption.label}
          </div>
          <div className="text-xs text-text-secondary mt-0.5">
            {selectedOption.description}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {getStatusIndicator(selectedOption)}
          <svg
            className={`h-4 w-4 text-text-tertiary transition-transform duration-150 ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-content border border-border-primary rounded-input shadow-modal">
          <div className="py-1">
            {searchOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => handleSelect(option)}
                disabled={option.disabled}
                className={`
                  w-full px-3 py-2 text-left transition-colors duration-150 flex items-center justify-between
                  ${option.disabled 
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'hover:bg-hover-blue focus:bg-hover-blue focus:outline-none'
                  }
                  ${option.value === selectedType ? 'bg-hover-blue' : ''}
                `}
              >
                <div className="flex-1">
                  <div className="font-medium text-text-primary text-sm">
                    {option.label}
                  </div>
                  <div className="text-xs text-text-secondary mt-0.5">
                    {option.disabled && option.disabledReason ? option.disabledReason : option.description}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {getStatusIndicator(option)}
                  {option.value === selectedType && (
                    <svg className="h-4 w-4 text-accent" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchTypeSelector;