/**
 * DiscussionSnippet Component
 * Displays individual Reddit discussion snippets with keyword highlighting
 * and professional metadata presentation
 */

import React from 'react';
import { highlightKeywords, truncateText } from '@/utils/textProcessing';
import { formatRelativeTime } from '@/utils/dateFormatting';
import type { ContextInstance, CollectionMetadata } from '@/types/api';

interface DiscussionSnippetProps {
  /** Discussion context instance */
  context: ContextInstance;
  /** Keywords to highlight in the text */
  keywords: string[];
  /** Collection metadata for subreddit mapping */
  collectionsMetadata: CollectionMetadata[];
  /** Additional CSS classes */
  className?: string;
}

export const DiscussionSnippet: React.FC<DiscussionSnippetProps> = ({
  context,
  keywords,
  collectionsMetadata,
  className = ''
}) => {
  // Find the collection metadata for this context
  const collection = collectionsMetadata.find(c => c.id === context.collection_id);
  const subreddit = collection?.subreddit || 'unknown';

  // Format the discussion text with keyword highlighting
  const highlightedText = highlightKeywords(context.context, keywords);
  
  // Truncate if too long (keep it readable in the snippet view)
  const displayText = truncateText(highlightedText, 280);
  
  // Format the timestamp
  const relativeTime = formatRelativeTime(context.created_utc);
  
  // Determine sentiment styling
  const getSentimentStyling = (score: number) => {
    if (score > 0.1) {
      return {
        color: 'text-success',
        bgColor: 'bg-green-100',
        borderColor: 'border-success',
        label: 'Positive'
      };
    } else if (score < -0.1) {
      return {
        color: 'text-danger',
        bgColor: 'bg-red-100',
        borderColor: 'border-danger',
        label: 'Negative'
      };
    } else {
      return {
        color: 'text-text-tertiary',
        bgColor: 'bg-gray-100',
        borderColor: 'border-border-secondary',
        label: 'Neutral'
      };
    }
  };

  const sentimentStyle = getSentimentStyling(context.sentiment_score);

  // Format content type for display
  const contentTypeLabel = context.content_type === 'post' ? 'Post' : 'Comment';
  
  return (
    <div className={`p-4 bg-panel rounded-input border border-border-primary hover:border-border-emphasis transition-all duration-150 ${className}`}>
      {/* Header with metadata */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          {/* Subreddit and content type */}
          <div className="flex items-center space-x-2">
            <span className="font-small text-text-tertiary">
              r/{subreddit}
            </span>
            <span className="text-text-tertiary">•</span>
            <span className="font-small text-text-tertiary">
              {contentTypeLabel}
            </span>
            <span className="text-text-tertiary">•</span>
            <span className="font-small text-text-tertiary">
              {relativeTime}
            </span>
          </div>
        </div>
        
        {/* Sentiment indicator */}
        <div className={`inline-flex items-center px-2 py-1 rounded-input text-xs font-medium border ${sentimentStyle.bgColor} ${sentimentStyle.color} ${sentimentStyle.borderColor}`}>
          {sentimentStyle.label}
        </div>
      </div>

      {/* Discussion content with keyword highlighting */}
      <div className="mb-3">
        <div 
          className="font-body text-text-secondary leading-relaxed"
          dangerouslySetInnerHTML={{ __html: displayText }}
        />
      </div>

      {/* Footer with technical details */}
      <div className="flex items-center justify-between pt-3 border-t border-border-primary">
        <div className="flex items-center space-x-4">
          <span className="font-small text-text-tertiary">
            Sentiment Score: 
            <span className={`ml-1 font-technical ${sentimentStyle.color}`}>
              {context.sentiment_score > 0 ? '+' : ''}{context.sentiment_score.toFixed(3)}
            </span>
          </span>
        </div>
        
        {/* Link indicator for Phase 5 context explorer */}
        <button 
          className="font-small text-accent hover:text-blue-700 transition-colors duration-150"
          onClick={() => {
            // Placeholder for Phase 5 - will open context explorer with this specific discussion
            console.log('Future: Open context explorer for', context.content_reddit_id);
          }}
        >
          View Full Context →
        </button>
      </div>
    </div>
  );
};

export default DiscussionSnippet;