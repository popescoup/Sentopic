/**
 * Collection Progress Hook
 * Manages simulated progress for collection process
 */

import { useState, useEffect, useCallback } from 'react';
import { useCollectionBatchStatus } from '@/hooks/useApi';
import type { CollectionParams } from '@/types/api';

export type CollectionPhase = 'posts' | 'comments' | 'processing' | 'complete';

export interface SubredditProgress {
  subreddit: string;
  status: 'pending' | 'collecting_posts' | 'collecting_comments' | 'completed';
  progress: number;
}

export interface CollectionProgressState {
  overallProgress: number;
  currentPhase: CollectionPhase;
  currentSubreddit: string | null;
  currentSubredditIndex: number;
  subredditProgresses: SubredditProgress[];
  statusMessage: string;
  isComplete: boolean;
}

export const useCollectionProgress = (
    batchId: string | null,
    subreddits: string[],
    collectionParams: CollectionParams,
    isActive: boolean,
    batchStatus?: any // Add batchStatus as a parameter
  ): CollectionProgressState => {
  const [overallProgress, setOverallProgress] = useState(0);
  const [currentPhase, setCurrentPhase] = useState<CollectionPhase>('posts');
  const [currentSubredditIndex, setCurrentSubredditIndex] = useState(0);
  const [subredditProgresses, setSubredditProgresses] = useState<SubredditProgress[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [hasReachedBuffer, setHasReachedBuffer] = useState(false);
  const [bufferStartTime, setBufferStartTime] = useState<number | null>(null);

  // Initialize subreddit progresses
  useEffect(() => {
    if (subreddits.length > 0) {
      const initialProgresses = subreddits.map(subreddit => ({
        subreddit,
        status: 'pending' as const,
        progress: 0
      }));
      setSubredditProgresses(initialProgresses);
    }
  }, [subreddits]);

  // Check if we have a temporary batch ID (timeout scenario)
  const isTempBatchId = batchId?.startsWith('temp-');
  
  // If we have a temp batch ID, we won't get real status updates
  // In this case, we'll just run the simulation to completion
  useEffect(() => {
    if (isTempBatchId) {
      console.log('Using temporary batch ID - running simulation only');
    }
  }, [isTempBatchId]);

  // Calculate time coefficients based on sort method
  const getTimeCoefficient = useCallback(() => {
    const { sort_method, time_period } = collectionParams;
    
    const timeCoefficients: Record<string, any> = {
      'new': 0.65,
      'hot': 2.7,
      'rising': 2.7,
      'top': {
        'hour': 0.75,
        'day': 2.9,
        'week': 3.4,
        'month': 3.4,
        'year': 3.8,
        'all': 3.8
      },
      'controversial': {
        'hour': 0.65,
        'day': 0.75,
        'week': 0.9,
        'month': 1.55,
        'year': 2.1,
        'all': 2.8
      }
    };

    if (['new', 'hot', 'rising'].includes(sort_method)) {
      return timeCoefficients[sort_method];
    } else if (['top', 'controversial'].includes(sort_method) && time_period) {
      return timeCoefficients[sort_method][time_period] || 3.7;
    }
    return 3.7; // Fallback
  }, [collectionParams]);

  // Calculate timing for each subreddit
  const calculateSubredditTiming = useCallback(() => {
    const commentTimePerPost = getTimeCoefficient();
    const postCollectionTime = collectionParams.posts_count / 100; // 1 second per 100 posts
    const commentCollectionTime = collectionParams.posts_count * commentTimePerPost;
    const totalTimePerSubreddit = postCollectionTime + commentCollectionTime;
    
    return {
      postTime: postCollectionTime * 1000, // Convert to milliseconds
      commentTime: commentCollectionTime * 1000,
      totalTime: totalTimePerSubreddit * 1000
    };
  }, [collectionParams, getTimeCoefficient]);

  // Generate status message
  const getStatusMessage = useCallback((
    phase: CollectionPhase,
    subreddit: string | null,
    inBuffer: boolean
  ): string => {
    if (phase === 'complete') {
      return 'Collection completed successfully!';
    }
    
    if (inBuffer) {
      return phase === 'posts' ? 'Processing posts...' : 'Processing comments...';
    }
    
    if (!subreddit) {
      return 'Initializing collection...';
    }
    
    switch (phase) {
      case 'posts':
        return `Retrieving r/${subreddit} posts`;
      case 'comments':
        return `Retrieving r/${subreddit} comments`;
      case 'processing':
        return 'Processing collected data...';
      default:
        return 'Starting collection...';
    }
  }, []);

  const statusMessage = getStatusMessage(
    currentPhase,
    currentSubredditIndex < subreddits.length ? subreddits[currentSubredditIndex] : null,
    hasReachedBuffer
  );

  // Main progress simulation effect
  useEffect(() => {
    if (!isActive || subreddits.length === 0 || isComplete) return;

    const timing = calculateSubredditTiming();
    const totalSubreddits = subreddits.length;
    const progressPerSubreddit = 90 / totalSubreddits; // Reserve 10% for buffer
    
    let timeouts: NodeJS.Timeout[] = [];
    let currentTime = 0;

    // Process each subreddit
    for (let i = 0; i < totalSubreddits; i++) {
      const subredditStartProgress = i * progressPerSubreddit;
      
      // Posts phase (quick)
      const postsEndTime = currentTime + timing.postTime;
      const postsProgress = subredditStartProgress + (progressPerSubreddit * 0.02); // 2% of subreddit progress
      
      timeouts.push(
        setTimeout(() => {
          // Check if backend completed early
          if (batchStatus?.status === 'completed') return;
          
          setCurrentSubredditIndex(i);
          setCurrentPhase('posts');
          setOverallProgress(Math.min(postsProgress, 90));
          
          setSubredditProgresses(prev => {
            const updated = [...prev];
            if (updated[i]) {
              updated[i].status = 'collecting_posts';
              updated[i].progress = 5;
            }
            return updated;
          });
        }, currentTime)
      );

      // Comments phase (slow, takes 98% of time)
      const commentSteps = 10; // Smooth progression
      const commentTimePerStep = timing.commentTime / commentSteps;
      const commentProgressPerStep = (progressPerSubreddit * 0.98) / commentSteps;
      
      for (let step = 1; step <= commentSteps; step++) {
        const stepTime = postsEndTime + (step * commentTimePerStep);
        const stepProgress = postsProgress + (step * commentProgressPerStep);
        
        timeouts.push(
          setTimeout(() => {
            // Check if backend completed early
            if (batchStatus?.status === 'completed') return;
            
            setCurrentPhase('comments');
            setOverallProgress(Math.min(stepProgress, 90));
            
            setSubredditProgresses(prev => {
              const updated = [...prev];
              if (updated[i]) {
                updated[i].status = 'collecting_comments';
                updated[i].progress = 5 + (step * 9.5); // 5% to 100%
              }
              return updated;
            });
          }, stepTime)
        );
      }

      // Mark subreddit as completed
      const subredditEndTime = currentTime + timing.totalTime;
      timeouts.push(
        setTimeout(() => {
          // Check if backend completed early
          if (batchStatus?.status === 'completed') return;
          
          setSubredditProgresses(prev => {
            const updated = [...prev];
            if (updated[i]) {
              updated[i].status = 'completed';
              updated[i].progress = 100;
            }
            return updated;
          });
        }, subredditEndTime)
      );

      currentTime = subredditEndTime;
    }

    // Enter buffer zone at 90%
    timeouts.push(
      setTimeout(() => {
        // Check if backend completed early
        if (batchStatus?.status === 'completed') return;
        
        setHasReachedBuffer(true);
        setBufferStartTime(Date.now());
        setCurrentPhase('posts');
        setOverallProgress(90);
      }, currentTime)
    );

    // Buffer zone: 90% to 95% (Processing posts - 5 seconds)
    for (let i = 91; i <= 95; i++) {
      timeouts.push(
        setTimeout(() => {
          // Check if backend completed early
          if (batchStatus?.status === 'completed') return;
          
          setOverallProgress(i);
        }, currentTime + ((i - 90) * 10000)) // 10 second per percent
      );
    }

    // Buffer zone: 96% to 99% (Processing comments - 1% every 2 minutes)
    // IMPORTANT: Only go up to 99% in simulation, wait for backend at 99%
    for (let i = 96; i <= 99; i++) {  // Changed from 100 to 99
        timeouts.push(
          setTimeout(() => {
            // Check if backend completed early
            if (batchStatus?.status === 'completed') return;
            
            setCurrentPhase('comments');
            setOverallProgress(i);
          }, currentTime + 5000 + ((i - 95) * 120000)) // 5 seconds + 2 minutes per percent
        );
      }
  
      // Auto-complete ONLY for temp batch IDs (timeout scenarios)
      // For real batch IDs, we'll wait at 99% until backend completes
      if (isTempBatchId) {
        timeouts.push(
          setTimeout(() => {
            if (!isComplete) {
              console.log('Simulation completed with temp batch ID - auto-completing to 100%');
              setOverallProgress(100);
              setCurrentPhase('complete');
              setIsComplete(true);
              setSubredditProgresses(prev => 
                prev.map(sp => ({ ...sp, status: 'completed', progress: 100 }))
              );
            }
          }, currentTime + 5000 + (4 * 120000) + 5000) // 5 seconds after reaching 99%
        );
      }
      // If NOT a temp batch ID, the simulation will stay at 99% until the backend completion effect triggers

    // Cleanup function
    return () => {
      timeouts.forEach(timeout => clearTimeout(timeout));
    };
}, [isActive, subreddits, collectionParams, calculateSubredditTiming, batchStatus?.status, isComplete, isTempBatchId]);

  // Handle actual completion from backend
  useEffect(() => {
    // Skip backend status check if we have a temp batch ID
    if (isTempBatchId) {
      return;
    }
    
    console.log('Checking batch status:', batchStatus?.status, 'isComplete:', isComplete);
    
    if (batchStatus?.status === 'completed' && !isComplete) {
      console.log('Backend completed! Jumping to 100%');
      
      // Immediately jump to 100% when backend completes
      setOverallProgress(100);
      setCurrentPhase('complete');
      setIsComplete(true);
      setHasReachedBuffer(false);
      
      // Mark all subreddits as completed immediately
      setSubredditProgresses(prev => 
        prev.map(sp => ({ ...sp, status: 'completed', progress: 100 }))
      );
      
      // Clear the current subreddit index
      setCurrentSubredditIndex(subreddits.length);
    }
  }, [batchStatus?.status, isComplete, subreddits.length, isTempBatchId]);

  return {
    overallProgress,
    currentPhase,
    currentSubreddit: currentSubredditIndex < subreddits.length ? subreddits[currentSubredditIndex] : null,
    currentSubredditIndex,
    subredditProgresses,
    statusMessage,
    isComplete
  };
};