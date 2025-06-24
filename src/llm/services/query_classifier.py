"""
Enhanced Query Classifier

Intelligent query routing with smart keyword extraction and natural language understanding.
Replaces rigid regex patterns with flexible NLP-based topic identification.
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import difflib


@dataclass
class QueryClassification:
    """Enhanced classification result for a user query."""
    query_type: str              # 'analytics', 'discussion', 'hybrid', 'command'
    confidence: float            # Confidence score 0.0 to 1.0
    target_keywords: List[str]   # Keywords intelligently extracted from query
    intent_details: Dict[str, any]  # Additional intent information
    suggested_approach: str      # Recommended search/response approach
    keyword_suggestions: List[str] = None  # Suggested similar keywords if exact matches not found


class QueryClassifier:
    """
    Enhanced query classifier with intelligent keyword extraction and natural language understanding.
    
    Key improvements:
    - Smart keyword extraction that identifies main topics
    - Fuzzy matching against available keywords
    - Better intent detection for analytics vs discussion questions
    - Graceful handling when keywords aren't in analysis data
    """
    
    def __init__(self):
        # Enhanced analytics signal patterns
        self.analytics_patterns = [
            # Frequency and statistics
            r'\b(how (often|frequent|much)|frequency|count|number of|total|mentions)\b',
            r'\b(most|least|top|bottom|highest|lowest|frequent)\b',
            r'\b(appears?|occurs?|mentioned|discussed)\b.*\b(often|frequently|much|times)\b',
            r'\b(statistics|stats|data|numbers|metrics)\b',
            r'\b(percentage|percent|ratio|proportion)\b',
            r'\bwhy (is|does|are)\b.*\b(frequent|common|popular|mentioned)\b',
            
            # Sentiment and trends
            r'\b(sentiment|opinion|feeling|attitude)\b.*\b(positive|negative|neutral)\b',
            r'\b(trend|trending|rising|falling|increasing|decreasing|changing)\b',
            r'\b(over time|temporal|timeline|period|recent|lately)\b',
            r'\b(average|mean|median|distribution)\b',
            
            # Comparative analytics
            r'\b(compare|comparison|versus|vs\.?|against|relative)\b',
            r'\b(rank|ranking|order|sort)\b',
            r'\b(correlation|relationship|co-occur|together|associated)\b',
        ]
        
        # Enhanced discussion signal patterns
        self.discussion_patterns = [
            # Direct content requests
            r'\b(what (do|are) people (say|think|discuss)|people\'s opinions)\b',
            r'\b(show me|find|give me)\b.*\b(examples?|discussions?|posts?|comments?)\b',
            r'\b(quotes?|conversations?|threads?|actual|real)\b',
            
            # Natural language discussion requests
            r'\b(tell me about|what.*about|how.*discuss)\b',
            r'\b(what can you tell me)\b',
            r'\b(how are people)\b',
            
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
        
        # Command patterns (much more restrictive now)
        self.command_patterns = [
            r'^\s*(help|commands?|\?|/help)\s*$',
            r'^\s*(summary|overview|status)\s*$',
            r'^\s*(explore|show|full)\s+(discussion|context|thread)\s+[a-z0-9]{6,}\s*$'
        ]
        
        # Compile patterns for efficiency
        self.compiled_analytics = [re.compile(pattern, re.IGNORECASE) for pattern in self.analytics_patterns]
        self.compiled_discussion = [re.compile(pattern, re.IGNORECASE) for pattern in self.discussion_patterns]
        self.compiled_hybrid = [re.compile(pattern, re.IGNORECASE) for pattern in self.hybrid_patterns]
        self.compiled_command = [re.compile(pattern, re.IGNORECASE) for pattern in self.command_patterns]
        
        # Common stop words to filter out
        self.stop_words = {
            'what', 'why', 'how', 'when', 'where', 'who', 'which', 'that', 'this',
            'are', 'is', 'was', 'were', 'do', 'does', 'did', 'can', 'could', 'should',
            'would', 'will', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'about', 'from', 'up', 'out', 'down', 'off', 'over',
            'under', 'again', 'further', 'then', 'once', 'here', 'there', 'all', 'any',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'don',
            'should', 'now', 'people', 'users', 'discussions', 'comments', 'posts',
            'say', 'think', 'feel', 'mention', 'talk', 'discuss', 'discussing',
            'tell', 'me', 'you', 'your', 'my', 'their', 'our', 'his', 'her', 'its'
        }
    
    def classify_query(self, query: str, available_keywords: List[str] = None) -> QueryClassification:
        """
        Enhanced query classification with intelligent keyword extraction.
        
        Args:
            query: User's question or request
            available_keywords: List of keywords from user's analysis (optional)
        
        Returns:
            QueryClassification with smart routing recommendation
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
        
        # Extract keywords intelligently
        target_keywords, keyword_suggestions = self._extract_keywords_intelligently(query, available_keywords)
        
        # Score each category
        analytics_score = self._score_patterns(query, self.compiled_analytics)
        discussion_score = self._score_patterns(query, self.compiled_discussion)
        hybrid_score = self._score_patterns(query, self.compiled_hybrid)
        command_score = self._score_patterns(query, self.compiled_command)
        
        # Boost scores based on keyword context
        if target_keywords:
            # If we found exact matches in available keywords, boost analytics score
            if available_keywords and any(kw in available_keywords for kw in target_keywords):
                analytics_score += 0.2
            
            # If query seems to be asking about content/discussions, boost discussion score
            if any(word in query.lower() for word in ['say', 'discuss', 'think', 'opinion', 'conversation']):
                discussion_score += 0.2
        
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
        if command_score > 0.8:
            return self._classify_as_command(query, target_keywords)
        
        # Enhanced hybrid detection
        if abs(analytics_score - discussion_score) < 0.3 and max_score > 0.3:
            primary_type = 'hybrid'
            confidence = min(max_score + 0.1, 0.9)
        else:
            confidence = min(max_score, 0.95)
        
        # If no keywords found but available_keywords exist, suggest some
        if not target_keywords and available_keywords:
            potential_keywords = self._suggest_keywords_from_query(query, available_keywords)
            if potential_keywords:
                target_keywords = potential_keywords[:2]  # Take top 2 suggestions
                keyword_suggestions = potential_keywords[2:5] if len(potential_keywords) > 2 else []
        
        # Build intent details
        intent_details = self._build_enhanced_intent_details(
            query, primary_type, scores, target_keywords, available_keywords
        )
        
        # Determine suggested approach
        suggested_approach = self._determine_enhanced_approach(
            primary_type, intent_details, target_keywords, keyword_suggestions
        )
        
        return QueryClassification(
            query_type=primary_type,
            confidence=confidence,
            target_keywords=target_keywords,
            intent_details=intent_details,
            suggested_approach=suggested_approach,
            keyword_suggestions=keyword_suggestions
        )
    
    def _extract_keywords_intelligently(self, query: str, available_keywords: List[str] = None) -> Tuple[List[str], List[str]]:
        """
        Intelligently extract keywords from natural language queries.
        
        Returns:
            Tuple of (exact_matches, suggested_similar_keywords)
        """
        extracted_keywords = []
        keyword_suggestions = []
        
        # Step 1: Extract quoted terms (highest priority)
        quoted_terms = re.findall(r'"([^"]*)"', query)
        extracted_keywords.extend(quoted_terms)
        
        # Step 2: Check for exact matches in available keywords
        if available_keywords:
            query_lower = query.lower()
            for keyword in available_keywords:
                if keyword.lower() in query_lower:
                    if keyword not in extracted_keywords:
                        extracted_keywords.append(keyword)
        
        # Step 3: Extract meaningful content words
        content_words = self._extract_content_words(query)
        
        # Step 4: For content words, find fuzzy matches in available keywords
        if available_keywords:
            for word in content_words:
                # Exact substring matches
                matches = [kw for kw in available_keywords if word.lower() in kw.lower() or kw.lower() in word.lower()]
                for match in matches:
                    if match not in extracted_keywords:
                        extracted_keywords.append(match)
                
                # Fuzzy matches for suggestions
                fuzzy_matches = difflib.get_close_matches(word, available_keywords, n=3, cutoff=0.6)
                for match in fuzzy_matches:
                    if match not in extracted_keywords and match not in keyword_suggestions:
                        keyword_suggestions.append(match)
        
        # Step 5: If no exact matches found, use content words as potential keywords
        if not extracted_keywords:
            # Take the most important content words
            important_words = self._rank_content_words(content_words, query)
            extracted_keywords.extend(important_words[:3])  # Top 3 most important words
        
        return extracted_keywords, keyword_suggestions
    
    def _extract_content_words(self, query: str) -> List[str]:
        """Extract meaningful content words from query."""
        # Remove punctuation and split into words
        cleaned_query = re.sub(r'[^\w\s]', ' ', query)
        words = [word.lower().strip() for word in cleaned_query.split() if word.strip()]
        
        # Filter out stop words and short words
        content_words = [
            word for word in words 
            if len(word) >= 3 and word not in self.stop_words
        ]
        
        return content_words
    
    def _rank_content_words(self, content_words: List[str], original_query: str) -> List[str]:
        """Rank content words by importance in the query."""
        if not content_words:
            return []
        
        word_scores = {}
        query_lower = original_query.lower()
        
        for word in content_words:
            score = 0
            
            # Longer words are generally more important
            score += len(word) * 0.1
            
            # Words that appear later in the query might be more important (the main topic)
            word_position = query_lower.rfind(word)
            if word_position != -1:
                # Higher score for words appearing later
                position_score = word_position / len(query_lower)
                score += position_score * 2
            
            # Capitalized words might be proper nouns (more important)
            if any(char.isupper() for char in original_query if word in original_query):
                score += 1
            
            # Words that look like they could be keywords (alphanumeric, no spaces)
            if word.isalnum():
                score += 0.5
            
            word_scores[word] = score
        
        # Sort by score and return
        ranked_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        return [word for word, score in ranked_words]
    
    def _suggest_keywords_from_query(self, query: str, available_keywords: List[str]) -> List[str]:
        """Suggest available keywords that might be relevant to the query."""
        if not available_keywords:
            return []
        
        content_words = self._extract_content_words(query)
        suggestions = []
        
        for keyword in available_keywords:
            keyword_lower = keyword.lower()
            
            # Check for partial matches with any content word
            for word in content_words:
                if (word in keyword_lower or keyword_lower in word or 
                    difflib.SequenceMatcher(None, word, keyword_lower).ratio() > 0.7):
                    if keyword not in suggestions:
                        suggestions.append(keyword)
                        break
        
        # If no good matches, return top keywords by alphabetical order (user can browse)
        if not suggestions:
            suggestions = sorted(available_keywords)[:5]
        
        return suggestions
    
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
    
    def _classify_as_command(self, query: str, target_keywords: List[str]) -> QueryClassification:
        """Handle command classification."""
        query_lower = query.lower().strip()
        
        intent_details = {'command_type': 'unknown'}
        
        if query_lower in ['help', 'commands', '?', '/help']:
            intent_details['command_type'] = 'help'
        elif query_lower in ['summary', 'overview', 'status']:
            intent_details['command_type'] = 'summary'
        elif re.search(r'^\s*(explore|show|full)\s+(discussion|context|thread)\s+[a-z0-9]{6,}\s*$', query, re.IGNORECASE):
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
    
    def _build_enhanced_intent_details(self, query: str, query_type: str, scores: Dict[str, float], 
                                     target_keywords: List[str], available_keywords: List[str] = None) -> Dict[str, any]:
        """Build enhanced intent information."""
        details = {
            'scores': scores,
            'has_keywords': bool(target_keywords),
            'keywords_in_analysis': False,
            'query_length': len(query.split()),
            'is_question': query.strip().endswith('?'),
            'content_words': self._extract_content_words(query)
        }
        
        # Check if extracted keywords are in the analysis
        if target_keywords and available_keywords:
            details['keywords_in_analysis'] = any(kw in available_keywords for kw in target_keywords)
        
        # Analytics-specific details
        if query_type in ['analytics', 'hybrid']:
            details['analytics_intent'] = []
            
            if re.search(r'\b(frequent|often|count|number|total|how much|how many)\b', query, re.IGNORECASE):
                details['analytics_intent'].append('frequency')
            if re.search(r'\b(sentiment|positive|negative|opinion|feeling)\b', query, re.IGNORECASE):
                details['analytics_intent'].append('sentiment')
            if re.search(r'\b(trend|rising|falling|changing|over time)\b', query, re.IGNORECASE):
                details['analytics_intent'].append('trends')
            if re.search(r'\b(compare|rank|top|most|least|versus)\b', query, re.IGNORECASE):
                details['analytics_intent'].append('comparison')
            if re.search(r'\b(co-occur|together|relationship|correlation)\b', query, re.IGNORECASE):
                details['analytics_intent'].append('relationships')
        
        # Discussion-specific details
        if query_type in ['discussion', 'hybrid']:
            details['discussion_intent'] = []
            
            if re.search(r'\b(examples?|show|find|give|tell me about)\b', query, re.IGNORECASE):
                details['discussion_intent'].append('examples')
            if re.search(r'\b(context|why|how|when|what.*about)\b', query, re.IGNORECASE):
                details['discussion_intent'].append('context')
            if re.search(r'\b(complaints?|problems?|issues?|frustrated|negative)\b', query, re.IGNORECASE):
                details['discussion_intent'].append('negative_sentiment')
            if re.search(r'\b(praise|love|positive|happy|satisfied)\b', query, re.IGNORECASE):
                details['discussion_intent'].append('positive_sentiment')
        
        return details
    
    def _determine_enhanced_approach(self, query_type: str, intent_details: Dict[str, any], 
                                   target_keywords: List[str], keyword_suggestions: List[str] = None) -> str:
        """Determine the optimal search and response approach."""
        if query_type == 'command':
            return 'command_handling'
        
        # Check if we have keywords that are in the analysis
        keywords_in_analysis = intent_details.get('keywords_in_analysis', False)
        
        if query_type == 'analytics':
            if keywords_in_analysis:
                return 'analytics_driven_search'
            elif target_keywords:
                return 'analytics_with_fallback'  # Try analytics, fallback to discussion
            else:
                return 'analytics_overview'
        
        elif query_type == 'discussion':
            if target_keywords:
                return 'discussion_search_with_keywords'
            else:
                return 'general_discussion_search'
        
        elif query_type == 'hybrid':
            if keywords_in_analysis:
                return 'analytics_with_examples'
            elif target_keywords:
                return 'hybrid_search_with_fallback'
            else:
                return 'comprehensive_overview'
        
        return 'intelligent_search'  # Default fallback
    
    def get_enhanced_search_strategy(self, classification: QueryClassification) -> Dict[str, any]:
        """
        Get detailed search strategy based on enhanced classification.
        
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
            'keyword_suggestions': classification.keyword_suggestions or [],
            'confidence': classification.confidence,
            'fallback_enabled': True  # Always enable graceful fallbacks
        }
        
        # Add specific search parameters based on approach
        if 'analytics' in classification.suggested_approach:
            strategy.update({
                'search_type': 'analytics_driven',
                'include_stats': True,
                'include_examples': 'minimal' if 'pure' in classification.suggested_approach else 'representative',
                'focus': 'data_insights',
                'enable_fallback': True
            })
        
        elif 'discussion' in classification.suggested_approach:
            strategy.update({
                'search_type': 'discussion_focused',
                'include_stats': classification.query_type == 'hybrid',
                'include_examples': 'comprehensive',
                'focus': 'conversation_content',
                'enable_fallback': True
            })
        
        elif 'hybrid' in classification.suggested_approach:
            strategy.update({
                'search_type': 'comprehensive',
                'include_stats': True,
                'include_examples': 'representative',
                'focus': 'insights_with_evidence',
                'enable_fallback': True
            })
        
        else:  # intelligent_search or fallback
            strategy.update({
                'search_type': 'auto_detect',
                'include_stats': 'auto',
                'include_examples': 'auto',
                'focus': 'best_available',
                'enable_fallback': True
            })
        
        return strategy


# Global enhanced query classifier instance
query_classifier = QueryClassifier()