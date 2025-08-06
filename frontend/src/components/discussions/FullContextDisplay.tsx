/**
 * FullContextDisplay Component
 * Displays complete Reddit content for Context Explorer Modal
 * Shows full text without windowing, optimized for modal display
 */

import React from 'react';
import { cleanRedditMarkdown } from '@/utils/textProcessing';
import { highlightKeywordsByPosition, highlightKeywordsByPositionWithTooltips } from '@/utils/keywordHighlighting';
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

  // Apply position-based highlighting with sentiment colors, conditional tooltips, and fuzzy matching
    let displayText: string;

    if (context.keyword_mentions && context.keyword_mentions.length > 0) {
    // Use fuzzy position-based highlighting with sentiment colors
    const adjustedKeywordMentions = context.keyword_mentions.map(mention => {
        // Start with the original position
        let basePosition = mention.position_in_content;
        
        // Skip if way out of bounds
        if (basePosition < -10 || basePosition > cleanedText.length + 10) {
        return null;
        }
        
        const keyword = mention.keyword.toLowerCase();
        const searchRadius = Math.min(50, Math.max(20, keyword.length * 5));
        
        // Search within the fuzzy window around the base position
        const searchStart = Math.max(0, basePosition - searchRadius);
        const searchEnd = Math.min(cleanedText.length - keyword.length + 1, basePosition + searchRadius + 1);
        
        for (let pos = searchStart; pos < searchEnd; pos++) {
        const textAtPosition = cleanedText.substring(pos, pos + keyword.length).toLowerCase();
        if (textAtPosition === keyword.toLowerCase()) {
            // Found exact match! Use this position
            return {
            ...mention,
            position_in_content: pos
            };
        }
        }
        
        // No exact match found within the fuzzy window
        return null;
    }).filter((mention): mention is NonNullable<typeof mention> => mention !== null);
    
    if (adjustedKeywordMentions.length > 0) {
        // Transform to PositionBasedKeyword interface
        const positionBasedKeywords = adjustedKeywordMentions.map(mention => ({
        keyword: mention.keyword,
        position: mention.position_in_content,
        sentiment_score: mention.sentiment_score
        }));

        // Use enhanced highlighting with tooltips for multiple keywords
        const hasMultipleKeywords = adjustedKeywordMentions.length > 1;
        displayText = highlightKeywordsByPositionWithTooltips(cleanedText, positionBasedKeywords, hasMultipleKeywords);
    } else {
        // No fuzzy matches found, use original text without highlighting
        displayText = cleanedText;
    }
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
        </div>

      {/* Full content with keyword highlighting */}
      <div className="mb-4">
        <div 
          className="font-body text-text-primary leading-relaxed text-base"
          dangerouslySetInnerHTML={{ __html: displayText }}
        />
      </div>

      {/* Footer with sentiment summary */}
        <div className="pt-4 border-t border-border-primary">
        <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
            <span className="font-small text-text-tertiary">
                {context.keyword_mentions && context.keyword_mentions.length > 1 ? 'Avg. Sentiment Score' : 'Sentiment Score'}: 
                <span className={`ml-1 font-technical ${sentimentStyle.color}`}>
                {avgSentiment > 0 ? '+' : ''}{avgSentiment.toFixed(3)}
                </span>
            </span>
            {context.keyword_mentions && context.keyword_mentions.length > 1 && (
                <span className="font-small text-text-tertiary italic">
                *Hover over keywords for individual sentiment scores
                </span>
            )}
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