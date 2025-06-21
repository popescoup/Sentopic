"""
RAG (Retrieval-Augmented Generation) Engine

Enhanced RAG engine with analytics awareness that combines search results with LLM 
generation using both analytical insights and natural Reddit discussion contexts.
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
    """Enhanced response from RAG engine with analytics awareness."""
    answer: str                     # AI-generated answer
    sources: List[Dict[str, Any]]   # Source attributions with full context
    analytics_insights: Dict[str, Any]  # Analytics data used in response
    search_type: str               # Search method used
    search_results_count: int      # Number of search results found
    discussions_used: int          # Number of complete discussions used
    tokens_used: int               # LLM tokens used
    cost_estimate: float           # Cost estimate for this query
    query_classification: Dict[str, Any]  # How the query was classified


class RAGEngine:
    """
    Analytics-aware RAG engine that intelligently combines analytical insights
    with natural Reddit discussion contexts for optimal response generation.
    """
    
    def __init__(self):
        self.max_discussions = 3      # Maximum complete discussions to include
        self.max_context_length = 8000  # Character limit for context
    
    def answer_question(self, question: str, collection_ids: List[str], 
                       search_type: str = 'auto', 
                       max_results: int = 5) -> RAGResponse:
        """
        Answer a question using analytics-aware RAG with intelligent query routing.
        
        Args:
            question: User's question
            collection_ids: Collection IDs to search in
            search_type: 'auto', 'keyword', 'local_semantic', 'cloud_semantic', or 'analytics_driven'
            max_results: Maximum search results to process
        
        Returns:
            RAGResponse with analytics-informed answer and rich sources
        """
        # Get available keywords for context
        available_keywords = self._get_available_keywords(collection_ids)
        
        # Classify the query to determine optimal approach
        classification = query_classifier.classify_query(question, available_keywords)
        
        # Get search strategy based on classification
        search_strategy = query_classifier.get_search_strategy(classification)
        
        # Handle different query types
        if classification.query_type == 'command':
            return self._handle_command_query(question, classification, collection_ids)
        
        elif classification.query_type == 'analytics':
            return self._handle_analytics_query(
                question, classification, collection_ids, max_results
            )
        
        elif classification.query_type == 'discussion':
            return self._handle_discussion_query(
                question, classification, collection_ids, search_type, max_results
            )
        
        elif classification.query_type == 'hybrid':
            return self._handle_hybrid_query(
                question, classification, collection_ids, search_type, max_results
            )
        
        else:
            # Fallback to original approach
            return self._handle_fallback_query(
                question, collection_ids, search_type, max_results, classification
            )
    
    def _handle_analytics_query(self, question: str, classification, 
                              collection_ids: List[str], max_results: int) -> RAGResponse:
        """Handle queries focused on analytics insights."""
        analytics_insights = {}
        search_results = []
        
        # Get target keywords from classification
        target_keywords = classification.target_keywords
        
        if target_keywords:
            # Get detailed analytics for target keywords
            for keyword in target_keywords[:3]:  # Limit to top 3 keywords
                keyword_overview = analytics_search_engine.get_keyword_overview(
                    keyword, collection_ids
                )
                if keyword_overview.get('found'):
                    analytics_insights[keyword] = keyword_overview
                    
                    # Get representative examples using analytics
                    keyword_results = analytics_search_engine.search_by_keyword_analytics(
                        keyword, collection_ids, limit=max_results // len(target_keywords) + 1
                    )
                    search_results.extend(keyword_results)
        
        else:
            # General analytics overview
            analytics_insights['overview'] = self._get_general_analytics_overview(collection_ids)
            
            # Get insights-based examples
            insight_results = analytics_search_engine.search_by_analytics_insights(
                collection_ids, 'most_frequent', limit=max_results
            )
            search_results.extend(insight_results)
        
        # Enrich with discussion contexts
        search_results = analytics_search_engine.enrich_with_discussion_context(search_results)
        
        # Generate analytics-focused response
        llm_response = self._generate_analytics_focused_answer(
            question, analytics_insights, search_results
        )
        
        # Format sources
        sources = self._format_analytics_sources(search_results, analytics_insights)
        
        return RAGResponse(
            answer=llm_response['content'],
            sources=sources,
            analytics_insights=analytics_insights,
            search_type='analytics_driven',
            search_results_count=len(search_results),
            discussions_used=len([r for r in search_results if r.discussion_context]),
            tokens_used=llm_response['tokens_used'],
            cost_estimate=llm_response['cost_estimate'],
            query_classification={
                'type': classification.query_type,
                'confidence': classification.confidence,
                'approach': classification.suggested_approach
            }
        )
    
    def _handle_discussion_query(self, question: str, classification,
                               collection_ids: List[str], search_type: str, 
                               max_results: int) -> RAGResponse:
        """Handle queries focused on discussion content."""
        search_results = []
        analytics_insights = {}
        
        # Use traditional search for discussion content
        if search_type == 'auto':
            search_type = 'keyword'  # Default for discussion queries
        
        search_engine = SearchEngineFactory.create_engine(search_type)
        traditional_results = search_engine.search(question, collection_ids, limit=max_results)
        
        # Convert to format compatible with analytics results
        for result in traditional_results:
            # Get minimal analytics context if keywords are available
            target_keywords = classification.target_keywords
            if target_keywords:
                for keyword in target_keywords:
                    keyword_overview = analytics_search_engine.get_keyword_overview(
                        keyword, collection_ids
                    )
                    if keyword_overview.get('found'):
                        analytics_insights[keyword] = {
                            'total_mentions': keyword_overview['total_mentions'],
                            'avg_sentiment': keyword_overview['avg_sentiment']
                        }
        
        # Build discussion contexts
        discussions = self._build_discussion_contexts_from_traditional(traditional_results)
        
        # Generate discussion-focused response
        llm_response = self._generate_discussion_focused_answer(
            question, discussions, analytics_insights
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
                'approach': classification.suggested_approach
            }
        )
    
    def _handle_hybrid_query(self, question: str, classification,
                           collection_ids: List[str], search_type: str, 
                           max_results: int) -> RAGResponse:
        """Handle queries that need both analytics and discussion insights."""
        analytics_insights = {}
        analytics_results = []
        traditional_results = []
        
        target_keywords = classification.target_keywords
        
        # Get analytics insights
        if target_keywords:
            for keyword in target_keywords[:2]:  # Limit for hybrid approach
                keyword_overview = analytics_search_engine.get_keyword_overview(
                    keyword, collection_ids
                )
                if keyword_overview.get('found'):
                    analytics_insights[keyword] = keyword_overview
                    
                    # Get some analytics-driven examples
                    keyword_results = analytics_search_engine.search_by_keyword_analytics(
                        keyword, collection_ids, limit=max_results // 2
                    )
                    analytics_results.extend(keyword_results)
        
        # Get discussion examples
        if search_type == 'auto':
            search_type = 'keyword'
        
        search_engine = SearchEngineFactory.create_engine(search_type)
        traditional_results = search_engine.search(question, collection_ids, limit=max_results // 2)
        
        # Combine and enrich results
        all_search_results = analytics_results
        discussions = self._build_discussion_contexts_from_traditional(traditional_results)
        
        # Enrich analytics results with discussion contexts
        analytics_results = analytics_search_engine.enrich_with_discussion_context(analytics_results)
        
        # Generate hybrid response
        llm_response = self._generate_hybrid_answer(
            question, analytics_insights, analytics_results, discussions
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
                'approach': classification.suggested_approach
            }
        )
    
    def _handle_command_query(self, question: str, classification,
                            collection_ids: List[str]) -> RAGResponse:
        """Handle command-type queries."""
        # This would be handled by the chat agent, but we provide a basic response
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
    
    def _handle_fallback_query(self, question: str, collection_ids: List[str],
                             search_type: str, max_results: int, 
                             classification) -> RAGResponse:
        """Fallback to original RAG approach when classification is uncertain."""
        # Use the original RAG approach from the previous implementation
        search_engine = SearchEngineFactory.create_engine(search_type)
        search_results = search_engine.search(question, collection_ids, limit=max_results)
        
        if not search_results:
            return RAGResponse(
                answer="I couldn't find any relevant discussions in your Reddit data that relate to this question. Try rephrasing your question or asking about different topics that might be covered in your collections.",
                sources=[],
                analytics_insights={},
                search_type=search_type,
                search_results_count=0,
                discussions_used=0,
                tokens_used=0,
                cost_estimate=0.0,
                query_classification={
                    'type': classification.query_type,
                    'confidence': classification.confidence,
                    'approach': 'fallback'
                }
            )
        
        # Build discussion contexts
        discussions = self._build_discussion_contexts_from_traditional(search_results)
        
        # Generate response
        llm_response = self._generate_answer_with_discussions(question, discussions)
        
        # Format sources
        sources = self._format_traditional_sources(search_results, discussions)
        
        return RAGResponse(
            answer=llm_response['content'],
            sources=sources,
            analytics_insights={},
            search_type=search_type,
            search_results_count=len(search_results),
            discussions_used=len(discussions),
            tokens_used=llm_response['tokens_used'],
            cost_estimate=llm_response['cost_estimate'],
            query_classification={
                'type': classification.query_type,
                'confidence': classification.confidence,
                'approach': 'fallback'
            }
        )
    
    def _generate_analytics_focused_answer(self, question: str, 
                                         analytics_insights: Dict[str, Any],
                                         search_results: List[AnalyticsSearchResult]) -> Dict[str, Any]:
        """Generate answer focused on analytics insights with supporting examples."""
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        # Build analytics context
        analytics_context = self._build_analytics_context(analytics_insights)
        
        # Build supporting examples context
        examples_context = self._build_examples_context_from_analytics(search_results)
        
        # Build prompts
        system_prompt = self._build_analytics_system_prompt()
        user_prompt = self._build_analytics_user_prompt(question, analytics_context, examples_context)
        
        # Generate response
        response = provider.generate(user_prompt, system_prompt)
        
        return {
            'content': response.content,
            'tokens_used': response.tokens_used,
            'cost_estimate': response.cost_estimate,
            'provider': response.provider,
            'model': response.model
        }
    
    def _generate_discussion_focused_answer(self, question: str, 
                                          discussions: List[Dict[str, Any]],
                                          analytics_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate answer focused on discussion content with minimal analytics context."""
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        # Build natural context from discussions (original approach)
        context = self._build_natural_context(discussions)
        
        # Add minimal analytics context if available
        if analytics_insights:
            analytics_summary = self._build_minimal_analytics_summary(analytics_insights)
            context = analytics_summary + "\n\n" + context
        
        # Build prompts
        system_prompt = self._build_enhanced_system_prompt()
        user_prompt = self._build_enhanced_user_prompt(question, context)
        
        # Generate response
        response = provider.generate(user_prompt, system_prompt)
        
        return {
            'content': response.content,
            'tokens_used': response.tokens_used,
            'cost_estimate': response.cost_estimate,
            'provider': response.provider,
            'model': response.model
        }
    
    def _generate_hybrid_answer(self, question: str, analytics_insights: Dict[str, Any],
                              analytics_results: List[AnalyticsSearchResult],
                              discussions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive answer combining analytics and discussions."""
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        # Build comprehensive context
        analytics_context = self._build_analytics_context(analytics_insights)
        examples_context = self._build_examples_context_from_analytics(analytics_results)
        discussions_context = self._build_natural_context(discussions)
        
        # Build prompts
        system_prompt = self._build_hybrid_system_prompt()
        user_prompt = self._build_hybrid_user_prompt(
            question, analytics_context, examples_context, discussions_context
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
    
    def _build_analytics_context(self, analytics_insights: Dict[str, Any]) -> str:
        """Build formatted analytics context for LLM."""
        if not analytics_insights:
            return "No specific analytics data available."
        
        context_parts = ["📊 ANALYTICS INSIGHTS:\n"]
        
        for keyword, data in analytics_insights.items():
            if keyword == 'overview':
                context_parts.append(f"GENERAL OVERVIEW:\n{data}\n")
                continue
            
            if not data.get('found'):
                continue
            
            context_parts.append(f"KEYWORD: '{keyword}'")
            context_parts.append(f"• Total mentions: {data['total_mentions']:,}")
            context_parts.append(f"• Average sentiment: {data['avg_sentiment']:+.3f}")
            context_parts.append(f"• Found in {data['collections_found']} collection(s)")
            
            # Add distribution info
            if data.get('mention_distribution'):
                dist = data['mention_distribution']
                context_parts.append(f"• Distribution: {dist.get('post', 0)} posts, {dist.get('comment', 0)} comments")
            
            # Add sentiment breakdown
            if data.get('sentiment_distribution'):
                sent_dist = data['sentiment_distribution']
                total_sent = sum(sent_dist.values())
                if total_sent > 0:
                    pos_pct = (sent_dist['positive'] + sent_dist['very_positive']) / total_sent * 100
                    neg_pct = (sent_dist['negative'] + sent_dist['very_negative']) / total_sent * 100
                    context_parts.append(f"• Sentiment breakdown: {pos_pct:.1f}% positive, {neg_pct:.1f}% negative")
            
            # Add top co-occurrences
            if data.get('top_cooccurrences'):
                cooccur_text = ", ".join([f"'{co['keyword']}' ({co['count']})" for co in data['top_cooccurrences'][:3]])
                context_parts.append(f"• Often appears with: {cooccur_text}")
            
            context_parts.append("")  # Empty line between keywords
        
        return "\n".join(context_parts)
    
    def _build_examples_context_from_analytics(self, search_results: List[AnalyticsSearchResult]) -> str:
        """Build examples context from analytics search results."""
        if not search_results:
            return "No specific examples found."
        
        context_parts = ["🗣️ SPECIFIC EXAMPLES FROM ANALYTICS:\n"]
        
        for i, result in enumerate(search_results[:5], 1):
            context_parts.append(f"EXAMPLE {i} - Keyword: '{result.keyword}'")
            context_parts.append(f"Sentiment: {result.sentiment_score:+.3f}")
            context_parts.append(f"Context: {result.mention_context}")
            
            if result.analytics_metadata:
                metadata = result.analytics_metadata
                if metadata.get('post_title'):
                    context_parts.append(f"Post: {metadata['post_title']}")
                if metadata.get('keyword_frequency_rank'):
                    context_parts.append(f"Frequency rank: #{metadata['keyword_frequency_rank']}")
            
            # Add discussion context if available
            if result.discussion_context:
                formatted_discussion = content_formatter.format_discussion_thread(result.discussion_context)
                # Truncate for context window
                truncated = content_formatter.format_content_for_context_window(formatted_discussion, 500)
                context_parts.append(f"Full Discussion:\n{truncated}")
            
            context_parts.append("")  # Empty line between examples
        
        return "\n".join(context_parts)
    
    def _build_analytics_system_prompt(self) -> str:
        """Build system prompt for analytics-focused responses."""
        return """You are an expert data analyst specializing in Reddit discussion analytics. You have access to precise analytical data including keyword frequencies, sentiment scores, co-occurrence patterns, and specific examples from Reddit discussions.

Your responses should be:
- DATA-DRIVEN: Lead with analytical insights and statistics
- PRECISE: Reference exact numbers, frequencies, and sentiment scores
- EVIDENCE-BASED: Support insights with specific examples from the data
- CONTEXTUAL: Explain what the numbers mean for understanding community behavior
- ACTIONABLE: Provide insights that help understand patterns and trends

When referencing analytics data:
- Quote exact statistics: "appears in X mentions with Y average sentiment"
- Reference ranking: "the #N most frequently discussed keyword"
- Explain sentiment: "predominantly positive with Z% of mentions being positive"
- Highlight patterns: "frequently co-occurs with keywords A, B, C"

Structure your response to clearly separate analytical insights from supporting discussion examples. Always reference the specific analytics data provided."""
    
    def _build_hybrid_system_prompt(self) -> str:
        """Build system prompt for comprehensive hybrid responses."""
        return """You are an expert at combining quantitative Reddit analytics with qualitative discussion analysis. You have access to both precise analytical data (frequencies, sentiment scores, patterns) and actual Reddit conversation examples.

Your responses should bridge quantitative and qualitative insights:
- ANALYTICAL FOUNDATION: Start with what the data shows statistically
- CONVERSATIONAL EVIDENCE: Support with actual quotes and discussion examples
- INTEGRATED INSIGHTS: Connect patterns in the data to real user conversations
- COMPREHENSIVE UNDERSTANDING: Combine both analytical and conversational perspectives

Structure your response to:
1. Lead with key analytical findings (frequencies, sentiment, trends)
2. Illustrate these findings with actual Reddit discussion examples
3. Explain how the data patterns manifest in real conversations
4. Provide actionable insights based on both data and discussions

Reference both statistical data and specific Reddit discussions to provide a complete picture."""
    
    def _build_analytics_user_prompt(self, question: str, analytics_context: str, 
                                   examples_context: str) -> str:
        """Build user prompt for analytics-focused queries."""
        return f"""Based on the analytical data and supporting examples from Reddit discussions, please answer this question:

QUESTION: {question}

{analytics_context}

{examples_context}

Please provide a data-driven answer that explains what the analytics show about this topic, supported by specific examples from the Reddit discussions. Reference exact statistics, sentiment scores, and patterns from the analytical data."""
    
    def _build_hybrid_user_prompt(self, question: str, analytics_context: str,
                                examples_context: str, discussions_context: str) -> str:
        """Build user prompt for hybrid queries."""
        return f"""Based on both analytical data and Reddit discussion examples, please answer this question:

QUESTION: {question}

{analytics_context}

{examples_context}

{discussions_context}

Please provide a comprehensive answer that combines analytical insights with real discussion examples. Show how the statistical patterns manifest in actual Reddit conversations and what this reveals about the community's perspectives."""
    
    # Include original methods for backward compatibility
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
        """Build natural conversation context from complete discussions (original method)."""
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
    
    def _build_enhanced_system_prompt(self) -> str:
        """Build enhanced system prompt for natural Reddit discussion analysis (original method)."""
        return """You are an expert at analyzing Reddit discussions and providing insights based on real conversations. You have access to complete Reddit discussion threads including posts and their comment conversations.

Your responses should be:
- CONVERSATIONAL: Based on actual Reddit discussions, capturing the tone and insights of real users
- SPECIFIC: Quote directly from posts and comments when relevant, using natural language
- CONTEXTUAL: Understand that posts and comments are part of ongoing conversations
- ATTRIBUTIVE: Reference specific discussions and users when making claims
- INSIGHTFUL: Identify patterns, consensus, disagreements, and notable perspectives from the discussions

When referencing Reddit content:
- Quote naturally: "One user mentioned..." or "In a discussion about X, someone said..."
- Use Post IDs and Comment IDs for attribution when helpful: (Post ID: abc123)
- Capture the conversational flow: how people respond to each other
- Note voting patterns: highly upvoted comments often represent community consensus

Format your response as a natural analysis of what the Reddit community is actually saying about the topic, with specific examples and quotes from the discussions."""
    
    def _build_enhanced_user_prompt(self, question: str, context: str) -> str:
        """Build enhanced user prompt with natural discussion context (original method)."""
        return f"""Based on these actual Reddit discussions from the user's data, please answer this question:

QUESTION: {question}

REDDIT DISCUSSIONS:
{context}

Please analyze what the Reddit community is actually saying about this topic. Include specific quotes and examples from the discussions above. Reference the Post IDs and Comment IDs when citing specific examples. Capture both the overall sentiment and any interesting disagreements or different perspectives you notice in the conversations."""
    
    def _generate_answer_with_discussions(self, question: str, 
                                        discussions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer using LLM with natural Reddit discussions (original method)."""
        provider = get_llm_provider()
        if not provider:
            raise RuntimeError("No LLM provider available. Please check your configuration.")
        
        context = self._build_natural_context(discussions)
        system_prompt = self._build_enhanced_system_prompt()
        user_prompt = self._build_enhanced_user_prompt(question, context)
        
        response = provider.generate(user_prompt, system_prompt)
        
        return {
            'content': response.content,
            'tokens_used': response.tokens_used,
            'cost_estimate': response.cost_estimate,
            'provider': response.provider,
            'model': response.model
        }
    
    def _get_available_keywords(self, collection_ids: List[str]) -> List[str]:
        """Get list of available keywords from analytics data."""
        session = db.get_session()
        try:
            from ...database import KeywordStat
            keywords = session.query(KeywordStat.keyword).filter(
                KeywordStat.collection_id.in_(collection_ids)
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
            from ...database import KeywordStat
            stats = session.query(KeywordStat).filter(
                KeywordStat.collection_id.in_(collection_ids)
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
    
    # Keep original methods for backward compatibility
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
                'description': 'Analytics-aware search using your keyword analysis data',
                'requires_indexing': False,
                'analytics_required': True,
                'indexed': has_analytics,
                'cost': 'Free',
                'quality': 'Best for frequency, sentiment, and pattern questions'
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


# Global RAG engine instance
rag_engine = RAGEngine()