/**
 * Project Workspace Page
 * Main interface for exploring analysis results
 * 
 * Phase 3.1: Core Workspace Implementation
 */

import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import MainLayout from '@/components/layout/MainLayout';
import { LoadingState } from '@/components/layout/LoadingSpinner';
import Card, { InsightCard } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { api, getErrorMessage } from '@/api/client';
import { getInsightData } from '@/utils/insightProcessing';

const ProjectWorkspace: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { data: project, isLoading, error } = useQuery({
    queryKey: ['project-results', projectId],
    queryFn: () => api.getAnalysisResults(projectId!),
    enabled: !!projectId && projectId.length > 0
  });

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

      {/* Research Context Bar */}
      <div className="mb-8">
        <h1 className="font-page-title text-text-primary mb-3">
          {project.name}
        </h1>
        <div className="flex flex-wrap items-center gap-4 font-body text-text-secondary">
          {project.research_question && (
            <>
              <span>Question: {project.research_question}</span>
              <span>•</span>
            </>
          )}
          <span>Keywords: {project.keywords.join(', ')}</span>
          <span>•</span>
          <span>Collections: {collectionsText}</span>
          <span>•</span>
          <span>Created {formatDate(project.created_at)}</span>
        </div>
      </div>

      {/* Key Findings Section */}
      {project.summary && (
        <Card className="mb-8 bg-gradient-panel">
          <div className="mb-4">
            <h2 className="font-section-header text-text-primary mb-2">
              Key Findings
            </h2>
            <p className="font-body text-text-secondary">
              {project.summary.summary_preview}
            </p>
          </div>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => handleComingSoon('Full AI Summary')}
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
                onClick={() => handleComingSoon('Keyword Overview')}
              />
              
              <InsightCard
                title="Keyword Relationships"
                value={insightData.relationships?.count.toLocaleString() || 'No data'}
                description={insightData.relationships?.description || 'No co-occurrence data available'}
                onClick={() => handleComingSoon('Keyword Relationships')}
              />
              
              <InsightCard
                title="Keyword Trends"
                value={insightData.trends.arrow}
                description={insightData.trends.description}
                trend={insightData.trends.direction}
                isArrowCard={true}
                onClick={() => handleComingSoon('Keyword Trends')}
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
                Representative discussions containing your keywords will appear here when analysis is complete.
              </p>
            </div>
            
            {project.status === 'completed' ? (
              <>
                <div className="space-y-4 mb-6">
                  {/* Placeholder discussion snippets */}
                  <div className="p-4 bg-panel rounded-input border border-border-primary">
                    <div className="flex items-start justify-between mb-2">
                      <span className="font-small text-text-tertiary">
                        {collectionsText.split(', ')[0]} • Analysis Results
                      </span>
                      <span className={project.stats.avg_sentiment >= 0 ? 'text-success' : 'text-danger'}>
                        {project.stats.avg_sentiment >= 0 ? 'Positive' : 'Negative'}
                      </span>
                    </div>
                    <p className="font-body text-text-secondary">
                      Discussion snippets with keyword highlighting will be displayed here. 
                      Click "Full Context Explorer" to browse all {project.stats.total_mentions.toLocaleString()} mentions found.
                    </p>
                  </div>
                </div>
                
                <div className="pt-4 border-t border-border-primary">
                  <Button 
                    variant="outline" 
                    fullWidth
                    onClick={() => handleComingSoon('Context Explorer')}
                  >
                    Full Context Explorer →
                  </Button>
                </div>
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

        {/* AI Sidebar Space */}
        <div className="lg:col-span-1">
          <Card className="bg-gradient-subtle">
            <div className="mb-4">
              <h3 className="font-section-header text-text-primary mb-2">
                AI Assistant
              </h3>
              <div className="flex items-center text-small text-text-tertiary">
                <div className="w-2 h-2 bg-text-tertiary rounded-full mr-2"></div>
                Coming in Phase 4
              </div>
            </div>
            
            <div className="mb-4 p-3 bg-content rounded-input border border-border-primary">
              <p className="font-body text-text-secondary text-sm">
                Interactive AI chat will be implemented in Phase 4. Ask questions about 
                patterns, get explanations of sentiment trends, and explore your data 
                through natural language conversations.
              </p>
            </div>
            
            <Button 
              variant="outline" 
              fullWidth
              onClick={() => handleComingSoon('AI Chat')}
            >
              Start Chat Session
            </Button>
          </Card>

          {/* Project Stats Card */}
          <Card className="mt-6">
            <div className="mb-4">
              <h3 className="font-section-header text-text-primary mb-2">
                Project Details
              </h3>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="font-body text-text-secondary">Keywords:</span>
                <span className="font-technical text-text-primary">
                  {project.keywords.length}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="font-body text-text-secondary">Collections:</span>
                <span className="font-technical text-text-primary">
                  {project.stats.collections_count}
                </span>
              </div>
              
              {project.status === 'completed' && (
                <>
                  <div className="flex justify-between items-center">
                    <span className="font-body text-text-secondary">Posts:</span>
                    <span className="font-technical text-text-primary">
                      {project.stats.posts_analyzed.toLocaleString()}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="font-body text-text-secondary">Comments:</span>
                    <span className="font-technical text-text-primary">
                      {project.stats.comments_analyzed.toLocaleString()}
                    </span>
                  </div>
                </>
              )}
              
              <div className="flex justify-between items-center">
                <span className="font-body text-text-secondary">Status:</span>
                <span className={`font-small px-2 py-1 rounded-input text-xs ${
                  project.status === 'completed' ? 'bg-green-100 text-success' :
                  project.status === 'running' ? 'bg-blue-100 text-accent' :
                  'bg-red-100 text-danger'
                }`}>
                  {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                </span>
              </div>
            </div>
          </Card>

          {/* Keywords Preview */}
          <Card className="mt-6">
            <div className="mb-4">
              <h3 className="font-section-header text-text-primary mb-2">
                Keywords
              </h3>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {project.keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-hover-blue text-accent font-small rounded-input text-xs"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* Phase Information */}
      <div className="mt-12 bg-panel rounded-default p-6 border border-border-primary">
        <h2 className="font-section-header text-text-primary mb-3">
          Project Workspace - Phase 3.1 Implementation
        </h2>
        
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              ✅ Implemented in Phase 3.1
            </h3>
            <ul className="font-body text-text-secondary space-y-1 text-sm">
              <li>• Real project data integration</li>
              <li>• Professional two-column layout</li>
              <li>• Functional insight cards (clickable)</li>
              <li>• Research context display</li>
              <li>• Loading and error states</li>
              <li>• Project status handling</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              🔄 Coming in Phase 4
            </h3>
            <ul className="font-body text-text-secondary space-y-1 text-sm">
              <li>• Interactive AI chat sidebar</li>
              <li>• Natural language querying</li>
              <li>• Context-aware AI responses</li>
              <li>• Chat session management</li>
              <li>• AI status integration</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              📊 Coming in Phase 5
            </h3>
            <ul className="font-body text-text-secondary space-y-1 text-sm">
              <li>• Interactive analysis modals</li>
              <li>• Advanced data visualizations</li>
              <li>• Context explorer with filters</li>
              <li>• Network relationship graphs</li>
              <li>• Trend analysis charts</li>
            </ul>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default ProjectWorkspace;