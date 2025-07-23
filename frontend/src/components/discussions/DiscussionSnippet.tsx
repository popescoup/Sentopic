/**
 * DiscussionSnippet Component
 * Displays individual Reddit discussion snippets with keyword highlighting
 * and professional metadata presentation
 */

import React from 'react';
import { cleanRedditMarkdown } from '@/utils/textProcessing';
import { createOptimalWindow } from '@/utils/textWindowing';
import { highlightKeywords } from '@/utils/keywordHighlighting';
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

  // Format the discussion text with new pipeline: clean → window → highlight
  const cleanedText = cleanRedditMarkdown(context.context);
  const textWindow = createOptimalWindow(cleanedText, keywords, { maxLength: 280 });
  // Create sentiment-based highlight classes
const getSentimentHighlightClasses = (score: number) => {
    if (score > 0.1) {
      return 'bg-green-200 text-green-800 px-1 py-0.5 rounded font-medium border border-green-300';
    } else if (score < -0.1) {
      return 'bg-red-200 text-red-800 px-1 py-0.5 rounded font-medium border border-red-300';
    } else {
      return 'bg-gray-200 text-gray-700 px-1 py-0.5 rounded font-medium border border-gray-300';
    }
  };
  
  const displayText = highlightKeywords(textWindow.text, keywords, {
    matchWordVariations: true, // Enable word variations for better matching
    highlightClasses: getSentimentHighlightClasses(context.sentiment_score)
  });
  
  // Determine if we should show windowing indicator
  const showWindowIndicator = textWindow.isWindowed && textWindow.windowType === 'middle';
  
  // CHANGED: Format the timestamp to show actual date instead of relative time
  // Option 1: Just the date (e.g., "Oct 15, 2024")
  const displayDate = formatDate(context.created_utc);
  
  // Option 2: Date + time (uncomment to use instead)
  // const displayDate = formatDateTime(context.created_utc);
  
  // Option 3: Custom format with more control
  // const displayDate = formatDate(context.created_utc, {
  //   year: 'numeric',
  //   month: 'short',
  //   day: 'numeric',
  //   weekday: 'short'  // Adds day of week like "Mon, Oct 15, 2024"
  // });
  
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