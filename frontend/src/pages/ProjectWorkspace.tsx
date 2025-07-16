/**
 * Project Workspace Page
 * Main interface for exploring analysis results
 * 
 * Phase 1: Placeholder with professional styling
 * Phase 3: Full implementation with insights dashboard and AI chat
 */

import React from 'react';
import { useParams, Link } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import Card, { InsightCard } from '@/components/ui/Card';
import Button from '@/components/ui/Button';

const ProjectWorkspace: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();

  return (
    <MainLayout title="Project Workspace">
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
          <span className="text-text-primary">Project {projectId}</span>
        </nav>
      </div>

      {/* Research Context Bar */}
      <div className="mb-8">
        <h1 className="font-page-title text-text-primary mb-3">
          iPhone Battery Analysis
        </h1>
        <div className="flex flex-wrap items-center gap-4 font-body text-text-secondary">
          <span>Keywords: battery, charging, drain, power</span>
          <span>•</span>
          <span>Collections: r/iphone, r/apple</span>
          <span>•</span>
          <span>Created 2 days ago</span>
        </div>
      </div>

      {/* Key Findings Section */}
      <Card className="mb-8 bg-gradient-panel">
        <div className="mb-4">
          <h2 className="font-section-header text-text-primary mb-2">
            Key Findings
          </h2>
          <p className="font-body text-text-secondary">
            AI-generated insights will appear here in Phase 3. This section will provide 
            business-relevant summary of discussion patterns and sentiment analysis.
          </p>
        </div>
        <Button variant="outline" size="sm">
          View Full Summary →
        </Button>
      </Card>

      {/* Insights Dashboard */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <InsightCard
          title="Keywords Overview"
          value="1,247"
          description="Total mentions found"
          trend="down"
          trendValue="-12%"
          onClick={() => alert('Keyword Analysis Modal will be implemented in Phase 5')}
        />
        
        <InsightCard
          title="Average Sentiment"
          value="-0.23"
          description="Negative sentiment detected"
          trend="down"
          trendValue="-0.05"
          onClick={() => alert('Sentiment Analysis Modal will be implemented in Phase 5')}
        />
        
        <InsightCard
          title="Co-occurrences"
          value="38"
          description="Keyword relationships"
          trend="up"
          trendValue="+5"
          onClick={() => alert('Co-occurrence Analysis Modal will be implemented in Phase 5')}
        />
      </div>

      {/* Two-column layout for main content and AI sidebar */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {/* Recent Discussions Section */}
          <Card>
            <div className="mb-4">
              <h3 className="font-section-header text-text-primary mb-2">
                Recent Discussions
              </h3>
              <p className="font-body text-text-secondary">
                Sample discussions will be displayed here with keyword highlighting 
                and sentiment indicators.
              </p>
            </div>
            
            <div className="space-y-4">
              {/* Example discussion snippets */}
              <div className="p-4 bg-panel rounded-input border border-border-primary">
                <div className="flex items-start justify-between mb-2">
                  <span className="font-small text-text-tertiary">r/iphone • 2 hours ago</span>
                  <span className="text-danger font-small">Negative</span>
                </div>
                <p className="font-body text-text-secondary">
                  "My <mark className="bg-yellow-200 px-1 rounded">battery</mark> life has been terrible since the update. 
                  <mark className="bg-yellow-200 px-1 rounded">Charging</mark> takes forever and the <mark className="bg-yellow-200 px-1 rounded">drain</mark> is insane..."
                </p>
              </div>
              
              <div className="p-4 bg-panel rounded-input border border-border-primary">
                <div className="flex items-start justify-between mb-2">
                  <span className="font-small text-text-tertiary">r/apple • 4 hours ago</span>
                  <span className="text-success font-small">Positive</span>
                </div>
                <p className="font-body text-text-secondary">
                  "Actually loving the new <mark className="bg-yellow-200 px-1 rounded">battery</mark> optimizations. 
                  My <mark className="bg-yellow-200 px-1 rounded">charging</mark> routine has improved significantly..."
                </p>
              </div>
            </div>
            
            <div className="mt-6 pt-4 border-t border-border-primary">
              <Button variant="outline" fullWidth>
                Full Context Explorer →
              </Button>
            </div>
          </Card>
        </div>

        {/* AI Sidebar */}
        <div className="lg:col-span-1">
          <Card className="bg-gradient-subtle">
            <div className="mb-4">
              <h3 className="font-section-header text-text-primary mb-2">
                AI Assistant
              </h3>
              <div className="flex items-center text-small text-text-tertiary">
                <div className="w-2 h-2 bg-success rounded-full mr-2"></div>
                Ready
              </div>
            </div>
            
            <div className="mb-4 p-3 bg-content rounded-input border border-border-primary">
              <p className="font-body text-text-secondary text-sm">
                Interactive AI chat will be implemented in Phase 4. Ask questions about 
                patterns, get explanations of sentiment trends, and explore your data 
                through natural language.
              </p>
            </div>
            
            <Button variant="primary" fullWidth>
              Start New Chat
            </Button>
          </Card>
        </div>
      </div>

      {/* Phase Information */}
      <div className="mt-12 bg-panel rounded-default p-6 border border-border-primary">
        <h2 className="font-section-header text-text-primary mb-3">
          Project Workspace Implementation Roadmap
        </h2>
        
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              Phase 3: Core Workspace
            </h3>
            <ul className="font-body text-text-secondary space-y-1 text-sm">
              <li>• Real analysis results display</li>
              <li>• Interactive insight cards</li>
              <li>• Discussion snippets with highlighting</li>
              <li>• AI summary integration</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              Phase 4: AI Integration
            </h3>
            <ul className="font-body text-text-secondary space-y-1 text-sm">
              <li>• Interactive AI chat sidebar</li>
              <li>• Natural language querying</li>
              <li>• Context-aware responses</li>
              <li>• Chat session management</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              Phase 5: Deep-Dive Modals
            </h3>
            <ul className="font-body text-text-secondary space-y-1 text-sm">
              <li>• Keyword analysis modal</li>
              <li>• Trends visualization</li>
              <li>• Context explorer with filters</li>
              <li>• Network relationship graphs</li>
            </ul>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default ProjectWorkspace;