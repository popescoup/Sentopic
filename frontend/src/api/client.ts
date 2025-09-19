/**
 * API Client for Sentopic Backend
 * Handles all HTTP communication with the FastAPI backend
 */

import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';
import type {
  ProjectResponse,
  ProjectCreate,
  ProjectListResponse,
  CollectionListResponse,
  CollectionCreateRequest,
  CollectionBatchResponse,
  CollectionBatchStatusResponse,
  ChatSessionListResponse,
  ChatMessageCreate,
  ChatResponse,
  ChatHistoryResponse,
  KeywordSuggestionRequest,
  KeywordSuggestionResponse,
  SubredditSuggestionRequest,
  SubredditSuggestionResponse,
  AIStatusResponse,
  AnalysisStatusResponse,
  HealthCheckResponse,
  APIError,
  AnalysisStartResponse,
  IndexingRequest,
  IndexingResponse,
  IndexingStatusResponse,
  AggregatedFilteredContextsResponse,
  TrendsResponse,
  ConfigurationStatus,
  RedditConfigUpdate,
  LLMConfigUpdate,
  ConfigUpdateResponse,
  ConnectionTestResult,
  DataClearResponse
} from '@/types/api';

// Get backend URL - support both Electron and web environments
async function getBackendURL(): Promise<string> {
  // Check if running in Electron
  if (typeof window !== 'undefined' && (window as any).electronAPI) {
    console.log('🔗 Running in Electron, getting dynamic backend URL...');
    try {
      const backendUrl = await (window as any).electronAPI.getBackendURL();
      if (backendUrl) {
        console.log(`✅ Got backend URL from Electron: ${backendUrl}`);
        return backendUrl;
      }
    } catch (error) {
      console.error('❌ Failed to get backend URL from Electron:', error);
    }
  }
  
  // Fallback to environment variable or default
  const fallbackUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  console.log(`🌐 Using fallback backend URL: ${fallbackUrl}`);
  return fallbackUrl;
}

