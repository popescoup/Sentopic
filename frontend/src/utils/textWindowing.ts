/**
 * Text Windowing Utilities
 * Smart text window extraction around keywords for optimal snippet display
 */

import { findKeywordMatches, type HighlightingOptions } from './keywordHighlighting';

export interface TextWindow {
  /** The windowed text content */
  text: string;
  /** Whether the text was truncated */
  isWindowed: boolean;
  /** Type of windowing applied */
  windowType: 'beginning' | 'middle' | 'end' | 'full';
  /** Start position in original text */
  originalStart: number;
  /** End position in original text */
  originalEnd: number;
}

export interface WindowingOptions {
  /** Maximum length of the windowed text */
  maxLength: number;
  /** Context padding around keywords (characters) */
  contextPadding: number;
  /** Whether to try to break at word boundaries */
  respectWordBoundaries: boolean;
  /** Maximum distance to look for word boundaries */
  wordBoundarySearchDistance: number;
  /** Text to use for leading ellipsis */
  leadingEllipsis: string;
  /** Text to use for trailing ellipsis */
  trailingEllipsis: string;
}

const DEFAULT_WINDOWING_OPTIONS: WindowingOptions = {
  maxLength: 280,
  contextPadding: 50,
  respectWordBoundaries: true,
  wordBoundarySearchDistance: 20,
  leadingEllipsis: '...',
  trailingEllipsis: '...'
};

/**
 * Creates an optimal text window around keywords
 * @param text - The original text
 * @param keywords - Keywords to center the window around
 * @param options - Windowing options
 * @returns TextWindow object with windowed text and metadata
 */
export const createOptimalWindow = (
  text: string,
  keywords: string[],
  options: Partial<WindowingOptions> = {}
): TextWindow => {
  if (!text) {
    return {
      text: '',
      isWindowed: false,
      windowType: 'full',
      originalStart: 0,
      originalEnd: 0
    };
  }

  const opts = { ...DEFAULT_WINDOWING_OPTIONS, ...options };

  // If text is already short enough, return as-is
  if (text.length <= opts.maxLength) {
    return {
      text: text,
      isWindowed: false,
      windowType: 'full',
      originalStart: 0,
      originalEnd: text.length
    };
  }

  // If no keywords provided, return beginning truncation
  if (!keywords || keywords.length === 0) {
    return createBeginningWindow(text, opts);
  }

  // Find keyword matches to determine optimal window position
  const matches = findKeywordMatches(text, keywords, {
    strictWordBoundaries: true,
    caseInsensitive: true,
    matchWordVariations: true // Use word variations for consistent windowing
  });

  // If no keywords found, return beginning truncation
  if (matches.length === 0) {
    return createBeginningWindow(text, opts);
  }

  // Find the earliest keyword position
  const earliestMatch = matches.reduce((earliest, current) => 
    current.start < earliest.start ? current : earliest
  );

  // If the earliest keyword is close to the beginning, show from start
  if (earliestMatch.start <= opts.contextPadding) {
    return createBeginningWindow(text, opts);
  }

  // If the earliest keyword is close to the end, show ending
  if (earliestMatch.start >= text.length - opts.maxLength + opts.contextPadding) {
    return createEndingWindow(text, opts);
  }

  // Create a middle window centered around the earliest keyword
  return createMiddleWindow(text, earliestMatch.start, opts);
};

/**
 * Creates a window from the beginning of the text
 */
const createBeginningWindow = (
  text: string,
  options: WindowingOptions
): TextWindow => {
  const maxContentLength = options.maxLength - options.trailingEllipsis.length;
  let endPos = Math.min(text.length, maxContentLength);

  // Try to end at a word boundary if requested
  if (options.respectWordBoundaries && endPos < text.length) {
    const searchStart = Math.max(0, endPos - options.wordBoundarySearchDistance);
    const lastSpaceIndex = text.lastIndexOf(' ', endPos);
    
    if (lastSpaceIndex > searchStart) {
      endPos = lastSpaceIndex;
    }
  }

  const windowedText = text.substring(0, endPos).trim();
  const needsEllipsis = endPos < text.length;

  return {
    text: needsEllipsis ? windowedText + options.trailingEllipsis : windowedText,
    isWindowed: needsEllipsis,
    windowType: 'beginning',
    originalStart: 0,
    originalEnd: endPos
  };
};

/**
 * Creates a window from the end of the text
 */
