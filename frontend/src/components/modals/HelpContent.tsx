/**
 * Help Content Component
 * Organized help documentation content with search functionality
 */

import React from 'react';
import CollapsibleSection from '@/components/ui/CollapsibleSection';

interface HelpContentProps {
  /** Additional CSS classes */
  className?: string;
}

export const HelpContent: React.FC<HelpContentProps> = ({ className = '' }) => {
  // Help content data structure
  const helpSections = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      defaultExpanded: true,
      content: {
        'Quick Start Guide (5-minute setup)': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">1. Configure API Access</h4>
              <p className="text-text-secondary mb-2">
                Before you can collect Reddit data, you need to set up API credentials:
              </p>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li>Go to <strong>Settings</strong> in the top-right corner</li>
                <li>Navigate to the <strong>Configuration</strong> tab</li>
                <li>Enter your Reddit API credentials (Client ID, Client Secret, User Agent)</li>
                <li>Optionally configure AI providers (Anthropic/OpenAI) for enhanced features</li>
                <li>Click <strong>Test Connection</strong> to verify your setup</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">2. Create Your First Collection</h4>
              <p className="text-text-secondary mb-2">
                Collections contain Reddit posts and comments from specific subreddits:
              </p>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li>Click <strong>Collection Manager</strong> in the header</li>
                <li>Select target subreddits and collection parameters</li>
                <li>Choose sorting method (hot, new, top, etc.) and time period</li>
                <li>Set the number of posts and comments to collect</li>
                <li>Start collection and monitor progress</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">3. Start Your First Analysis Project</h4>
              <p className="text-text-secondary mb-2">
                Projects analyze your collections to find business insights:
              </p>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li>Click <strong>New Project</strong> from the Projects Dashboard</li>
                <li>Enter your research question (e.g., "What do people think about electric vehicles?")</li>
                <li>Define relevant keywords or use AI suggestions</li>
                <li>Select which collections to analyze</li>
                <li>Click <strong>Start Analysis</strong> and monitor progress</li>
              </ul>
            </div>
            
            <div className="bg-panel p-4 rounded-default">
              <p className="text-text-secondary">
                <strong>💡 Pro Tip:</strong> Start with a focused research question and 3-5 specific keywords 
                for better results. You can always create additional projects to explore different angles.
              </p>
            </div>
          </div>
        ),
        'First Project Walkthrough': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Project Creation Process</h4>
              <p className="text-text-secondary mb-3">
                Follow this step-by-step guide to create your first analysis project:
              </p>
              
              <div className="space-y-3">
                <div className="border-l-4 border-accent pl-4">
                  <h5 className="font-medium text-text-primary">Research Question</h5>
                  <p className="text-text-secondary text-sm">
                    Be specific and actionable. Good examples: "What features do users want in project management tools?" 
                    or "What are the main complaints about food delivery apps?"
                  </p>
                </div>
                
                <div className="border-l-4 border-accent pl-4">
                  <h5 className="font-medium text-text-primary">Keyword Selection</h5>
                  <p className="text-text-secondary text-sm">
                    Choose 3-8 relevant keywords. Mix broad terms ("project management") with specific ones ("Slack", "Asana"). 
                    Use the AI suggestion feature for inspiration.
                  </p>
                </div>
                
                <div className="border-l-4 border-accent pl-4">
                  <h5 className="font-medium text-text-primary">Collection Selection</h5>
                  <p className="text-text-secondary text-sm">
                    Select collections that contain discussions relevant to your research. 
                    Consider subreddit themes and user demographics.
                  </p>
                </div>
              </div>
            </div>
          </div>
        ),
        'Understanding Your Results': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Key Metrics Explained</h4>
              <div className="grid gap-4">
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Total Mentions</h5>
                  <p className="text-text-secondary text-sm">
                    Number of times your keywords appeared in the analyzed content. Higher numbers indicate more discussion volume.
                  </p>
                </div>
                
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Average Sentiment</h5>
                  <p className="text-text-secondary text-sm">
                    Overall emotional tone (-1 to +1 scale). Positive values indicate favorable discussions, negative values suggest criticism or problems.
                  </p>
                </div>
                
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Keyword Co-occurrences</h5>
                  <p className="text-text-secondary text-sm">
                    Shows which keywords appear together frequently, revealing connected topics and user associations.
                  </p>
                </div>
                
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Trend Direction</h5>
                  <p className="text-text-secondary text-sm">
                    Whether mention frequency is rising, falling, or stable over time. Helpful for identifying emerging topics.
                  </p>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Reading the AI Summary</h4>
              <p className="text-text-secondary mb-2">
                The AI-generated summary provides business-focused insights based on your research question. Look for:
              </p>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li><strong>Key themes:</strong> Major topics of discussion</li>
                <li><strong>User sentiment:</strong> Overall positive or negative trends</li>
                <li><strong>Pain points:</strong> Common problems or complaints mentioned</li>
                <li><strong>Opportunities:</strong> Unmet needs or feature requests</li>
                <li><strong>Competitive insights:</strong> Mentions of competitors or alternatives</li>
              </ul>
            </div>
          </div>
        ),
      },
    },
    {
      id: 'features-overview',
      title: 'Features Overview',
      content: {
        'Project Management': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Creating and Managing Projects</h4>
              <p className="text-text-secondary mb-3">
                Projects are the core organizational unit in Sentopic. Each project represents a focused business research investigation.
              </p>
              
              <div className="space-y-3">
                <div>
                  <h5 className="font-medium text-text-primary mb-1">Project Dashboard</h5>
                  <p className="text-text-secondary text-sm">
                    The main landing page shows all your projects with key metrics, creation dates, and AI-generated summaries. 
                    Click any project to dive into detailed results.
                  </p>
                </div>
                
                <div>
                  <h5 className="font-medium text-text-primary mb-1">Project Workspace</h5>
                  <p className="text-text-secondary text-sm">
                    Each project has its own workspace with insights dashboard, discussion examples, and AI chat assistant. 
                    Use the modal system to explore detailed analytics.
                  </p>
                </div>
                
                <div>
                  <h5 className="font-medium text-text-primary mb-1">Project Configuration</h5>
                  <p className="text-text-secondary text-sm">
                    Customize analysis parameters including partial keyword matching, context window size, and AI summary generation.
                  </p>
                </div>
              </div>
            </div>
          </div>
        ),
        'Data Collection Process': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Reddit Data Collection</h4>
              <p className="text-text-secondary mb-3">
                Collections gather Reddit posts and comments from specified subreddits using the Reddit API.
              </p>
              
              <div className="bg-panel p-4 rounded-default space-y-3">
                <div>
                  <h5 className="font-medium text-text-primary mb-1">Collection Parameters</h5>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-4">
                    <li><strong>Sort Method:</strong> How posts are ranked (hot, new, top, controversial)</li>
                    <li><strong>Time Period:</strong> Date range for "top" sorting (hour, day, week, month, year, all)</li>
                    <li><strong>Post Count:</strong> Number of posts to collect per subreddit</li>
                    <li><strong>Comment Depth:</strong> Root comments and replies per post</li>
                    <li><strong>Minimum Upvotes:</strong> Quality filter for content</li>
                  </ul>
                </div>
              </div>
              
              <div>
                <h4 className="font-subsection text-text-primary mb-2">Collection Status Monitoring</h4>
                <p className="text-text-secondary mb-2">
                  Track collection progress in real-time:
                </p>
                <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                  <li><strong>Running:</strong> Actively collecting data from Reddit</li>
                  <li><strong>Completed:</strong> Successfully gathered all requested content</li>
                  <li><strong>Failed:</strong> Encountered errors (check API limits or subreddit availability)</li>
                </ul>
              </div>
            </div>
          </div>
        ),
        'Analysis Capabilities': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Keyword Analysis</h4>
              <p className="text-text-secondary mb-2">
                Advanced text processing to find and analyze keyword mentions:
              </p>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li><strong>Exact Matching:</strong> Find precise keyword phrases</li>
                <li><strong>Partial Matching:</strong> Include words containing your keywords</li>
                <li><strong>Context Windows:</strong> Capture surrounding text for better context</li>
                <li><strong>Sentiment Scoring:</strong> Emotional tone analysis for each mention</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Co-occurrence Analysis</h4>
              <p className="text-text-secondary mb-2">
                Discover relationships between keywords by analyzing which terms appear together:
              </p>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li>Identify connected topics and user associations</li>
                <li>Separate analysis for posts vs. comments</li>
                <li>Network visualization of keyword relationships</li>
                <li>Weighted connections based on frequency</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Trend Analysis</h4>
              <p className="text-text-secondary mb-2">
                Track how keyword mentions change over time:
              </p>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li>Daily, weekly, or monthly trend visualization</li>
                <li>Multiple keyword comparison</li>
                <li>Sentiment trends alongside mention frequency</li>
                <li>Rising, falling, or stable trend classification</li>
              </ul>
            </div>
          </div>
        ),
        'AI-Powered Insights': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">AI Features Overview</h4>
              <p className="text-text-secondary mb-3">
                Sentopic integrates multiple AI capabilities to enhance your research workflow.
              </p>
              
              <div className="grid gap-4">
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Keyword Suggestions</h5>
                  <p className="text-text-secondary text-sm">
                    AI analyzes your research question to suggest relevant keywords you might have missed.
                  </p>
                </div>
                
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Analysis Summarization</h5>
                  <p className="text-text-secondary text-sm">
                    Generates business-focused summaries of your findings, highlighting key insights and opportunities.
                  </p>
                </div>
                
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Interactive Chat Assistant</h5>
                  <p className="text-text-secondary text-sm">
                    Ask questions about your analysis results and get contextual answers with supporting evidence.
                  </p>
                </div>
                
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Semantic Search</h5>
                  <p className="text-text-secondary text-sm">
                    Find relevant discussions using natural language queries, not just exact keyword matches.
                  </p>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Chat Assistant Usage Tips</h4>
              <p className="text-text-secondary mb-2">
                Get the most out of your AI chat assistant:
              </p>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li><strong>Be specific:</strong> "What are the main complaints about delivery apps?" vs. "Tell me about sentiment"</li>
                <li><strong>Ask for examples:</strong> Request specific Reddit discussions that support insights</li>
                <li><strong>Explore connections:</strong> Ask about relationships between different keywords</li>
                <li><strong>Business focus:</strong> Frame questions around actionable business decisions</li>
              </ul>
            </div>
          </div>
        ),
      },
    },
    {
      id: 'advanced-topics',
      title: 'Advanced Topics',
      content: {
        'Keyword Optimization Strategies': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Choosing Effective Keywords</h4>
              <p className="text-text-secondary mb-3">
                Strategic keyword selection is crucial for meaningful analysis results.
              </p>
              
              <div className="space-y-3">
                <div>
                  <h5 className="font-medium text-text-primary mb-1">Keyword Categories</h5>
                  <div className="bg-panel p-3 rounded-default">
                    <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-4">
                      <li><strong>Brand Terms:</strong> Company names, product names, competitors</li>
                      <li><strong>Category Terms:</strong> Industry or product category keywords</li>
                      <li><strong>Feature Terms:</strong> Specific features, capabilities, or attributes</li>
                      <li><strong>Problem Terms:</strong> Pain points, issues, challenges users face</li>
                      <li><strong>Sentiment Terms:</strong> Emotional language that reveals user feelings</li>
                    </ul>
                  </div>
                </div>
                
                <div>
                  <h5 className="font-medium text-text-primary mb-1">Best Practices</h5>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                    <li>Start with 3-5 core keywords, expand based on co-occurrence findings</li>
                    <li>Include both broad and specific terms</li>
                    <li>Test different keyword variations (plurals, abbreviations, slang)</li>
                    <li>Monitor keyword performance and refine over time</li>
                    <li>Use AI suggestions as inspiration, not gospel</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Partial Matching Configuration</h4>
              <p className="text-text-secondary mb-2">
                Control how strictly keywords are matched in content:
              </p>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li><strong>Exact matching:</strong> Only finds precise keyword phrases</li>
                <li><strong>Partial matching:</strong> Includes words containing your keywords</li>
                <li>Use partial matching for brand names with common variations</li>
                <li>Use exact matching for common words to avoid false positives</li>
              </ul>
            </div>
          </div>
        ),
        'Sentiment Analysis Interpretation': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Understanding Sentiment Scores</h4>
              <p className="text-text-secondary mb-3">
                Sentiment analysis provides numerical scores from -1 (very negative) to +1 (very positive).
              </p>
              
              <div className="bg-panel p-4 rounded-default">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-danger font-technical text-lg">-1.0 to -0.3</div>
                    <div className="text-text-secondary text-sm">Negative</div>
                    <div className="text-text-tertiary text-sm">Criticism, complaints, problems</div>
                  </div>
                  <div>
                    <div className="text-text-secondary font-technical text-lg">-0.3 to +0.3</div>
                    <div className="text-text-secondary text-sm">Neutral</div>
                    <div className="text-text-tertiary text-sm">Factual, mixed, or balanced</div>
                  </div>
                  <div>
                    <div className="text-success font-technical text-lg">+0.3 to +1.0</div>
                    <div className="text-text-secondary text-sm">Positive</div>
                    <div className="text-text-tertiary text-sm">Praise, satisfaction, recommendations</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Business Interpretation</h4>
              <ul className="list-disc list-inside space-y-2 text-text-secondary ml-4">
                <li><strong>Highly Negative (-0.7 to -1.0):</strong> Major issues requiring immediate attention</li>
                <li><strong>Moderately Negative (-0.3 to -0.7):</strong> Areas for improvement, minor complaints</li>
                <li><strong>Neutral (-0.3 to +0.3):</strong> Factual discussions, mixed opinions</li>
                <li><strong>Moderately Positive (+0.3 to +0.7):</strong> General satisfaction, mild praise</li>
                <li><strong>Highly Positive (+0.7 to +1.0):</strong> Strong advocacy, recommendations</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Context Considerations</h4>
              <p className="text-text-secondary mb-2">
                Remember that sentiment analysis has limitations:
              </p>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li>Sarcasm and irony may be misinterpreted</li>
                <li>Context window size affects accuracy</li>
                <li>Reddit's informal language can challenge analysis</li>
                <li>Always read actual examples to validate insights</li>
              </ul>
            </div>
          </div>
        ),
        'Trend Analysis Best Practices': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Interpreting Trend Data</h4>
              <p className="text-text-secondary mb-3">
                Trend analysis reveals how discussion patterns change over time.
              </p>
              
              <div className="space-y-3">
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Rising Trends</h5>
                  <p className="text-text-secondary text-sm">
                    Increasing mention frequency may indicate growing interest, emerging problems, or viral topics. 
                    Investigate recent events or product launches.
                  </p>
                </div>
                
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Falling Trends</h5>
                  <p className="text-text-secondary text-sm">
                    Decreasing mentions might suggest declining interest, resolved issues, or seasonal effects. 
                    Consider external factors affecting discussion volume.
                  </p>
                </div>
                
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Stable Trends</h5>
                  <p className="text-text-secondary text-sm">
                    Consistent mention levels indicate steady, ongoing discussion. Good for baseline understanding 
                    of typical conversation volume.
                  </p>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Time Period Selection</h4>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li><strong>Daily:</strong> High granularity for short-term analysis, event tracking</li>
                <li><strong>Weekly:</strong> Balanced view, smooths daily fluctuations</li>
                <li><strong>Monthly:</strong> Long-term patterns, seasonal trends</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Trend Analysis Tips</h4>
              <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                <li>Look for patterns, not just individual data points</li>
                <li>Compare multiple keywords to understand relative changes</li>
                <li>Consider external events that might influence discussions</li>
                <li>Use both mention frequency and sentiment trends together</li>
                <li>Longer time periods provide more reliable trend indicators</li>
              </ul>
            </div>
          </div>
        ),
        'Business Insight Extraction': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">From Data to Actionable Insights</h4>
              <p className="text-text-secondary mb-3">
                Transform your analysis results into concrete business decisions and strategies.
              </p>
              
              <div className="space-y-4">
                <div>
                  <h5 className="font-medium text-text-primary mb-2">Product Development Insights</h5>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                    <li>Identify frequently mentioned missing features</li>
                    <li>Find pain points with current solutions</li>
                    <li>Discover user workflow patterns and needs</li>
                    <li>Monitor competitor feature discussions</li>
                  </ul>
                </div>
                
                <div>
                  <h5 className="font-medium text-text-primary mb-2">Market Research Applications</h5>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                    <li>Gauge market sentiment toward new product categories</li>
                    <li>Understand user demographics and preferences</li>
                    <li>Identify emerging trends before they become mainstream</li>
                    <li>Track brand perception and competitive positioning</li>
                  </ul>
                </div>
                
                <div>
                  <h5 className="font-medium text-text-primary mb-2">Customer Support Intelligence</h5>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                    <li>Find common issues users discuss informally</li>
                    <li>Identify gaps in official documentation</li>
                    <li>Monitor sentiment around support experience</li>
                    <li>Discover community-generated solutions</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Creating Action Plans</h4>
              <p className="text-text-secondary mb-2">
                Turn insights into specific next steps:
              </p>
              <div className="bg-panel p-4 rounded-default">
                <ol className="list-decimal list-inside space-y-2 text-text-secondary">
                  <li><strong>Prioritize findings:</strong> Focus on high-frequency, high-impact issues</li>
                  <li><strong>Validate insights:</strong> Cross-reference with other data sources</li>
                  <li><strong>Define success metrics:</strong> How will you measure improvement?</li>
                  <li><strong>Assign ownership:</strong> Who will act on each insight?</li>
                  <li><strong>Set timelines:</strong> When will changes be implemented?</li>
                  <li><strong>Monitor impact:</strong> Create follow-up projects to track results</li>
                </ol>
              </div>
            </div>
          </div>
        ),
      },
    },
    {
      id: 'troubleshooting',
      title: 'Troubleshooting',
      content: {
        'Common Issues & Solutions': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Collection Problems</h4>
              <div className="space-y-3">
                <div className="border-l-4 border-danger pl-4">
                  <h5 className="font-medium text-text-primary mb-1">Collection Failed or Incomplete</h5>
                  <p className="text-text-secondary text-sm mb-2">
                    <strong>Possible causes:</strong> API rate limits, invalid subreddit names, network issues
                  </p>
                  <p className="text-text-secondary text-sm">
                    <strong>Solutions:</strong>
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-4">
                    <li>Check if subreddit names are spelled correctly and exist</li>
                    <li>Reduce the number of posts/comments requested</li>
                    <li>Verify Reddit API credentials in Settings</li>
                    <li>Try collecting from fewer subreddits simultaneously</li>
                  </ul>
                </div>
                
                <div className="border-l-4 border-warning pl-4">
                  <h5 className="font-medium text-text-primary mb-1">Very Low Post/Comment Counts</h5>
                  <p className="text-text-secondary text-sm mb-2">
                    <strong>Possible causes:</strong> Inactive subreddits, high minimum upvote requirements, restrictive time periods
                  </p>
                  <p className="text-text-secondary text-sm">
                    <strong>Solutions:</strong>
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-4">
                    <li>Lower minimum upvote requirements</li>
                    <li>Use broader time periods (month/year instead of day/week)</li>
                    <li>Choose more active subreddits</li>
                    <li>Try different sorting methods (hot/new instead of top)</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Analysis Problems</h4>
              <div className="space-y-3">
                <div className="border-l-4 border-danger pl-4">
                  <h5 className="font-medium text-text-primary mb-1">No Keyword Mentions Found</h5>
                  <p className="text-text-secondary text-sm mb-2">
                    <strong>Possible causes:</strong> Keywords too specific, wrong subreddit selection, exact matching too strict
                  </p>
                  <p className="text-text-secondary text-sm">
                    <strong>Solutions:</strong>
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-4">
                    <li>Enable partial keyword matching</li>
                    <li>Try broader or alternative keywords</li>
                    <li>Use AI keyword suggestions</li>
                    <li>Review actual collection content to verify relevance</li>
                  </ul>
                </div>
                
                <div className="border-l-4 border-warning pl-4">
                  <h5 className="font-medium text-text-primary mb-1">Analysis Stuck or Taking Too Long</h5>
                  <p className="text-text-secondary text-sm mb-2">
                    <strong>Possible causes:</strong> Large collections, complex keyword sets, server load
                  </p>
                  <p className="text-text-secondary text-sm">
                    <strong>Solutions:</strong>
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-4">
                    <li>Wait for processing to complete (can take several minutes)</li>
                    <li>Refresh the page and check analysis status</li>
                    <li>For persistent issues, create a new project with fewer collections</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        ),
        'API Configuration Problems': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Reddit API Issues</h4>
              <div className="space-y-3">
                <div className="border-l-4 border-danger pl-4">
                  <h5 className="font-medium text-text-primary mb-1">Connection Test Failed</h5>
                  <p className="text-text-secondary text-sm mb-2">
                    <strong>Check these common issues:</strong>
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-4">
                    <li>Client ID and Client Secret are correct and complete</li>
                    <li>Reddit app is configured as "script" type (not web app)</li>
                    <li>User Agent follows format: "appname/version by /u/username"</li>
                    <li>No extra spaces or special characters in credentials</li>
                  </ul>
                </div>
                
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Getting Reddit API Credentials</h5>
                  <ol className="list-decimal list-inside space-y-1 text-text-secondary text-sm ml-4">
                    <li>Go to <a href="https://www.reddit.com/prefs/apps" className="text-accent hover:underline" target="_blank" rel="noopener noreferrer">reddit.com/prefs/apps</a></li>
                    <li>Click "Create App" or "Create Another App"</li>
                    <li>Choose "script" as the app type</li>
                    <li>Name your app (e.g., "Sentopic Research Tool")</li>
                    <li>Add a description and redirect URI (can be http://localhost)</li>
                    <li>Copy the Client ID (under app name) and Client Secret</li>
                  </ol>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">AI Provider Configuration</h4>
              <div className="space-y-3">
                <div className="border-l-4 border-warning pl-4">
                  <h5 className="font-medium text-text-primary mb-1">AI Features Unavailable</h5>
                  <p className="text-text-secondary text-sm mb-2">
                    <strong>Solutions:</strong>
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-4">
                    <li>Configure at least one AI provider (Anthropic or OpenAI) in Settings</li>
                    <li>Verify API keys are valid and have sufficient credits</li>
                    <li>Check that required features are enabled for your account</li>
                    <li>Test individual provider connections</li>
                  </ul>
                </div>
                
                <div className="bg-panel p-3 rounded-default">
                  <h5 className="font-medium text-text-primary mb-1">Getting AI API Keys</h5>
                  <div className="space-y-2 text-text-secondary text-sm">
                    <div>
                      <strong>Anthropic (Claude):</strong> Visit <a href="https://console.anthropic.com" className="text-accent hover:underline" target="_blank" rel="noopener noreferrer">console.anthropic.com</a>, 
                      create account, go to API keys section
                    </div>
                    <div>
                      <strong>OpenAI (GPT):</strong> Visit <a href="https://platform.openai.com/api-keys" className="text-accent hover:underline" target="_blank" rel="noopener noreferrer">platform.openai.com</a>, 
                      create account, generate new API key
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ),
        'Performance Optimization': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Optimizing Collection Performance</h4>
              <div className="space-y-3">
                <div>
                  <h5 className="font-medium text-text-primary mb-1">Recommended Collection Sizes</h5>
                  <div className="bg-panel p-3 rounded-default">
                    <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-4">
                      <li><strong>Small collections:</strong> 100-500 posts, 10-50 comments per post</li>
                      <li><strong>Medium collections:</strong> 500-1000 posts, 50-100 comments per post</li>
                      <li><strong>Large collections:</strong> 1000+ posts, 100+ comments per post</li>
                    </ul>
                    <p className="text-text-secondary text-sm mt-2">
                      Start small and scale up based on your needs and analysis performance.
                    </p>
                  </div>
                </div>
                
                <div>
                  <h5 className="font-medium text-text-primary mb-1">Collection Strategy Tips</h5>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                    <li>Collect from multiple smaller subreddits rather than one large one</li>
                    <li>Use appropriate time periods (don't collect "all time" unless needed)</li>
                    <li>Set reasonable minimum upvote thresholds to filter quality content</li>
                    <li>Consider collecting in batches during off-peak hours</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Analysis Performance</h4>
              <div className="space-y-3">
                <div>
                  <h5 className="font-medium text-text-primary mb-1">Keyword Optimization</h5>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                    <li>Start with 3-5 core keywords, expand gradually</li>
                    <li>Avoid overly broad keywords that generate excessive matches</li>
                    <li>Use exact matching for common words to reduce processing time</li>
                    <li>Consider keyword relevance to your specific research question</li>
                  </ul>
                </div>
                
                <div>
                  <h5 className="font-medium text-text-primary mb-1">Context Window Settings</h5>
                  <p className="text-text-secondary text-sm mb-2">
                    Balance context quality with performance:
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                    <li><strong>50-100 words:</strong> Fast processing, basic context</li>
                    <li><strong>100-200 words:</strong> Balanced approach (recommended)</li>
                    <li><strong>200+ words:</strong> Rich context, slower processing</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        ),
        'Data Quality Guidelines': (
          <div className="space-y-4">
            <div>
              <h4 className="font-subsection text-text-primary mb-2">Ensuring High-Quality Results</h4>
              <p className="text-text-secondary mb-3">
                Good data quality is essential for meaningful business insights.
              </p>
              
              <div className="space-y-4">
                <div>
                  <h5 className="font-medium text-text-primary mb-2">Subreddit Selection Criteria</h5>
                  <div className="bg-panel p-3 rounded-default">
                    <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-4">
                      <li><strong>Relevance:</strong> Choose communities directly related to your research topic</li>
                      <li><strong>Activity level:</strong> Prefer subreddits with regular, recent posts</li>
                      <li><strong>User demographics:</strong> Consider if the community matches your target audience</li>
                      <li><strong>Discussion quality:</strong> Avoid overly promotional or low-quality communities</li>
                      <li><strong>Size balance:</strong> Mix of large and niche communities for comprehensive coverage</li>
                    </ul>
                  </div>
                </div>
                
                <div>
                  <h5 className="font-medium text-text-primary mb-2">Content Quality Filters</h5>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                    <li>Set minimum upvote thresholds to filter spam and low-quality content</li>
                    <li>Prefer posts with active comment discussions</li>
                    <li>Consider time periods that avoid major events that might skew results</li>
                    <li>Balance between fresh content (recent) and popular content (top rated)</li>
                  </ul>
                </div>
                
                <div>
                  <h5 className="font-medium text-text-primary mb-2">Validation Best Practices</h5>
                  <ul className="list-disc list-inside space-y-1 text-text-secondary ml-4">
                    <li>Always review sample discussions to validate AI insights</li>
                    <li>Cross-reference findings with multiple projects or keyword sets</li>
                    <li>Be aware of seasonal trends and external events affecting discussions</li>
                    <li>Consider the limitations of Reddit demographics (skews young, male, tech-savvy)</li>
                    <li>Supplement Reddit insights with other data sources when making business decisions</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="bg-warning bg-opacity-10 border border-warning border-opacity-30 p-4 rounded-default">
              <h4 className="font-medium text-text-primary mb-2">⚠️ Important Data Considerations</h4>
              <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-4">
                <li>Reddit represents a specific demographic and may not reflect the general population</li>
                <li>Discussion volume and sentiment can be influenced by external events, viral posts, or brigading</li>
                <li>Anonymous nature of Reddit means user motivations may not align with typical customer behavior</li>
                <li>Always validate insights with additional research methods before making major business decisions</li>
              </ul>
            </div>
          </div>
        ),
      },
    },
  ];

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Help Sections */}
      <div className="space-y-4">
        {helpSections.map((section) => (
          <CollapsibleSection
            key={section.id}
            title={section.title}
            defaultExpanded={section.defaultExpanded}
          >
            <div className="space-y-6">
              {Object.entries(section.content).map(([subTitle, content]) => (
                <div key={subTitle}>
                  <h3 className="font-section-header text-text-primary mb-3 pb-2 border-b border-border-secondary">
                    {subTitle}
                  </h3>
                  <div className="prose prose-sm max-w-none">
                    {content}
                  </div>
                </div>
              ))}
            </div>
          </CollapsibleSection>
        ))}
      </div>

      {/* Footer Links */}
      <div className="mt-8">
        <div className="border-t border-border-primary pt-4 mt-4">
          <div className="bg-panel p-4 rounded-default">
            <h4 className="font-medium text-text-primary mb-3">Additional Resources</h4>
            <div className="text-sm">
              <h5 className="font-medium text-text-primary mb-2">External Documentation</h5>
              <ul className="space-y-1">
                <li>
                  <a 
                    href="https://www.reddit.com/dev/api/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-accent hover:underline"
                  >
                    Reddit API Documentation
                  </a>
                </li>
                <li>
                  <a 
                    href="https://docs.anthropic.com/claude/docs" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-accent hover:underline"
                  >
                    Anthropic Claude API Docs
                  </a>
                </li>
                <li>
                  <a 
                    href="https://platform.openai.com/docs" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-accent hover:underline"
                  >
                    OpenAI API Documentation
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpContent;