"""
Analysis Summarization Service

Generates intelligent AI summaries of analytics results that explain what the data
reveals about user research topics. Focuses on actionable insights, unexpected
patterns, and trend analysis.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ...database import db


class AnalysisSummarizer:
    """
    Service for generating AI-powered summaries of analytics results.
    
    Takes structured analytics data and creates comprehensive insights that
    highlight key findings, trends, and unexpected patterns in the data.
    """
    
    def __init__(self):
        pass
    
    def generate_summary(self, session_id: str, user_query: str = None) -> Dict[str, Any]:
        """
        Generate an AI summary for an analysis session.
        
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
        
        # Get trends data for top keywords (to understand temporal patterns)
        top_keywords = [kw['keyword'] for kw in session_results['keywords_data'][:5]]
        trends_data = analytics_engine.get_trends(session_id, top_keywords, 'daily')
        
        # Get relationships for top keyword (to understand co-occurrences)
        relationships_data = None
        if top_keywords:
            relationships_data = analytics_engine.get_relationships(session_id, top_keywords[0])
        
        # Prepare structured data for the LLM
        analysis_data = self._prepare_analysis_data(
            session_results, trends_data, relationships_data
        )
        
        # Generate summary using LLM
        summary_content = self._generate_llm_summary(analysis_data, user_query)
        
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
                'generated_at': datetime.utcnow().isoformat()
            }
        }
    
    def _prepare_analysis_data(self, session_results: Dict[str, Any], 
                              trends_data: Dict[str, Any], 
                              relationships_data: Dict[str, Any]) -> str:
        """
        Prepare structured analysis data for LLM consumption.
        
        Args:
            session_results: Complete session results from analytics engine
            trends_data: Trends analysis data
            relationships_data: Keyword relationships data
        
        Returns:
            Formatted string with analysis data
        """
        # Extract key information
        total_mentions = session_results.get('total_mentions', 0)
        avg_sentiment = session_results.get('avg_sentiment', 0.0)
        keywords_analyzed = len(session_results.get('keywords', []))
        collections_count = len(session_results.get('collection_ids', []))
        
        # Keywords breakdown
        keywords_data = session_results.get('keywords_data', [])
        
        # Build structured data summary
        data_summary = f"""ANALYSIS DATA SUMMARY
===================================

OVERVIEW:
- Total mentions found: {total_mentions:,}
- Keywords analyzed: {keywords_analyzed}
- Collections analyzed: {collections_count}
- Overall sentiment: {avg_sentiment:+.4f} (scale: -1.0 to +1.0)

TOP KEYWORDS BY MENTIONS:
"""
        
        # Add top keywords by mentions
        top_by_mentions = sorted(keywords_data, key=lambda x: x['total_mentions'], reverse=True)[:10]
        for i, kw in enumerate(top_by_mentions, 1):
            data_summary += f"{i}. '{kw['keyword']}': {kw['total_mentions']} mentions, {kw['avg_sentiment']:+.3f} sentiment\n"
        
        # Add sentiment distribution
        data_summary += "\nSENTIMENT DISTRIBUTION:\n"
        positive_kw = [kw for kw in keywords_data if kw['avg_sentiment'] > 0.1]
        negative_kw = [kw for kw in keywords_data if kw['avg_sentiment'] < -0.1]
        neutral_kw = [kw for kw in keywords_data if -0.1 <= kw['avg_sentiment'] <= 0.1]
        
        data_summary += f"- Positive keywords: {len(positive_kw)}/{len(keywords_data)}\n"
        data_summary += f"- Negative keywords: {len(negative_kw)}/{len(keywords_data)}\n"
        data_summary += f"- Neutral keywords: {len(neutral_kw)}/{len(keywords_data)}\n"
        
        # Add most positive and negative keywords
        if positive_kw:
            most_positive = max(positive_kw, key=lambda x: x['avg_sentiment'])
            data_summary += f"- Most positive: '{most_positive['keyword']}' ({most_positive['avg_sentiment']:+.3f})\n"
        
        if negative_kw:
            most_negative = min(negative_kw, key=lambda x: x['avg_sentiment'])
            data_summary += f"- Most negative: '{most_negative['keyword']}' ({most_negative['avg_sentiment']:+.3f})\n"
        
        # Add trends information if available
        if trends_data and trends_data.get('trends'):
            data_summary += "\nTIME TRENDS:\n"
            for keyword, time_data in trends_data['trends'].items():
                if time_data:
                    dates = sorted(time_data.keys())
                    if len(dates) > 1:
                        first_period = time_data[dates[0]]
                        last_period = time_data[dates[-1]]
                        trend_direction = "📈 rising" if last_period['mentions'] > first_period['mentions'] else "📉 declining" if last_period['mentions'] < first_period['mentions'] else "→ stable"
                        data_summary += f"- '{keyword}': {trend_direction} ({first_period['mentions']} → {last_period['mentions']} mentions)\n"
        
        # Add relationships if available
        if relationships_data and relationships_data.get('relationships'):
            target_keyword = relationships_data['target_keyword']
            relationships = relationships_data['relationships'][:5]  # Top 5 relationships
            if relationships:
                data_summary += f"\nTOP CO-OCCURRENCES WITH '{target_keyword}':\n"
                for rel in relationships:
                    data_summary += f"- '{rel['keyword']}': {rel['cooccurrence_count']} co-occurrences\n"
        
        return data_summary
    
    def _generate_llm_summary(self, analysis_data: str, user_query: str = None) -> Dict[str, Any]:
        """
        Generate summary using LLM.
        
        Args:
            analysis_data: Prepared analysis data
            user_query: Optional user's original research description
        
        Returns:
            Dictionary with LLM response details
        """
        # Get LLM provider
        from ...llm import get_llm_provider
        
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        # Build prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(analysis_data, user_query)
        
        # Generate summary
        response = provider.generate(user_prompt, system_prompt)
        
        return {
            'content': response.content,
            'provider': response.provider,
            'model': response.model,
            'tokens_used': response.tokens_used,
            'cost_estimate': response.cost_estimate
        }
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for summary generation."""
        return """You are an expert data analyst specializing in social media sentiment analysis and trend identification. Your role is to analyze Reddit discussion data and provide comprehensive, actionable insights.

