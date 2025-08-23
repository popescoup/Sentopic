/**
 * API Hooks
 * Custom hooks for common API operations with TanStack Query
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/client';
export { settingsQueryKeys } from './useSettings';
import type {
  ProjectResponse,
  ProjectCreate,
  ProjectListResponse,
  CollectionListResponse,
  CollectionCreateRequest,
  AIStatusResponse,
  AnalysisStatusResponse,
  HealthCheckResponse,
  AnalysisStartResponse,
  ChatSessionListResponse,
  ChatMessageCreate,
  ChatResponse,
  ChatHistoryResponse,
  IndexingRequest,
  IndexingResponse,
  IndexingStatusResponse,
  TrendsResponse
} from '@/types/api';

// Query keys for consistent cache management
export const queryKeys = {
  health: ['health'] as const,
  projects: ['projects'] as const,
  project: (id: string) => ['projects', id] as const,
  analysisStatus: (id: string) => ['projects', id, 'analysis', 'status'] as const,
  collections: ['collections'] as const,
  aiStatus: ['ai', 'status'] as const,
  chatSessions: (projectId: string) => ['projects', projectId, 'chat', 'sessions'] as const,
  chatHistory: (sessionId: string) => ['chat', sessionId, 'history'] as const,
  indexingStatus: (projectId: string) => ['projects', projectId, 'indexing', 'status'] as const,
  trends: (projectId: string, keywords: string[], timePeriod: string) => ['projects', projectId, 'trends', keywords, timePeriod] as const,
} as const;

// ============================================================================
// SYSTEM HOOKS
// ============================================================================

export const useHealthCheck = () => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => api.healthCheck(),
    refetchInterval: 30000, // Check every 30 seconds
    retry: 1,
  });
};

// ============================================================================
// PROJECT HOOKS
// ============================================================================

export const useProjects = () => {
  return useQuery({
    queryKey: queryKeys.projects,
    queryFn: () => api.getProjects(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useProject = (projectId: string | undefined, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: queryKeys.project(projectId!),
    queryFn: () => api.getProject(projectId!),
    enabled: options?.enabled !== undefined ? (!!projectId && options.enabled) : !!projectId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (projectData: ProjectCreate) => api.createProject(projectData),
    onSuccess: () => {
      // Invalidate projects list to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
  });
};

export const useCreateProjectWithAnalysis = () => {
  const queryClient = useQueryClient();
  
  return useMutation<ProjectResponse, Error, ProjectCreate>({
    mutationFn: async (projectData: ProjectCreate) => {
      // Create project first
      const newProject = await api.createProject(projectData);
      
      // Start analysis immediately
      await api.startAnalysis(newProject.id);
      
      return newProject;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
  });
};

export const useDeleteProject = () => {
    const queryClient = useQueryClient();
    
    return useMutation({
      mutationFn: (projectId: string) => api.deleteProject(projectId),
      onMutate: async (projectId: string) => {
        // Cancel any outgoing refetches (so they don't overwrite our optimistic update)
        await queryClient.cancelQueries({ queryKey: queryKeys.projects });
  
        // Snapshot the previous value
        const previousProjects = queryClient.getQueryData(queryKeys.projects);
  
        // Optimistically update to remove the project
        queryClient.setQueryData(queryKeys.projects, (old: any) => {
          if (!old?.projects) return old;
          return {
            ...old,
            projects: old.projects.filter((project: any) => project.id !== projectId),
            total_count: old.total_count - 1
          };
        });
  
        // Return a context object with the snapshotted value
        return { previousProjects };
      },
      onError: (error, projectId, context) => {
        // If the mutation fails, use the context returned from onMutate to roll back
        if (context?.previousProjects) {
          queryClient.setQueryData(queryKeys.projects, context.previousProjects);
        }
      },
      onSettled: () => {
        // Always refetch after error or success to ensure server state sync
        queryClient.invalidateQueries({ queryKey: queryKeys.projects });
      },
    });
  };

// ============================================================================
// ANALYSIS HOOKS
// ============================================================================

export const useStartAnalysis = () => {
  const queryClient = useQueryClient();
  
  return useMutation<AnalysisStartResponse, Error, string>({
    mutationFn: (projectId: string) => api.startAnalysis(projectId),
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.project(projectId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.analysisStatus(projectId) });
    },
  });
};

export const useAnalysisStatus = (projectId: string | undefined, enabled = true) => {
  return useQuery({
    queryKey: queryKeys.analysisStatus(projectId!),
    queryFn: () => api.getAnalysisStatus(projectId!),
    enabled: !!projectId && enabled,
    refetchInterval: (data) => {
      // Poll every 3 seconds if analysis is running
      return data?.status === 'running' ? 3000 : false;
    },
    retry: 1,
  });
};

// ============================================================================
// COLLECTION HOOKS
// ============================================================================

export const useCollections = () => {
  return useQuery({
    queryKey: queryKeys.collections,
    queryFn: () => api.getCollections(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useCreateCollections = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: CollectionCreateRequest) => api.createCollections(request),
    onSuccess: () => {
      // Invalidate collections list to refetch after creation
      queryClient.invalidateQueries({ queryKey: queryKeys.collections });
    },
  });
};

export const useCollectionBatchStatus = (batchId: string, enabled = true) => {
  return useQuery({
    queryKey: ['collections', 'batch', batchId, 'status'],
    queryFn: () => api.getCollectionBatchStatus(batchId),
    enabled: !!batchId && enabled,
    refetchInterval: (data) => {
      // Poll every 2 seconds regardless of status to catch completion
      return data?.status === 'completed' ? false : 2000;
    },
    retry: 1,
  });
};

export const useDeleteCollection = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (collectionId: string) => api.deleteCollection(collectionId),
    onMutate: async (collectionId: string) => {
      // Cancel any outgoing refetches (so they don't overwrite our optimistic update)
      await queryClient.cancelQueries({ queryKey: queryKeys.collections });

      // Snapshot the previous value
      const previousCollections = queryClient.getQueryData(queryKeys.collections);

      // Optimistically update to remove the collection
      queryClient.setQueryData(queryKeys.collections, (old: any) => {
        if (!old?.collections) return old;
        return {
          ...old,
          collections: old.collections.filter((collection: any) => collection.id !== collectionId),
          total_count: old.total_count - 1
        };
      });

      // Return a context object with the snapshotted value
      return { previousCollections };
    },
    onError: (error, collectionId, context) => {
      // If the mutation fails, use the context returned from onMutate to roll back
      if (context?.previousCollections) {
        queryClient.setQueryData(queryKeys.collections, context.previousCollections);
      }
    },
    onSettled: () => {
      // Always refetch after error or success to ensure server state sync
      queryClient.invalidateQueries({ queryKey: queryKeys.collections });
    },
  });
};

// ============================================================================
// AI HOOKS
// ============================================================================

export const useAIStatus = () => {
  return useQuery({
    queryKey: queryKeys.aiStatus,
    queryFn: () => api.getAIStatus(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
};

// ============================================================================
// CHAT HOOKS
// ============================================================================

export const useChatSessions = (projectId: string | undefined) => {
  return useQuery({
    queryKey: queryKeys.chatSessions(projectId!),
    queryFn: () => api.getChatSessions(projectId!),
    enabled: !!projectId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useStartChatSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (projectId: string) => api.startChatSession(projectId),
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.chatSessions(projectId) });
    },
  });
};

export const useSendChatMessage = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ sessionId, message }: { sessionId: string; message: ChatMessageCreate }) => 
      api.sendChatMessage(sessionId, message),
    onSuccess: (_, { sessionId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.chatHistory(sessionId) });
    },
  });
};

export const useChatHistory = (sessionId: string | undefined, limit = 50) => {
  return useQuery({
    queryKey: queryKeys.chatHistory(sessionId!),
    queryFn: () => api.getChatHistory(sessionId!, limit),
    enabled: !!sessionId,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};

// ============================================================================
// INDEXING HOOKS
// ============================================================================

export const useIndexingStatus = (projectId: string | undefined) => {
  return useQuery({
    queryKey: queryKeys.indexingStatus(projectId!),
    queryFn: () => api.getIndexingStatus(projectId!),
    enabled: !!projectId,
    staleTime: 30 * 1000, // 30 seconds
    retry: 1,
  });
};

export const useStartIndexing = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ projectId, request }: { projectId: string; request: IndexingRequest }) => 
      api.startIndexing(projectId, request),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.indexingStatus(projectId) });
    },
  });
};

// ============================================================================
// UTILITY HOOKS
// ============================================================================

/**
 * Hook for managing loading and error states
 */
