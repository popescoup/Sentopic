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
  sentiment_distribution: {
      positive: number;  // percentage
      neutral: number;   // percentage
      negative: number;  // percentage
  };
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
    cooccurrences?: KeywordCooccurrence[];
    trend_summaries?: Record<string, TrendSummary>;
    sample_contexts?: ContextInstance[];
    keywords_data?: KeywordData[];
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

export interface IndexingRequest {
  provider_type: 'local' | 'openai';
  force_reindex?: boolean;
}

export interface IndexingResponse {
  status: string;
  message: string;
  provider_type: string;
  estimated_duration_minutes: number;
  total_content_items: number;
  started_at: string;
}

export interface IndexingStatusResponse {
  indexing_status: Record<string, string>;
  search_capabilities: Record<string, boolean>;
  total_content_items: number;
  local_indexed: number;
  cloud_indexed: number;
  current_indexing?: Record<string, any> | null;
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

  export interface KeywordCooccurrence {
    keyword1: string;
    keyword2: string;
    cooccurrence_count: number;
    in_posts: number;
    in_comments: number;
    avg_sentiment: number;
  }

export interface TrendSummary {
  trend_direction: 'rising' | 'falling' | 'stable' | 'insufficient_data';
  total_mentions: number;
}

export interface KeywordMentionDetail {
  keyword: string;
  position_in_content: number;
  sentiment_score: number;
}

export interface ContextInstance {
  content_type: 'post' | 'comment';
  content_reddit_id: string;
  context: string;
  sentiment_score: number;
  created_utc: number;
  collection_id: string;
  keyword_mentions: KeywordMentionDetail[];
}

export interface AggregatedKeywordMention {
  keyword: string;
  position_in_content: number;
  sentiment_score: number;
}

export interface FilteredContextInstance {
  content_type: 'post' | 'comment';
  content_reddit_id: string;
  collection_id: string;
  context: string;
  avg_sentiment_score: number;
  created_utc: number;
  keyword_mentions: AggregatedKeywordMention[];
  parent_post_id?: string;
}

export interface AggregatedFilteredContextsResponse {
  contexts: FilteredContextInstance[];
  pagination: PaginationInfo;
  filters_applied: Record<string, any>;
}

interface PaginationInfo {
  page: number;
  limit: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface KeywordData {
  keyword: string;
  total_mentions: number;
  avg_sentiment: number;
  posts_found_in: number;
  comments_found_in: number;
  collections_found_in: string[];
  first_mention_date: number;
  last_mention_date: number;
}

// Network visualization interfaces
export interface NetworkNode extends d3.SimulationNodeDatum {
  id: string;
  connectionCount: number;
  totalWeight: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface NetworkLink extends d3.SimulationLinkDatum<NetworkNode> {
  source: string | NetworkNode;
  target: string | NetworkNode;
  weight: number;
  inPosts: number;
  inComments: number;
  index?: number;
}

export interface NetworkData {
  nodes: NetworkNode[];
  links: NetworkLink[];
  metadata: {
    totalNodes: number;
    totalLinks: number;
    maxConnections: number;
    minConnections: number;
    maxWeight: number;
    minWeight: number;
  };
}

export interface TrendsDataPoint {
  time_period: string;
  formatted_date: string;
  [key: string]: string | number; // Dynamic fields for keyword mentions and sentiment
}

export interface TrendsDateRange {
  start_date: string | null;
  end_date: string | null;
}

export interface TrendsSummary {
  total_periods: number;
  total_mentions: number;
  date_coverage: string;
}

export interface TrendsResponse {
  keywords_analyzed: string[];
  time_period: string;
  date_range: TrendsDateRange;
  chart_data: TrendsDataPoint[];
  summary: TrendsSummary;
}