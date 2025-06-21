"""
Analysis Summarization Service

Enhanced summarization that combines analytics data with actual Reddit discussions
to provide comprehensive, actionable insights with real examples.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ...database import db
from .rag_engine import rag_engine
from .content_formatter import content_formatter


class AnalysisSummarizer:
    """
    Enhanced service for generating AI-powered summaries that combine
    structured analytics with real Reddit discussion examples.
    """
    
    def __init__(self):
        pass
    
    def generate_summary(self, session_id: str, user_query: str = None) -> Dict[str, Any]:
        """
        Generate an enhanced AI summary combining analytics data with real examples.
        
        Args:
            session_id: Analysis session ID to summarize
            user_query: Optional user's original research description
        
        Returns:
            Dictionary with summary results and metadata
        """
        # Get analysis session and results
        analysis_session = db.get_analysis_session(session_id)
        if not analysis_session:
            raise ValueError(f"Analysis session not found: {session_id}")
        
        if analysis_session.status != 'completed':
            raise ValueError(f"Analysis session not completed: {analysis_session.status}")
        
        # Import analytics engine to get comprehensive results
        from ...analytics import analytics_engine
        
        # Get comprehensive session results
        session_results = analytics_engine.get_session_results(session_id)
        
        # Get trends data for top keywords
        top_keywords = [kw['keyword'] for kw in session_results['keywords_data'][:5]]
        trends_data = analytics_engine.get_trends(session_id, top_keywords, 'daily')
        
        # Get relationships for top keyword
        relationships_data = None
        if top_keywords:
            relationships_data = analytics_engine.get_relationships(session_id, top_keywords[0])
        
        # Get real discussion examples that illustrate the findings
        collection_ids = json.loads(analysis_session.collection_ids)
        discussion_examples = rag_engine.get_representative_examples(
            collection_ids, top_keywords, limit=5
        )
        
        # Prepare enhanced analysis data with examples
        analysis_data = self._prepare_enhanced_analysis_data(
            session_results, trends_data, relationships_data, discussion_examples
        )
        
        # Generate summary using LLM with both analytics and examples
        summary_content = self._generate_enhanced_llm_summary(
            analysis_data, user_query, discussion_examples
        )
        
        # Save summary to database
        db.save_llm_summary(
            session_id=session_id,
            user_query=user_query or "",
            summary_text=summary_content['content'],
            provider_used=summary_content['provider'],
            model_used=summary_content['model'],
            tokens_used=summary_content['tokens_used'],
            cost_estimate=summary_content['cost_estimate']
        )
        
        return {
            'session_id': session_id,
            'summary': summary_content['content'],
            'metadata': {
                'provider': summary_content['provider'],
                'model': summary_content['model'],
                'tokens_used': summary_content['tokens_used'],
                'cost_estimate': summary_content['cost_estimate'],
                'generated_at': datetime.utcnow().isoformat(),
                'examples_used': len(discussion_examples),
                'analytics_included': True
            }
        }
    
    def _prepare_enhanced_analysis_data(self, session_results: Dict[str, Any], 
                                      trends_data: Dict[str, Any], 
                                      relationships_data: Dict[str, Any],
                                      discussion_examples: List[Dict[str, Any]]) -> str:
        """
        Prepare enhanced analysis data that combines analytics with real examples.
        
        Args:
            session_results: Complete session results from analytics engine
            trends_data: Trends analysis data
            relationships_data: Keyword relationships data
            discussion_examples: Actual Reddit discussion examples
        
        Returns:
            Formatted string with enhanced analysis data
        """
        # Start with basic analytics data
        data_summary = self._build_analytics_summary(session_results, trends_data, relationships_data)
        
        # Add actual discussion examples
        if discussion_examples:
            data_summary += "\n\n" + "="*60
            data_summary += "\nREAL DISCUSSION EXAMPLES:"
            data_summary += "\n" + "="*60
            data_summary += "\n\nHere are actual Reddit discussions that illustrate these patterns:\n"
            
            for i, example in enumerate(discussion_examples, 1):
                post_title = example.get('discussion_data', {}).get('post', {}).get('title', 'Unknown Post')
                subreddit = example.get('discussion_data', {}).get('post', {}).get('subreddit', 'unknown')
                comment_count = example.get('comment_count', 0)
                
                data_summary += f"\nEXAMPLE {i}: r/{subreddit} - {post_title}\n"
                data_summary += f"({comment_count} comments)\n"
                data_summary += "-" * 40 + "\n"
                
                # Include formatted discussion text (truncated for summary)
                formatted_text = example.get('formatted_text', '')
                if len(formatted_text) > 1000:
                    formatted_text = formatted_text[:1000] + "\n[... discussion continues ...]"
                
                data_summary += formatted_text + "\n"
        
        return data_summary
    
    def _build_analytics_summary(self, session_results: Dict[str, Any],
                                trends_data: Dict[str, Any], 
                                relationships_data: Dict[str, Any]) -> str:
        """Build the analytics portion of the summary."""
        # Extract key information
        total_mentions = session_results.get('total_mentions', 0)
        avg_sentiment = session_results.get('avg_sentiment', 0.0)
        keywords_analyzed = len(session_results.get('keywords', []))
        collections_count = len(session_results.get('collection_ids', []))
        
        # Keywords breakdown
        keywords_data = session_results.get('keywords_data', [])
        
        # Build structured data summary
        data_summary = f"""COMPREHENSIVE ANALYSIS SUMMARY
