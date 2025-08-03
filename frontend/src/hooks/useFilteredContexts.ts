/**
 * Custom hook for managing filtered contexts API calls and state
 * Handles pagination, filtering, and caching for the Context Explorer Modal
 */

import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/client';
import type { AggregatedFilteredContextsResponse } from '@/types/api';

export interface FilterState {
  primary_keyword?: string;
  secondary_keyword?: string;
  min_sentiment: number;
  max_sentiment: number;
  sort_by: 'newest' | 'oldest' | 'sentiment_asc' | 'sentiment_desc';
  page: number;
  limit: number;
}

export const useFilteredContexts = (
  projectId: string | undefined,
  filters: FilterState,
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: ['filtered-contexts', projectId, filters],
    queryFn: () => {
      if (!projectId) {
        throw new Error('Project ID is required');
      }
      return api.getFilteredContexts(projectId, filters);
    },
    enabled: enabled && !!projectId,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1,
  });
};

export const getDefaultFilters = (): FilterState => ({
  primary_keyword: undefined, // Will show all keywords
  secondary_keyword: undefined,
  min_sentiment: -1.0,
  max_sentiment: 1.0,
  sort_by: 'newest',
  page: 1,
  limit: 20,
});