"""
Sentiment Analysis Module

Handles VADER sentiment analysis with configurable context windows
around detected keywords.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from typing import List, Tuple


class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def extract_context_window(self, text: str, keyword: str, position: int, 
                              window_words: int = 5) -> str:
        """
        Extract context window around a keyword in text.
        
        Args:
            text: Full text content
            keyword: The keyword found in the text
            position: Character position of the keyword in text
            window_words: Number of words to include before and after keyword
        
        Returns:
            Context string with keyword and surrounding words
        """
        # Split text into words while preserving word boundaries
        words = text.split()
        
        # Find the word index that contains our keyword position
        keyword_word_index = self._find_keyword_word_index(text, position, words)
        
        if keyword_word_index == -1:
            # Fallback: use the keyword itself if we can't find the exact position
            return keyword
        
        # Calculate context window boundaries
        start_index = max(0, keyword_word_index - window_words)
        end_index = min(len(words), keyword_word_index + 1 + window_words)
        
        # Extract context words
        context_words = words[start_index:end_index]
        
        return ' '.join(context_words)
    
    def _find_keyword_word_index(self, text: str, char_position: int, words: List[str]) -> int:
        """
        Find the word index that contains the character at the given position.
        
        Args:
            text: Full text content
            char_position: Character position in text
            words: List of words from text.split()
        
        Returns:
            Word index, or -1 if not found
        """
        current_pos = 0
        
        for i, word in enumerate(words):
            word_start = current_pos
            word_end = current_pos + len(word)
            
            # Check if our character position falls within this word
            if word_start <= char_position < word_end:
                return i
            
            # Move to next word (account for space)
            current_pos = word_end + 1
        
        return -1
    
    def analyze_sentiment(self, context: str) -> float:
        """
        Analyze sentiment of the given context text.
        
        Args:
            context: Text to analyze for sentiment
        
        Returns:
            Compound sentiment score from -1 (negative) to +1 (positive)
        """
        scores = self.analyzer.polarity_scores(context)
        return scores['compound']
    
    def analyze_keyword_sentiment(self, text: str, keyword: str, position: int,
                                 window_words: int =5) -> Tuple[str, float]:
        """
        Extract context around keyword and analyze its sentiment.
        
        Args:
            text: Full text content
            keyword: The keyword found in the text
            position: Character position of the keyword in text
            window_words: Number of words to include before and after keyword
        
        Returns:
            Tuple of (context_text, sentiment_score)
        """
        context = self.extract_context_window(text, keyword, position, window_words)
        sentiment = self.analyze_sentiment(context)
        
        return context, sentiment


# Global sentiment analyzer instance
sentiment_analyzer = SentimentAnalyzer()