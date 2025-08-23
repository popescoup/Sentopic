/**
 * Settings API Hooks
 * Custom hooks for configuration management operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/client';
import type {
  ConfigurationStatus,
  RedditConfigUpdate,
  LLMConfigUpdate,
  ConfigUpdateResponse,
  ConnectionTestResult,
  DataClearResponse
} from '@/types/api';

// Query keys for consistent cache management
export const settingsQueryKeys = {
  status: ['settings', 'status'] as const,
} as const;

/**
 * Hook to get current configuration status
 */
export const useConfigStatus = () => {
  return useQuery({
    queryKey: settingsQueryKeys.status,
    queryFn: () => api.getConfigStatus(),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30 * 1000, // Refresh every 30 seconds
    retry: 1,
  });
};

/**
 * Hook to update Reddit configuration
 */
export const useUpdateRedditConfig = () => {
  const queryClient = useQueryClient();
  
  return useMutation<ConfigUpdateResponse, Error, RedditConfigUpdate>({
    mutationFn: (config: RedditConfigUpdate) => api.updateRedditConfig(config),
    onSuccess: () => {
      // Invalidate status to refresh configuration display
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.status });
      // Also invalidate AI status since Reddit config might affect overall system status
      queryClient.invalidateQueries({ queryKey: ['ai', 'status'] });
    },
  });
};

/**
 * Hook to update LLM configuration
 */
export const useUpdateLLMConfig = () => {
  const queryClient = useQueryClient();
  
  return useMutation<ConfigUpdateResponse, Error, LLMConfigUpdate>({
    mutationFn: (config: LLMConfigUpdate) => api.updateLLMConfig(config),
    onSuccess: () => {
      // Invalidate status to refresh configuration display
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.status });
      // Invalidate AI status since LLM config directly affects AI availability
      queryClient.invalidateQueries({ queryKey: ['ai', 'status'] });
    },
  });
};

/**
 * Hook to test all API connections
 */
export const useTestConnections = () => {
  const queryClient = useQueryClient();
  
  return useMutation<ConnectionTestResult, Error, void>({
    mutationFn: () => api.testAllConnections(),
    onSuccess: () => {
      // Invalidate status to refresh connection indicators
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.status });
    },
  });
};

/**
 * Hook to reset configuration to defaults
 */
export const useResetConfiguration = () => {
  const queryClient = useQueryClient();
  
  return useMutation<DataClearResponse, Error, void>({
    mutationFn: () => api.resetConfiguration(),
    onSuccess: () => {
      // Invalidate all relevant queries since configuration affects everything
      queryClient.invalidateQueries({ queryKey: settingsQueryKeys.status });
      queryClient.invalidateQueries({ queryKey: ['ai', 'status'] });
      queryClient.invalidateQueries({ queryKey: ['health'] });
    },
  });
};

/**
 * Hook to clear all application data
 */
export const useClearAllData = () => {
  const queryClient = useQueryClient();
  
  return useMutation<DataClearResponse, Error, void>({
    mutationFn: () => api.clearAllData(),
    onSuccess: () => {
      // Invalidate all data-related queries since everything was deleted
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: ['collections'] });
      // Note: We don't invalidate settings status since configuration wasn't changed
    },
  });
};

/**
 * Hook for managing form state and validation
 */
export const useSettingsForm = () => {
  const { data: configStatus, isLoading: statusLoading } = useConfigStatus();
  
  // Extract current configuration for form initialization
  const currentRedditConfig = {
    client_id: '', // We don't return actual values for security
    client_secret: '',
    user_agent: ''
  };
  
  const currentLLMConfig: LLMConfigUpdate = {
    enabled: configStatus?.llm.enabled || false,
    default_provider: 'anthropic',
    providers: {
      anthropic: {
        api_key: '', // We don't return actual values for security
        model: 'claude-3-5-sonnet-20240620',
        max_tokens: 4000,
        temperature: 0.1
      },
      openai: {
        api_key: '',
        model: 'gpt-4o',
        max_tokens: 4000,
        temperature: 0.1
      }
    },
    features: {
      keyword_suggestion: configStatus?.llm.features?.keyword_suggestion || false,
      summarization: configStatus?.llm.features?.summarization || false,
      rag_search: configStatus?.llm.features?.rag_search || false,
      chat_agent: configStatus?.llm.features?.chat_agent || false
    },
    embeddings: {
      provider: 'openai',
      model: 'text-embedding-3-small',
      storage: 'sqlite'
    }
  };
  
  return {
    configStatus,
    statusLoading,
    currentRedditConfig,
    currentLLMConfig,
  };
};