// Create axios instance with base configuration
const createApiClient = async (): Promise<AxiosInstance> => {
  const baseURL = await getBackendURL();
  
  const client = axios.create({
    baseURL,
    timeout: 30000, // 30 seconds default
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor for logging in development
  client.interceptors.request.use(
    (config) => {
      if (import.meta.env.DEV) {
        console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
      }
      return config;
    },
    (error) => {
      console.error('❌ API Request Error:', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      if (import.meta.env.DEV) {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
      }
      return response;
    },
    (error: AxiosError<APIError>) => {
      console.error('❌ API Error:', error);
      
      // Handle different types of errors
      if (error.response?.data) {
        // Backend returned an error response with details
        const apiError = error.response.data;
        throw new Error(apiError.message || 'An API error occurred');
      } else if (error.request) {
        // Network error - no response received
        throw new Error('Unable to connect to the server. Please check your connection.');
      } else {
        // Something else happened
        throw new Error(error.message || 'An unexpected error occurred');
      }
    }
  );

  return client;
};

// Create the main API client instance (async)
let apiClientPromise: Promise<AxiosInstance> | null = null;

function getApiClient(): Promise<AxiosInstance> {
  if (!apiClientPromise) {
    apiClientPromise = createApiClient();
  }
  return apiClientPromise;
}

// Export the client promise for backwards compatibility
export const apiClient = getApiClient();

// API client class with typed methods
export class SentopicAPI {
  private clientPromise: Promise<AxiosInstance>;

  constructor() {
    this.clientPromise = getApiClient();
  }

  private async getClient(): Promise<AxiosInstance> {
    return await this.clientPromise;
  }

  // ============================================================================
  // SYSTEM ENDPOINTS
  // ============================================================================

  async healthCheck(): Promise<HealthCheckResponse> {
    const client = await this.getClient();
    const response = await client.get<HealthCheckResponse>('/health');
    return response.data;
  }

  // ============================================================================
  // PROJECT ENDPOINTS
  // ============================================================================

  async getProjects(): Promise<ProjectListResponse> {
    const client = await this.getClient();
    const response = await client.get<ProjectListResponse>('/projects');
    return response.data;
  }

  async getProject(projectId: string): Promise<ProjectResponse> {
    const client = await this.getClient();
    const response = await client.get<ProjectResponse>(`/projects/${projectId}`);
    return response.data;
  }

  async createProject(projectData: ProjectCreate): Promise<ProjectResponse> {
    const client = await this.getClient();
    const response = await client.post<ProjectResponse>('/projects', projectData);
    return response.data;
  }

  async deleteProject(projectId: string): Promise<void> {
    const client = await this.getClient();
    await client.delete(`/projects/${projectId}`);
  }

  // ============================================================================
  // ANALYSIS WORKFLOW ENDPOINTS
  // ============================================================================

  async startAnalysis(projectId: string): Promise<AnalysisStartResponse> {
    const client = await this.getClient();
    const response = await client.post<AnalysisStartResponse>(`/projects/${projectId}/analysis/start`);
    return response.data;
  }

  async getAnalysisStatus(projectId: string): Promise<AnalysisStatusResponse> {
    const client = await this.getClient();
    const response = await client.get<AnalysisStatusResponse>(`/projects/${projectId}/analysis/status`);
    return response.data;
  }

  async getAnalysisResults(projectId: string): Promise<ProjectResponse> {
    const client = await this.getClient();
    const response = await client.get<ProjectResponse>(`/projects/${projectId}/analysis/results`);
    return response.data;
  }

  async startIndexing(projectId: string, request: IndexingRequest): Promise<IndexingResponse> {
    const client = await this.getClient();
    const response = await client.post<IndexingResponse>(`/projects/${projectId}/indexing`, request, {
      timeout: 9000000 // 150 minutes timeout for collections
    });
    return response.data;
  }

  async getIndexingStatus(projectId: string): Promise<IndexingStatusResponse> {
    const client = await this.getClient();
    const response = await client.get<IndexingStatusResponse>(`/projects/${projectId}/indexing/status`);
    return response.data;
  }

  // ============================================================================
  // COLLECTION ENDPOINTS
  // ============================================================================

  async getCollections(): Promise<CollectionListResponse> {
    const client = await this.getClient();
    const response = await client.get<CollectionListResponse>('/collections');
    return response.data;
  }

  async createCollections(request: CollectionCreateRequest): Promise<CollectionBatchResponse> {
    const client = await this.getClient();
    // Use a much longer timeout for collection requests since they run synchronously
    const response = await client.post<CollectionBatchResponse>('/collections', request, {
      timeout: 9000000 // 150 minutes timeout for collections
    });
    return response.data;
  }

  async getCollectionBatchStatus(batchId: string): Promise<CollectionBatchStatusResponse> {
    const client = await this.getClient();
    const response = await client.get<CollectionBatchStatusResponse>(`/collections/${batchId}/status`);
    return response.data;
  }

  async deleteCollection(collectionId: string): Promise<void> {
    const client = await this.getClient();
    await client.delete(`/collections/${collectionId}`);
  }

  async deleteMultipleCollections(collectionIds: string[]): Promise<any> {
    const client = await this.getClient();
    const [primaryId, ...additionalIds] = collectionIds;
    const queryParams = additionalIds.length > 0 
      ? `?additional_ids=${additionalIds.join(',')}` 
      : '';
    
    const response = await client.delete(`/collections/${primaryId}${queryParams}`);
    return response.data;
  }

  // ============================================================================
  // AI AND CHAT ENDPOINTS
  // ============================================================================

  async getAIStatus(): Promise<AIStatusResponse> {
    const client = await this.getClient();
    const response = await client.get<AIStatusResponse>('/ai/status');
    return response.data;
  }

  async suggestKeywords(request: KeywordSuggestionRequest): Promise<KeywordSuggestionResponse> {
    const client = await this.getClient();
    const response = await client.post<KeywordSuggestionResponse>('/ai/keywords/suggest', request);
    return response.data;
  }

  async suggestSubreddits(request: SubredditSuggestionRequest): Promise<SubredditSuggestionResponse> {
    const client = await this.getClient();
    const response = await client.post<SubredditSuggestionResponse>('/ai/subreddits/suggest', request);
    return response.data;
  }

  async getChatSessions(projectId: string): Promise<ChatSessionListResponse> {
    const client = await this.getClient();
    const response = await client.get<ChatSessionListResponse>(`/projects/${projectId}/chat/sessions`);
    return response.data;
  }

  async startChatSession(projectId: string): Promise<{ session_id: string; created_at: string; message: string }> {
    const client = await this.getClient();
    const response = await client.post(`/projects/${projectId}/chat/sessions`);
    return response.data;
  }

  async sendChatMessage(chatSessionId: string, message: ChatMessageCreate): Promise<ChatResponse> {
    const client = await this.getClient();
    const response = await client.post<ChatResponse>(`/chat/${chatSessionId}/messages`, message);
    return response.data;
  }

  async getChatHistory(chatSessionId: string, limit = 50): Promise<ChatHistoryResponse> {
    const client = await this.getClient();
    const response = await client.get<ChatHistoryResponse>(`/chat/${chatSessionId}/history?limit=${limit}`);
    return response.data;
  }

  async getFilteredContexts(
    projectId: string, 
    filters: {
      primary_keyword?: string;
      secondary_keyword?: string;
      min_sentiment: number;
      max_sentiment: number;
      sort_by: string;
      page: number;
      limit: number;
    }
  ): Promise<AggregatedFilteredContextsResponse> {
    const client = await this.getClient();
    const params = new URLSearchParams({
      min_sentiment: filters.min_sentiment.toString(),
      max_sentiment: filters.max_sentiment.toString(),
      sort_by: filters.sort_by,
      page: filters.page.toString(),
      limit: filters.limit.toString(),
    });
  
    if (filters.primary_keyword) {
      params.append('primary_keyword', filters.primary_keyword);
    }
  
    if (filters.secondary_keyword) {
      params.append('secondary_keyword', filters.secondary_keyword);
    }
  
    const response = await client.get<AggregatedFilteredContextsResponse>(
      `/projects/${projectId}/contexts/filtered?${params.toString()}`
    );
    return response.data;
  }

  async getTrends(
    projectId: string,
    keywords: string[],
    timePeriod: string = 'weekly'
  ): Promise<TrendsResponse> {
    const client = await this.getClient();
    const params = new URLSearchParams({
      time_period: timePeriod,
    });

    keywords.forEach(keyword => {
      params.append('keywords', keyword);
    });

    const response = await client.get<TrendsResponse>(
      `/projects/${projectId}/trends?${params.toString()}`
    );
    return response.data;
  }

  async getConfigStatus(): Promise<ConfigurationStatus> {
    const client = await this.getClient();
    const response = await client.get<ConfigurationStatus>('/config/status');
    return response.data;
  }

  async updateRedditConfig(config: RedditConfigUpdate): Promise<ConfigUpdateResponse> {
    const client = await this.getClient();
    const response = await client.post<ConfigUpdateResponse>('/config/reddit', config);
    return response.data;
  }

  async updateLLMConfig(config: LLMConfigUpdate): Promise<ConfigUpdateResponse> {
    const client = await this.getClient();
    const response = await client.post<ConfigUpdateResponse>('/config/llm', config);
    return response.data;
  }

  async testAllConnections(): Promise<ConnectionTestResult> {
    const client = await this.getClient();
    const response = await client.post<ConnectionTestResult>('/config/test-connections');
    return response.data;
  }

  async resetConfiguration(): Promise<DataClearResponse> {
    const client = await this.getClient();
    const response = await client.delete<DataClearResponse>('/config/reset');
    return response.data;
  }

  async clearAllData(): Promise<DataClearResponse> {
    const client = await this.getClient();
    const response = await client.delete<DataClearResponse>('/config/clear-data');
    return response.data;
  }

}


// Export singleton instance
export const api = new SentopicAPI();

// Export error handling utilities
export const isAPIError = (error: unknown): error is AxiosError<APIError> => {
  return axios.isAxiosError(error);
};

export const getErrorMessage = (error: unknown): string => {
  if (isAPIError(error)) {
    return error.response?.data?.message || error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
};