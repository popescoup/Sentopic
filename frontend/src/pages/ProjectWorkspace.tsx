/**
 * Project Workspace Page
 * Main interface for exploring analysis results
 * 
 * Phase 4.2: AI Q&A Integration
 * ENHANCED: Keyword relationship navigation to Context Explorer
 */

import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import MainLayout from '@/components/layout/MainLayout';
import { LoadingState } from '@/components/layout/LoadingSpinner';
import Card, { InsightCard } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import { DiscussionSnippet } from '@/components/discussions';
import { ContextExplorerModal, KeywordOverviewModal, KeywordRelationshipsModal, TrendsModal } from '@/components/modals';
import AIQuestionPanel from '@/components/ai/AIQuestionPanel';
import { api, getErrorMessage } from '@/api/client';
import { getInsightData } from '@/utils/insightProcessing';
import type { ContextInstance } from '@/types/api';

const getUniqueContexts = (contexts?: ContextInstance[]) => {
  if (!contexts) return [];
  
  const seen = new Set<string>();
  return contexts
    .filter(context => {
      const key = context.content_reddit_id;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .slice(0, 3);
};

const ProjectWorkspace: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  // Modal state management
  const [isSummaryModalOpen, setIsSummaryModalOpen] = React.useState(false);
  const [isContextExplorerOpen, setIsContextExplorerOpen] = React.useState(false);
  const [isKeywordOverviewOpen, setIsKeywordOverviewOpen] = React.useState(false);
  const [isKeywordRelationshipsOpen, setIsKeywordRelationshipsOpen] = React.useState(false);
  const [isTrendsModalOpen, setIsTrendsModalOpen] = React.useState(false);
  
  // NEW: State for managing initial context explorer filters
  const [contextExplorerInitialFilters, setContextExplorerInitialFilters] = React.useState<{
    primary_keyword?: string;
    secondary_keyword?: string;
  } | undefined>(undefined);

  // NEW: State for managing initial trends modal keywords
  const [trendsModalInitialKeywords, setTrendsModalInitialKeywords] = React.useState<string[] | undefined>(undefined);
  
  // NEW: State for project info modal
  const [isProjectInfoModalOpen, setIsProjectInfoModalOpen] = React.useState(false);

  const { data: project, isLoading, error } = useQuery({
    queryKey: ['project-results', projectId],
    queryFn: () => api.getAnalysisResults(projectId!),
    enabled: !!projectId && projectId.length > 0
  });

  // Quick verification log
  React.useEffect(() => {
    if (project?.sample_contexts) {
      console.log('🔍 Raw sample_contexts from backend:', project.sample_contexts);
      console.log('🔍 Sample contexts count:', project.sample_contexts.length);
      console.log('🔍 Sample context IDs:', project.sample_contexts.map(c => c.content_reddit_id));
    }
  }, [project?.sample_contexts]);

  // Deduplicate contexts at the top level to avoid hook ordering issues
  const uniqueContexts = React.useMemo(() => {
    return getUniqueContexts(project?.sample_contexts);
  }, [project?.sample_contexts]);

  // NEW: Handle keyword relationship exploration
  const handleExploreRelationship = React.useCallback((keyword1: string, keyword2: string) => {
    console.log(`🔍 Exploring relationship: "${keyword1}" + "${keyword2}"`);
    
    // Set initial filters for context explorer
    setContextExplorerInitialFilters({
      primary_keyword: keyword1,
      secondary_keyword: keyword2
    });
    
    // Close relationships modal and open context explorer
    setIsKeywordRelationshipsOpen(false);
    setIsContextExplorerOpen(true);
  }, []);

  // NEW: Handle keyword exploration
  const handleExploreKeyword = React.useCallback((keyword: string) => {
    console.log(`🔍 Exploring keyword: "${keyword}"`);
    
    // Set initial filters for context explorer
    setContextExplorerInitialFilters({
      primary_keyword: keyword,
      secondary_keyword: undefined
    });
    
    // Close keyword overview modal and open context explorer
    setIsKeywordOverviewOpen(false);
    setIsContextExplorerOpen(true);
  }, []);

  // NEW: Handle trends view for keyword relationships
  const handleViewTrends = React.useCallback((keyword1: string, keyword2: string) => {
    console.log(`🔍 Viewing trends for: "${keyword1}" + "${keyword2}"`);
    
    // Set initial keywords for trends modal
    setTrendsModalInitialKeywords([keyword1, keyword2]);
    
    // Close relationships modal and open trends modal
    setIsKeywordRelationshipsOpen(false);
    setIsTrendsModalOpen(true);
  }, []);

  // NEW: Handle trends modal close (clear initial keywords)
  const handleTrendsModalClose = React.useCallback(() => {
    setIsTrendsModalOpen(false);
    // Clear initial keywords when modal closes
    setTrendsModalInitialKeywords(undefined);
  }, []);

  // NEW: Handle trends view for single keyword
  const handleViewKeywordTrends = React.useCallback((keyword: string) => {
    console.log(`🔍 Viewing trends for keyword: "${keyword}"`);
    
    // Set initial keyword for trends modal (single keyword)
    setTrendsModalInitialKeywords([keyword]);
    
    // Close keyword overview modal and open trends modal
    setIsKeywordOverviewOpen(false);
    setIsTrendsModalOpen(true);
  }, []);

  // NEW: Handle context explorer close (clear initial filters)
  const handleContextExplorerClose = React.useCallback(() => {
    setIsContextExplorerOpen(false);
    // Clear initial filters when modal closes
    setContextExplorerInitialFilters(undefined);
  }, []);

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    if (diffDays <= 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  // Handle coming soon modals for Phase 5 features
  const handleComingSoon = (feature: string) => {
    alert(`${feature} will be implemented in Phase 5 with interactive modals and detailed analytics.`);
  };

  // Loading state
  if (isLoading) {
    return (
      <MainLayout title="Project Workspace">
        <LoadingState 
          title="Loading Project..."
          description="Fetching your project analysis and insights."
        />
      </MainLayout>
    );
  }

  // Error state
  if (error || !project) {
    return (
      <MainLayout title="Project Not Found">
        <Card className="text-center py-12">
          <div className="text-danger mb-4">
            <svg
              className="h-12 w-12 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          
          <h3 className="font-subsection text-text-primary mb-2">
            Project Not Found
          </h3>
          
          <p className="font-body text-text-secondary mb-6 max-w-md mx-auto">
            {error ? getErrorMessage(error) : 'The requested project could not be found or may have been deleted.'}
          </p>
          
          <div className="flex justify-center space-x-3">
            <Button variant="primary" onClick={() => navigate('/')}>
              Back to Projects
            </Button>
          </div>
        </Card>
      </MainLayout>
    );
  }

  // Format collections display
  const collectionsText = project.collections_metadata
    .map(c => `r/${c.subreddit}`)
    .join(', ');

  // Format insights data using the new utility functions
  const insightData = getInsightData(project);

  return (
    <MainLayout title={`${project.name} - Project Workspace`}>
      {/* Breadcrumb Navigation */}
      <div className="mb-6">
        <nav className="flex items-center space-x-2 font-body text-text-secondary">
          <Link 
            to="/" 
            className="hover:text-text-primary transition-colors duration-150"
          >
            Projects
          </Link>
          <span>→</span>
          <span className="text-text-primary">{project.name}</span>
        </nav>
      </div>

      {/* Minimal Header with Project Info Icon */}
      <div className="mb-6">
        <div className="flex items-center gap-3">
          <h1 className="font-page-title text-text-primary">{project.name}</h1>
          <button
            onClick={() => setIsProjectInfoModalOpen(true)}
            className="text-accent hover:text-accent-dark transition-colors flex-shrink-0 -translate-y-2"
            title="Project Information"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>
        {project.research_question && (
          <p className="font-body text-text-secondary mt-1">{project.research_question}</p>
        )}
      </div>

      {/* Analysis Summary Section */}
      {project.summary && (
        <Card className="mb-8 bg-gradient-panel">
          <div className="mb-4">
            <h2 className="font-section-header text-text-primary mb-2">
              Analysis Summary
            </h2>
            <p className="font-body text-text-secondary">
              {project.summary.summary_preview}
            </p>
          </div>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => setIsSummaryModalOpen(true)}
          >
            View Full Summary →
          </Button>
        </Card>
      )}

      {/* Status Information */}
      {project.status === 'running' && (
        <Card className="mb-8 border-accent bg-hover-blue">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="animate-spin h-5 w-5 text-accent mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <div>
              <h3 className="font-subsection text-text-primary mb-1">
                Analysis in Progress
              </h3>
              <p className="font-body text-text-secondary">
                Your project is currently being analyzed. Results will appear here when complete.
              </p>
            </div>
          </div>
        </Card>
      )}

      {project.status === 'failed' && (
        <Card className="mb-8 border-danger bg-red-50">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-danger mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="font-subsection text-danger mb-1">
                Analysis Failed
              </h3>
              <p className="font-body text-text-secondary">
                There was an error processing your project. Please try creating a new project or contact support.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Two-column layout for main content and AI sidebar */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {/* Insights Dashboard */}
          {project.status === 'completed' && (
            <div className="grid gap-6 md:grid-cols-3 mb-8">
              <InsightCard
                title="Keyword Overview"
                value={insightData.overview.totalMentions.toLocaleString()}
                description={insightData.overview.description}
                onClick={() => setIsKeywordOverviewOpen(true)}
              />
              
              <InsightCard
                title="Keyword Relationships"
                value={insightData.relationships?.count.toLocaleString() || '0'}
                description={insightData.relationships?.description || 'No co-occurrence data available'}
                onClick={() => setIsKeywordRelationshipsOpen(true)}
              />
              
              <InsightCard
                title="Keyword Trends"
                value={insightData.trends.arrow}
                description={insightData.trends.description}
                trend={insightData.trends.direction}
                isArrowCard={true}
                onClick={() => setIsTrendsModalOpen(true)}
              />
            </div>
          )}

          {/* Recent Discussions Section */}
          <Card>
            <div className="mb-4">
              <h3 className="font-section-header text-text-primary mb-2">
                Recent Discussions
              </h3>
              <p className="font-body text-text-secondary">
                Representative discussions containing your keywords from your analysis results.
              </p>
            </div>
  
            {project.status === 'completed' ? (
              <>
                {uniqueContexts.length > 0 ? (
                  <>
                    <div className="space-y-4 mb-6">
                      {uniqueContexts.map((context, index) => (
                        <DiscussionSnippet
                          key={context.content_reddit_id}
                          context={context}
                          keywords={project.keywords}
                          collectionsMetadata={project.collections_metadata}
                        />
                      ))}
                    </div>

                    <div className="pt-4 border-t border-border-primary">
                      <Button 
                        variant="outline" 
                        fullWidth
                        onClick={() => setIsContextExplorerOpen(true)}
                      >
                        Explore All {project.stats.total_mentions.toLocaleString()} Mentions →
                      </Button>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-text-tertiary mb-4">
                      <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </div>
                    <h4 className="font-subsection text-text-primary mb-2">
                      No Discussions Found
                    </h4>
                    <p className="font-body text-text-secondary mb-4 max-w-md mx-auto">
                      No discussions containing your keywords were found in the selected collections. 
                      Try expanding your keyword list or selecting additional collections.
                    </p>
                    <Button 
                      variant="outline"
                      onClick={() => handleComingSoon('Edit Project')}
                    >
                      Refine Keywords
                    </Button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8">
                <p className="font-body text-text-tertiary">
                  Discussion analysis will appear here when your project analysis is complete.
                </p>
              </div>
            )}
          </Card>
        </div>

        {/* AI Q&A Sidebar */}
        <div className="lg:col-span-1">
          {project.status === 'completed' ? (
            <AIQuestionPanel projectId={projectId!} />
          ) : (
            <Card className="bg-gradient-subtle">
              <div className="mb-4">
                <h3 className="font-section-header text-text-primary mb-2">
                  AI Assistant
                </h3>
                <div className="flex items-center text-small text-text-tertiary">
                  <div className="w-2 h-2 bg-text-tertiary rounded-full mr-2"></div>
                  Waiting for analysis
                </div>
              </div>
              
              <div className="mb-4 p-3 bg-content rounded-input border border-border-primary">
                <p className="font-body text-text-secondary text-sm">
                  AI Q&A will be available once your project analysis is complete. 
                  Ask questions about patterns, sentiment trends, and explore your data 
                  through natural language conversations.
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>

        {/* AI Summary Modal */}
        {project.summary && (
        <Modal
          isOpen={isSummaryModalOpen}
          onClose={() => setIsSummaryModalOpen(false)}
          title="AI Analysis Summary"
          size="lg"
        >
          <div className="max-h-96 overflow-y-auto">
            <div className="font-body text-text-primary leading-relaxed whitespace-pre-wrap">
              {project.summary.summary_text}
            </div>
          </div>
        </Modal>
      )}

      {/* Project Info Modal */}
      <Modal
        isOpen={isProjectInfoModalOpen}
        onClose={() => setIsProjectInfoModalOpen(false)}
        title="Project Information"
        size="lg"
      >
        <div className="space-y-6">
          {/* Project Details */}
          <div>
            <h3 className="font-section-header text-text-primary mb-3">Project Details</h3>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <span className="font-body text-text-secondary">Project Name:</span>
                <p className="font-technical text-text-primary">{project.name}</p>
              </div>
              <div>
                <span className="font-body text-text-secondary">Created:</span>
                <p className="font-technical text-text-primary">{formatDate(project.created_at)}</p>
              </div>
              {project.research_question && (
                <div className="md:col-span-2">
                  <span className="font-body text-text-secondary">Research Question:</span>
                  <p className="font-technical text-text-primary mt-1">{project.research_question}</p>
                </div>
              )}
            </div>
          </div>

          {/* Keywords */}
          <div>
            <h3 className="font-section-header text-text-primary mb-3">
              Keywords ({project.keywords.length})
            </h3>
            <div className="flex flex-wrap gap-2">
              {project.keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-hover-blue text-accent font-small rounded text-sm"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>

          {/* Collections */}
          <div>
            <h3 className="font-section-header text-text-primary mb-3">
              Collections ({project.stats.collections_count})
            </h3>
            <div className="space-y-3">
              {project.collections_metadata.map((collection, index) => (
                <details key={index} className="group">
                  <summary className="flex items-center justify-between cursor-pointer hover:bg-gradient-subtle p-3 rounded-lg transition-colors">
                    <div className="flex items-center gap-3">
                      <span className="font-technical text-text-primary text-lg">
                        r/{collection.subreddit}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-text-secondary">
                        {collection.sort_method}
                        {collection.time_period && ` (${collection.time_period})`}
                      </span>
                      <svg 
                        className="w-4 h-4 text-text-tertiary transition-transform group-open:rotate-180" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </summary>
                  
                  <div className="mt-3 pl-6 pr-3 pb-3 border-l-2 border-border-primary">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-text-secondary">Sort Method:</span>
                        <span className="ml-2 font-technical text-text-primary">
                          {collection.sort_method}
                          {collection.time_period && (
                            <span className="text-text-secondary"> ({collection.time_period})</span>
                          )}
                        </span>
                      </div>
                      <div>
                        <span className="text-text-secondary">Posts Requested:</span>
                        <span className="ml-2 font-technical text-text-primary">
                          {collection.posts_requested}
                        </span>
                      </div>
                      <div>
                        <span className="text-text-secondary">Root Comments:</span>
                        <span className="ml-2 font-technical text-text-primary">
                          {collection.root_comments_requested || 0} per post
                        </span>
                      </div>
                      <div>
                        <span className="text-text-secondary">Replies per Root:</span>
                        <span className="ml-2 font-technical text-text-primary">
                          {collection.replies_per_root || 0}
                        </span>
                      </div>
                      <div>
                        <span className="text-text-secondary">Min Upvotes:</span>
                        <span className="ml-2 font-technical text-text-primary">
                          {collection.min_upvotes || 0}
                        </span>
                      </div>
                      <div>
                        <span className="text-text-secondary">Created:</span>
                        <span className="ml-2 font-technical text-text-primary">
                          {formatDate(collection.created_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                </details>
              ))}
            </div>
          </div>

          {/* Analysis Statistics */}
          {project.status === 'completed' && (
            <div>
              <h3 className="font-section-header text-text-primary mb-3">Analysis Statistics</h3>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="p-4 bg-gradient-subtle rounded-lg">
                  <div className="text-2xl font-technical text-text-primary">
                    {project.stats.posts_analyzed.toLocaleString()}
                  </div>
                  <div className="text-sm text-text-secondary">Posts with Keywords</div>
                </div>
                <div className="p-4 bg-gradient-subtle rounded-lg">
                  <div className="text-2xl font-technical text-text-primary">
                    {project.stats.comments_analyzed.toLocaleString()}
                  </div>
                  <div className="text-sm text-text-secondary">Comments with Keywords</div>
                </div>
                <div className="p-4 bg-gradient-subtle rounded-lg">
                  <div className="text-2xl font-technical text-text-primary">
                    {project.stats.total_mentions.toLocaleString()}
                  </div>
                  <div className="text-sm text-text-secondary">Total Mentions</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </Modal>

      {/* Context Explorer Modal - ENHANCED with initial filters */}
      <ContextExplorerModal
        isOpen={isContextExplorerOpen}
        onClose={handleContextExplorerClose}
        project={project}
        initialFilters={contextExplorerInitialFilters}
      />

      {/* Keyword Overview Modal */}
      <KeywordOverviewModal
        isOpen={isKeywordOverviewOpen}
        onClose={() => setIsKeywordOverviewOpen(false)}
        project={project}
        onExploreKeyword={handleExploreKeyword}
        onViewTrends={handleViewKeywordTrends}
      />

      {/* Keyword Relationships Modal - ENHANCED with exploration handler */}
      <KeywordRelationshipsModal
        isOpen={isKeywordRelationshipsOpen}
        onClose={() => setIsKeywordRelationshipsOpen(false)}
        project={project}
        onExploreRelationship={handleExploreRelationship}
        onViewTrends={handleViewTrends}
      />

      {/* Trends Modal */}
      <TrendsModal
        isOpen={isTrendsModalOpen}
        onClose={handleTrendsModalClose}
        project={project}
        initialKeywords={trendsModalInitialKeywords}
      />
    </MainLayout>
  );
};

export default ProjectWorkspace;