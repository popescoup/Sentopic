/**
 * Keyword Overview Modal
 * Advanced keyword statistics and analysis display
 * Provides comprehensive view of keyword performance with sorting capabilities
 */

import React, { useState, useMemo } from 'react';
import Modal from '@/components/ui/Modal';
import type { ProjectResponse, KeywordData } from '@/types/api';

interface KeywordOverviewModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Function to call when modal should close */
  onClose: () => void;
  /** Project data containing keyword statistics */
  project: ProjectResponse;
}

type SortOption = 'mentions' | 'sentiment' | 'alphabetical';

const KeywordOverviewModal: React.FC<KeywordOverviewModalProps> = ({
  isOpen,
  onClose,
  project
}) => {
  // Sorting state
  const [sortBy, setSortBy] = useState<SortOption>('mentions');

  // Get and sort keyword data
  const sortedKeywords = useMemo(() => {
    const keywordsData = project.keywords_data || [];
    
    switch (sortBy) {
      case 'mentions':
        return [...keywordsData].sort((a, b) => b.total_mentions - a.total_mentions);
      case 'sentiment':
        return [...keywordsData].sort((a, b) => b.avg_sentiment - a.avg_sentiment);
      case 'alphabetical':
        return [...keywordsData].sort((a, b) => a.keyword.localeCompare(b.keyword));
      default:
        return keywordsData;
    }
  }, [project.keywords_data, sortBy]);

  // Sentiment color helper function (matching ContextExplorerModal pattern)
  const getSentimentColor = (sentiment: number): string => {
    if (sentiment > 0.0001) return 'text-success';
    if (sentiment < -0.0001) return 'text-danger';
    return 'text-text-secondary';
  };

  // Sort options for dropdown
  const sortOptions = [
    { value: 'mentions', label: 'Most Mentions First' },
    { value: 'sentiment', label: 'Most Positive First' },
    { value: 'alphabetical', label: 'Alphabetical' }
  ];

  // Format collections for display
  const formatCollections = (collections: string[]): string => {
    if (!collections || collections.length === 0) return 'None';
    if (collections.length === 1) return '1 collection';
    return `${collections.length} collections`;
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Keyword Overview"
      size="xl"
      className="max-h-[90vh]"
    >
      <div className="max-h-[75vh] overflow-y-auto pr-1">
        {/* Sort Controls */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="font-medium text-text-primary">
                {sortedKeywords.length} keyword{sortedKeywords.length !== 1 ? 's' : ''} found
              </span>
            </div>
            
            <div className="flex items-center space-x-3">
              <label className="font-medium text-text-primary">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                className="px-3 py-2 border border-border-secondary rounded-input bg-content text-text-primary focus:border-accent focus:ring-2 focus:ring-accent focus:ring-offset-1 focus:outline-none"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Keywords Table */}
        {sortedKeywords.length > 0 ? (
          <div className="border border-border-primary rounded-default overflow-hidden">
            <table className="w-full">
            <thead className="bg-panel border-b border-border-primary">
                <tr>
                    <th className="px-4 py-3 text-left font-subsection text-text-primary">
                    Keyword
                    </th>
                    <th className="px-4 py-3 text-right font-subsection text-text-primary">
                    Total Mentions
                    </th>
                    <th className="px-4 py-3 text-right font-subsection text-text-primary">
                    Avg Sentiment
                    </th>
                    <th className="px-4 py-3 text-right font-subsection text-text-primary">
                    In Posts
                    </th>
                    <th className="px-4 py-3 text-right font-subsection text-text-primary">
                    In Comments
                    </th>
                    <th className="px-4 py-3 text-center font-subsection text-text-primary">
                    Collections
                    </th>
                </tr>
                </thead>
              <tbody className="divide-y divide-border-primary">
                {sortedKeywords.map((keyword, index) => (
                  <tr 
                    key={keyword.keyword}
                    className={`hover:bg-hover-blue transition-colors duration-150 ${
                      index % 2 === 0 ? 'bg-content' : 'bg-panel'
                    }`}
                  >
                    {/* Keyword Name */}
                    <td className="px-4 py-3">
                      <span className="font-medium text-text-primary">
                        {keyword.keyword}
                      </span>
                    </td>
                    
                    {/* Total Mentions */}
                    <td className="px-4 py-3 text-right">
                      <span className="font-technical text-text-primary">
                        {keyword.total_mentions.toLocaleString()}
                      </span>
                    </td>
                    
                    {/* Average Sentiment */}
                    <td className="px-4 py-3 text-right">
                      <span className={`font-technical font-medium ${getSentimentColor(keyword.avg_sentiment)}`}>
                        {keyword.avg_sentiment >= 0 ? '+' : ''}{keyword.avg_sentiment.toFixed(3)}
                      </span>
                    </td>
                    
                    {/* Posts Found In */}
                    <td className="px-4 py-3 text-right">
                      <span className="font-technical text-text-secondary">
                        {keyword.posts_found_in.toLocaleString()}
                      </span>
                    </td>
                    
                    {/* Comments Found In */}
                    <td className="px-4 py-3 text-right">
                      <span className="font-technical text-text-secondary">
                        {keyword.comments_found_in.toLocaleString()}
                      </span>
                    </td>
                    
                    {/* Collections */}
                    <td className="px-4 py-3 text-center">
                      <span className="font-small text-text-secondary">
                        {formatCollections(keyword.collections_found_in)}
                      </span>
                    </td>
                    
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          /* Empty State */
          <div className="text-center py-12">
            <div className="text-text-tertiary mb-4">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="font-subsection text-text-primary mb-2">
              No Keyword Data Available
            </h3>
            <p className="font-body text-text-secondary max-w-md mx-auto">
              Keyword statistics are not available for this project. This may be because the analysis is still running or has not been completed yet.
            </p>
          </div>
        )}
      </div>
    </Modal>
  );
};

export default KeywordOverviewModal;