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
  AIStatusResponse,
  AnalysisStatusResponse,
  HealthCheckResponse,
  APIError,
  AnalysisStartResponse,
  IndexingRequest,
  IndexingResponse,
  IndexingStatusResponse
} from '@/types/api';

// Create axios instance with base configuration
const createApiClient = (): AxiosInstance => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  
  const client = axios.create({
    baseURL,
    timeout: 30000, // 30 seconds
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

// Create the main API client instance
export const apiClient = createApiClient();

// API client class with typed methods
export class SentopicAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = apiClient;
  }

  // ============================================================================
  // SYSTEM ENDPOINTS
  // ============================================================================

  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await this.client.get<HealthCheckResponse>('/health');
    return response.data;
  }

  // ============================================================================
  // PROJECT ENDPOINTS
  // ============================================================================

  async getProjects(): Promise<ProjectListResponse> {
    const response = await this.client.get<ProjectListResponse>('/projects');
    return response.data;
  }

  async getProject(projectId: string): Promise<ProjectResponse> {
    const response = await this.client.get<ProjectResponse>(`/projects/${projectId}`);
    return response.data;
  }

  async createProject(projectData: ProjectCreate): Promise<ProjectResponse> {
    const response = await this.client.post<ProjectResponse>('/projects', projectData);
    return response.data;
  }

  async deleteProject(projectId: string): Promise<void> {
    await this.client.delete(`/projects/${projectId}`);
  }

  // ============================================================================
  // ANALYSIS WORKFLOW ENDPOINTS
  // ============================================================================

  async startAnalysis(projectId: string): Promise<AnalysisStartResponse> {
    const response = await this.client.post<AnalysisStartResponse>(`/projects/${projectId}/analysis/start`);
    return response.data;
  }

  async getAnalysisStatus(projectId: string): Promise<AnalysisStatusResponse> {
    const response = await this.client.get<AnalysisStatusResponse>(`/projects/${projectId}/analysis/status`);
    return response.data;
  }

  async getAnalysisResults(projectId: string): Promise<ProjectResponse> {
    const response = await this.client.get<ProjectResponse>(`/projects/${projectId}/analysis/results`);
    return response.data;
  }

  async startIndexing(projectId: string, request: IndexingRequest): Promise<IndexingResponse> {
    const response = await this.client.post<IndexingResponse>(`/projects/${projectId}/indexing`, request);
    return response.data;
  }

  async getIndexingStatus(projectId: string): Promise<IndexingStatusResponse> {
    const response = await this.client.get<IndexingStatusResponse>(`/projects/${projectId}/indexing/status`);
    return response.data;
  }

  // ============================================================================
  // COLLECTION ENDPOINTS
  // ============================================================================

  async getCollections(): Promise<CollectionListResponse> {
    const response = await this.client.get<CollectionListResponse>('/collections');
    return response.data;
  }

  async createCollections(request: CollectionCreateRequest): Promise<CollectionBatchResponse> {
    const response = await this.client.post<CollectionBatchResponse>('/collections', request);
    return response.data;
  }

  async getCollectionBatchStatus(batchId: string): Promise<CollectionBatchStatusResponse> {
    const response = await this.client.get<CollectionBatchStatusResponse>(`/collections/${batchId}/status`);
    return response.data;
  }

  async deleteCollection(collectionId: string): Promise<void> {
    await this.client.delete(`/collections/${collectionId}`);
  }

  async deleteMultipleCollections(collectionIds: string[]): Promise<any> {
    const [primaryId, ...additionalIds] = collectionIds;
    const queryParams = additionalIds.length > 0 
      ? `?additional_ids=${additionalIds.join(',')}` 
      : '';
    
    const response = await this.client.delete(`/collections/${primaryId}${queryParams}`);
    return response.data;
  }

  // ============================================================================
  // AI AND CHAT ENDPOINTS
  // ============================================================================

  async getAIStatus(): Promise<AIStatusResponse> {
    const response = await this.client.get<AIStatusResponse>('/ai/status');
    return response.data;
  }

  async suggestKeywords(request: KeywordSuggestionRequest): Promise<KeywordSuggestionResponse> {
    const response = await this.client.post<KeywordSuggestionResponse>('/ai/keywords/suggest', request);
    return response.data;
  }

  async getChatSessions(projectId: string): Promise<ChatSessionListResponse> {
    const response = await this.client.get<ChatSessionListResponse>(`/projects/${projectId}/chat/sessions`);
    return response.data;
  }

  async startChatSession(projectId: string): Promise<{ session_id: string; created_at: string; message: string }> {
    const response = await this.client.post(`/projects/${projectId}/chat/sessions`);
    return response.data;
  }

  async sendChatMessage(chatSessionId: string, message: ChatMessageCreate): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>(`/chat/${chatSessionId}/messages`, message);
    return response.data;
  }

  async getChatHistory(chatSessionId: string, limit = 50): Promise<ChatHistoryResponse> {
    const response = await this.client.get<ChatHistoryResponse>(`/chat/${chatSessionId}/history?limit=${limit}`);
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