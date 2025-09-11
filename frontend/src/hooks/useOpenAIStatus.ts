/**
 * OpenAI Status Hook
 * Extracts OpenAI API configuration status from the existing config status
 */

import { useConfigStatus } from './useSettings';

export const useOpenAIStatus = () => {
  const { data: configStatus, isLoading, error } = useConfigStatus();
  
  return {
    isOpenAIConfigured: configStatus?.llm?.providers?.openai?.connected ?? false,
    isLoading,
    error,
    openAIError: configStatus?.llm?.providers?.openai?.error,
    lastChecked: configStatus?.timestamp,
    // Additional useful info
    isConfigured: configStatus?.llm?.providers?.openai?.configured ?? false,
    isConnected: configStatus?.llm?.providers?.openai?.connected ?? false,
  };
};