export const useApiState = () => {
  const healthQuery = useHealthCheck();
  const aiStatusQuery = useAIStatus();

  return {
    isBackendConnected: healthQuery.isSuccess,
    isAIAvailable: aiStatusQuery.data?.ai_available ?? false,
    backendError: healthQuery.error,
    isLoading: healthQuery.isLoading || aiStatusQuery.isLoading,
  };
};

/**
 * Hook for polling analysis progress
 */
export const useAnalysisPolling = (projectId: string | undefined, isRunning: boolean) => {
  const queryClient = useQueryClient();
  
  return useQuery({
    queryKey: queryKeys.analysisStatus(projectId!),
    queryFn: () => api.getAnalysisStatus(projectId!),
    enabled: !!projectId && isRunning,
    refetchInterval: 3000, // Poll every 3 seconds
    onSuccess: (data) => {
      // Stop polling when analysis completes or fails
      if (data.status === 'completed' || data.status === 'failed') {
        // Invalidate project data to get updated results
        queryClient.invalidateQueries({ queryKey: queryKeys.project(projectId!) });
      }
    },
  });
};

/**
 * Hook for polling indexing progress
 */
export const useIndexingPolling = (projectId: string | undefined, isIndexing: boolean) => {
  const queryClient = useQueryClient();
  
  return useQuery({
    queryKey: queryKeys.indexingStatus(projectId!),
    queryFn: () => api.getIndexingStatus(projectId!),
    enabled: !!projectId && isIndexing,
    refetchInterval: 3000, // Poll every 3 seconds
    onSuccess: (data) => {
      // Stop polling when indexing completes
      if (!data.current_indexing) {
        queryClient.invalidateQueries({ queryKey: queryKeys.indexingStatus(projectId!) });
      }
    },
  });
};

// ============================================================================
// TRENDS HOOKS
// ============================================================================

export const useTrends = (
  projectId: string | undefined,
  keywords: string[],
  timePeriod: string = 'weekly',
  enabled = true
) => {
  return useQuery({
    queryKey: queryKeys.trends(projectId!, keywords, timePeriod),
    queryFn: () => api.getTrends(projectId!, keywords, timePeriod),
    enabled: !!projectId && keywords.length > 0 && enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
};