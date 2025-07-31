/**
 * Keyword Highlighting Utilities
 * Dedicated system for finding and highlighting keywords in text
 */

import { escapeHtml } from './textProcessing';

export interface KeywordMatch {
  keyword: string;
  start: number;
  end: number;
  matchedText: string;
}

export interface HighlightingOptions {
  /** Whether to match only complete words (default: true) */
  strictWordBoundaries: boolean;
  /** Whether to perform case-insensitive matching (default: true) */
  caseInsensitive: boolean;
  /** Whether to match word variations like plurals, verb forms (default: false) */
  matchWordVariations: boolean;
  /** CSS classes to apply to highlighted keywords */
  highlightClasses: string;
  /** Whether to escape HTML in the text before highlighting (default: true) */
  escapeHtml: boolean;
}

const DEFAULT_HIGHLIGHTING_OPTIONS: HighlightingOptions = {
  strictWordBoundaries: true,
  caseInsensitive: true,
  matchWordVariations: false,
  highlightClasses: 'bg-accent text-white px-1 py-0.5 rounded font-medium',
  escapeHtml: true
};

/**
 * Generates word variation patterns for flexible keyword matching
 * Handles common variations like plurals, verb forms, etc.
 * @param keyword - Base keyword to generate variations for
 * @returns Array of regex patterns to match variations
 */
const generateWordVariations = (keyword: string): string[] => {
  const variations = [keyword]; // Always include the original
  const lowerKeyword = keyword.toLowerCase();
  
  // Handle plurals and verb forms
  if (lowerKeyword.length > 3) {
    // Add common suffixes
    const suffixes = ['s', 'es', 'ed', 'ing', 'er', 'est', 'ly', 'ion', 'tion', 'ness', 'ment'];
    
    suffixes.forEach(suffix => {
      variations.push(`${keyword}${suffix}`);
    });
    
    // Handle words ending in 'y' -> 'ies'
    if (lowerKeyword.endsWith('y')) {
      const base = keyword.slice(0, -1);
      variations.push(`${base}ies`);
    }
    
    // Handle words ending in 'e' -> drop 'e' and add suffix
    if (lowerKeyword.endsWith('e')) {
      const base = keyword.slice(0, -1);
      variations.push(`${base}ing`);
      variations.push(`${base}ed`);
    }
    
    // Handle doubling consonants (e.g., 'run' -> 'running')
    if (lowerKeyword.length >= 3) {
      const lastChar = lowerKeyword[lowerKeyword.length - 1];
      const secondLastChar = lowerKeyword[lowerKeyword.length - 2];
      const thirdLastChar = lowerKeyword[lowerKeyword.length - 3];
      
      // Simple consonant doubling rule (not perfect but catches common cases)
      if (!/[aeiou]/.test(lastChar) && /[aeiou]/.test(secondLastChar) && !/[aeiou]/.test(thirdLastChar)) {
        variations.push(`${keyword}${lastChar}ing`);
        variations.push(`${keyword}${lastChar}ed`);
      }
    }
  }
  
  return variations;
};

/**
 * Finds all keyword matches in text
 * @param text - The text to search in
 * @param keywords - Array of keywords to find
 * @param options - Highlighting options
 * @returns Array of keyword matches with positions
 */
export const findKeywordMatches = (
  text: string,
  keywords: string[],
  options: Partial<HighlightingOptions> = {}
): KeywordMatch[] => {
  if (!text || !keywords || keywords.length === 0) {
    return [];
  }

  const opts = { ...DEFAULT_HIGHLIGHTING_OPTIONS, ...options };
  const matches: KeywordMatch[] = [];

  keywords.forEach(keyword => {
    if (!keyword.trim()) return;

    // Get keyword variations if enabled
    const keywordVariations = opts.matchWordVariations 
      ? generateWordVariations(keyword)
      : [keyword];

    keywordVariations.forEach(variation => {
      // Escape special regex characters in the variation
      const escapedVariation = variation.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      
      // Build regex pattern based on options
      let pattern;
      if (opts.strictWordBoundaries) {
        pattern = `\\b(${escapedVariation})\\b`;
      } else {
        pattern = `(${escapedVariation})`;
      }

      const flags = opts.caseInsensitive ? 'gi' : 'g';
      const regex = new RegExp(pattern, flags);
      
      let match;
      while ((match = regex.exec(text)) !== null) {
        matches.push({
          keyword: keyword, // Always use the original keyword, not the variation
          start: match.index,
          end: match.index + match[0].length,
          matchedText: match[0]
        });
        
        // Prevent infinite loop on zero-length matches
        if (match.index === regex.lastIndex) {
          regex.lastIndex++;
        }
      }
    });
  });

  // Sort matches by position and remove duplicates
  const sortedMatches = matches.sort((a, b) => a.start - b.start);
  
  // Remove overlapping matches (keep the first/longest one)
  const filteredMatches: KeywordMatch[] = [];
  sortedMatches.forEach(match => {
    const hasOverlap = filteredMatches.some(existing => 
      (match.start >= existing.start && match.start < existing.end) ||
      (match.end > existing.start && match.end <= existing.end)
    );
    
    if (!hasOverlap) {
      filteredMatches.push(match);
    }
  });

  return filteredMatches;
};

/**
 * Applies highlighting to text based on keyword matches
 * @param text - The original text
 * @param matches - Array of keyword matches to highlight
 * @param options - Highlighting options
 * @returns HTML string with highlighted keywords
 */