Your analysis should be:
- DATA-DRIVEN: Base conclusions on the actual numbers and patterns in the data
- INSIGHTFUL: Highlight unexpected patterns, anomalies, and significant trends
- ACTIONABLE: Provide insights that help understand what the data reveals
- OBJECTIVE: Let the data speak for itself without making unfounded assumptions

Structure your analysis to cover:
1. Overall findings and key takeaways
2. Sentiment patterns and what drives them
3. Notable trends over time (if available)
4. Significant keyword relationships and co-occurrences
5. Unexpected or surprising patterns in the data
6. What the keyword choices and discussion patterns suggest about the research focus

Write in a professional, analytical tone. Use specific numbers and percentages from the data. Avoid speculation beyond what the data supports."""
    
    def _build_user_prompt(self, analysis_data: str, user_query: str = None) -> str:
        """Build the user prompt with analysis data."""
        prompt = f"""Analyze the following Reddit discussion data and provide a comprehensive summary of key insights and findings.

{analysis_data}"""
        
        if user_query:
            prompt += f"""

CONTEXT: The user described their research interest as: "{user_query}"

Consider this context when interpreting the significance of the findings, but base your analysis primarily on what the data reveals."""
        
        prompt += """

Please provide a comprehensive analysis that covers:
1. The most significant findings from this data
2. Sentiment patterns and what they indicate
3. Temporal trends and patterns over time
4. Keyword relationships and co-occurrences
5. Any surprising or unexpected discoveries
6. What these discussion patterns reveal about the topic being analyzed

Focus on actionable insights and concrete observations from the data."""
        
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
                    'generated_at': datetime.fromtimestamp(summary.generated_at).isoformat()
                }
            }
        return None
    
    def regenerate_summary(self, session_id: str, user_query: str = None) -> Dict[str, Any]:
        """
        Regenerate summary for an existing session.
        
        Args:
            session_id: Analysis session ID
            user_query: Optional updated research description
        
        Returns:
            Dictionary with new summary results
        """
        # If no user_query provided, try to get the existing one
        if user_query is None:
            existing_summary = self.get_existing_summary(session_id)
            if existing_summary:
                user_query = existing_summary['user_query']
        
        # Generate new summary (this will overwrite the existing one)
        return self.generate_summary(session_id, user_query)


# Global summarizer instance
analysis_summarizer = AnalysisSummarizer()