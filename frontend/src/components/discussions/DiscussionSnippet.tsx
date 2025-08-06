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

  // Position-aware text windowing
const originalText = context.context;
const cleanedText = cleanRedditMarkdown(originalText);

// Prepare known positions for windowing if available
const knownPositions = context.keyword_mentions?.map(mention => ({
  keyword: mention.keyword,
  position: mention.position_in_content
}));

const textWindow = createOptimalWindow(
  cleanedText, 
  keywords, 
  { maxLength: 280 }, 
  knownPositions
);

// Re-add debug logging
console.log('Window Debug (Updated):', {
  originalTextLength: originalText.length,
  cleanedTextLength: cleanedText.length,
  windowText: textWindow.text,
  windowType: textWindow.windowType,
  keywordMentions: context.keyword_mentions,
  knownPositions: knownPositions,
  keywordsFoundInWindow: keywords.filter(k => 
    textWindow.text.toLowerCase().includes(k.toLowerCase())
  ),
  windowStart: textWindow.originalStart,
  windowEnd: textWindow.originalEnd
});

// NEW: Debug the highlighting pipeline
if (context.keyword_mentions && context.keyword_mentions.length > 0) {
  console.log('Highlighting Debug:', {
    keywordMentions: context.keyword_mentions,
    windowStart: textWindow.originalStart,
    highlightingMethod: 'position-based'
  });
  
  context.keyword_mentions.forEach((mention, index) => {
    let basePosition = mention.position_in_content - textWindow.originalStart;
    console.log(`Mention ${index} (${mention.keyword}):`, {
      originalPosition: mention.position_in_content,
      windowStart: textWindow.originalStart,
      adjustedPosition: basePosition,
      isInBounds: basePosition >= -20 && basePosition <= textWindow.text.length + 20,
      textAtPosition: textWindow.text.substring(
        Math.max(0, basePosition - 5), 
        Math.min(textWindow.text.length, basePosition + mention.keyword.length + 5)
      )
    });
  });
}

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
      const searchRadius = Math.min(50, Math.max(20, keyword.length * 5));
      
      // Search within the fuzzy window around the base position
      const searchStart = Math.max(0, basePosition - searchRadius);
      const searchEnd = Math.min(textWindow.text.length - keyword.length + 1, basePosition + searchRadius + 1);
      
      for (let pos = searchStart; pos < searchEnd; pos++) {
        const textAtPosition = textWindow.text.substring(pos, pos + keyword.length).toLowerCase();
        if (textAtPosition === keyword.toLowerCase()) {  // <-- Add .toLowerCase()
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

  
  // Calculate sentiment for keywords visible in the preview window
const calculateVisibleKeywordsSentiment = () => {
  if (!context.keyword_mentions || context.keyword_mentions.length === 0) {
    return {
      score: context.sentiment_score,
      label: 'Sentiment Score',
      keywordCount: 0
    };
  }

  // Find which keywords are actually visible in the windowed text
  const visibleKeywordMentions = context.keyword_mentions.filter(mention => {
    const adjustedPosition = mention.position_in_content - textWindow.originalStart;
    // Check if the keyword position falls within our text window
    return adjustedPosition >= -mention.keyword.length && 
           adjustedPosition <= textWindow.text.length + mention.keyword.length;
  });

  if (visibleKeywordMentions.length === 0) {
    // Fallback to overall sentiment if no keywords found in window
    return {
      score: context.sentiment_score,
      label: 'Sentiment Score',
      keywordCount: 0
    };
  }

  if (visibleKeywordMentions.length === 1) {
    // Single visible keyword - use its specific sentiment
    return {
      score: visibleKeywordMentions[0].sentiment_score,
      label: 'Sentiment Score',
      keywordCount: 1
    };
  }

  // Multiple visible keywords - calculate average
  const avgSentiment = visibleKeywordMentions.reduce((sum, mention) => 
    sum + mention.sentiment_score, 0) / visibleKeywordMentions.length;
  
  return {
    score: avgSentiment,
    label: 'Avg. Sentiment Score',
    keywordCount: visibleKeywordMentions.length
  };
};

const visibleSentiment = calculateVisibleKeywordsSentiment();

// Determine sentiment styling
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

const sentimentStyle = getSentimentStyling(visibleSentiment.score);

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
          {visibleSentiment.label}: 
          <span className={`ml-1 font-technical ${sentimentStyle.color}`}>
            {visibleSentiment.score > 0 ? '+' : ''}{visibleSentiment.score.toFixed(3)}
          </span>
        </span>
        </div>
      </div>
    </div>
  );
};

export default DiscussionSnippet;