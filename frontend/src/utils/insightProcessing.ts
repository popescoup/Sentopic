/**
 * Utility functions for processing analysis data into insight card displays
 */

import type { ProjectResponse, KeywordCooccurrence, TrendSummary } from '@/types/api';

/**
 * Formats sentiment value for display
 */
export const formatSentiment = (sentiment: number): string => {
  if (sentiment >= 0) {
    return `+${sentiment.toFixed(2)}`;
  }
  return sentiment.toFixed(2);
};

/**
 * Formats large numbers with commas
 */
export const formatNumber = (num: number): string => {
  return num.toLocaleString();
};

/**
 * Gets the top keyword co-occurrence from analysis data
 */
export const getTopCooccurrence = (project: ProjectResponse): {
  count: number;
  pair: string;
  description: string;
} | null => {
  try {
    if (!project.cooccurrences || project.cooccurrences.length === 0) {
      return {
        count: 0,
        pair: 'No relationships found',
        description: 'No keyword co-occurrences detected in the analysis'
      };
    }

    // Find the co-occurrence with the highest count
    const topCooccurrence = project.cooccurrences.reduce((max, current) => {
      const currentCount = current.cooccurrence_count || 0;
      const maxCount = max.cooccurrence_count || 0;
      return currentCount > maxCount ? current : max;
    });

    const count = topCooccurrence.cooccurrence_count || 0;
    const keyword1 = topCooccurrence.keyword1 || '';
    const keyword2 = topCooccurrence.keyword2 || '';

    if (!keyword1 || !keyword2) {
      return {
        count: 0,
        pair: 'Invalid data',
        description: 'Co-occurrence data appears to be malformed'
      };
    }

    const sentiment = topCooccurrence.avg_sentiment || 0;
    const sentimentText = sentiment >= 0 ? `+${sentiment.toFixed(3)}` : sentiment.toFixed(3);
            
    return {
        count,
        pair: `"${keyword1}" + "${keyword2}"`,
        description: `Top relationship: "${keyword1}" and "${keyword2}" appear together ${formatNumber(count)} times (avg sentiment: ${sentimentText})`
    };
    
  } catch (error) {
    console.error('Error processing co-occurrence data:', error);
    return {
      count: 0,
      pair: 'Error',
      description: 'Unable to process relationship data'
    };
  }
};

/**
 * Gets the overall trend direction from all keyword trends
 */
export const getOverallTrend = (project: ProjectResponse): {
  direction: 'up' | 'down' | 'neutral';
  arrow: string;
  description: string;
} => {
  try {
    if (!project.trend_summaries || Object.keys(project.trend_summaries).length === 0) {
      return {
        direction: 'neutral',
        arrow: '→',
        description: 'No trend data available'
      };
    }

    // Count trend directions across all keywords
    const trendCounts = { up: 0, down: 0, neutral: 0 };

    Object.values(project.trend_summaries).forEach((trendData) => {
      const direction = trendData.trend_direction;
      
      if (direction === 'rising') {
        trendCounts.up++;
      } else if (direction === 'falling') {
        trendCounts.down++;
      } else {
        // 'stable' or 'insufficient_data'
        trendCounts.neutral++;
      }
    });

    // Find the most common trend direction
    let overallDirection: 'up' | 'down' | 'neutral' = 'neutral';
    let maxCount = trendCounts.neutral;

    if (trendCounts.up > maxCount) {
      overallDirection = 'up';
      maxCount = trendCounts.up;
    }
    if (trendCounts.down > maxCount) {
      overallDirection = 'down';
    }

    // Generate description and arrow
    const arrows = { up: '↗', down: '↘', neutral: '→' };
    const descriptions = {
      up: 'Keywords on average have been mentioned with increased frequency over time',
      down: 'Keywords on average have been mentioned with decreased frequency over time',
      neutral: 'Keywords on average have been mentioned with stable frequency over time'
    };

    return {
      direction: overallDirection,
      arrow: arrows[overallDirection],
      description: descriptions[overallDirection]
    };
  } catch (error) {
    console.error('Error processing trend data:', error);
    return {
      direction: 'neutral',
      arrow: '→',
      description: 'Unable to determine trend direction'
    };
  }
};

/**
 * Checks if a project has sufficient data for insights
 */
export const hasInsightData = (project: ProjectResponse): boolean => {
  return project.status === 'completed' && project.stats.total_mentions > 0;
};

/**
 * Gets formatted insight data for all three cards
 */
export const getInsightData = (project: ProjectResponse) => {
  const hasData = hasInsightData(project);

  return {
    overview: {
      totalMentions: hasData ? project.stats.total_mentions : 0,
      avgSentiment: hasData ? project.stats.avg_sentiment : 0,
      description: hasData 
        ? `total keyword mentions with an average sentiment of ${formatSentiment(project.stats.avg_sentiment)}`
        : 'Analysis in progress or no data available'
    },
    relationships: hasData ? getTopCooccurrence(project) : null,
    trends: getOverallTrend(project)
  };
};