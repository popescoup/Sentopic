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

  // Apply position-based highlighting with proximity-based keyword matching
let displayText: string;

if (context.keyword_mentions && context.keyword_mentions.length > 0) {
  // Instead of trying to map positions, search for each keyword using proximity
  const foundKeywords: Array<{
    keyword: string;
    position: number;
    sentiment_score: number;
  }> = [];
  
  context.keyword_mentions.forEach(mention => {
    const keyword = mention.keyword.toLowerCase().trim();
    if (!keyword) return;
    
    // Get the approximate expected position in cleaned text
    // Use a rough ratio to estimate where the keyword should be
    const positionRatio = mention.position_in_content / context.context.length;
    const estimatedPosition = Math.floor(positionRatio * cleanedText.length);
    
    // Search around the estimated position first, then expand outward
    const searchRadius = Math.max(100, keyword.length * 10);
    const searchStart = Math.max(0, estimatedPosition - searchRadius);
    const searchEnd = Math.min(cleanedText.length, estimatedPosition + searchRadius);
    
    const cleanedLower = cleanedText.toLowerCase();
    let bestMatch: { position: number; distance: number } | null = null;
    
    // Find all occurrences in the search area
    let searchPos = searchStart;
    while (searchPos < searchEnd) {
      const foundIndex = cleanedLower.indexOf(keyword, searchPos);
      if (foundIndex === -1 || foundIndex >= searchEnd) break;
      
      // Check if it's a whole word
      const beforeChar = foundIndex > 0 ? cleanedText[foundIndex - 1] : ' ';
      const afterChar = foundIndex + keyword.length < cleanedText.length ? cleanedText[foundIndex + keyword.length] : ' ';
      const isWholeWord = /\W/.test(beforeChar) && /\W/.test(afterChar);
      
      if (isWholeWord) {
        const distance = Math.abs(foundIndex - estimatedPosition);
        
        if (!bestMatch || distance < bestMatch.distance) {
          bestMatch = { position: foundIndex, distance };
        }
      }
      
      searchPos = foundIndex + 1;
    }
    
    // If we found a match near the expected position, use it
    if (bestMatch) {
      // Check for overlaps with already found keywords
      const hasOverlap = foundKeywords.some(existing => {
        const existingEnd = existing.position + existing.keyword.length;
        const currentEnd = bestMatch!.position + keyword.length;
        return (bestMatch!.position < existingEnd && currentEnd > existing.position);
      });
      
      if (!hasOverlap) {
        // Validate that the found position actually contains the keyword
        const actualText = cleanedText.substring(bestMatch.position, bestMatch.position + mention.keyword.length);
        const expectedKeyword = mention.keyword.toLowerCase();
        
        if (actualText.toLowerCase() === expectedKeyword) {
          foundKeywords.push({
            keyword: mention.keyword, // Original casing
            position: bestMatch.position,
            sentiment_score: mention.sentiment_score // Correct sentiment for this specific occurrence
          });
        } else {
          console.warn(`Position validation failed for "${mention.keyword}":`, {
            expectedKeyword,
            actualText,
            position: bestMatch.position,
            contentId: context.content_reddit_id
          });
          
          // Try one more search without word boundary restrictions as fallback
          const simpleIndex = cleanedLower.indexOf(expectedKeyword);
          if (simpleIndex !== -1) {
            const simpleActualText = cleanedText.substring(simpleIndex, simpleIndex + mention.keyword.length);
            if (simpleActualText.toLowerCase() === expectedKeyword) {
              foundKeywords.push({
                keyword: mention.keyword,
                position: simpleIndex,
                sentiment_score: mention.sentiment_score
              });
              console.log(`Fallback search succeeded for "${mention.keyword}" at position ${simpleIndex}`);
            }
          }
        }
      }
    }
  });
  
  // Debug logging
  console.log('Keyword search results:', {
    contentId: context.content_reddit_id,
    originalMentions: context.keyword_mentions.map(m => ({
      keyword: m.keyword,
      originalPos: m.position_in_content,
      sentiment: m.sentiment_score
    })),
    foundKeywords: foundKeywords.map(f => ({
      keyword: f.keyword,
      foundPos: f.position,
      sentiment: f.sentiment_score,
      textAtPosition: cleanedText.substring(f.position, f.position + f.keyword.length)
    })),
    textLengths: {
      original: context.context.length,
      cleaned: cleanedText.length,
      ratio: cleanedText.length / context.context.length
    },
    cleanedTextPreview: cleanedText.substring(0, 200) + '...'
  });
  
  if (foundKeywords.length > 0) {
    // Sort by position
    foundKeywords.sort((a, b) => a.position - b.position);
    
    // Debug each keyword before highlighting
    foundKeywords.forEach((kw, index) => {
      const actualText = cleanedText.substring(kw.position, kw.position + kw.keyword.length);
      console.log(`Pre-highlight validation ${index}:`, {
        keyword: kw.keyword,
        position: kw.position,
        expectedText: kw.keyword,
        actualTextAtPosition: actualText,
        matches: actualText.toLowerCase() === kw.keyword.toLowerCase(),
        surroundingText: cleanedText.substring(Math.max(0, kw.position - 10), kw.position + kw.keyword.length + 10)
      });
    });
    
    // Use the highlighting function
    const hasMultipleKeywords = foundKeywords.length > 1;
    displayText = highlightKeywordsByPositionWithTooltips(cleanedText, foundKeywords, hasMultipleKeywords);
  } else {
    console.log('No keywords found for highlighting');
    displayText = cleanedText;
  }
} else {
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