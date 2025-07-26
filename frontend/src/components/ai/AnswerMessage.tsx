/**
 * Answer Message Component
 * Displays AI responses with sources and analytics insights
 */

import React, { useState } from 'react';
import type { ChatResponse } from '@/types/api';

interface AnswerMessageProps {
  response: ChatResponse;
  timestamp: string;
}

const AnswerMessage: React.FC<AnswerMessageProps> = ({
  response,
  timestamp
}) => {
  const [showSources, setShowSources] = useState(false);
  const [showInsights, setShowInsights] = useState(false);

  // Format timestamp for display
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.abs(now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      const minutes = Math.floor(diffInHours * 60);
      return minutes <= 1 ? 'Just now' : `${minutes}m ago`;
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  // Get search type display name
  const getSearchTypeDisplay = (searchType: string) => {
    switch (searchType) {
      case 'keyword':
        return 'Keyword Search';
      case 'local_semantic':
        return 'Semantic (Local)';
      case 'cloud_semantic':
        return 'Semantic (Cloud)';
      case 'analytics_driven':
        return 'Analytics Search';
      default:
        return 'Auto Search';
    }
  };

  const hasAdditionalInfo = response.sources.length > 0 || Object.keys(response.analytics_insights).length > 0;

  return (
    <div className="mb-4">
      {/* AI Response Bubble */}
      <div className="flex justify-start">
        <div className="max-w-[85%]">
          {/* AI Avatar/Icon */}
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
              </svg>
            </div>

            <div className="flex-1">
              {/* Response Content */}
              <div className="bg-panel border border-border-primary px-4 py-3 rounded-input rounded-tl-sm">
                <p className="font-body text-sm text-text-primary leading-relaxed whitespace-pre-wrap">
                  {response.message}
                </p>
              </div>

              {/* Metadata and Actions */}
              <div className="flex items-center justify-between mt-1">
                <div className="flex items-center space-x-2 text-xs text-text-tertiary">
                  <span>{getSearchTypeDisplay(response.search_type)}</span>
                  <span>•</span>
                  <span>{response.discussions_found} discussions found</span>
                  <span>•</span>
                  <span>{formatTime(timestamp)}</span>
                </div>

                {/* Additional Info Toggles */}
                {hasAdditionalInfo && (
                  <div className="flex items-center space-x-1">
                    {response.sources.length > 0 && (
                      <button
                        onClick={() => setShowSources(!showSources)}
                        className="text-xs text-accent hover:text-blue-700 transition-colors duration-150 px-2 py-1 rounded hover:bg-hover-blue"
                      >
                        {showSources ? 'Hide' : 'Show'} Sources ({response.sources.length})
                      </button>
                    )}
                    
                    {Object.keys(response.analytics_insights).length > 0 && (
                      <button
                        onClick={() => setShowInsights(!showInsights)}
                        className="text-xs text-accent hover:text-blue-700 transition-colors duration-150 px-2 py-1 rounded hover:bg-hover-blue"
                      >
                        {showInsights ? 'Hide' : 'Show'} Data
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Sources Expansion */}
              {showSources && response.sources.length > 0 && (
                <div className="mt-3 p-3 bg-content border border-border-primary rounded-input">
                  <h5 className="font-medium text-text-primary text-xs mb-2">Sources:</h5>
                  <div className="space-y-2">
                    {response.sources.slice(0, 3).map((source, index) => (
                      <div key={index} className="text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-text-primary">
                            {source.content_type === 'post' ? 'Post' : 'Comment'}
                          </span>
                          {source.relevance_score && (
                            <span className="text-text-tertiary">
                              {Math.round(source.relevance_score * 100)}% relevant
                            </span>
                          )}
                        </div>
                        {source.snippet && (
                          <p className="text-text-secondary mt-1 italic">
                            "{source.snippet.substring(0, 120)}..."
                          </p>
                        )}
                      </div>
                    ))}
                    {response.sources.length > 3 && (
                      <p className="text-xs text-text-tertiary">
                        + {response.sources.length - 3} more sources
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Analytics Insights Expansion */}
              {showInsights && Object.keys(response.analytics_insights).length > 0 && (
                <div className="mt-3 p-3 bg-content border border-border-primary rounded-input">
                  <h5 className="font-medium text-text-primary text-xs mb-2">Analytics Data:</h5>
                  <div className="space-y-2">
                    {Object.entries(response.analytics_insights).map(([key, value], index) => (
                      <div key={index} className="text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-text-primary capitalize">
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <span className="text-text-secondary font-mono">
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Cost Information (if available) */}
              {response.cost_estimate > 0 && (
                <div className="mt-2 text-xs text-text-tertiary">
                  Cost: ${response.cost_estimate.toFixed(4)} • Tokens: {response.tokens_used}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnswerMessage;