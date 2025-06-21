"""
Query Classifier

Intelligent query routing to determine if users are asking about analytics data
vs. wanting discussion examples, enabling optimal response strategies.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QueryClassification:
    """Classification result for a user query."""
    query_type: str              # 'analytics', 'discussion', 'hybrid', 'command'
    confidence: float            # Confidence score 0.0 to 1.0
    target_keywords: List[str]   # Keywords extracted from query
    intent_details: Dict[str, any]  # Additional intent information
    suggested_approach: str      # Recommended search/response approach


class QueryClassifier:
    """
    Classifies user queries to determine optimal search and response strategies.
    
    Routes queries between:
    - Analytics questions (frequencies, sentiment, trends, stats)
    - Discussion questions (what people say, examples, opinions)
    - Hybrid questions (both analytics and examples)
    - Commands (special system functions)
    """
    
    def __init__(self):
        # Analytics signal patterns
        self.analytics_patterns = [
            # Frequency and statistics
            r'\b(how (often|frequent|much)|frequency|count|number of|total|mentions)\b',
            r'\b(most|least|top|bottom|highest|lowest|frequent)\b',
            r'\b(appears?|occurs?|mentioned|discussed)\b.*\b(often|frequently|much|times)\b',
            r'\b(statistics|stats|data|numbers|metrics)\b',
            r'\b(percentage|percent|ratio|proportion)\b',
            
            # Sentiment and trends
            r'\b(sentiment|opinion|feeling|attitude)\b.*\b(positive|negative|neutral)\b',
            r'\b(trend|trending|rising|falling|increasing|decreasing|changing)\b',
            r'\b(over time|temporal|timeline|period|recent|lately)\b',
            r'\b(average|mean|median|distribution)\b',
            
            # Comparative analytics
            r'\b(compare|comparison|versus|vs\.?|against|relative)\b',
            r'\b(rank|ranking|order|sort)\b',
            r'\b(correlation|relationship|co-occur|together|associated)\b',
            
            # Meta-analytics questions
            r'\bwhy (is|does|are)\b.*\b(frequent|common|popular|mentioned)\b',
            r'\b(explain|reason|cause)\b.*\b(high|low|frequency|count)\b'
        ]
        
        # Discussion signal patterns
        self.discussion_patterns = [
            # Direct content requests
            r'\b(what (do|are) people (say|think|discuss)|people\'s opinions)\b',
            r'\b(show me|find|give me)\b.*\b(examples?|discussions?|posts?|comments?)\b',
            r'\b(quotes?|conversations?|threads?|actual|real)\b',
            
            # Contextual understanding
            r'\b(context|how|why|when)\b.*\b(people|users|community)\b',
            r'\b(complaints?|praise|criticisms?|problems?|issues?)\b',
            r'\b(experiences?|stories|examples|cases)\b',
            
            # Emotional and qualitative
            r'\b(feel|think|believe|opinion|perspective|view)\b',
            r'\b(frustrated|happy|angry|excited|disappointed|satisfied)\b',
            r'\b(love|hate|like|dislike|enjoy|prefer)\b'
        ]
        
        # Hybrid signal patterns
        self.hybrid_patterns = [
            r'\b(insights?|patterns?|overview|summary)\b',
            r'\bwhat.*\b(main|key|primary|significant)\b',
            r'\b(understand|comprehens\w+|analysis|analyze)\b',
            r'\b(both|combination|together|overall)\b'
        ]
        
        # Command patterns
        self.command_patterns = [
            r'^\s*(help|commands?|\?|/help)\s*$',
            r'^\s*(summary|overview|status)\s*$',
            r'\b(show|explore|full)\b.*\b(discussion|context|thread)\b.*\b[a-z0-9]{6,}\b',
            r'\bfull context for\b',
            r'\bsearch (types?|methods?|options?)\b'
        ]
        
        # Compile patterns for efficiency
        self.compiled_analytics = [re.compile(pattern, re.IGNORECASE) for pattern in self.analytics_patterns]
        self.compiled_discussion = [re.compile(pattern, re.IGNORECASE) for pattern in self.discussion_patterns]
        self.compiled_hybrid = [re.compile(pattern, re.IGNORECASE) for pattern in self.hybrid_patterns]
        self.compiled_command = [re.compile(pattern, re.IGNORECASE) for pattern in self.command_patterns]
    
    def classify_query(self, query: str, available_keywords: List[str] = None) -> QueryClassification:
        """
        Classify a user query to determine optimal response strategy.
        
        Args:
            query: User's question or request
            available_keywords: List of keywords from user's analysis (optional)
        
        Returns:
            QueryClassification with routing recommendation
        """
        if not query or not query.strip():
            return QueryClassification(
                query_type='discussion',
                confidence=0.5,
                target_keywords=[],
                intent_details={},
                suggested_approach='general_search'
            )
        
        query = query.strip()
        
        # Extract potential keywords from query
        target_keywords = self._extract_keywords(query, available_keywords)
        
        # Score each category
        analytics_score = self._score_patterns(query, self.compiled_analytics)
        discussion_score = self._score_patterns(query, self.compiled_discussion)
        hybrid_score = self._score_patterns(query, self.compiled_hybrid)
        command_score = self._score_patterns(query, self.compiled_command)
        
        # Additional scoring factors
        keyword_context_bonus = 0.2 if target_keywords else 0
        analytics_score += keyword_context_bonus if any(kw in query.lower() for kw in ['frequent', 'often', 'sentiment', 'trend']) else 0
        
        # Determine primary classification
        scores = {
            'analytics': analytics_score,
            'discussion': discussion_score,
            'hybrid': hybrid_score,
            'command': command_score
        }
        
        max_score = max(scores.values())
        primary_type = max(scores, key=scores.get)
        
        # Override logic for special cases
        if command_score > 0.7:
            return self._classify_as_command(query, target_keywords)
        
        # If analytics and discussion scores are close, classify as hybrid
        if abs(analytics_score - discussion_score) < 0.3 and max_score > 0.3:
            primary_type = 'hybrid'
            confidence = min(max_score, 0.9)
        else:
            confidence = min(max_score, 0.95)
        
        # Build intent details
        intent_details = self._build_intent_details(query, primary_type, scores, target_keywords)
        
        # Determine suggested approach
        suggested_approach = self._determine_approach(primary_type, intent_details, target_keywords)
        
        return QueryClassification(
            query_type=primary_type,
            confidence=confidence,
            target_keywords=target_keywords,
            intent_details=intent_details,
            suggested_approach=suggested_approach
        )
    
    def _score_patterns(self, query: str, patterns: List[re.Pattern]) -> float:
        """Score query against a set of patterns."""
        matches = 0
        total_strength = 0
        
        for pattern in patterns:
            match = pattern.search(query)
            if match:
                matches += 1
                # Longer matches get higher scores
                match_strength = len(match.group(0)) / len(query)
                total_strength += match_strength
        
        if matches == 0:
            return 0.0
        
        # Normalize score: base score + bonus for multiple matches
        base_score = total_strength / len(patterns)
        match_bonus = min(matches * 0.1, 0.3)  # Bonus for multiple pattern matches
        
        return min(base_score + match_bonus, 1.0)
    
    def _extract_keywords(self, query: str, available_keywords: List[str] = None) -> List[str]:
        """Extract potential keywords from the query."""
        extracted = []
        query_lower = query.lower()
        
        if available_keywords:
            # Check for exact keyword matches
            for keyword in available_keywords:
                if keyword.lower() in query_lower:
                    extracted.append(keyword)
        
        # Extract quoted terms
        quoted_terms = re.findall(r'"([^"]*)"', query)
        extracted.extend(quoted_terms)
        
        # Extract potential single-word keywords (nouns, adjectives)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', query)
        content_words = [w for w in words if w.lower() not in {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 
            'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its',
            'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'she',
            'that', 'this', 'with', 'have', 'from', 'they', 'know', 'want', 'been', 'good',
            'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long',
            'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were', 'what'
        }]
        
        # Add content words that might be keywords
        extracted.extend(content_words[:3])  # Limit to prevent noise
        
        return list(set(extracted))  # Remove duplicates
    
    def _classify_as_command(self, query: str, target_keywords: List[str]) -> QueryClassification:
        """Handle command classification."""
        query_lower = query.lower().strip()
        
        intent_details = {'command_type': 'unknown'}
        
        if query_lower in ['help', 'commands', '?', '/help']:
            intent_details['command_type'] = 'help'
        elif query_lower in ['summary', 'overview', 'status']:
            intent_details['command_type'] = 'summary'
        elif re.search(r'\b(show|explore|full)\b.*\b(discussion|context|thread)\b', query, re.IGNORECASE):
            intent_details['command_type'] = 'explore_discussion'
            # Try to extract content ID
            content_id_match = re.search(r'\b[a-z0-9]{6,}\b', query)
            if content_id_match:
                intent_details['content_id'] = content_id_match.group(0)
        
        return QueryClassification(
            query_type='command',
            confidence=0.9,
            target_keywords=target_keywords,
            intent_details=intent_details,
            suggested_approach='command_handling'
        )
    
    def _build_intent_details(self, query: str, query_type: str, scores: Dict[str, float], 
                            target_keywords: List[str]) -> Dict[str, any]:
        """Build detailed intent information."""
        details = {
            'scores': scores,
            'has_keywords': bool(target_keywords),
            'query_length': len(query.split()),
            'is_question': query.strip().endswith('?')
        }
        
        # Analytics-specific details
        if query_type in ['analytics', 'hybrid']:
            details['analytics_intent'] = []
            
            if re.search(r'\b(frequent|often|count|number|total)\b', query, re.IGNORECASE):
                details['analytics_intent'].append('frequency')
            if re.search(r'\b(sentiment|positive|negative|opinion|feeling)\b', query, re.IGNORECASE):
                details['analytics_intent'].append('sentiment')
            if re.search(r'\b(trend|rising|falling|changing|over time)\b', query, re.IGNORECASE):
                details['analytics_intent'].append('trends')
            if re.search(r'\b(compare|rank|top|most|least)\b', query, re.IGNORECASE):
                details['analytics_intent'].append('comparison')
            if re.search(r'\b(co-occur|together|relationship|correlation)\b', query, re.IGNORECASE):
                details['analytics_intent'].append('relationships')
        
        # Discussion-specific details
        if query_type in ['discussion', 'hybrid']:
            details['discussion_intent'] = []
            
            if re.search(r'\b(examples?|show|find|give)\b', query, re.IGNORECASE):
                details['discussion_intent'].append('examples')
            if re.search(r'\b(context|why|how|when)\b', query, re.IGNORECASE):
                details['discussion_intent'].append('context')
            if re.search(r'\b(complaints?|problems?|issues?|frustrated)\b', query, re.IGNORECASE):
                details['discussion_intent'].append('negative_sentiment')
            if re.search(r'\b(praise|love|positive|happy|satisfied)\b', query, re.IGNORECASE):
                details['discussion_intent'].append('positive_sentiment')
        
        return details
    
    def _determine_approach(self, query_type: str, intent_details: Dict[str, any], 
                          target_keywords: List[str]) -> str:
        """Determine the optimal search and response approach."""
        if query_type == 'command':
            return 'command_handling'
        
        if query_type == 'analytics':
            if target_keywords:
                return 'analytics_driven_search'
            else:
                return 'analytics_overview'
        
        elif query_type == 'discussion':
            if target_keywords:
                return 'keyword_discussion_search'
            else:
                return 'general_discussion_search'
        
        elif query_type == 'hybrid':
            if target_keywords:
                return 'analytics_with_examples'
            else:
                return 'comprehensive_overview'
        
        return 'general_search'
    
    def get_search_strategy(self, classification: QueryClassification) -> Dict[str, any]:
        """
        Get detailed search strategy based on classification.
        
        Args:
            classification: Query classification result
        
        Returns:
            Dictionary with search strategy details
        """
        strategy = {
            'approach': classification.suggested_approach,
            'use_analytics': classification.query_type in ['analytics', 'hybrid'],
            'use_discussions': classification.query_type in ['discussion', 'hybrid'],
            'keywords': classification.target_keywords,
            'confidence': classification.confidence
        }
        
        # Add specific search parameters
        if classification.query_type == 'analytics':
            strategy.update({
                'search_type': 'analytics_driven',
                'include_stats': True,
                'include_examples': 'minimal',
                'focus': 'data_insights'
            })
        
        elif classification.query_type == 'discussion':
            strategy.update({
                'search_type': 'discussion_focused',
                'include_stats': False,
                'include_examples': 'comprehensive',
                'focus': 'conversation_content'
            })
        
        elif classification.query_type == 'hybrid':
            strategy.update({
                'search_type': 'comprehensive',
                'include_stats': True,
                'include_examples': 'representative',
                'focus': 'insights_with_evidence'
            })
        
        return strategy


# Global query classifier instance
query_classifier = QueryClassifier()