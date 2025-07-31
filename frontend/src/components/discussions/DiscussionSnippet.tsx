/**
 * DiscussionSnippet Component
 * Displays individual Reddit discussion snippets with keyword highlighting
 * and professional metadata presentation
 */

import React from 'react';
import { cleanRedditMarkdown } from '@/utils/textProcessing';
import { createOptimalWindow } from '@/utils/textWindowing';
import { highlightKeywords, highlightKeywordsByPosition } from '@/utils/keywordHighlighting';
import { formatDate, formatDateTime } from '@/utils/dateFormatting'; // Import both options
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

  // Fuzzy position matching approach
  const originalText = context.context;
  const cleanedText = cleanRedditMarkdown(originalText);
  const textWindow = createOptimalWindow(cleanedText, keywords, { maxLength: 280 });
  
  // Apply fuzzy position-based highlighting with sentiment colors
  let displayText: string;
  
  if (context.keyword_mentions && context.keyword_mentions.length > 0) {
    const adjustedKeywordMentions = context.keyword_mentions.map(mention => {
      // Start with the calculated position
      let basePosition = mention.position_in_content - textWindow.originalStart;
      
      // Skip if way out of bounds
      if (basePosition < -10 || basePosition > textWindow.text.length + 10) {
        return null;
      }
      
      const keyword = mention.keyword.toLowerCase();
      const searchRadius = 5; // 5 character window as requested
      
      // Search within the fuzzy window around the base position
      const searchStart = Math.max(0, basePosition - searchRadius);
      const searchEnd = Math.min(textWindow.text.length - keyword.length + 1, basePosition + searchRadius + 1);
      
      for (let pos = searchStart; pos < searchEnd; pos++) {
        const textAtPosition = textWindow.text.substring(pos, pos + keyword.length).toLowerCase();
        if (textAtPosition === keyword) {
          // Found exact match! Use this position
          return {
            ...mention,
            position: pos
          };
        }
      }
      
      // No exact match found within the fuzzy window
      return null;
    }).filter((mention): mention is NonNullable<typeof mention> => mention !== null);
    
    if (adjustedKeywordMentions.length > 0) {
      displayText = highlightKeywordsByPosition(textWindow.text, adjustedKeywordMentions);
    } else {
      // No fuzzy matches found, use original text without highlighting
      displayText = textWindow.text;
    }
  } else {
    // No keyword mention data, use original text
    displayText = textWindow.text;
  }
  
  // Determine if we should show windowing indicator
  const showWindowIndicator = textWindow.isWindowed && textWindow.windowType === 'middle';
  
  // CHANGED: Format the timestamp to show actual date instead of relative time
  const displayDate = formatDate(context.created_utc);

  
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
              {displayDate}
            </span>
          </div>
        </div>
      </div>

      {/* Discussion content with keyword highlighting */}
      <div className="mb-3">
        {showWindowIndicator && (
          <div className="font-small text-text-tertiary mb-1 italic">
            Showing relevant excerpt...
          </div>
        )}
        <div 
          className="font-body text-text-secondary leading-relaxed"
          dangerouslySetInnerHTML={{ __html: displayText }}
        />
      </div>

      {/* Footer with technical details */}
      <div className="flex items-center justify-between pt-3 border-t border-border-primary">
        <div className="flex items-center space-x-4">
        <span className="font-small text-text-tertiary">
          {context.keyword_mentions && context.keyword_mentions.length > 1 ? 'Avg. Sentiment Score' : 'Sentiment Score'}: 
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