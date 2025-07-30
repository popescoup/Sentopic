/**
 * useSearchType Hook
 * Manages search type selection and indexing status for semantic search
 */

import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/client';
import type { IndexingStatusResponse, ChatMessageCreate } from '@/types/api';

// Extract the search type from ChatMessageCreate for consistency
type SearchType = NonNullable<ChatMessageCreate['search_type']>;

interface UseSearchTypeReturn {
  searchType: SearchType; // Changed from string to SearchType
  setSearchType: (type: SearchType) => void; // Changed from string to SearchType
  indexingStatus: IndexingStatusResponse | undefined;
  isIndexingInProgress: boolean;
  isIndexingRequired: (searchType: SearchType) => boolean; // Changed from string to SearchType
  startIndexing: (providerType: 'local' | 'openai') => Promise<void>;
  refetchIndexingStatus: () => void;
}

export const useSearchType = (projectId: string): UseSearchTypeReturn => {
  const [searchType, setSearchTypeState] = useState<SearchType>('keyword'); // Changed from string to SearchType
  const [isIndexingInProgress, setIsIndexingInProgress] = useState(false);

  // Query for indexing status
  const {
    data: indexingStatus,
    refetch: refetchIndexingStatus,
    error: indexingError
  } = useQuery({
    queryKey: ['indexing-status', projectId],
    queryFn: () => api.getIndexingStatus(projectId),
    enabled: !!projectId,
    refetchInterval: (data) => {
      // Poll every 3 seconds if indexing is in progress
      return isIndexingInProgress ? 3000 : false;
    },
    retry: 1,
  });

  console.log('🔍 useSearchType - indexingStatus from API:', indexingStatus);
  console.log('🔍 useSearchType - isIndexingInProgress:', isIndexingInProgress);

  // Update indexing progress based on status
  useEffect(() => {
    if (indexingStatus?.current_indexing) {
      setIsIndexingInProgress(true);
    } else {
      setIsIndexingInProgress(false);
    }
  }, [indexingStatus]);

  // Check if indexing is required for a given search type
  const isIndexingRequired = useCallback((searchType: SearchType): boolean => { // Changed from string to SearchType
    if (!indexingStatus) return true; // Assume required if we don't know status
    
    if (searchType === 'local_semantic') {
      return indexingStatus.indexing_status.local !== 'complete';
    } else if (searchType === 'cloud_semantic') {
      return indexingStatus.indexing_status.cloud !== 'complete';
    }
    
    return false; // Keyword search doesn't require indexing
  }, [indexingStatus]);

  // Start indexing process
  const startIndexing = useCallback(async (providerType: 'local' | 'openai') => {
    try {
      setIsIndexingInProgress(true);
      
      await api.startIndexing(projectId, {
        provider_type: providerType,
        force_reindex: false
      });
      
      // Refresh status to get updated information
      refetchIndexingStatus();
      
    } catch (error) {
      setIsIndexingInProgress(false);
      throw error;
    }
  }, [projectId, refetchIndexingStatus]);

  // Wrapper to validate search type changes
  const setSearchType = useCallback((type: SearchType) => { // Changed from string to SearchType
    // Validate search type - TypeScript will now enforce this at compile time
    setSearchTypeState(type);
  }, []);

  // Handle indexing errors
  useEffect(() => {
    if (indexingError) {
      console.error('Indexing status error:', indexingError);
      setIsIndexingInProgress(false);
    }
  }, [indexingError]);

  return {
    searchType,
    setSearchType,
    indexingStatus,
    isIndexingInProgress,
    isIndexingRequired,
    startIndexing,
    refetchIndexingStatus
  };
};