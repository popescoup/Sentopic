/**
 * Collection Progress Component
 * Real-time progress monitoring during collection
 */

import React from 'react';
import Card from '@/components/ui/Card';
import LoadingSpinner from '@/components/layout/LoadingSpinner';
import type { CollectionBatchStatusResponse } from '@/types/api';

interface CollectionProgressProps {
  batchId: string;
  batchStatus?: CollectionBatchStatusResponse;
  isLoading: boolean;
}

export const CollectionProgress: React.FC<CollectionProgressProps> = ({
  batchId,
  batchStatus,
  isLoading
}) => {
  // Helper function to format time
  const formatTime = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleTimeString();
    } catch {
      return 'Unknown';
    }
  };

  // Helper function to get status styling
  const getStatusStyling = (status: string) => {
    switch (status) {
      case 'completed':
        return {
          color: 'text-success',
          bg: 'bg-green-100',
          icon: '✅'
        };
      case 'running':
        return {
          color: 'text-accent',
          bg: 'bg-blue-100',
          icon: '🔄'
        };
      case 'failed':
        return {
          color: 'text-danger',
          bg: 'bg-red-100',
          icon: '❌'
        };
      default:
        return {
          color: 'text-text-tertiary',
          bg: 'bg-gray-100',
          icon: '⏳'
        };
    }
  };

  // Loading state
  if (isLoading && !batchStatus) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <LoadingSpinner size="lg" />
        <p className="mt-4 font-body text-text-secondary">
          Initializing collection...
        </p>
      </div>
    );
  }

  // Error state
  if (!batchStatus) {
    return (
      <div className="text-center py-12">
        <div className="text-danger mb-4">
          <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="font-subsection text-danger mb-2">
          Unable to Load Progress
        </h3>
        <p className="font-body text-text-secondary">
          Could not retrieve collection status. The collection may still be running in the background.
        </p>
      </div>
    );
  }

  const overallStyling = getStatusStyling(batchStatus.status);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h3 className="font-subsection text-text-primary mb-2">
          Collection in Progress
        </h3>
        <p className="font-body text-text-secondary">
          Collecting data from {batchStatus.collections.length} subreddit{batchStatus.collections.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Overall Progress */}
      <Card className={`${overallStyling.bg} border-2 border-current ${overallStyling.color}`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <span className="text-2xl mr-3">{overallStyling.icon}</span>
            <div>
              <h4 className="font-subsection text-text-primary">
                Overall Progress
              </h4>
              <p className="font-body text-text-secondary capitalize">
                Status: {batchStatus.status}
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-semibold text-text-primary">
              {batchStatus.progress_percentage}%
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
            style={{ width: `${batchStatus.progress_percentage}%` }}
          />
        </div>

        {/* Status Details */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="font-semibold text-success">
              {batchStatus.completed_subreddits.length}
            </div>
            <div className="font-small text-text-secondary">Completed</div>
          </div>
          <div>
            <div className="font-semibold text-danger">
              {batchStatus.failed_subreddits.length}
            </div>
            <div className="font-small text-text-secondary">Failed</div>
          </div>
          <div>
            <div className="font-semibold text-text-primary">
              {batchStatus.collections.length - batchStatus.completed_subreddits.length - batchStatus.failed_subreddits.length}
            </div>
            <div className="font-small text-text-secondary">Remaining</div>
          </div>
        </div>
      </Card>

      {/* Current Activity */}
      {batchStatus.status === 'running' && batchStatus.current_subreddit && (
        <Card className="bg-hover-blue border-accent">
          <div className="flex items-center">
            <div className="animate-spin text-accent text-xl mr-3">⚡</div>
            <div>
              <h4 className="font-subsection text-text-primary">
                Currently Processing
              </h4>
              <p className="font-body text-accent">
                r/{batchStatus.current_subreddit}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Individual Subreddit Progress */}
      <div>
        <h4 className="font-subsection text-text-primary mb-3">
          Individual Subreddit Progress
        </h4>
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {batchStatus.collections.map((collection) => {
            const collectionStyling = getStatusStyling(collection.status);
            const progressPercentage = collection.posts_requested > 0 
              ? Math.round((collection.posts_collected / collection.posts_requested) * 100)
              : 0;

            return (
              <Card key={collection.id} className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <span className="text-lg mr-2">{collectionStyling.icon}</span>
                    <div>
                      <h5 className="font-subsection text-text-primary">
                        r/{collection.subreddit}
                      </h5>
                      <p className={`font-small ${collectionStyling.color} capitalize`}>
                        {collection.status}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-technical text-text-primary">
                      {collection.posts_collected}/{collection.posts_requested}
                    </div>
                    <div className="font-small text-text-secondary">
                      posts
                    </div>
                  </div>
                </div>

                {/* Individual Progress Bar */}
                {collection.status === 'running' && (
                  <div className="w-full bg-border-primary rounded-full h-2 mb-2">
                    <div 
                      className="bg-accent h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progressPercentage}%` }}
                    />
                  </div>
                )}

                {/* Collection Stats */}
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">
                    Comments: <span className="text-text-primary font-technical">
                      {collection.comments_collected.toLocaleString()}
                    </span>
                  </span>
                  {collection.status === 'completed' && (
                    <span className="text-success">
                      ✓ Completed
                    </span>
                  )}
                  {collection.status === 'failed' && collection.error_message && (
                    <span className="text-danger text-xs" title={collection.error_message}>
                      ⚠ Error
                    </span>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Timing Information */}
      <Card className="bg-panel">
        <h4 className="font-subsection text-text-primary mb-3">
          Collection Details
        </h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-text-secondary">Started:</span>
            <div className="font-technical text-text-primary">
              {formatTime(batchStatus.started_at)}
            </div>
          </div>
          {batchStatus.estimated_completion && batchStatus.status === 'running' && (
            <div>
              <span className="text-text-secondary">Estimated Completion:</span>
              <div className="font-technical text-text-primary">
                {formatTime(batchStatus.estimated_completion)}
              </div>
            </div>
          )}
          <div>
            <span className="text-text-secondary">Batch ID:</span>
            <div className="font-technical text-text-primary text-xs">
              {batchId}
            </div>
          </div>
          <div>
            <span className="text-text-secondary">Collections:</span>
            <div className="font-technical text-text-primary">
              {batchStatus.collections.length} subreddit{batchStatus.collections.length !== 1 ? 's' : ''}
            </div>
          </div>
        </div>
      </Card>

      {/* Completion Message */}
      {batchStatus.status === 'completed' && (
        <Card className="bg-green-50 border-success text-center">
          <div className="text-success text-4xl mb-2">🎉</div>
          <h4 className="font-subsection text-success mb-2">
            Collection Completed Successfully!
          </h4>
          <p className="font-body text-text-secondary mb-4">
            All {batchStatus.completed_subreddits.length} subreddit{batchStatus.completed_subreddits.length !== 1 ? 's have' : ' has'} been collected successfully.
            You can now use {batchStatus.completed_subreddits.length !== 1 ? 'these collections' : 'this collection'} in your analysis projects.
          </p>
          <div className="text-sm text-text-secondary">
            This modal will close automatically in a few seconds...
          </div>
        </Card>
      )}

      {/* Failure Summary */}
      {batchStatus.status === 'completed' && batchStatus.failed_subreddits.length > 0 && (
        <Card className="bg-yellow-50 border-yellow-400">
          <h4 className="font-subsection text-yellow-700 mb-2">
            ⚠ Partial Collection
          </h4>
          <p className="font-body text-text-secondary mb-2">
            Some subreddits failed to collect:
          </p>
          <div className="flex flex-wrap gap-2">
            {batchStatus.failed_subreddits.map(subreddit => (
              <span
                key={subreddit}
                className="px-2 py-1 bg-yellow-200 text-yellow-800 rounded font-small"
              >
                r/{subreddit}
              </span>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default CollectionProgress;