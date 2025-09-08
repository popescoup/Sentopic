/**
 * Review Step Component
 * Step 3: Review and confirm collection settings
 */

import React from 'react';
import type { CollectionWizardFormData } from '@/hooks/useCollectionWizardState';

export interface ReviewStepProps {
  /** Current form data */
  formData: CollectionWizardFormData;
  /** Function to update form data */
  updateFormData: (updates: Partial<CollectionWizardFormData>) => void;
  /** Validation errors */
  errors: Record<string, string>;
}

export const ReviewStep: React.FC<ReviewStepProps> = ({
  formData,
  updateFormData,
  errors
}) => {
  return (
    <div className="space-y-6">
      {/* Subreddits Review */}
      <div>
        <h4 className="font-subsection text-text-primary mb-3">
          Target Subreddits ({formData.subreddits.length})
        </h4>
        <div className="flex flex-wrap gap-2">
          {formData.subreddits.map(subreddit => (
            <span
              key={subreddit}
              className="px-3 py-1 bg-hover-blue text-accent rounded-full font-small"
            >
              r/{subreddit}
            </span>
          ))}
        </div>
      </div>

      {/* Parameters Review */}
      <div>
        <h4 className="font-subsection text-text-primary mb-3">
          Collection Parameters
        </h4>
        <div className="bg-panel border border-border-primary rounded-default p-4 space-y-2">
          <div className="flex justify-between">
            <span className="font-body text-text-secondary">Sort Method:</span>
            <span className="font-technical text-text-primary capitalize">
              {formData.parameters.sort_method}
              {formData.parameters.time_period && ` (${formData.parameters.time_period})`}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="font-body text-text-secondary">Posts per Subreddit:</span>
            <span className="font-technical text-text-primary">
              {formData.parameters.posts_count}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="font-body text-text-secondary">Root Comments per Post:</span>
            <span className="font-technical text-text-primary">
              {formData.parameters.root_comments}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="font-body text-text-secondary">Replies per Root Comment:</span>
            <span className="font-technical text-text-primary">
              {formData.parameters.replies_per_root}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="font-body text-text-secondary">Minimum Upvotes:</span>
            <span className="font-technical text-text-primary">
              {formData.parameters.min_upvotes}
            </span>
          </div>
        </div>
      </div>

      {/* Estimated Stats */}
      <div>
        <h4 className="font-subsection text-text-primary mb-3">
          Estimated Collection Size
        </h4>
        <div className="bg-hover-blue border border-accent rounded-default p-4 space-y-2">
          <div className="flex justify-between">
            <span className="font-body text-text-secondary">Total Posts:</span>
            <span className="font-technical text-accent">
              ~{formData.subreddits.length * formData.parameters.posts_count}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="font-body text-text-secondary">Expected Comments:</span>
            <span className="font-technical text-accent">
              ~{formData.subreddits.length * formData.parameters.posts_count * 
              formData.parameters.root_comments * (1 + formData.parameters.replies_per_root)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="font-body text-text-secondary">Estimated Duration:</span>
            <span className="font-technical text-accent">
              {(() => {
                // Time coefficients (lower and upper bounds) in seconds per post for comment collection
                const timeCoefficients = {
                  'new': { min: 0.6, max: 0.8 },
                  'hot': { min: 2.4, max: 3.6 },
                  'rising': { min: 2.4, max: 3.6 },
                  'top': {
                    'hour': { min: 0.7, max: 0.9 },
                    'day': { min: 2.6, max: 3.8 },
                    'week': { min: 3.0, max: 4.4 },
                    'month': { min: 3.0, max: 4.4 },
                    'year': { min: 3.3, max: 4.9 },
                    'all': { min: 3.3, max: 4.9 }
                  },
                  'controversial': {
                    'hour': { min: 0.6, max: 0.8 },
                    'day': { min: 0.7, max: 1.0 },
                    'week': { min: 1.0, max: 1.4 },
                    'month': { min: 1.4, max: 2.1 },
                    'year': { min: 1.9, max: 2.9 },
                    'all': { min: 2.5, max: 3.7 }
                  }
                };
                
                // Get the time coefficient range for comment collection
                let commentTimeRange: { min: number, max: number };
                if (['new', 'hot', 'rising'].includes(formData.parameters.sort_method)) {
                  commentTimeRange = timeCoefficients[formData.parameters.sort_method as keyof typeof timeCoefficients] as { min: number, max: number };
                } else if (['top', 'controversial'].includes(formData.parameters.sort_method) && formData.parameters.time_period) {
                  const methodCoeffs = timeCoefficients[formData.parameters.sort_method as 'top' | 'controversial'];
                  commentTimeRange = methodCoeffs[formData.parameters.time_period as keyof typeof methodCoeffs] || { min: 3.3, max: 4.9 };
                } else {
                  // Fallback for unknown combinations
                  commentTimeRange = { min: 3.3, max: 4.9 };
                }
                
                // Calculate time range per subreddit in seconds
                const postCollectionTime = formData.parameters.posts_count / 100; // 1 second per 100 posts
                const commentCollectionTimeMin = formData.parameters.posts_count * commentTimeRange.min;
                const commentCollectionTimeMax = formData.parameters.posts_count * commentTimeRange.max;
                const totalTimePerSubredditMin = postCollectionTime + commentCollectionTimeMin;
                const totalTimePerSubredditMax = postCollectionTime + commentCollectionTimeMax;
                
                // Calculate total time range for all subreddits
                const totalTimeSecondsMin = formData.subreddits.length * totalTimePerSubredditMin;
                const totalTimeSecondsMax = formData.subreddits.length * totalTimePerSubredditMax;
                
                // Convert to minutes - use floor for min, ceil for max to preserve range
                const estimatedMinutesMin = Math.max(1, Math.floor(totalTimeSecondsMin / 60));
                const estimatedMinutesMax = Math.max(1, Math.ceil(totalTimeSecondsMax / 60));

                // Ensure we always have a range (if they're the same, add 1 to max)
                const finalMin = estimatedMinutesMin;
                const finalMax = estimatedMinutesMin === estimatedMinutesMax ? estimatedMinutesMax + 1 : estimatedMinutesMax;

                // Check if both estimates are under 1 minute
                const totalTimeMinutesMin = totalTimeSecondsMin / 60;
                const totalTimeMinutesMax = totalTimeSecondsMax / 60;

                if (totalTimeMinutesMax < 1) {
                  return "< 1";
                }

                return `${finalMin} - ${finalMax}`;
              })()} minutes
            </span>
          </div>
        </div>
      </div>

      {/* Submit Error */}
      {errors.submit && (
        <div className="p-3 bg-red-50 border border-danger rounded-input">
          <p className="font-body text-danger">{errors.submit}</p>
        </div>
      )}
    </div>
  );
};

export default ReviewStep;