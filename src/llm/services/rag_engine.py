"""
Enhanced RAG (Retrieval-Augmented Generation) Engine

Enhanced RAG engine with intelligent fallbacks and graceful handling of keywords
not found in analysis data. Provides comprehensive responses regardless of keyword availability.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from .search_engine import SearchEngineFactory, SearchResult
from .discussion_builder import discussion_builder
from .content_formatter import content_formatter
from .analytics_search_engine import analytics_search_engine, AnalyticsSearchResult
from .query_classifier import query_classifier
from ...llm import get_llm_provider
from ...database import db, Post, Comment


@dataclass
class RAGResponse:
    """Enhanced response from RAG engine with analytics awareness and fallback info."""
    answer: str                     # AI-generated answer
    sources: List[Dict[str, Any]]   # Source attributions with full context
    analytics_insights: Dict[str, Any]  # Analytics data used in response
    search_type: str               # Search method used
    search_results_count: int      # Number of search results found
    discussions_used: int          # Number of complete discussions used
    tokens_used: int               # LLM tokens used
    cost_estimate: float           # Cost estimate for this query
    query_classification: Dict[str, Any]  # How the query was classified
    fallback_info: Dict[str, Any] = None  # Information about fallbacks used


class RAGEngine:
    """
    Enhanced RAG engine with intelligent keyword extraction, graceful fallbacks,
    and comprehensive responses regardless of analytics data availability.
    """
    
    def __init__(self):
        self.max_discussions = 3      # Maximum complete discussions to include
        self.max_context_length = 8000  # Character limit for context
    
    def answer_question(self, question: str, collection_ids: List[str], 
                    search_type: str = 'auto', 
                    max_results: int = 5,
                    analysis_session_id: str = None) -> RAGResponse:
        """
        Answer a question using enhanced RAG with intelligent keyword extraction and fallbacks.
        
        Args:
            question: User's question
            collection_ids: Collection IDs to search in
            search_type: 'auto', 'keyword', 'local_semantic', 'cloud_semantic', or 'analytics_driven'
            max_results: Maximum search results to process
        
        Returns:
            RAGResponse with comprehensive answer and fallback information
        """
        # Get available keywords for context
        available_keywords = self._get_available_keywords(collection_ids, analysis_session_id)

        # Classify the query intelligently
        classification = query_classifier.classify_query(question, available_keywords)
        
        # Get enhanced search strategy
        search_strategy = query_classifier.get_enhanced_search_strategy(classification)
        

        # Handle different approaches with graceful fallbacks
        if classification.query_type == 'command':
            return self._handle_command_query(question, classification, collection_ids)
        
        elif classification.suggested_approach in ['analytics_driven_search', 'analytics_with_examples']:
            return self._handle_analytics_query_enhanced(
                question, classification, collection_ids, max_results, search_strategy, analysis_session_id
            )
        
        elif classification.suggested_approach in ['analytics_with_fallback', 'hybrid_search_with_fallback']:
            return self._handle_hybrid_with_fallback(
                question, classification, collection_ids, search_type, max_results, search_strategy
            )
        
        elif classification.suggested_approach in ['discussion_search_with_keywords', 'general_discussion_search']:
            return self._handle_discussion_query_enhanced(
                question, classification, collection_ids, search_type, max_results, search_strategy
            )
        
        else:
            # Intelligent search - let the system figure out the best approach
            return self._handle_intelligent_search(
                question, classification, collection_ids, search_type, max_results, search_strategy
            )
    
    def _handle_analytics_query_enhanced(self, question: str, classification, 
                                        collection_ids: List[str], max_results: int,
                                        search_strategy: Dict[str, Any], 
                                        analysis_session_id: str = None) -> RAGResponse:
        """Handle analytics queries with enhanced fallback capabilities."""
        analytics_insights = {}
        search_results = []
        fallback_info = {}
        
        target_keywords = classification.target_keywords
        
        if target_keywords:
            analytics_keywords_found = []
            fallback_keywords = []
            
            # Try analytics for each keyword
            for keyword in target_keywords[:3]:
                keyword_overview = analytics_search_engine.get_keyword_overview(keyword, collection_ids, analysis_session_id)

                if keyword_overview.get('found'):
                    analytics_keywords_found.append(keyword)
                    analytics_insights[keyword] = keyword_overview
                    
                    # Get representative examples using analytics
                    keyword_results = analytics_search_engine.search_by_keyword_analytics(
                        keyword, collection_ids, limit=max_results // len(target_keywords) + 1
                    )
                    search_results.extend(keyword_results)
                else:
                    fallback_keywords.append(keyword)
            
            # Handle fallback keywords using discussion search
            if fallback_keywords:
                fallback_info['keywords_not_in_analysis'] = fallback_keywords
                fallback_info['fallback_method'] = 'discussion_search'
                
                # Use traditional search for keywords not in analytics
                for keyword in fallback_keywords:
                    fallback_results = self._search_discussions_for_keyword(
                        keyword, collection_ids, max_results // len(fallback_keywords) + 1
                    )
                    if fallback_results:
                        # Convert to analytics-style results for consistent handling
                        converted_results = self._convert_traditional_to_analytics_style(
                            fallback_results, keyword
                        )
                        search_results.extend(converted_results)
                        
                        fallback_info[f'discussions_found_for_{keyword}'] = len(fallback_results)
        
        else:
            # No specific keywords - provide general analytics overview
            analytics_insights['overview'] = self._get_general_analytics_overview(collection_ids)
            
            # Get insights-based examples
            insight_results = analytics_search_engine.search_by_analytics_insights(
                collection_ids, 'most_frequent', limit=max_results
            )
            search_results.extend(insight_results)
        
        # Enrich with discussion contexts
        search_results = analytics_search_engine.enrich_with_discussion_context(search_results)
        
        # Generate enhanced response
        llm_response = self._generate_enhanced_analytics_answer(
            question, analytics_insights, search_results, fallback_info
        )
        
        # Format sources
        sources = self._format_analytics_sources(search_results, analytics_insights)

        return RAGResponse(
            answer=llm_response['content'],
            sources=sources,
            analytics_insights=analytics_insights,
            search_type='analytics_with_fallback',
            search_results_count=len(search_results),
            discussions_used=len([r for r in search_results if r.discussion_context]),
            tokens_used=llm_response['tokens_used'],
            cost_estimate=llm_response['cost_estimate'],
            query_classification={
                'type': classification.query_type,
                'confidence': classification.confidence,
                'approach': classification.suggested_approach,
                'keywords_extracted': classification.target_keywords
            },
            fallback_info=fallback_info
        )
    
    def _handle_discussion_query_enhanced(self, question: str, classification,
                                        collection_ids: List[str], search_type: str, 
                                        max_results: int, search_strategy: Dict[str, Any]) -> RAGResponse:
        """Handle discussion queries with enhanced keyword understanding."""
        search_results = []
        analytics_insights = {}
        fallback_info = {}
        
        target_keywords = classification.target_keywords
        
        # Build search query
        if target_keywords:
            # Use the most important keywords for search
            search_query = " ".join(target_keywords[:2])  # Top 2 keywords
            fallback_info['search_keywords_used'] = target_keywords[:2]
        else:
            # Use the original question
            search_query = question
        
        # Use appropriate search method
        if search_type == 'auto':
            search_type = 'keyword'  # Default for discussion queries
        
        try:
            search_engine = SearchEngineFactory.create_engine(search_type)
            traditional_results = search_engine.search(search_query, collection_ids, limit=max_results)
        except Exception as e:
            # Fallback to keyword search if other methods fail
            fallback_info['search_fallback'] = f"Fell back to keyword search due to: {str(e)}"
            search_engine = SearchEngineFactory.create_engine('keyword')
            traditional_results = search_engine.search(search_query, collection_ids, limit=max_results)
        
        # Get minimal analytics context if keywords are available
        if target_keywords:
            available_keywords = self._get_available_keywords(collection_ids)
            for keyword in target_keywords:
                if keyword in available_keywords:
                    keyword_overview = analytics_search_engine.get_keyword_overview(keyword, collection_ids)
                    if keyword_overview.get('found'):
                        analytics_insights[keyword] = {
                            'total_mentions': keyword_overview['total_mentions'],
                            'avg_sentiment': keyword_overview['avg_sentiment'],
                            'context': 'minimal_for_discussion_query'
                        }
        
        # Build discussion contexts
        discussions = self._build_discussion_contexts_from_traditional(traditional_results)
        
        # Generate discussion-focused response with analytics context
        llm_response = self._generate_enhanced_discussion_answer(
            question, discussions, analytics_insights, fallback_info, target_keywords
        )
        
        # Format sources
        sources = self._format_traditional_sources(traditional_results, discussions)
        
        return RAGResponse(
            answer=llm_response['content'],
            sources=sources,
            analytics_insights=analytics_insights,
            search_type=search_type,
            search_results_count=len(traditional_results),
            discussions_used=len(discussions),
            tokens_used=llm_response['tokens_used'],
            cost_estimate=llm_response['cost_estimate'],
            query_classification={
                'type': classification.query_type,
                'confidence': classification.confidence,
                'approach': classification.suggested_approach,
                'keywords_extracted': classification.target_keywords
            },
            fallback_info=fallback_info
        )
    
    def _handle_hybrid_with_fallback(self, question: str, classification,
                                   collection_ids: List[str], search_type: str, 
                                   max_results: int, search_strategy: Dict[str, Any]) -> RAGResponse:
        """Handle hybrid queries with comprehensive fallback strategies."""
        analytics_insights = {}
        analytics_results = []
        traditional_results = []
        fallback_info = {}
        
        target_keywords = classification.target_keywords
        
        # Try analytics first
        if target_keywords:
            analytics_keywords = []
            discussion_keywords = []
            
            for keyword in target_keywords[:2]:
                keyword_overview = analytics_search_engine.get_keyword_overview(keyword, collection_ids)
                if keyword_overview.get('found'):
                    analytics_keywords.append(keyword)
                    analytics_insights[keyword] = keyword_overview
                    
                    # Get analytics-driven examples
                    keyword_results = analytics_search_engine.search_by_keyword_analytics(
                        keyword, collection_ids, limit=max_results // 2
                    )
                    analytics_results.extend(keyword_results)
                else:
                    discussion_keywords.append(keyword)
            
            fallback_info['analytics_keywords'] = analytics_keywords
            fallback_info['fallback_keywords'] = discussion_keywords
        
        # Get discussion examples using best available method
        search_query = question
        if target_keywords:
            search_query = " ".join(target_keywords)
        
        if search_type == 'auto':
            search_type = 'keyword'
        
        try:
            search_engine = SearchEngineFactory.create_engine(search_type)
            traditional_results = search_engine.search(search_query, collection_ids, limit=max_results // 2)
        except Exception as e:
            fallback_info['discussion_search_fallback'] = str(e)
            search_engine = SearchEngineFactory.create_engine('keyword')
            traditional_results = search_engine.search(search_query, collection_ids, limit=max_results // 2)
        
        # Combine and enrich results
        discussions = self._build_discussion_contexts_from_traditional(traditional_results)
        analytics_results = analytics_search_engine.enrich_with_discussion_context(analytics_results)
        
        # Generate comprehensive hybrid response
        llm_response = self._generate_enhanced_hybrid_answer(
            question, analytics_insights, analytics_results, discussions, fallback_info
        )
        
        # Format combined sources
        sources = self._format_hybrid_sources(analytics_results, traditional_results, discussions)
        
        return RAGResponse(
            answer=llm_response['content'],
            sources=sources,
            analytics_insights=analytics_insights,
            search_type=f"hybrid_{search_type}",
            search_results_count=len(analytics_results) + len(traditional_results),
            discussions_used=len(analytics_results) + len(discussions),
            tokens_used=llm_response['tokens_used'],
            cost_estimate=llm_response['cost_estimate'],
            query_classification={
                'type': classification.query_type,
                'confidence': classification.confidence,
                'approach': classification.suggested_approach,
                'keywords_extracted': classification.target_keywords
            },
            fallback_info=fallback_info
        )
    
    def _handle_intelligent_search(self, question: str, classification,
                                 collection_ids: List[str], search_type: str, 
                                 max_results: int, search_strategy: Dict[str, Any]) -> RAGResponse:
        """Handle queries with fully intelligent search strategy selection."""
        # Try the best available search method based on what's available
        try:
            results = SearchEngineFactory.search_with_best_available(
                question, collection_ids, limit=max_results, 
                prefer_analytics=classification.query_type in ['analytics', 'hybrid']
            )
        except Exception:
            # Ultimate fallback - use keyword search
            search_engine = SearchEngineFactory.create_engine('keyword')
            results = search_engine.search(question, collection_ids, limit=max_results)
        
        # Build discussion contexts
        discussions = self._build_discussion_contexts_from_traditional(results)
        
        # Get any available analytics context
        analytics_insights = {}
        if classification.target_keywords:
            available_keywords = self._get_available_keywords(collection_ids)
            for keyword in classification.target_keywords:
                if keyword in available_keywords:
                    keyword_overview = analytics_search_engine.get_keyword_overview(keyword, collection_ids)
                    if keyword_overview.get('found'):
                        analytics_insights[keyword] = keyword_overview
        
        # Generate intelligent response
        llm_response = self._generate_intelligent_answer(
            question, discussions, analytics_insights, classification
        )
        
        # Format sources
        sources = self._format_traditional_sources(results, discussions)
        
        return RAGResponse(
            answer=llm_response['content'],
            sources=sources,
            analytics_insights=analytics_insights,
            search_type='intelligent_auto',
            search_results_count=len(results),
            discussions_used=len(discussions),
            tokens_used=llm_response['tokens_used'],
            cost_estimate=llm_response['cost_estimate'],
            query_classification={
                'type': classification.query_type,
                'confidence': classification.confidence,
                'approach': 'intelligent_search',
                'keywords_extracted': classification.target_keywords
            },
            fallback_info={'method': 'intelligent_auto_selection'}
        )
    
    def _search_discussions_for_keyword(self, keyword: str, collection_ids: List[str], 
                                      limit: int) -> List[SearchResult]:
        """Search for discussions containing a specific keyword."""
        try:
            # Try semantic search first if available
            search_engine = SearchEngineFactory.create_engine('cloud_semantic')
            return search_engine.search(keyword, collection_ids, limit)
        except:
            try:
                search_engine = SearchEngineFactory.create_engine('local_semantic')
                return search_engine.search(keyword, collection_ids, limit)
            except:
                # Fallback to keyword search
                search_engine = SearchEngineFactory.create_engine('keyword')
                return search_engine.search(keyword, collection_ids, limit)
    
    def _convert_traditional_to_analytics_style(self, traditional_results: List[SearchResult], 
                                              keyword: str) -> List[AnalyticsSearchResult]:
        """Convert traditional search results to analytics-style results for consistent handling."""
        analytics_results = []
        
        for result in traditional_results:
            # Create a mock analytics result
            analytics_result = AnalyticsSearchResult(
                content_id=result.content_id,
                content_type=result.content_type,
                collection_id=result.collection_id,
                keyword=keyword,
                mention_context=result.content_text[:200] + "..." if len(result.content_text) > 200 else result.content_text,
                sentiment_score=0.0,  # No sentiment analysis for fallback results
                analytics_metadata={
                    'source': 'fallback_search',
                    'relevance_score': result.relevance_score,
                    'original_metadata': result.metadata,
                    'note': f"Found via discussion search ('{keyword}' not in analysis data)"
                }
            )
            analytics_results.append(analytics_result)
        
        return analytics_results
    
    def _generate_enhanced_analytics_answer(self, question: str, analytics_insights: Dict[str, Any],
                                          search_results: List[AnalyticsSearchResult],
                                          fallback_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate answer with analytics insights and fallback information."""
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        # Build analytics context
        analytics_context = self._build_analytics_context(analytics_insights)
        
        # Build examples context with fallback info
        examples_context = self._build_examples_context_with_fallbacks(search_results, fallback_info)
        
        # Build enhanced system prompt
        system_prompt = self._build_enhanced_analytics_system_prompt()
        
        # Build user prompt with fallback context
        user_prompt = self._build_enhanced_analytics_user_prompt(
            question, analytics_context, examples_context, fallback_info
        )
        
        # Generate response
        response = provider.generate(user_prompt, system_prompt)
        
        return {
            'content': response.content,
            'tokens_used': response.tokens_used,
            'cost_estimate': response.cost_estimate,
            'provider': response.provider,
            'model': response.model
        }
    
    def _generate_enhanced_discussion_answer(self, question: str, discussions: List[Dict[str, Any]],
                                           analytics_insights: Dict[str, Any], fallback_info: Dict[str, Any],
                                           target_keywords: List[str]) -> Dict[str, Any]:
        """Generate discussion-focused answer with analytics context and keyword info."""
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        # Build natural context from discussions
        context = self._build_natural_context(discussions)
        
        # Add analytics context if available
        if analytics_insights:
            analytics_summary = self._build_minimal_analytics_summary(analytics_insights)
            context = analytics_summary + "\n\n" + context
        
        # Build enhanced system prompt for discussions
        system_prompt = self._build_enhanced_discussion_system_prompt()
        
        # Build user prompt with keyword and fallback info
        user_prompt = self._build_enhanced_discussion_user_prompt(
            question, context, target_keywords, fallback_info
        )
        
        # Generate response
        response = provider.generate(user_prompt, system_prompt)
        
        return {
            'content': response.content,
            'tokens_used': response.tokens_used,
            'cost_estimate': response.cost_estimate,
            'provider': response.provider,
            'model': response.model
        }
    
    def _generate_enhanced_hybrid_answer(self, question: str, analytics_insights: Dict[str, Any],
                                       analytics_results: List[AnalyticsSearchResult],
                                       discussions: List[Dict[str, Any]],
                                       fallback_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive hybrid answer with fallback information."""
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        # Build comprehensive context
        analytics_context = self._build_analytics_context(analytics_insights)
        examples_context = self._build_examples_context_with_fallbacks(analytics_results, fallback_info)
        discussions_context = self._build_natural_context(discussions)
        
        # Build enhanced hybrid system prompt
        system_prompt = self._build_enhanced_hybrid_system_prompt()
        
        # Build comprehensive user prompt
        user_prompt = self._build_enhanced_hybrid_user_prompt(
            question, analytics_context, examples_context, discussions_context, fallback_info
        )
        
        # Generate response
        response = provider.generate(user_prompt, system_prompt)
        
        return {
            'content': response.content,
            'tokens_used': response.tokens_used,
            'cost_estimate': response.cost_estimate,
            'provider': response.provider,
            'model': response.model
        }
    
    def _generate_intelligent_answer(self, question: str, discussions: List[Dict[str, Any]],
                                   analytics_insights: Dict[str, Any], classification) -> Dict[str, Any]:
        """Generate intelligent answer using best available information."""
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        # Build context from available information
        context = self._build_natural_context(discussions)
        
        if analytics_insights:
            analytics_summary = self._build_minimal_analytics_summary(analytics_insights)
            context = analytics_summary + "\n\n" + context
        
        # Build intelligent system prompt
        system_prompt = self._build_intelligent_system_prompt()
        
        # Build user prompt with classification info
        user_prompt = self._build_intelligent_user_prompt(question, context, classification)
        
        # Generate response
        response = provider.generate(user_prompt, system_prompt)
        
        return {
            'content': response.content,
            'tokens_used': response.tokens_used,
            'cost_estimate': response.cost_estimate,
            'provider': response.provider,
            'model': response.model
        }
    
    # Enhanced prompt building methods
    def _build_enhanced_analytics_system_prompt(self) -> str:
        """Build enhanced system prompt for analytics with fallback handling."""
        return """You are an expert data analyst specializing in Reddit discussion analytics with intelligent fallback capabilities. You analyze both structured analytics data and actual Reddit discussions, gracefully handling cases where some keywords may not be in the formal analysis.

Your responses should be:
- COMPREHENSIVE: Use all available data, both analytics and discussion examples
- TRANSPARENT: Clearly explain what data you have vs. what you found through search
- GRACEFUL: When keywords aren't in the analysis, still provide valuable insights from discussions
- EVIDENCE-BASED: Support findings with specific numbers and real examples
- HELPFUL: Always provide useful information, even with incomplete analytics data
- NATURAL: Weave discussion examples naturally into your analysis using phrases like "in one discussion..." or "another gardener mentioned..." rather than numbered lists

When referencing discussion examples, integrate them smoothly into your analysis rather than listing them as separate numbered items. Focus on the insights and patterns rather than the structure of the examples.

When handling mixed data sources:
- Clearly distinguish between analytics data and discussion search results
- Explain fallback methods used when analytics data isn't available
- Combine insights from both sources for comprehensive understanding
- Note limitations and suggest how to get more complete data if needed

Structure responses to show both what the data definitively shows and what the discussions reveal."""
    
    def _build_enhanced_discussion_system_prompt(self) -> str:
        """Build enhanced system prompt for discussion queries with keyword awareness."""
        return """You are an expert at analyzing Reddit discussions with intelligent keyword understanding. You can extract insights from actual conversations while being aware of the topics the user is specifically interested in.

Your responses should be:
- CONVERSATION-FOCUSED: Based on actual Reddit discussions and user interactions
- KEYWORD-AWARE: Understand and highlight the specific topics the user asked about
- CONTEXTUAL: Explain what people are really saying about these topics
- SPECIFIC: Quote and reference actual discussions when relevant
- INSIGHTFUL: Identify patterns and perspectives from real conversations

When the user asks about specific topics:
- Focus on finding and explaining discussions related to those topics
- Explain how people talk about these subjects, even if not using exact keywords
- Provide context about the community perspectives and conversations
- Note when you find related discussions that might be relevant

Always base your analysis on actual Reddit conversations while being mindful of the topics the user is interested in."""
    
    def _build_enhanced_analytics_user_prompt(self, question: str, analytics_context: str,
                                            examples_context: str, fallback_info: Dict[str, Any]) -> str:
        """Build enhanced analytics user prompt with fallback information."""
        prompt = f"""Please answer this question using the available analytics data and discussion examples:

QUESTION: {question}

{analytics_context}

{examples_context}"""

        if fallback_info:
            prompt += f"\n\nFALLBACK INFORMATION:\n"
            if fallback_info.get('keywords_not_in_analysis'):
                prompt += f"Note: The following keywords were not found in the formal analysis but I searched for discussions: {', '.join(fallback_info['keywords_not_in_analysis'])}\n"
            if fallback_info.get('fallback_method'):
                prompt += f"Fallback method used: {fallback_info['fallback_method']}\n"

        prompt += """\n\nPlease provide a comprehensive answer that:
1. Uses the available analytics data where possible
2. Incorporates discussion examples to illustrate patterns
3. Explains any limitations or fallback methods used
4. Provides valuable insights regardless of data completeness
5. Suggests how to get more complete analytics if relevant"""

        return prompt
    
    def _build_enhanced_discussion_user_prompt(self, question: str, context: str,
                                             target_keywords: List[str], fallback_info: Dict[str, Any]) -> str:
        """Build enhanced discussion user prompt with keyword context."""
        prompt = f"""Please analyze these Reddit discussions to answer this question:

QUESTION: {question}"""

        if target_keywords:
            prompt += f"\n\nTOPICS OF INTEREST: {', '.join(target_keywords)}"

        prompt += f"""

REDDIT DISCUSSIONS:
{context}"""

        if fallback_info.get('search_keywords_used'):
            prompt += f"\n\nSEARCH NOTE: I focused on discussions containing: {', '.join(fallback_info['search_keywords_used'])}"

        prompt += """\n\nPlease provide an analysis that:
1. Explains what the Reddit community is saying about the topics of interest
2. Highlights relevant conversations and perspectives
3. Includes specific examples and quotes from the discussions
4. Explains how people talk about these topics, even if using different words
5. Provides insights into community opinions and experiences"""

        return prompt
    
    # Keep existing utility methods but enhance them
    def _build_examples_context_with_fallbacks(self, search_results: List[AnalyticsSearchResult], 
                                            fallback_info: Dict[str, Any]) -> str:
        """Build examples context that includes fallback information."""
        if not search_results:
            return "No specific examples found."
    
        context_parts = ["🗣️ DISCUSSION EXAMPLES:\n"]
    
        analytics_count = 0
        fallback_count = 0
    
        for result in search_results[:5]:
            is_fallback = result.analytics_metadata.get('source') == 'fallback_search'
        
            if is_fallback:
                fallback_count += 1
                context_parts.append(f"Discussion about '{result.keyword}' (Found via discussion search):")
            else:
                analytics_count += 1
                context_parts.append(f"Discussion about '{result.keyword}' (From analytics data):")
                context_parts.append(f"Sentiment: {result.sentiment_score:+.3f}")
        
            context_parts.append(f"Context: {result.mention_context}")
            
            if result.analytics_metadata and not is_fallback:
                metadata = result.analytics_metadata
                if metadata.get('post_title'):
                    context_parts.append(f"Post: {metadata['post_title']}")
            
            # Add discussion context if available
            if result.discussion_context:
                formatted_discussion = content_formatter.format_discussion_thread(result.discussion_context)
                truncated = content_formatter.format_content_for_context_window(formatted_discussion, 500)
                context_parts.append(f"Full Discussion:\n{truncated}")
            
            context_parts.append("")  # Empty line between examples
        
        # Add summary of data sources
        if analytics_count > 0 and fallback_count > 0:
            context_parts.insert(1, f"Data sources: {analytics_count} from formal analysis, {fallback_count} from discussion search\n")
        elif fallback_count > 0:
            context_parts.insert(1, f"Note: All examples found via discussion search (keywords not in formal analysis)\n")
        
        return "\n".join(context_parts)
    
    # Keep all existing utility methods unchanged
    def _handle_command_query(self, question: str, classification, collection_ids: List[str]) -> RAGResponse:
        """Handle command-type queries."""
        command_type = classification.intent_details.get('command_type', 'unknown')
        
        if command_type == 'help':
            answer = "This is the RAG engine. For full help, please use the chat interface."
        elif command_type == 'summary':
            analytics_insights = {'overview': self._get_general_analytics_overview(collection_ids)}
            answer = f"Your analysis covers {len(collection_ids)} collections. Use the chat interface for detailed exploration."
        else:
            answer = "Command queries are best handled through the chat interface."
        
        return RAGResponse(
            answer=answer,
            sources=[],
            analytics_insights={},
            search_type='command',
            search_results_count=0,
            discussions_used=0,
            tokens_used=0,
            cost_estimate=0.0,
            query_classification={
                'type': classification.query_type,
                'confidence': classification.confidence,
                'approach': classification.suggested_approach
            }
        )

    # Include all existing utility methods (unchanged)
    def _build_discussion_contexts_from_traditional(self, search_results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Build discussion contexts from traditional search results."""
        discussions = []
        processed_posts = set()
        
        for result in search_results:
            try:
                if result.content_type == 'post':
                    if result.content_id not in processed_posts:
                        discussion = discussion_builder.build_discussion_from_post(
                            result.content_id, result.collection_id
                        )
                        if discussion.get('post'):
                            discussions.append(discussion)
                            processed_posts.add(result.content_id)
                
                elif result.content_type == 'comment':
                    parent_post_id = result.metadata.get('post_reddit_id')
                    if parent_post_id and parent_post_id not in processed_posts:
                        discussion = discussion_builder.build_discussion_from_comment(
                            result.content_id, result.collection_id
                        )
                        if discussion.get('post'):
                            discussions.append(discussion)
                            processed_posts.add(parent_post_id)
                
                if len(discussions) >= self.max_discussions:
                    break
                    
            except Exception:
                continue
        
        return discussions
    
    def _build_natural_context(self, discussions: List[Dict[str, Any]]) -> str:
        """Build natural conversation context from complete discussions."""
        if not discussions:
            return "No relevant discussions found."
        
        context_parts = ["Here are the relevant Reddit discussions from your data:\n"]
        
        for i, discussion in enumerate(discussions, 1):
            formatted_discussion = content_formatter.format_discussion_thread(discussion)
            
            post_title = discussion.get('post', {}).get('title', 'Unknown Post')
            subreddit = discussion.get('post', {}).get('subreddit', 'unknown')
            comment_count = len(discussion.get('comments', []))
            
            discussion_header = f"\n{'='*60}\nDISCUSSION {i}: r/{subreddit}\n{post_title}\n({comment_count} comments shown)\n{'='*60}\n"
            
            full_discussion = discussion_header + formatted_discussion
            
            current_length = sum(len(part) for part in context_parts)
            if current_length + len(full_discussion) > self.max_context_length:
                remaining_space = self.max_context_length - current_length - 100
                if remaining_space > 500:
                    truncated_discussion = content_formatter.format_content_for_context_window(
                        full_discussion, remaining_space
                    )
                    context_parts.append(truncated_discussion)
                break
            else:
                context_parts.append(full_discussion)
        
        return "\n".join(context_parts)
    
    def _build_analytics_context(self, analytics_insights: Dict[str, Any]) -> str:
        """Build formatted analytics context for LLM."""
        if not analytics_insights:
            return "No specific analytics data available."
        
        context_parts = ["📊 ANALYTICS INSIGHTS:\n"]
        
        for keyword, data in analytics_insights.items():
            if keyword == 'overview':
                context_parts.append(f"GENERAL OVERVIEW:\n{data}\n")
                continue
            
            if not data.get('found', True):  # Handle both old and new format
                continue
            
            context_parts.append(f"KEYWORD: '{keyword}'")
            context_parts.append(f"• Total mentions: {data.get('total_mentions', 'N/A'):,}")
            context_parts.append(f"• Average sentiment: {data.get('avg_sentiment', 0):+.3f}")
            context_parts.append(f"• Found in {data.get('collections_found', 0)} collection(s)")
            
            # Add distribution info if available
            if data.get('mention_distribution'):
                dist = data['mention_distribution']
                context_parts.append(f"• Distribution: {dist.get('post', 0)} posts, {dist.get('comment', 0)} comments")
            
            context_parts.append("")  # Empty line between keywords
        
        return "\n".join(context_parts)
    
    def _get_available_keywords(self, collection_ids: List[str], analysis_session_id: str = None) -> List[str]:
        """Get list of available keywords from analytics data."""
        session = db.get_session()
        try:
            from ...database import KeywordStat, AnalysisSession
            import json
    
            # If specific session provided, use only that session
            if analysis_session_id:
                matching_session_ids = [analysis_session_id]
            else:
                # Fallback to old behavior
                analysis_sessions = session.query(AnalysisSession).all()
                matching_session_ids = []
                for analysis_session in analysis_sessions:
                    session_collection_ids = json.loads(analysis_session.collection_ids)
                    if any(collection_id in session_collection_ids for collection_id in collection_ids):
                        matching_session_ids.append(analysis_session.id)
        
            if not matching_session_ids:
                return []
        
            keywords = session.query(KeywordStat.keyword).filter(
                KeywordStat.analysis_session_id.in_(matching_session_ids)
            ).distinct().all()
            return [kw.keyword for kw in keywords]
        except:
            return []
        finally:
            session.close()
    
    def _get_general_analytics_overview(self, collection_ids: List[str]) -> str:
        """Get general analytics overview for collections."""
        session = db.get_session()
        try:
            from ...database import KeywordStat, AnalysisSession
            import json
        
            analysis_sessions = session.query(AnalysisSession).all()
        
            matching_session_ids = []
            for analysis_session in analysis_sessions:
                session_collection_ids = json.loads(analysis_session.collection_ids)
                if any(collection_id in session_collection_ids for collection_id in collection_ids):
                    matching_session_ids.append(analysis_session.id)
        
            if not matching_session_ids:
                return f"Analysis covers {len(collection_ids)} collections."
        
            stats = session.query(KeywordStat).filter(
                KeywordStat.analysis_session_id.in_(matching_session_ids)
            ).all()
        
            total_keywords = len(set(stat.keyword for stat in stats))
            total_mentions = sum(stat.total_mentions for stat in stats)
            avg_sentiment = sum(stat.avg_sentiment * stat.total_mentions for stat in stats) / total_mentions if total_mentions > 0 else 0
        
            return f"Analysis covers {total_keywords} keywords with {total_mentions:,} total mentions and {avg_sentiment:+.3f} average sentiment across {len(collection_ids)} collections."
        except:
            return f"Analysis covers {len(collection_ids)} collections."
        finally:
            session.close()
    
    def _build_minimal_analytics_summary(self, analytics_insights: Dict[str, Any]) -> str:
        """Build minimal analytics summary for discussion-focused responses."""
        if not analytics_insights:
            return ""
        
        summary_parts = ["📊 Quick Analytics Context:"]
        for keyword, data in analytics_insights.items():
            if isinstance(data, dict) and data.get('total_mentions'):
                summary_parts.append(f"• '{keyword}': {data['total_mentions']} mentions, {data['avg_sentiment']:+.2f} sentiment")
        
        if len(summary_parts) > 1:
            return "\n".join(summary_parts) + "\n"
        return ""
    
    def _format_analytics_sources(self, search_results: List[AnalyticsSearchResult], 
                                analytics_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format analytics search results as sources."""
        sources = []
        
        for result in search_results:
            source = {
                'content_id': result.content_id,
                'content_type': result.content_type,
                'collection_id': result.collection_id,
                'keyword': result.keyword,
                'sentiment_score': result.sentiment_score,
                'mention_context': result.mention_context,
                'analytics_metadata': result.analytics_metadata,
                'source_type': 'analytics_driven'
            }
            
            if result.discussion_context:
                source['discussion_context'] = result.discussion_context
            
            sources.append(source)
        
        return sources
    
    def _format_traditional_sources(self, search_results: List[SearchResult], 
                                  discussions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format traditional search results as sources."""
        sources = []
        
        for result in search_results:
            source = {
                'content_id': result.content_id,
                'content_type': result.content_type,
                'collection_id': result.collection_id,
                'relevance_score': result.relevance_score,
                'metadata': result.metadata,
                'source_type': 'traditional_search'
            }
            sources.append(source)
        
        return sources
    
    def _format_hybrid_sources(self, analytics_results: List[AnalyticsSearchResult],
                             traditional_results: List[SearchResult],
                             discussions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format hybrid sources combining analytics and traditional results."""
        sources = []
        
        # Add analytics sources
        sources.extend(self._format_analytics_sources(analytics_results, {}))
        
        # Add traditional sources
        sources.extend(self._format_traditional_sources(traditional_results, discussions))
        
        return sources
    
    # Add remaining system prompt methods
    def _build_enhanced_hybrid_system_prompt(self) -> str:
        """Build enhanced system prompt for comprehensive hybrid responses."""
        return """You are an expert at combining quantitative Reddit analytics with qualitative discussion analysis, gracefully handling mixed data sources and fallback methods.

Your responses should bridge quantitative and qualitative insights:
- ANALYTICAL FOUNDATION: Start with what the data shows statistically where available
- CONVERSATIONAL EVIDENCE: Support with actual quotes and discussion examples
- TRANSPARENT METHODOLOGY: Explain what data sources were used and any limitations
- INTEGRATED INSIGHTS: Connect patterns in data to real user conversations
- COMPREHENSIVE UNDERSTANDING: Provide complete picture using all available sources

When working with mixed data sources:
- Clearly indicate which insights come from formal analytics vs. discussion search
- Explain fallback methods used when complete analytics aren't available
- Combine both perspectives for fuller understanding
- Suggest how to get more complete analytics if relevant

Structure your response to provide the most complete picture possible using all available information."""
    
    def _build_intelligent_system_prompt(self) -> str:
        """Build system prompt for intelligent auto-detection responses."""
        return """You are an intelligent assistant that analyzes Reddit data using the best available methods. You adapt your approach based on what data is available and provide comprehensive insights regardless of data completeness.

Your responses should be:
- ADAPTIVE: Use whatever data sources are available effectively
- INSIGHTFUL: Extract meaningful patterns from available information
- TRANSPARENT: Explain what analysis methods were used
- HELPFUL: Always provide valuable insights regardless of data limitations
- COMPREHENSIVE: Combine all available information for best understanding

When analyzing data:
- Use structured analytics data when available
- Fall back to discussion analysis when needed
- Explain your methodology and any limitations
- Provide actionable insights based on available information
- Suggest ways to get more complete data if relevant

Focus on providing the best possible analysis using available information sources."""
    
    def _build_enhanced_hybrid_user_prompt(self, question: str, analytics_context: str,
                                         examples_context: str, discussions_context: str,
                                         fallback_info: Dict[str, Any]) -> str:
        """Build comprehensive user prompt for hybrid analysis."""
        prompt = f"""Please provide a comprehensive analysis using all available data sources:

QUESTION: {question}

{analytics_context}

{examples_context}

{discussions_context}"""

        if fallback_info:
            prompt += f"\n\nMETHODOLOGY NOTES:\n"
            for key, value in fallback_info.items():
                if key != 'method':
                    prompt += f"• {key}: {value}\n"

        prompt += """\n\nPlease provide a comprehensive answer that:
1. Combines analytical insights with real discussion examples
2. Explains what the data definitively shows vs. what discussions suggest
3. Notes any methodology or data source limitations
4. Provides actionable insights based on all available information
5. Suggests how to get more complete analytics if relevant"""

        return prompt
    
    def _build_intelligent_user_prompt(self, question: str, context: str, classification) -> str:
        """Build user prompt for intelligent analysis."""
        prompt = f"""Please analyze this information to answer the question using intelligent data analysis:

QUESTION: {question}

AVAILABLE DATA:
{context}"""

        if classification.target_keywords:
            prompt += f"\n\nEXTRACTED TOPICS: {', '.join(classification.target_keywords)}"

        prompt += f"""\n\nQUERY ANALYSIS:
• Type: {classification.query_type}
• Confidence: {classification.confidence:.2f}
• Approach: {classification.suggested_approach}

Please provide an intelligent analysis that:
1. Uses the available data effectively regardless of source
2. Focuses on the topics the user is interested in
3. Provides insights based on actual Reddit conversations
4. Explains what the data reveals about user perspectives
5. Offers actionable understanding of the topic"""

        return prompt

    # Keep all existing methods for backward compatibility
    def get_full_context(self, content_id: str, content_type: str, collection_id: str) -> Optional[Dict[str, Any]]:
        """Get full context for a specific piece of content using discussion builder."""
        try:
            if content_type == 'post':
                discussion = discussion_builder.build_discussion_from_post(content_id, collection_id)
                return discussion.get('post') if discussion else None
            else:
                discussion = discussion_builder.build_discussion_from_comment(content_id, collection_id)
                comments = discussion.get('comments', [])
                for comment in comments:
                    if comment.get('reddit_id') == content_id:
                        return comment
                return None
        except Exception:
            return None
    
    def get_available_search_types(self, collection_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get available search types and their status for given collections."""
        from ..embeddings import vector_storage
        
        # Check indexing status
        embedding_stats = vector_storage.get_embedding_stats(collection_ids)
        has_local_embeddings = any(
            model_info['provider'] == 'local' 
            for model_info in embedding_stats.get('by_model', [])
        )
        has_cloud_embeddings = any(
            model_info['provider'] == 'openai' 
            for model_info in embedding_stats.get('by_model', [])
        )
        
        # Check analytics availability
        has_analytics = bool(self._get_available_keywords(collection_ids))
        
        search_types = {
            'keyword': {
                'available': True,
                'description': 'Keyword-based search with full discussion context',
                'requires_indexing': False,
                'cost': 'Free',
                'quality': 'Good for exact matches'
            },
            'local_semantic': {
                'available': has_local_embeddings,
                'description': 'Local semantic search with natural conversation understanding',
                'requires_indexing': True,
                'indexed': has_local_embeddings,
                'cost': 'Free (one-time indexing time)',
                'quality': 'Better for conceptual questions'
            },
            'cloud_semantic': {
                'available': has_cloud_embeddings,
                'description': 'Cloud semantic search with advanced understanding',
                'requires_indexing': True,
                'indexed': has_cloud_embeddings,
                'cost': 'Paid (OpenAI API tokens)',
                'quality': 'Best for complex conceptual questions'
            },
            'analytics_driven': {
                'available': has_analytics,
                'description': 'Analytics-aware search using your keyword analysis data with intelligent fallbacks',
                'requires_indexing': False,
                'analytics_required': True,
                'indexed': has_analytics,
                'cost': 'Free',
                'quality': 'Best for frequency, sentiment, and pattern questions with graceful fallbacks'
            }
        }
        
        return search_types
    
    def get_representative_examples(self, collection_ids: List[str], 
                                  keywords: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """Get representative discussion examples for summarization and analysis."""
        try:
            examples = discussion_builder.get_representative_examples(
                collection_ids, keywords, limit
            )
            
            formatted_examples = []
            for example in examples:
                formatted_text = content_formatter.format_discussion_thread(example)
                formatted_examples.append({
                    'discussion_data': example,
                    'formatted_text': formatted_text,
                    'post_title': example.get('post', {}).get('title', ''),
                    'subreddit': example.get('post', {}).get('subreddit', ''),
                    'comment_count': len(example.get('comments', []))
                })
            
            return formatted_examples
            
        except Exception:
            return []


# Global enhanced RAG engine instance
rag_engine = RAGEngine()