====================================

OVERVIEW:
- Total keyword mentions found: {total_mentions:,}
- Keywords analyzed: {keywords_analyzed}
- Collections analyzed: {collections_count}
- Overall sentiment: {avg_sentiment:+.4f} (scale: -1.0 to +1.0)

TOP KEYWORDS BY MENTIONS:
"""
        
        # Add top keywords by mentions
        top_by_mentions = sorted(keywords_data, key=lambda x: x['total_mentions'], reverse=True)[:10]
        for i, kw in enumerate(top_by_mentions, 1):
            data_summary += f"{i}. '{kw['keyword']}': {kw['total_mentions']} mentions, {kw['avg_sentiment']:+.3f} sentiment\n"
        
        # Add sentiment analysis
        data_summary += "\nSENTIMENT PATTERNS:\n"
        positive_kw = [kw for kw in keywords_data if kw['avg_sentiment'] > 0.1]
        negative_kw = [kw for kw in keywords_data if kw['avg_sentiment'] < -0.1]
        neutral_kw = [kw for kw in keywords_data if -0.1 <= kw['avg_sentiment'] <= 0.1]
        
        data_summary += f"- Positive keywords: {len(positive_kw)}/{len(keywords_data)} "
        data_summary += f"({100*len(positive_kw)/len(keywords_data):.1f}%)\n"
        data_summary += f"- Negative keywords: {len(negative_kw)}/{len(keywords_data)} "
        data_summary += f"({100*len(negative_kw)/len(keywords_data):.1f}%)\n"
        data_summary += f"- Neutral keywords: {len(neutral_kw)}/{len(keywords_data)} "
        data_summary += f"({100*len(neutral_kw)/len(keywords_data):.1f}%)\n"
        
        # Add most positive and negative keywords
        if positive_kw:
            most_positive = max(positive_kw, key=lambda x: x['avg_sentiment'])
            data_summary += f"- Most positive: '{most_positive['keyword']}' ({most_positive['avg_sentiment']:+.3f}, "
            data_summary += f"{most_positive['total_mentions']} mentions)\n"
        
        if negative_kw:
            most_negative = min(negative_kw, key=lambda x: x['avg_sentiment'])
            data_summary += f"- Most negative: '{most_negative['keyword']}' ({most_negative['avg_sentiment']:+.3f}, "
            data_summary += f"{most_negative['total_mentions']} mentions)\n"
        
        # Add engagement patterns
        data_summary += "\nENGAGEMENT PATTERNS:\n"
        high_engagement = [kw for kw in keywords_data if kw['total_mentions'] > total_mentions / len(keywords_data)]
        data_summary += f"- High-discussion keywords: {len(high_engagement)} keywords generate above-average discussion\n"
        
        # Add temporal trends if available
        if trends_data and trends_data.get('trends'):
            data_summary += "\nTEMPORAL TRENDS:\n"
            for keyword, time_data in list(trends_data['trends'].items())[:5]:  # Top 5 trending keywords
                if time_data:
                    dates = sorted(time_data.keys())
                    if len(dates) > 1:
                        first_period = time_data[dates[0]]
                        last_period = time_data[dates[-1]]
                        if last_period['mentions'] > first_period['mentions']:
                            trend_direction = "📈 rising"
                            trend_pct = ((last_period['mentions'] - first_period['mentions']) / 
                                       max(first_period['mentions'], 1)) * 100
                        elif last_period['mentions'] < first_period['mentions']:
                            trend_direction = "📉 declining"
                            trend_pct = ((first_period['mentions'] - last_period['mentions']) / 
                                       max(first_period['mentions'], 1)) * 100
                        else:
                            trend_direction = "→ stable"
                            trend_pct = 0
                        
                        data_summary += f"- '{keyword}': {trend_direction} "
                        if trend_pct > 0:
                            data_summary += f"({trend_pct:.0f}% change, "
                        else:
                            data_summary += f"("
                        data_summary += f"{first_period['mentions']} → {last_period['mentions']} mentions)\n"
        
        # Add keyword relationships if available
        if relationships_data and relationships_data.get('relationships'):
            target_keyword = relationships_data['target_keyword']
            relationships = relationships_data['relationships'][:5]  # Top 5 relationships
            if relationships:
                data_summary += f"\nKEYWORD CO-OCCURRENCES WITH '{target_keyword}':\n"
                for rel in relationships:
                    data_summary += f"- '{rel['keyword']}': appears together {rel['cooccurrence_count']} times "
                    data_summary += f"({rel['in_posts']} posts, {rel['in_comments']} comments)\n"
        
        return data_summary
    
    def _generate_enhanced_llm_summary(self, analysis_data: str, user_query: str = None,
                                     discussion_examples: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate enhanced summary using LLM with both analytics and examples.
        
        Args:
            analysis_data: Complete analysis data with examples
            user_query: Optional user's original research description
            discussion_examples: Actual Reddit discussion examples
        
        Returns:
            Dictionary with LLM response details
        """
        # Get LLM provider
        from ...llm import get_llm_provider
        
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        # Build enhanced prompt
        system_prompt = self._build_enhanced_system_prompt()
        user_prompt = self._build_enhanced_user_prompt(analysis_data, user_query, discussion_examples)
        
        # Generate summary
        response = provider.generate(user_prompt, system_prompt)
        
        return {
            'content': response.content,
            'provider': response.provider,
            'model': response.model,
            'tokens_used': response.tokens_used,
            'cost_estimate': response.cost_estimate
        }
    
    def _build_enhanced_system_prompt(self) -> str:
        """Build enhanced system prompt for summary generation with examples."""
        return """You are an expert data analyst specializing in social media sentiment analysis and Reddit discussion patterns. You analyze both quantitative data and qualitative discussions to provide comprehensive insights.

Your analysis should be:
- COMPREHENSIVE: Combine statistical patterns with real conversation examples
- EVIDENCE-BASED: Support findings with both numbers and actual quotes from discussions
- CONTEXTUAL: Understand Reddit's conversational culture and community dynamics
- ACTIONABLE: Provide insights that help understand what people actually think and feel
- BALANCED: Present both statistical trends and individual perspectives from real users

Structure your analysis to cover:
1. KEY FINDINGS: Most significant discoveries from both data and discussions
2. SENTIMENT LANDSCAPE: What the numbers show AND what people are actually saying
3. DISCUSSION PATTERNS: How conversations unfold, what topics generate engagement
4. COMMUNITY INSIGHTS: What the discussions reveal about user perspectives and concerns
5. NOTABLE EXAMPLES: Specific quotes or discussions that illustrate key patterns
6. IMPLICATIONS: What these patterns suggest about the topic being researched

When referencing actual discussions:
- Quote naturally and contextually
- Note voting patterns and community response
- Highlight both consensus and disagreement
- Reference specific posts/comments when illustrative

Write in a professional analytical tone that bridges quantitative insights with qualitative understanding of human conversations."""
    
    def _build_enhanced_user_prompt(self, analysis_data: str, user_query: str = None,
                                  discussion_examples: List[Dict[str, Any]] = None) -> str:
        """Build enhanced user prompt with both analytics and examples."""
        prompt = f"""Analyze this comprehensive Reddit data that includes both statistical analysis and actual discussion examples.

{analysis_data}"""
        
        if user_query:
            prompt += f"""

ORIGINAL RESEARCH CONTEXT: The user described their research interest as: "{user_query}"

Consider this context when interpreting the significance of the findings, but base your analysis primarily on what the data and discussions reveal."""
        
        prompt += """

Please provide a comprehensive analysis that covers:

1. **EXECUTIVE SUMMARY**: The most significant findings from both the statistical data and actual discussions

2. **SENTIMENT & OPINION LANDSCAPE**: What the quantitative sentiment scores show AND what people are actually expressing in their conversations

3. **DISCUSSION DYNAMICS**: How conversations unfold around these topics - what generates engagement, agreement, or controversy

4. **KEY INSIGHTS FROM REAL CONVERSATIONS**: Specific examples from the actual Reddit discussions that illustrate important patterns or perspectives

5. **TRENDING PATTERNS**: What's gaining or losing momentum in the discussions over time

6. **COMMUNITY PERSPECTIVES**: What these discussions reveal about how the Reddit community views these topics

7. **ACTIONABLE TAKEAWAYS**: What someone researching this topic should understand based on both the data patterns and real user conversations

Focus on bridging the quantitative findings with the qualitative insights from actual human discussions. Use specific examples and quotes from the real Reddit conversations to illustrate your points."""
        
        return prompt
    
    def get_existing_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get existing summary for a session if it exists.
        
        Args:
            session_id: Analysis session ID
        
        Returns:
            Summary data or None if no summary exists
        """
        summary = db.get_llm_summary(session_id)
        if summary:
            return {
                'session_id': session_id,
                'summary': summary.summary_text,
                'user_query': summary.user_query,
                'metadata': {
                    'provider': summary.provider_used,
                    'model': summary.model_used,
                    'tokens_used': summary.tokens_used,
                    'cost_estimate': summary.cost_estimate,
                    'generated_at': datetime.fromtimestamp(summary.generated_at).isoformat(),
                    'analytics_included': True,
                    'examples_included': True
                }
            }
        return None
    
    def regenerate_summary(self, session_id: str, user_query: str = None) -> Dict[str, Any]:
        """
        Regenerate enhanced summary for an existing session.
        
        Args:
            session_id: Analysis session ID
            user_query: Optional updated research description
        
        Returns:
            Dictionary with new enhanced summary results
        """
        # If no user_query provided, try to get the existing one
        if user_query is None:
            existing_summary = self.get_existing_summary(session_id)
            if existing_summary:
                user_query = existing_summary['user_query']
        
        # Generate new enhanced summary (this will overwrite the existing one)
        return self.generate_summary(session_id, user_query)


# Global summarizer instance
analysis_summarizer = AnalysisSummarizer()