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