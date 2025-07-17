/**
 * TypeScript interfaces that mirror the FastAPI backend models
 * These ensure type safety between frontend and backend
 */

// Base project interfaces
export interface ProjectStats {
    total_mentions: number;
    avg_sentiment: number;
    keywords_count: number;
    collections_count: number;
    posts_analyzed: number;
    comments_analyzed: number;
  }
  
  export interface ProjectSummary {
    summary_text: string;
    summary_preview: string;
    generated_at: string;
    provider: string;
    model: string;
  }
  
  export interface ProjectResponse {
    id: string;
    name: string;
    research_question?: string;
    keywords: string[];
    collection_ids: string[];
    status: 'running' | 'completed' | 'failed';
    created_at: string;
    partial_matching: boolean;
    context_window_words: number;
    stats: ProjectStats;
    summary?: ProjectSummary;
    collections_metadata: CollectionMetadata[];
  }
  
  export interface ProjectCreate {
    name: string;
    research_question?: string;
    keywords: string[];
    collection_ids: string[];
    partial_matching?: boolean;
    context_window_words?: number;
    generate_summary?: boolean;
  }
  
  export interface ProjectListResponse {
    projects: ProjectResponse[];
    total_count: number;
  }
  
  // Collection interfaces
  export interface CollectionMetadata {
    id: string;
    subreddit: string;
    sort_method: string;
    time_period?: string;
    created_at: string;
    status: string;
    posts_requested: number;
  }
  
  export interface CollectionParams {
    sort_method: 'hot' | 'new' | 'rising' | 'top' | 'controversial';
    time_period?: 'hour' | 'day' | 'week' | 'month' | 'year' | 'all';
    posts_count: number;
    root_comments: number;
    replies_per_root: number;
    min_upvotes: number;
  }
  
  export interface CollectionCreateRequest {
    subreddits: string[];
    collection_params: CollectionParams;
  }
  
  export interface CollectionResponse {
    id: string;
    subreddit: string;
    sort_method: string;
    time_period?: string;
    posts_requested: number;
    posts_collected: number;
    comments_collected: number;
    status: 'running' | 'completed' | 'failed';
    created_at: string;
    error_message?: string;
  }
  
  export interface CollectionListResponse {
    collections: CollectionResponse[];
    total_count: number;
  }
  
  export interface CollectionBatchResponse {
    batch_id: string;
    collection_ids: string[];
    subreddits: string[];
    status: string;
    started_at: string;
    estimated_duration_minutes: number;
  }
  
  export interface CollectionBatchStatusResponse {
    batch_id: string;
    status: string;
    progress_percentage: number;
    current_subreddit?: string;
    completed_subreddits: string[];
    failed_subreddits: string[];
    collections: CollectionResponse[];
    started_at: string;
    estimated_completion?: string;
  }
  
  // AI and Chat interfaces
  export interface ChatMessage {
    id: number;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    tokens_used: number;
    cost_estimate: number;
  }
  
  export interface ChatMessageCreate {
    message: string;
    search_type?: 'auto' | 'keyword' | 'local_semantic' | 'cloud_semantic' | 'analytics_driven';
  }
  
  export interface ChatResponse {
    message: string;
    sources: any[];
    analytics_insights: Record<string, any>;
    search_type: string;
    discussions_found: number;
    tokens_used: number;
    cost_estimate: number;
    session_id: string;
    query_classification: Record<string, any>;
  }
  
  export interface ChatSessionInfo {
    session_id: string;
    created_at: string;
    last_active: string;
    message_count: number;
    preview: string;
  }
  
  export interface ChatSessionListResponse {
    sessions: ChatSessionInfo[];
    total_count: number;
  }
  
  export interface ChatHistoryResponse {
    messages: ChatMessage[];
    session_id: string;
    total_messages: number;
  }
  
  export interface KeywordSuggestionRequest {
    research_description: string;
    max_keywords?: number;
  }
  
  export interface KeywordSuggestionResponse {
    keywords: string[];
    research_description: string;
    provider: string;
    model: string;
    tokens_used: number;
    cost_estimate: number;
  }
  
  export interface AIStatusResponse {
    ai_available: boolean;
    providers: Record<string, {
      available: boolean;
      model: string;
      status: string;
    }>;
    features: {
      keyword_suggestion: boolean;
      summarization: boolean;
      chat_agent: boolean;
      rag_search: boolean;
    };
    default_provider?: string;
    embeddings_info: Record<string, any>;
  }
  
  // Analysis workflow interfaces
  export interface AnalysisStatusResponse {
    project_id: string;
    status: 'running' | 'completed' | 'failed';
    created_at: string;
    last_updated: string;
    progress_percentage?: number;
    estimated_completion_minutes?: number;
    current_phase?: string;
    elapsed_minutes?: number;
    completed_at?: string;
    total_mentions?: number;
    average_sentiment?: number;
    has_ai_summary?: boolean;
    error?: string;
    message: string;
    troubleshooting_tips?: string[];
  }
  
  // Error handling
  export interface APIError {
    error: string;
    message: string;
    details?: Record<string, any>;
  }
  
  // Health check
  export interface HealthCheckResponse {
    status: 'healthy' | 'degraded' | 'unhealthy';
    timestamp: string;
    service: string;
    version: string;
    components?: Record<string, string>;
    error?: string;
  }

  export interface AnalysisStartResponse {
    status: string;
    message: string;
  }