/**
 * FullContextDisplay Component
 * Displays complete Reddit content for Context Explorer Modal
 * Shows full text without windowing, optimized for modal display
 */

import React from 'react';
import { cleanRedditMarkdown } from '@/utils/textProcessing';
import { highlightKeywordsByPosition } from '@/utils/keywordHighlighting';
import { formatDate } from '@/utils/dateFormatting';
import type { ContextInstance, FilteredContextInstance, CollectionMetadata } from '@/types/api';

interface FullContextDisplayProps {
  /** Complete context instance */
  context: ContextInstance | FilteredContextInstance;
  /** Keywords to highlight in the text */
  keywords: string[];
  /** Collection metadata for subreddit mapping */
  collectionsMetadata: CollectionMetadata[];
  /** Additional CSS classes */
  className?: string;
}

export const FullContextDisplay: React.FC<FullContextDisplayProps> = ({
  context,
  keywords,
  collectionsMetadata,
  className = ''
}) => {
  // Find the collection metadata for this context
  const collection = collectionsMetadata.find(c => c.id === context.collection_id);
  const subreddit = collection?.subreddit || 'unknown';

  // Clean the full text content
  const cleanedText = cleanRedditMarkdown(context.context);

  // Apply position-based highlighting with sentiment colors
  let displayText: string;

  if (context.keyword_mentions && context.keyword_mentions.length > 0) {
    // Transform keyword mentions to match PositionBasedKeyword interface
    const positionBasedKeywords = context.keyword_mentions.map(mention => ({
      keyword: mention.keyword,
      position: mention.position_in_content,
      sentiment_score: mention.sentiment_score
    }));
  
    displayText = highlightKeywordsByPosition(cleanedText, positionBasedKeywords);
  } else {
    // Fallback to plain text if no position data
    displayText = cleanedText;
  }

  // Format the timestamp
  const displayDate = formatDate(context.created_utc);

  // Determine sentiment styling for overall context
  const getSentimentStyling = (score: number) => {
    if (score > 0.001) {
      return {
        color: 'text-success',
        bgColor: 'bg-green-100',
        borderColor: 'border-success',
        label: 'Positive'
      };
    } else if (score < -0.001) {
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

  // Use the correct property name from FilteredContextInstance
  const avgSentiment = 'avg_sentiment_score' in context ? context.avg_sentiment_score : context.sentiment_score;
  const sentimentStyle = getSentimentStyling(avgSentiment);
  const contentTypeLabel = context.content_type === 'post' ? 'Post' : 'Comment';

  return (
    <div className={`p-6 bg-content rounded-default border border-border-primary hover:border-border-emphasis transition-all duration-150 ${className}`}>
      {/* Header with metadata */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {/* Subreddit and content type */}
          <div className="flex items-center space-x-2">
            <span className="font-medium text-text-primary">
              r/{subreddit}
            </span>
            <span className="text-text-tertiary">•</span>
            <span className="font-small text-text-tertiary">
              {contentTypeLabel}
            </span>
            <span className="text-text-tertiary">•</span>
            <span className="font-small text-text-tertiary">
              {displayDate}
            </span>
          </div>
        </div>

        {/* Overall sentiment indicator */}
        <div className={`px-2 py-1 rounded-input text-xs ${sentimentStyle.bgColor} ${sentimentStyle.borderColor} border`}>
          <span className={`font-medium ${sentimentStyle.color}`}>
          {sentimentStyle.label} ({avgSentiment > 0 ? '+' : ''}{avgSentiment.toFixed(3)})
          </span>
        </div>
      </div>

      {/* Full content with keyword highlighting */}
      <div className="mb-4">
        <div 
          className="font-body text-text-primary leading-relaxed text-base"
          dangerouslySetInnerHTML={{ __html: displayText }}
        />
      </div>

      {/* Footer with keyword mentions summary */}
      <div className="pt-4 border-t border-border-primary">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="font-small text-text-tertiary">
              Keywords Found: 
              <span className="ml-1 font-medium text-text-primary">
                {context.keyword_mentions?.length || 0}
              </span>
            </span>
            
            {/* Individual keyword mentions with sentiment */}
            <div className="flex flex-wrap gap-2">
              {context.keyword_mentions?.map((mention, index) => {
                const mentionSentimentStyle = getSentimentStyling(mention.sentiment_score);
                return (
                  <span
                    key={index}
                    className={`px-2 py-1 rounded-input text-xs font-medium ${mentionSentimentStyle.bgColor} ${mentionSentimentStyle.color} border ${mentionSentimentStyle.borderColor}`}
                    title={`${mention.keyword}: ${mention.sentiment_score > 0 ? '+' : ''}${mention.sentiment_score.toFixed(3)}`}
                  >
                    {mention.keyword}
                  </span>
                );
              })}
            </div>
          </div>

          {/* Reddit link indicator */}
            <button 
            className="font-small text-accent hover:text-blue-700 transition-colors duration-150"
            onClick={() => {
                if (context.content_type === 'post') {
                // For posts, use direct link
                const redditUrl = `https://redd.it/${context.content_reddit_id}`;
                window.open(redditUrl, '_blank', 'noopener,noreferrer');
                } else if ('parent_post_id' in context && context.parent_post_id) {
                // For comments with parent post ID, construct proper comment URL
                const redditUrl = `https://reddit.com/comments/${context.parent_post_id}/comment/${context.content_reddit_id}`;
                window.open(redditUrl, '_blank', 'noopener,noreferrer');
                } else {
                // Fallback for comments without parent post ID
                alert(`Comment ID: ${context.content_reddit_id} (Parent post not found)`);
                }
            }}
            >
            View on Reddit →
            </button>
        </div>
      </div>
    </div>
  );
};

export default FullContextDisplay;