export const applyHighlighting = (
  text: string,
  matches: KeywordMatch[],
  options: Partial<HighlightingOptions> = {}
): string => {
  if (!text || !matches || matches.length === 0) {
    const opts = { ...DEFAULT_HIGHLIGHTING_OPTIONS, ...options };
    return opts.escapeHtml ? escapeHtml(text) : text;
  }

  const opts = { ...DEFAULT_HIGHLIGHTING_OPTIONS, ...options };
  let result = opts.escapeHtml ? escapeHtml(text) : text;
  
  // Apply highlighting in reverse order to maintain correct positions
  const sortedMatches = [...matches].sort((a, b) => b.start - a.start);
  
  sortedMatches.forEach(match => {
    const beforeMatch = result.substring(0, match.start);
    const matchText = result.substring(match.start, match.end);
    const afterMatch = result.substring(match.end);
    
    const highlightedMatch = `<mark class="${opts.highlightClasses}">${matchText}</mark>`;
    result = beforeMatch + highlightedMatch + afterMatch;
  });

  return result;
};

/**
 * One-step function to highlight keywords in text (maintains backward compatibility)
 * @param text - The text to highlight keywords in
 * @param keywords - Array of keywords to highlight
 * @param options - Highlighting options
 * @returns HTML string with highlighted keywords
 */
export const highlightKeywords = (
  text: string,
  keywords: string[],
  options: Partial<HighlightingOptions> = {}
): string => {
  if (!text || !keywords || keywords.length === 0) {
    const opts = { ...DEFAULT_HIGHLIGHTING_OPTIONS, ...options };
    return opts.escapeHtml ? escapeHtml(text) : text;
  }

  const matches = findKeywordMatches(text, keywords, options);
  return applyHighlighting(text, matches, options);
};

/**
 * Finds the position of the first keyword match in text
 * @param text - Text to search in
 * @param keywords - Keywords to look for
 * @param options - Search options
 * @returns Position of first keyword, or -1 if none found
 */
export const findFirstKeywordPosition = (
  text: string,
  keywords: string[],
  options: Partial<HighlightingOptions> = {}
): number => {
  const matches = findKeywordMatches(text, keywords, options);
  return matches.length > 0 ? matches[0].start : -1;
};

/**
 * Checks if text contains any of the specified keywords
 * @param text - Text to check
 * @param keywords - Keywords to look for
 * @param options - Search options
 * @returns True if any keywords are found
 */
export const containsKeywords = (
  text: string,
  keywords: string[],
  options: Partial<HighlightingOptions> = {}
): boolean => {
  return findFirstKeywordPosition(text, keywords, options) !== -1;
};

/**
 * Interface for position-based keyword data
 */
export interface PositionBasedKeyword {
  keyword: string;
  position: number;
  sentiment_score: number;
}

/**
 * Apply highlighting based on exact positions and individual sentiment scores
 * @param text - The original text
 * @param positionKeywords - Array of keywords with positions and sentiment scores
 * @param options - Highlighting options
 * @returns HTML string with position-based highlighted keywords
 */
export const highlightKeywordsByPosition = (
  text: string,
  positionKeywords: PositionBasedKeyword[],
  options: Partial<HighlightingOptions> = {}
): string => {
  if (!text || !positionKeywords || positionKeywords.length === 0) {
    const opts = { ...DEFAULT_HIGHLIGHTING_OPTIONS, ...options };
    return opts.escapeHtml ? escapeHtml(text) : text;
  }

  const opts = { ...DEFAULT_HIGHLIGHTING_OPTIONS, ...options };
  let result = opts.escapeHtml ? escapeHtml(text) : text;
  
  // Sort by position in reverse order to maintain correct positions during replacement
  const sortedKeywords = [...positionKeywords].sort((a, b) => b.position - a.position);
  
  // Apply highlighting for each keyword at its exact position
  sortedKeywords.forEach(keywordData => {
    const { keyword, position, sentiment_score } = keywordData;
    
    // Find the end position of the keyword
    const endPosition = position + keyword.length;
    
    // Ensure the position is valid
    if (position >= 0 && endPosition <= result.length) {
      const beforeMatch = result.substring(0, position);
      const matchText = result.substring(position, endPosition);
      const afterMatch = result.substring(endPosition);
      
      // Generate sentiment-based highlight classes
      const sentimentClasses = getSentimentHighlightClasses(sentiment_score);
      const highlightedMatch = `<mark class="${sentimentClasses}" data-sentiment="${sentiment_score.toFixed(3)}">${matchText}</mark>`;
      
      result = beforeMatch + highlightedMatch + afterMatch;
    }
  });

  return result;
};

/**
 * Generate sentiment-based CSS classes for highlighting
 * @param score - Sentiment score (-1 to +1)
 * @returns CSS class string for highlighting
 */
const getSentimentHighlightClasses = (score: number): string => {
  if (score > 0.1) {
    return 'bg-green-200 text-green-800 px-1 py-0.5 rounded font-medium border border-green-300';
  } else if (score < -0.1) {
    return 'bg-red-200 text-red-800 px-1 py-0.5 rounded font-medium border border-red-300';
  } else {
    return 'bg-gray-200 text-gray-700 px-1 py-0.5 rounded font-medium border border-gray-300';
  }
};