const createEndingWindow = (
  text: string,
  options: WindowingOptions
): TextWindow => {
  const maxContentLength = options.maxLength - options.leadingEllipsis.length;
  let startPos = Math.max(0, text.length - maxContentLength);

  // Try to start at a word boundary if requested
  if (options.respectWordBoundaries && startPos > 0) {
    const searchEnd = Math.min(text.length, startPos + options.wordBoundarySearchDistance);
    const nextSpaceIndex = text.indexOf(' ', startPos);
    
    if (nextSpaceIndex !== -1 && nextSpaceIndex < searchEnd) {
      startPos = nextSpaceIndex + 1;
    }
  }

  const windowedText = text.substring(startPos).trim();
  const needsEllipsis = startPos > 0;

  return {
    text: needsEllipsis ? options.leadingEllipsis + windowedText : windowedText,
    isWindowed: needsEllipsis,
    windowType: 'end',
    originalStart: startPos,
    originalEnd: text.length
  };
};

/**
 * Creates a window in the middle of the text around a specific position
 */
const createMiddleWindow = (
  text: string,
  centerPosition: number,
  options: WindowingOptions
): TextWindow => {
  const ellipsisLength = options.leadingEllipsis.length + options.trailingEllipsis.length;
  const maxContentLength = options.maxLength - ellipsisLength;

  // Calculate initial window boundaries
  const halfWindow = Math.floor(maxContentLength / 2);
  let startPos = Math.max(0, centerPosition - halfWindow);
  let endPos = Math.min(text.length, startPos + maxContentLength);

  // Adjust start position if we hit the end
  if (endPos === text.length && startPos > 0) {
    startPos = Math.max(0, text.length - maxContentLength);
  }

  // Try to adjust boundaries to word boundaries if requested
  if (options.respectWordBoundaries) {
    // Adjust start position to word boundary
    if (startPos > 0) {
      const searchStart = Math.max(0, startPos - options.wordBoundarySearchDistance);
      const spaceIndex = text.lastIndexOf(' ', startPos);
      if (spaceIndex > searchStart) {
        startPos = spaceIndex + 1;
      }
    }

    // Adjust end position to word boundary
    if (endPos < text.length) {
      const searchEnd = Math.min(text.length, endPos + options.wordBoundarySearchDistance);
      const spaceIndex = text.indexOf(' ', endPos);
      if (spaceIndex !== -1 && spaceIndex < searchEnd) {
        endPos = spaceIndex;
      }
    }
  }

  const windowedText = text.substring(startPos, endPos).trim();
  const needsLeadingEllipsis = startPos > 0;
  const needsTrailingEllipsis = endPos < text.length;

  let finalText = windowedText;
  if (needsLeadingEllipsis) {
    finalText = options.leadingEllipsis + finalText;
  }
  if (needsTrailingEllipsis) {
    finalText = finalText + options.trailingEllipsis;
  }

  return {
    text: finalText,
    isWindowed: needsLeadingEllipsis || needsTrailingEllipsis,
    windowType: 'middle',
    originalStart: startPos,
    originalEnd: endPos
  };
};

/**
 * Creates multiple windows around different keyword clusters
 * @param text - The original text
 * @param keywords - Keywords to find
 * @param options - Windowing options
 * @returns Array of text windows, one for each keyword cluster
 */
export const createMultipleWindows = (
  text: string,
  keywords: string[],
  options: Partial<WindowingOptions> = {}
): TextWindow[] => {
  const opts = { ...DEFAULT_WINDOWING_OPTIONS, ...options };
  const matches = findKeywordMatches(text, keywords, {
    strictWordBoundaries: true,
    caseInsensitive: true,
    matchWordVariations: true // Use word variations for consistent windowing
  });

  if (matches.length === 0) {
    return [createOptimalWindow(text, keywords, options)];
  }

  // Group matches into clusters based on proximity
  const clusters: typeof matches[] = [];
  const clusterDistance = opts.maxLength / 2;

  matches.forEach(match => {
    let addedToCluster = false;
    
    for (const cluster of clusters) {
      const clusterStart = Math.min(...cluster.map(m => m.start));
      const clusterEnd = Math.max(...cluster.map(m => m.end));
      
      if (match.start >= clusterStart - clusterDistance && 
          match.start <= clusterEnd + clusterDistance) {
        cluster.push(match);
        addedToCluster = true;
        break;
      }
    }
    
    if (!addedToCluster) {
      clusters.push([match]);
    }
  });

  // Create a window for each cluster
  return clusters.map(cluster => {
    const clusterCenter = (cluster[0].start + cluster[cluster.length - 1].end) / 2;
    return createMiddleWindow(text, clusterCenter, opts);
  });
};