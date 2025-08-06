/**
 * Text Processing Utilities
 * Core text utilities for cleaning, truncation, and basic processing
 * Complex highlighting and windowing moved to dedicated modules
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
   * Truncates text to a specified length, preserving word boundaries
   * @param text - The text to truncate (plain text only)
   * @param maxLength - Maximum number of characters
   * @param suffix - Suffix to add when truncated (default: '...')
   * @returns Truncated text
   */
  export const truncateText = (text: string, maxLength: number, suffix: string = '...'): string => {
    if (!text || text.length <= maxLength) {
      return text;
    }
  
    // Find the last space within the character limit to avoid cutting words
    const truncateAt = text.lastIndexOf(' ', maxLength - suffix.length);
    const cutPoint = truncateAt > 0 ? truncateAt : maxLength - suffix.length;
    
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
   * Strips HTML tags from text, leaving only plain text
   * @param html - HTML string to clean
   * @returns Plain text content
   */
  export const stripHtmlTags = (html: string): string => {
    if (!html) return '';
    
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    return tempDiv.textContent || tempDiv.innerText || '';
  };
  
  /**
   * Normalizes whitespace in text (removes extra spaces, newlines, etc.)
   * @param text - Text to normalize
   * @returns Text with normalized whitespace
   */
  export const normalizeWhitespace = (text: string): string => {
    if (!text) return '';
    
    return text
      .replace(/\s+/g, ' ')
      .replace(/\n\s*\n/g, '\n')
      .trim();
  };
  
  /**
   * Checks if text appears to be primarily ASCII (for formatting decisions)
   * @param text - Text to check
   * @returns True if text is mostly ASCII characters
   */
  export const isAsciiText = (text: string): boolean => {
    if (!text) return true;
    
    const asciiCount = text.split('').filter(char => char.charCodeAt(0) < 128).length;
    return (asciiCount / text.length) > 0.9;
  };
  
  /**
   * Gets a safe substring that doesn't break in the middle of words
   * @param text - Text to substring
   * @param start - Start position
   * @param maxLength - Maximum length from start
   * @returns Safe substring
   */
  export const safeSubstring = (text: string, start: number, maxLength: number): string => {
    if (!text || start >= text.length) return '';
    
    const end = Math.min(start + maxLength, text.length);
    let substring = text.substring(start, end);
    
    // If we didn't reach the end and we're in the middle of a word, trim to last space
    if (end < text.length && substring.length > 0) {
      const lastSpaceIndex = substring.lastIndexOf(' ');
      if (lastSpaceIndex > substring.length - 20) { // Only trim if space is reasonably close to end
        substring = substring.substring(0, lastSpaceIndex);
      }
    }
    
    return substring.trim();
  };

  /**
 * Validates that a position-based highlight is safe to apply
 * @param text - The text to validate against
 * @param keyword - The keyword being highlighted
 * @param position - The position where highlighting should occur
 * @returns True if the highlight is safe to apply
 */
export const validateHighlightPosition = (text: string, keyword: string, position: number): boolean => {
  if (!text || !keyword || position < 0) return false;
  
  const endPosition = position + keyword.length;
  if (endPosition > text.length) return false;
  
  const textAtPosition = text.substring(position, endPosition);
  return textAtPosition.toLowerCase().trim() === keyword.toLowerCase().trim();
};