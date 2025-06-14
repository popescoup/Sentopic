"""
Sentopic Analytics Engine

Phase 2 analytics components for keyword analysis, sentiment analysis,
co-occurrence tracking, and trend analysis.
"""

from .engine import AnalyticsEngine

# Global analytics engine instance
analytics_engine = AnalyticsEngine()

__all__ = ['analytics_engine', 'AnalyticsEngine']