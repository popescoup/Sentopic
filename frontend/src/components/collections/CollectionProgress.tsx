/**
 * Collection Progress Component
 * Simulated progress monitoring during collection
 */

import React from 'react';
import Card from '@/components/ui/Card';
import { useCollectionProgress } from '@/hooks/useCollectionProgress';
import type { CollectionBatchStatusResponse, CollectionParams } from '@/types/api';

interface CollectionProgressProps {
  batchId: string;
  batchStatus?: CollectionBatchStatusResponse;
  isLoading: boolean;
  subreddits: string[];
  collectionParams: CollectionParams;
}

export const CollectionProgress: React.FC<CollectionProgressProps> = ({
  batchId,
  batchStatus,
  isLoading,
  subreddits,
  collectionParams
}) => {
  // Use simulated progress hook
  const {
    overallProgress,
    currentPhase,
    currentSubreddit,
    subredditProgresses,
    statusMessage,
    isComplete
  } = useCollectionProgress(
    batchId,
    subreddits,
    collectionParams,
    true, // isActive
    batchStatus // Pass batchStatus
  );

  // Helper function to get status styling
  const getStatusStyling = (status: string) => {
    switch (status) {
      case 'completed':
        return {
          color: 'text-success',
          bg: 'bg-green-100'
        };
      case 'collecting_posts':
      case 'collecting_comments':
        return {
          color: 'text-accent',
          bg: 'bg-blue-100'
        };
      case 'pending':
      default:
        return {
          color: 'text-text-tertiary',
          bg: 'bg-gray-100'
        };
    }
  };

  const overallStyling = isComplete 
    ? { color: 'text-success', bg: 'bg-green-100' }
    : { color: 'text-accent', bg: 'bg-blue-100' };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h3 className="font-subsection text-text-primary mb-2">
          Collection in Progress
        </h3>
        <p className="font-body text-text-secondary">
          Collecting data from {subreddits.length} subreddit{subreddits.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Overall Progress */}
      <Card className={`${overallStyling.bg} border-2 border-current ${overallStyling.color}`}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h4 className="font-subsection text-text-primary">
              Overall Progress
            </h4>
            <p className="font-body text-text-secondary capitalize">
              {statusMessage}
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-semibold text-text-primary">
              {Math.round(overallProgress)}%
            </div>
            <div className="font-small text-text-secondary">
              Complete
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-border-primary rounded-full h-3 mb-4">
          <div 
            className="bg-accent h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${overallProgress}%` }}
          />
        </div>

        {/* Status Details */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="font-semibold text-success">
              {subredditProgresses.filter(sp => sp.status === 'completed').length}
            </div>
            <div className="font-small text-text-secondary">Completed</div>
          </div>
          <div>
            <div className="font-semibold text-accent">
              {subredditProgresses.filter(sp => 
                sp.status === 'collecting_posts' || sp.status === 'collecting_comments'
              ).length}
            </div>
            <div className="font-small text-text-secondary">Processing</div>
          </div>
          <div>
            <div className="font-semibold text-text-primary">
              {subredditProgresses.filter(sp => sp.status === 'pending').length}
            </div>
            <div className="font-small text-text-secondary">Remaining</div>
          </div>
        </div>
      </Card>

      {/* Current Activity */}
      {!isComplete && currentSubreddit && (
        <Card className="bg-hover-blue border-accent">
          <div className="flex items-center">
            <div className="mr-3">
              <svg className="animate-spin h-5 w-5 text-accent" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <div>
              <h4 className="font-subsection text-text-primary">
                Currently Processing
              </h4>
              <p className="font-body text-accent">
                r/{currentSubreddit}
              </p>
              <p className="font-small text-text-secondary mt-1">
                {currentPhase === 'posts' ? 'Retrieving posts...' : 'Retrieving comments...'}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Individual Subreddit Progress - only show for multiple subreddits */}
      {subreddits.length > 1 && (
        <div>
          <h4 className="font-subsection text-text-primary mb-3">
            Individual Subreddit Progress
          </h4>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {subredditProgresses.map((subredditProgress) => {
              const styling = getStatusStyling(subredditProgress.status);

              return (
                <Card key={subredditProgress.subreddit} className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h5 className="font-subsection text-text-primary">
                        r/{subredditProgress.subreddit}
                      </h5>
                      <p className={`font-small ${styling.color} capitalize`}>
                        {subredditProgress.status === 'collecting_posts' ? 'Retrieving posts' :
                         subredditProgress.status === 'collecting_comments' ? 'Retrieving comments' :
                         subredditProgress.status === 'completed' ? 'Completed' : 'Pending'}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="font-technical text-text-primary">
                        {Math.round(subredditProgress.progress)}%
                      </div>
                    </div>
                  </div>

                  {/* Individual Progress Bar */}
                  {(subredditProgress.status === 'collecting_posts' || 
                    subredditProgress.status === 'collecting_comments') && (
                    <div className="w-full bg-border-primary rounded-full h-2">
                      <div 
                        className="bg-accent h-2 rounded-full transition-all duration-300"
                        style={{ width: `${subredditProgress.progress}%` }}
                      />
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* Completion Message */}
      {isComplete && (
        <Card className="bg-green-50 border-success text-center">
          <h4 className="font-subsection text-success mb-4">
            Collection Completed Successfully!
          </h4>
          <p className="font-body text-text-secondary mb-4">
            All {subreddits.length} subreddit{subreddits.length !== 1 ? 's have' : ' has'} been collected successfully.
            You can now use {subreddits.length !== 1 ? 'these collections' : 'this collection'} in your analysis projects.
          </p>
          <div className="text-sm text-text-secondary">
            This modal will close automatically in a few seconds...
          </div>
        </Card>
      )}
    </div>
  );
};

export default CollectionProgress;