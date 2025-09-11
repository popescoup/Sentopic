/**
 * Reddit Status Hook
 * Extracts Reddit API configuration status from the existing config status
 */

import { useConfigStatus } from './useSettings';

export const useRedditStatus = () => {
  const { data: configStatus, isLoading, error } = useConfigStatus();
  
  return {
    isRedditConfigured: configStatus?.reddit?.connected ?? false,
    isLoading,
    error,
    redditError: configStatus?.reddit?.error,
    lastChecked: configStatus?.timestamp,
    // Additional useful info
    isConfigured: configStatus?.reddit?.configured ?? false,
    isConnected: configStatus?.reddit?.connected ?? false,
  };
};