/**
 * Keyword Overview Modal
 * Advanced keyword statistics and analysis display
 * Provides comprehensive view of keyword performance with sorting capabilities
 */

import React, { useState, useMemo } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { Search, TrendingUp } from 'lucide-react';
import type { ProjectResponse, KeywordData } from '@/types/api';

interface KeywordOverviewModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Function to call when modal should close */
  onClose: () => void;
  /** Project data containing keyword statistics */
  project: ProjectResponse;
  /** Function to call when user wants to explore specific keyword */
  onExploreKeyword: (keyword: string) => void;
  /** Function to call when user wants to view trends for specific keyword */
  onViewTrends: (keyword: string) => void;
}

type SortOption = 'mentions' | 'sentiment' | 'alphabetical';

// Helper function to calculate weighted average sentiment
const calculateWeightedAverageSentiment = (keywordsData: any[]) => {
  if (!keywordsData || keywordsData.length === 0) return 0;
  
  const totalWeightedSentiment = keywordsData.reduce((sum, kw) => {
    return sum + (kw.avg_sentiment * kw.total_mentions);
  }, 0);
  
  const totalMentions = keywordsData.reduce((sum, kw) => sum + kw.total_mentions, 0);
  
  return totalMentions > 0 ? totalWeightedSentiment / totalMentions : 0;
};

// Helper function to calculate sentiment distribution from keywords data
const calculateSentimentDistribution = (keywordsData: any[]) => {
  if (!keywordsData || keywordsData.length === 0) {
    return { positive: 0, neutral: 0, negative: 0 };
  }
  
  // Use weighted calculation based on mention counts
  let totalMentions = 0;
  let positiveWeighted = 0;
  let neutralWeighted = 0;
  let negativeWeighted = 0;
  
  keywordsData.forEach(kw => {
    const mentions = kw.total_mentions;
    totalMentions += mentions;
    
    if (kw.avg_sentiment > 0.1) {
      positiveWeighted += mentions;
    } else if (kw.avg_sentiment < -0.1) {
      negativeWeighted += mentions;
    } else {
      neutralWeighted += mentions;
    }
  });
  
  if (totalMentions === 0) {
    return { positive: 0, neutral: 0, negative: 0 };
  }
  
  return {
    positive: Math.round((positiveWeighted / totalMentions) * 100),
    neutral: Math.round((neutralWeighted / totalMentions) * 100),
    negative: Math.round((negativeWeighted / totalMentions) * 100)
  };
};

