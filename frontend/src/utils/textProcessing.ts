/**
 * Text Processing Utilities
 * Functions for keyword highlighting, text truncation, and safe HTML processing
 */

/**
 * Escapes HTML characters to prevent XSS attacks
 */
export const escapeHtml = (text: string): string => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  };
  
  /**
   * Highlights keywords in text with HTML markup
   * @param text - The text to search for keywords
   * @param keywords - Array of keywords to highlight
   * @returns HTML string with highlighted keywords
   */
  export const highlightKeywords = (text: string, keywords: string[]): string => {
    if (!text || !keywords || keywords.length === 0) {
      return escapeHtml(text);
    }
  
    // Escape HTML first to prevent XSS
    let escapedText = escapeHtml(text);
    
    // Create a regex pattern for all keywords (case-insensitive, word boundaries)
    const keywordPattern = keywords
      .map(keyword => keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')) // Escape special regex chars
      .join('|');
    
    // Create regex with word boundaries to match whole words only
    const regex = new RegExp(`\\b(${keywordPattern})\\b`, 'gi');
    
    // Replace keywords with highlighted versions
    return escapedText.replace(regex, (match) => {
      return `<mark class="bg-accent text-white px-1 py-0.5 rounded font-medium">${match}</mark>`;
    });
  };
  
  /**
   * Truncates text to a specified length, preserving word boundaries
   * @param text - The text to truncate (can contain HTML)
   * @param maxLength - Maximum number of characters
   * @param suffix - Suffix to add when truncated (default: '...')
   * @returns Truncated text
   */
  export const truncateText = (text: string, maxLength: number, suffix: string = '...'): string => {
    if (!text || text.length <= maxLength) {
      return text;
    }
  
    // Handle HTML content - we need to count text content, not HTML tags
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = text;
    const textContent = tempDiv.textContent || tempDiv.innerText || '';
    
    if (textContent.length <= maxLength) {
      return text;
    }
  
    // Find the last space within the character limit to avoid cutting words
    const truncateAt = textContent.lastIndexOf(' ', maxLength - suffix.length);
    const cutPoint = truncateAt > 0 ? truncateAt : maxLength - suffix.length;
    
    // If the original text contains HTML, we need to reconstruct it carefully
    if (text !== textContent) {
      // For simplicity with HTML content, truncate the text content and re-highlight
      const truncatedTextContent = textContent.substring(0, cutPoint).trim() + suffix;
      return truncatedTextContent;
    }
    
    // For plain text, simple truncation
    return text.substring(0, cutPoint).trim() + suffix;
  };
  
  /**
   * Extracts preview text from longer content
   * @param text - The full text content
   * @param maxSentences - Maximum number of sentences to include
   * @param maxLength - Maximum character length
   * @returns Preview text
   */
  export const extractPreview = (text: string, maxSentences: number = 2, maxLength: number = 200): string => {
    if (!text) return '';
    
    // Split into sentences (basic approach)
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    
    // Take the first N sentences
    let preview = sentences.slice(0, maxSentences).join('. ').trim();
    
    // Add period if it doesn't end with punctuation
    if (preview && !preview.match(/[.!?]$/)) {
      preview += '.';
    }
    
    // Truncate if still too long
    if (preview.length > maxLength) {
      preview = truncateText(preview, maxLength);
    }
    
    return preview;
  };
  
  /**
   * Cleans Reddit markdown formatting for display
   * @param text - Text with Reddit markdown
   * @returns Cleaned text
   */
  export const cleanRedditMarkdown = (text: string): string => {
    if (!text) return '';
    
    return text
      // Remove Reddit-style quotes (> text)
      .replace(/^>\s*/gm, '')
      // Remove bold/italic markdown (* ** _)
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/_(.*?)_/g, '$1')
      // Remove strikethrough
      .replace(/~~(.*?)~~/g, '$1')
      // Remove code blocks
      .replace(/`(.*?)`/g, '$1')
      // Clean up multiple spaces and newlines
      .replace(/\s+/g, ' ')
      .trim();
  };
  
  /**
 * Counts words in text (excluding HTML tags)
 * @param text - Text to count words in
 * @returns Number of words
 */
