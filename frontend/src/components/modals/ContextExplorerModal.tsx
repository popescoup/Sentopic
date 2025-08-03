/**
 * Context Explorer Modal
 * Advanced filtering and exploration of keyword contexts
 * Provides comprehensive search and navigation through Reddit discussions
 */

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { LoadingState } from '@/components/layout/LoadingSpinner';
import { FullContextDisplay } from '@/components/discussions';
import { useFilteredContexts, getDefaultFilters, type FilterState } from '@/hooks/useFilteredContexts';
import type { ProjectResponse } from '@/types/api';

interface ContextExplorerModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Function to call when modal should close */
  onClose: () => void;
  /** Project data for filtering and display */
  project: ProjectResponse;
}

export const ContextExplorerModal: React.FC<ContextExplorerModalProps> = ({
  isOpen,
  onClose,
  project
}) => {
  // Filter state management
  const [filters, setFilters] = useState<FilterState>(getDefaultFilters());
  
  // Reset filters when modal opens
  useEffect(() => {
    if (isOpen) {
      setFilters(getDefaultFilters());
    }
  }, [isOpen]);

  // API call for filtered contexts
  const { 
      data: contextData, 
      isLoading, 
      error,
      refetch 
    } = useFilteredContexts(project.id, filters, isOpen);
  
    // Convert error to string for display
    const errorMessage = error instanceof Error ? error.message : 
                        error ? String(error) : 'An unexpected error occurred';

  // Handle filter changes
  const updateFilter = (key: keyof FilterState, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: key !== 'page' ? 1 : value // Reset to page 1 when changing filters
    }));
  };

  // Handle pagination
  const goToPage = (page: number) => {
    updateFilter('page', page);
  };

  // Validate sentiment range
  const isValidSentimentRange = filters.min_sentiment <= filters.max_sentiment;

  // Available sort options
  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'sentiment_desc', label: 'Most Positive First' },
    { value: 'sentiment_asc', label: 'Most Negative First' }
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Context Explorer"
      size="xl"
      className="max-h-[90vh]"
      >
      <div className="max-h-[75vh] overflow-y-auto">
          {/* Filter Controls */}
          <div className="border-b border-border-primary pb-6 mb-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {/* Primary Keyword Filter */}
            <div>
              <label className="block font-medium text-text-primary mb-2">
                Primary Keyword
              </label>
              <select
                value={filters.primary_keyword || ''}
                onChange={(e) => updateFilter('primary_keyword', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-border-secondary rounded-input bg-content text-text-primary focus:border-accent focus:ring-2 focus:ring-accent focus:ring-offset-1 focus:outline-none"
              >
                <option value="">All Keywords</option>
                {project.keywords.map(keyword => (
                  <option key={keyword} value={keyword}>
                    {keyword}
                  </option>
                ))}
              </select>
            </div>

            {/* Secondary Keyword Filter */}
            <div>
              <label className="block font-medium text-text-primary mb-2">
                Secondary Keyword
              </label>
              <select
                value={filters.secondary_keyword || ''}
                onChange={(e) => updateFilter('secondary_keyword', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-border-secondary rounded-input bg-content text-text-primary focus:border-accent focus:ring-2 focus:ring-accent focus:ring-offset-1 focus:outline-none"
              >
                <option value="">None (No Co-occurrence)</option>
                {project.keywords.map(keyword => (
                  <option key={keyword} value={keyword}>
                    {keyword}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort Options */}
            <div>
              <label className="block font-medium text-text-primary mb-2">
                Sort By
              </label>
              <select
                value={filters.sort_by}
                onChange={(e) => updateFilter('sort_by', e.target.value)}
                className="w-full px-3 py-2 border border-border-secondary rounded-input bg-content text-text-primary focus:border-accent focus:ring-2 focus:ring-accent focus:ring-offset-1 focus:outline-none"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Results Per Page */}
            <div>
              <label className="block font-medium text-text-primary mb-2">
                Results Per Page
              </label>
              <select
                value={filters.limit}
                onChange={(e) => updateFilter('limit', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-border-secondary rounded-input bg-content text-text-primary focus:border-accent focus:ring-2 focus:ring-accent focus:ring-offset-1 focus:outline-none"
              >
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
            </div>
          </div>

          {/* Sentiment Range Controls */}
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <Input
              label="Minimum Sentiment"
              type="number"
              min="-1"
              max="1"
              step="0.01"
              value={filters.min_sentiment}
              onChange={(e) => updateFilter('min_sentiment', parseFloat(e.target.value))}
              hasError={!isValidSentimentRange}
              helpText="Range: -1.0 (very negative) to +1.0 (very positive)"
            />
            <Input
              label="Maximum Sentiment"
              type="number"
              min="-1"
              max="1"
              step="0.01"
              value={filters.max_sentiment}
              onChange={(e) => updateFilter('max_sentiment', parseFloat(e.target.value))}
              hasError={!isValidSentimentRange}
              error={!isValidSentimentRange ? "Maximum must be greater than or equal to minimum" : undefined}
            />
          </div>

          {/* Applied Filters Summary */}
          <div className="mt-4 p-3 bg-panel rounded-input border border-border-primary">
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="font-medium text-text-primary">Active Filters:</span>
              
              {filters.primary_keyword ? (
                <span className="px-2 py-1 bg-accent text-white rounded text-xs">
                  Primary: {filters.primary_keyword}
                </span>
              ) : (
                <span className="px-2 py-1 bg-gray-200 text-text-secondary rounded text-xs">
                  All Keywords
                </span>
              )}
              
              {filters.secondary_keyword && (
                <span className="px-2 py-1 bg-accent text-white rounded text-xs">
                  Secondary: {filters.secondary_keyword}
                </span>
              )}
              
              <span className="px-2 py-1 bg-gray-200 text-text-secondary rounded text-xs">
                Sentiment: {filters.min_sentiment.toFixed(2)} to {filters.max_sentiment.toFixed(2)}
              </span>
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div>
          {/* Results Header */}
          {contextData && (
            <div className="flex items-center justify-between mb-4">
              <div className="font-medium text-text-primary">
                {contextData.pagination.total_count === 0 ? (
                  'No Posts/Comments Found'
                ) : (
                  <>
                    Showing {((contextData.pagination.page - 1) * contextData.pagination.limit) + 1}–
                    {Math.min(contextData.pagination.page * contextData.pagination.limit, contextData.pagination.total_count)} of {' '}
                    {contextData.pagination.total_count.toLocaleString()} contexts
                  </>
                )}
              </div>

              {/* Pagination Controls */}
              {contextData.pagination.total_pages > 1 && (
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!contextData.pagination.has_previous}
                    onClick={() => goToPage(contextData.pagination.page - 1)}
                  >
                    Previous
                  </Button>
                  
                  <span className="font-technical text-text-secondary px-2">
                    Page {contextData.pagination.page} of {contextData.pagination.total_pages}
                  </span>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!contextData.pagination.has_next}
                    onClick={() => goToPage(contextData.pagination.page + 1)}
                  >
                    Next
                  </Button>
                </div>
              )}
            </div>
          )}

          {/* Results Content */}
          <div>
            {isLoading && (
              <LoadingState 
                title="Loading Contexts..."
                description="Searching through discussions for your filtered keywords."
              />
            )}

            {!!error && (
            <div className="text-center py-8">
                <div className="text-danger mb-4">
                <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                </div>
                <h3 className="font-subsection text-text-primary mb-2">Error Loading Contexts</h3>
                <p className="font-body text-text-secondary mb-4">
                {errorMessage}
                </p>
                <Button variant="outline" onClick={() => refetch()}>
                Try Again
                </Button>
            </div>
            )}

            {contextData && contextData.contexts.length === 0 && !isLoading && (
              <div className="text-center py-12">
                <div className="text-text-tertiary mb-4">
                  <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h3 className="font-subsection text-text-primary mb-2">
                  No Posts/Comments Found
                </h3>
                <p className="font-body text-text-secondary mb-4 max-w-md mx-auto">
                  No discussions match your current filter criteria. Try adjusting your keywords or sentiment range.
                </p>
                <Button 
                  variant="outline"
                  onClick={() => setFilters(getDefaultFilters())}
                >
                  Reset Filters
                </Button>
              </div>
            )}

            {contextData && contextData.contexts.length > 0 && (
              <div className="space-y-6">
                {contextData.contexts.map((context, index) => (
                  <FullContextDisplay
                    key={`${context.content_reddit_id}-${index}`}
                    context={context}
                    keywords={project.keywords}
                    collectionsMetadata={project.collections_metadata}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default ContextExplorerModal;