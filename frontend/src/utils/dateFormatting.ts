/**
 * Date Formatting Utilities
 * Functions for converting Reddit timestamps to user-friendly formats
 */

/**
 * Formats a Unix timestamp to a relative time string
 * @param timestamp - Unix timestamp (seconds since epoch)
 * @returns Relative time string (e.g., "2 hours ago", "3 days ago")
 */
export const formatRelativeTime = (timestamp: number): string => {
    if (!timestamp || timestamp <= 0) {
      return 'Unknown time';
    }
  
    const now = Date.now();
    const postTime = timestamp * 1000; // Convert to milliseconds
    const diffMs = now - postTime;
    
    // If timestamp is in the future (shouldn't happen but handle gracefully)
    if (diffMs < 0) {
      return 'Just now';
    }
  
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    const diffWeeks = Math.floor(diffDays / 7);
    const diffMonths = Math.floor(diffDays / 30);
    const diffYears = Math.floor(diffDays / 365);
  
    if (diffSeconds < 60) {
      return 'Just now';
    } else if (diffMinutes < 60) {
      return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else if (diffWeeks < 4) {
      return `${diffWeeks} week${diffWeeks !== 1 ? 's' : ''} ago`;
    } else if (diffMonths < 12) {
      return `${diffMonths} month${diffMonths !== 1 ? 's' : ''} ago`;
    } else {
      return `${diffYears} year${diffYears !== 1 ? 's' : ''} ago`;
    }
  };
  
  /**
   * Formats a Unix timestamp to a standard date string
   * @param timestamp - Unix timestamp (seconds since epoch)
   * @param options - Intl.DateTimeFormat options
   * @returns Formatted date string
   */
  export const formatDate = (
    timestamp: number, 
    options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }
  ): string => {
    if (!timestamp || timestamp <= 0) {
      return 'Unknown date';
    }
  
    try {
      const date = new Date(timestamp * 1000);
      return date.toLocaleDateString(undefined, options);
    } catch (error) {
      console.warn('Error formatting date:', error);
      return 'Invalid date';
    }
  };
  
  /**
   * Formats a Unix timestamp to a full date and time string
   * @param timestamp - Unix timestamp (seconds since epoch)
   * @returns Full date and time string
   */
  export const formatDateTime = (timestamp: number): string => {
    if (!timestamp || timestamp <= 0) {
      return 'Unknown date and time';
    }
  
    try {
      const date = new Date(timestamp * 1000);
      return date.toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      console.warn('Error formatting datetime:', error);
      return 'Invalid date';
    }
  };
  
  /**
   * Checks if a timestamp represents a recent date (within last N days)
   * @param timestamp - Unix timestamp (seconds since epoch)
   * @param days - Number of days to consider as "recent" (default: 7)
   * @returns True if the timestamp is recent
   */
  export const isRecent = (timestamp: number, days: number = 7): boolean => {
    if (!timestamp || timestamp <= 0) {
      return false;
    }
  
    const now = Date.now();
    const postTime = timestamp * 1000;
    const diffMs = now - postTime;
    const diffDays = diffMs / (1000 * 60 * 60 * 24);
    
    return diffDays <= days;
  };
  
  /**
   * Gets a short relative time format for compact displays
   * @param timestamp - Unix timestamp (seconds since epoch)
   * @returns Short relative time (e.g., "2h", "3d", "1w")
   */
  export const formatShortRelativeTime = (timestamp: number): string => {
    if (!timestamp || timestamp <= 0) {
      return '?';
    }
  
    const now = Date.now();
    const postTime = timestamp * 1000;
    const diffMs = now - postTime;
    
    if (diffMs < 0) {
      return 'now';
    }
  
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    const diffWeeks = Math.floor(diffDays / 7);
    const diffMonths = Math.floor(diffDays / 30);
    const diffYears = Math.floor(diffDays / 365);
  
    if (diffSeconds < 60) {
      return 'now';
    } else if (diffMinutes < 60) {
      return `${diffMinutes}m`;
    } else if (diffHours < 24) {
      return `${diffHours}h`;
    } else if (diffDays < 7) {
      return `${diffDays}d`;
    } else if (diffWeeks < 4) {
      return `${diffWeeks}w`;
    } else if (diffMonths < 12) {
      return `${diffMonths}mo`;
    } else {
      return `${diffYears}y`;
    }
  };
  
  /**
   * Formats a timestamp for use in tooltips or detailed views
   * @param timestamp - Unix timestamp (seconds since epoch)
   * @returns Detailed timestamp string
   */
  export const formatTooltipTime = (timestamp: number): string => {
    if (!timestamp || timestamp <= 0) {
      return 'Unknown timestamp';
    }
  
    try {
      const date = new Date(timestamp * 1000);
      const relative = formatRelativeTime(timestamp);
      const absolute = date.toLocaleString();
      
      return `${relative} (${absolute})`;
    } catch (error) {
      console.warn('Error formatting tooltip time:', error);
      return 'Invalid timestamp';
    }
  };