export const countWords = (text: string): number => {
    if (!text) return 0;
    
    // Remove HTML tags and count words
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = text;
    const textContent = tempDiv.textContent || tempDiv.innerText || '';
    
    return textContent.trim().split(/\s+/).filter(word => word.length > 0).length;
  };
  
  /**
   * Intelligently extracts the best snippet with keyword highlighting
   * @param text - The text to process
   * @param keywords - Array of keywords to highlight and use for windowing
   * @param maxLength - Maximum character length for the snippet
   * @returns Object with displayText and windowing information
   */
  export const getOptimalSnippetWithHighlights = (
    text: string, 
    keywords: string[], 
    maxLength: number
  ): { displayText: string; isWindowed: boolean; windowType: 'beginning' | 'middle' | 'full' } => {
    if (!text || !keywords || keywords.length === 0) {
      const truncated = truncateText(escapeHtml(text), maxLength);
      return {
        displayText: truncated,
        isWindowed: truncated.length < text.length,
        windowType: truncated.length < text.length ? 'beginning' : 'full'
      };
    }
  
    // Clean text for analysis (remove Reddit markdown for keyword finding)
    const cleanText = cleanRedditMarkdown(text);
    
    // If text is already short enough, show everything with highlights
    if (cleanText.length <= maxLength) {
      return {
        displayText: highlightKeywords(cleanText, keywords),
        isWindowed: false,
        windowType: 'full'
      };
    }
  
    // Find all keyword positions in the clean text
    const keywordPositions: Array<{ keyword: string; start: number; end: number }> = [];
    
    keywords.forEach(keyword => {
      const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`\\b${escapedKeyword}\\b`, 'gi');
      let match;
      
      while ((match = regex.exec(cleanText)) !== null) {
        keywordPositions.push({
          keyword: match[0],
          start: match.index,
          end: match.index + match[0].length
        });
      }
    });
  
    // If no keywords found in clean text, fall back to beginning truncation
    if (keywordPositions.length === 0) {
      const truncated = truncateText(highlightKeywords(text, keywords), maxLength);
      return {
        displayText: truncated,
        isWindowed: true,
        windowType: 'beginning'
      };
    }
  
    // Find the earliest keyword position
    const earliestKeyword = keywordPositions.reduce((earliest, current) => 
      current.start < earliest.start ? current : earliest
    );
  
    // If the earliest keyword is close to the beginning, show from start
    const contextPadding = 50; // Characters of context around keywords
    if (earliestKeyword.start <= contextPadding) {
      const truncated = truncateText(highlightKeywords(text, keywords), maxLength);
      return {
        displayText: truncated,
        isWindowed: true,
        windowType: 'beginning'
      };
    }
  
    // Calculate optimal window around the earliest keyword
    const windowStart = Math.max(0, earliestKeyword.start - contextPadding);
    const windowEnd = Math.min(cleanText.length, windowStart + maxLength - 3); // -3 for "..."
  
    // Find a good break point to start the window (try to start at word boundary)
    let actualStart = windowStart;
    if (windowStart > 0) {
      // Look for space within 20 characters before our calculated start
      const searchStart = Math.max(0, windowStart - 20);
      const spaceIndex = cleanText.lastIndexOf(' ', windowStart);
      if (spaceIndex > searchStart) {
        actualStart = spaceIndex + 1;
      }
    }
  
    // Extract the window text
    let windowText = cleanText.substring(actualStart, windowEnd).trim();
    
    // Ensure we end at a reasonable break point
    if (windowEnd < cleanText.length) {
      const lastSpaceIndex = windowText.lastIndexOf(' ');
      if (lastSpaceIndex > windowText.length - 50) { // Only trim if space is reasonably close to end
        windowText = windowText.substring(0, lastSpaceIndex);
      }
      windowText += '...';
    }
  
    // Add leading ellipsis if we started in the middle
    if (actualStart > 0) {
      windowText = '...' + windowText;
    }
  
    // Apply keyword highlighting to the windowed text
    const highlightedText = highlightKeywords(windowText, keywords);
  
    return {
      displayText: highlightedText,
      isWindowed: true,
      windowType: 'middle'
    };
  };