const KeywordOverviewModal: React.FC<KeywordOverviewModalProps> = ({
  isOpen,
  onClose,
  project,
  onExploreKeyword,
  onViewTrends
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

  // Handle explore context click
  const handleExploreClick = (keyword: string) => {
    onExploreKeyword(keyword);
  };

  // Handle trends view click
  const handleViewTrends = (keyword: string) => {
    onViewTrends(keyword);
  };

  // Sort options for dropdown
  const sortOptions = [
    { value: 'mentions', label: 'Most Mentions First' },
    { value: 'sentiment', label: 'Most Positive First' },
    { value: 'alphabetical', label: 'Alphabetical' }
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Keyword Overview"
      size="xl"
      className="max-h-[90vh]"
    >
      <div className="max-h-[75vh] overflow-y-auto pr-1">
        {/* Stats Summary Section */}
        <div className="mb-8 p-6 bg-panel rounded-default border border-border-primary">
          <h3 className="font-subsection text-text-primary mb-4">Keyword Statistics Overview</h3>
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {/* Total Mentions */}
            <div className="text-center">
              <div className="text-2xl font-semibold text-text-primary">
                {sortedKeywords.reduce((sum, kw) => sum + kw.total_mentions, 0).toLocaleString()}
              </div>
              <div className="text-text-secondary text-sm">Total Mentions</div>
            </div>
            
            {/* Average Sentiment */}
            <div className="text-center">
              <div className={`text-2xl font-semibold ${
                (() => {
                  const avgSent = calculateWeightedAverageSentiment(sortedKeywords);
                  return avgSent > 0.0001 ? 'text-success' : avgSent < -0.0001 ? 'text-danger' : 'text-text-secondary';
                })()
              }`}>
                {(() => {
                  const avgSent = calculateWeightedAverageSentiment(sortedKeywords);
                  return (avgSent >= 0 ? '+' : '') + avgSent.toFixed(3);
                })()}
              </div>
              <div className="text-text-secondary text-sm">Average Sentiment</div>
            </div>
            
            {/* Sentiment Distribution */}
<div className="text-center">
  <div className="text-2xl font-semibold text-text-primary">
    {(() => {
      const distribution = project.stats.sentiment_distribution || calculateSentimentDistribution(sortedKeywords);
      return (
        <div className="flex justify-center space-x-2">
          <span className="text-success">{distribution.positive}%</span>
          <span className="text-text-tertiary">/</span>
          <span className="text-text-secondary">{distribution.neutral}%</span>
          <span className="text-text-tertiary">/</span>
          <span className="text-danger">{distribution.negative}%</span>
        </div>
      );
    })()}
  </div>
  <div className="text-text-secondary text-sm">Sentiment Distribution</div>
</div>
            
            {/* Posts vs Comments */}
            <div className="text-center">
              <div className="text-2xl font-semibold text-text-primary">
                {(() => {
                  const totalPosts = project.stats.posts_analyzed || 0;
                  const totalComments = project.stats.comments_analyzed || 0;
                  const total = totalPosts + totalComments;
                  
                  if (total === 0) return '0% / 0%';
                  
                  const postsPercent = Math.round((totalPosts / total) * 100);
                  const commentsPercent = Math.round((totalComments / total) * 100);
                  return `${postsPercent}% / ${commentsPercent}%`;
                })()}
              </div>
              <div className="text-text-secondary text-sm">Posts / Comments</div>
            </div>
          </div>
          </div>

        {/* Sort Controls */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
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
                    <th className="px-4 py-3 text-center font-subsection text-text-primary">
                    Total Mentions
                  </th>
                  <th className="px-4 py-3 text-center font-subsection text-text-primary">
                    Avg Sentiment
                  </th>
                  <th className="px-4 py-3 text-center font-subsection text-text-primary">
                    Posts / Comments
                  </th>
                  <th className="px-4 py-3 text-center font-subsection text-text-primary">
                    Action
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
                    <td className="px-4 py-3 text-center">
                      <span className="font-technical text-text-primary">
                        {keyword.total_mentions.toLocaleString()}
                      </span>
                    </td>
                    
                    {/* Average Sentiment */}
                    <td className="px-4 py-3 text-center">
                      <span className={`font-technical font-medium ${getSentimentColor(keyword.avg_sentiment)}`}>
                        {keyword.avg_sentiment >= 0 ? '+' : ''}{keyword.avg_sentiment.toFixed(3)}
                      </span>
                    </td>
                    
                    {/* Posts / Comments Ratio */}
                    <td className="px-4 py-3 text-center">
                      <span className="font-technical text-text-secondary">
                        {(() => {
                          const totalPosts = keyword.posts_found_in || 0;
                          const totalComments = keyword.comments_found_in || 0;
                          const total = totalPosts + totalComments;
                          
                          if (total === 0) return '0% / 0%';
                          
                          const postsPercent = Math.round((totalPosts / total) * 100);
                          const commentsPercent = Math.round((totalComments / total) * 100);
                          return `${postsPercent}% / ${commentsPercent}%`;
                        })()}
                      </span>
                    </td>
                    
                    {/* Action */}
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center justify-center space-x-2">
                        <div className="relative group">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleExploreClick(keyword.keyword)}
                            className="p-2 w-10 h-10 flex items-center justify-center"
                          >
                            <Search className="h-3 w-3" />
                          </Button>
                          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                            Explore contexts
                          </div>
                        </div>
                        <div className="relative group">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewTrends(keyword.keyword)}
                            className="p-2 w-10 h-10 flex items-center justify-center"
                          >
                            <TrendingUp className="h-3 w-3" />
                          </Button>
                          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                            View trends
                          </div>
                        </div>
                      </div>
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