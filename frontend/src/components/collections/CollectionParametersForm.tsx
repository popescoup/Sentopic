/**
 * Collection Parameters Form Component
 * Configuration form for Reddit collection parameters
 */

import React from 'react';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';
import type { CollectionParams } from '@/types/api';

interface CollectionParametersFormProps {
  parameters: CollectionParams;
  onParametersChange: (parameters: CollectionParams) => void;
  errors: Record<string, string>;
}

// Preset configurations for common use cases
const PARAMETER_PRESETS = {
  quick: {
    name: 'Quick Scan',
    description: 'Fast collection for quick insights',
    params: {
      posts_count: 25,
      root_comments: 5,
      replies_per_root: 2,
      min_upvotes: 1
    }
  },
  balanced: {
    name: 'Balanced',
    description: 'Good balance of coverage and speed',
    params: {
      posts_count: 50,
      root_comments: 10,
      replies_per_root: 3,
      min_upvotes: 1
    }
  },
  comprehensive: {
    name: 'Comprehensive',
    description: 'Deep collection for thorough analysis',
    params: {
      posts_count: 100,
      root_comments: 20,
      replies_per_root: 5,
      min_upvotes: 0
    }
  },
  quality: {
    name: 'Quality Focused',
    description: 'Higher upvote threshold for quality content',
    params: {
      posts_count: 75,
      root_comments: 15,
      replies_per_root: 3,
      min_upvotes: 5
    }
  }
};

export const CollectionParametersForm: React.FC<CollectionParametersFormProps> = ({
  parameters,
  onParametersChange,
  errors
}) => {
  // Update specific parameter
  const updateParameter = <K extends keyof CollectionParams>(
    key: K,
    value: CollectionParams[K]
  ) => {
    const newParameters = { ...parameters, [key]: value };
    
    // Auto-clear time_period if sort method changes to one that doesn't need it
    if (key === 'sort_method' && !['top', 'controversial'].includes(value as string)) {
      newParameters.time_period = undefined;
    }
    
    onParametersChange(newParameters);
  };

  // Apply preset configuration
  const applyPreset = (presetKey: keyof typeof PARAMETER_PRESETS) => {
    const preset = PARAMETER_PRESETS[presetKey];
    onParametersChange({
      ...parameters,
      ...preset.params
    });
  };

  // Calculate estimated collection size
  const calculateEstimatedSize = () => {
    const estimatedComments = parameters.posts_count * parameters.root_comments * (1 + parameters.replies_per_root);
    const estimatedDuration = Math.max(1, Math.ceil(parameters.posts_count / 25)); // Rough estimate
    
    return {
      posts: parameters.posts_count,
      comments: estimatedComments,
      duration: estimatedDuration
    };
  };

  const estimates = calculateEstimatedSize();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="font-subsection text-text-primary mb-2">
          Configure Collection Parameters
        </h3>
        <p className="font-body text-text-secondary">
          Set up how you want to collect Reddit data. These parameters will be applied to all selected subreddits.
        </p>
      </div>

      {/* Sort Method Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block font-medium text-text-primary mb-2">
            Sort Method
          </label>
          <select
            value={parameters.sort_method}
            onChange={(e) => updateParameter('sort_method', e.target.value as any)}
            className="w-full px-3 py-2 border border-border-secondary rounded-input bg-content text-text-primary focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent mx-1"
          >
            <option value="hot">Hot (most active discussions)</option>
            <option value="new">New (most recent posts)</option>
            <option value="rising">Rising (gaining popularity)</option>
            <option value="top">Top (highest scoring)</option>
            <option value="controversial">Controversial (most debated)</option>
          </select>
          <p className="mt-1 text-sm text-text-tertiary">
            {parameters.sort_method === 'hot' && 'Active discussions with high engagement'}
            {parameters.sort_method === 'new' && 'Most recently posted content'}
            {parameters.sort_method === 'rising' && 'Posts gaining popularity quickly'}
            {parameters.sort_method === 'top' && 'Highest scoring posts in time period'}
            {parameters.sort_method === 'controversial' && 'Posts with mixed reactions'}
          </p>
        </div>

        {/* Time Period (conditional) */}
        {['top', 'controversial'].includes(parameters.sort_method) && (
          <div className="mx-1">
            <label className="block font-medium text-text-primary mb-2">
              Time Period *
            </label>
            <select
              value={parameters.time_period || ''}
              onChange={(e) => updateParameter('time_period', (e.target.value || undefined) as CollectionParams['time_period'])}
              className={`w-full px-3 py-2 border rounded-input bg-content text-text-primary focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent ${
                errors.time_period ? 'border-danger' : 'border-border-secondary'
              }`}
            >
              <option value="">Select time period</option>
              <option value="hour">Past Hour</option>
              <option value="day">Past Day</option>
              <option value="week">Past Week</option>
              <option value="month">Past Month</option>
              <option value="year">Past Year</option>
              <option value="all">All Time</option>
            </select>
            {errors.time_period && (
              <p className="mt-1 text-sm text-danger">{errors.time_period}</p>
            )}
          </div>
        )}
      </div>

      {/* Collection Size Parameters */}
      <div>
        <h4 className="font-subsection text-text-primary mb-3">
          Collection Size
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="mx-1">
            <Input
                label="Posts per Subreddit"
                type="number"
                min="1"
                max="1000"
                value={parameters.posts_count}
                onChange={(e) => {
                const value = e.target.value === '' ? '' : parseInt(e.target.value) || 1;
                updateParameter('posts_count', value as any);
                }}
                onBlur={(e) => {
                if (e.target.value === '' || parseInt(e.target.value) < 1) {
                    updateParameter('posts_count', 1);
                }
                }}
                error={errors.posts_count}
                helpText="Number of posts to collect from each subreddit (1-1000)"
                fullWidth
            />
          </div>

          <div className="mx-1">
          <Input
                label="Root Comments per Post"
                type="number"
                min="0"
                max="100"
                value={parameters.root_comments}
                onChange={(e) => {
                  const value = e.target.value === '' ? '' : parseInt(e.target.value) || 0;
                  updateParameter('root_comments', value as any);
                }}
                onBlur={(e) => {
                  if (e.target.value === '' || parseInt(e.target.value) < 0) {
                    updateParameter('root_comments', 0);
                  }
                }}
                error={errors.root_comments}
                helpText="Top-level comments to collect for each post (0-100)"
                fullWidth
            />
            </div>
        </div>
      </div>

      {/* Comment Collection Parameters */}
      <div>
        <h4 className="font-subsection text-text-primary mb-3">
          Comment Collection
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="mx-1">
        <Input
            label="Replies per Root Comment"
            type="number"
            min="0"
            max="50"
            value={parameters.replies_per_root}
            onChange={(e) => {
              const value = e.target.value === '' ? '' : parseInt(e.target.value) || 0;
              updateParameter('replies_per_root', value as any);
            }}
            onBlur={(e) => {
              if (e.target.value === '' || parseInt(e.target.value) < 0) {
                updateParameter('replies_per_root', 0);
              }
            }}
            error={errors.replies_per_root}
            helpText="Number of replies to collect for each root comment (0-50)"
            fullWidth
          />
        </div>

        <div className="mx-1">
        <Input
            label="Minimum Upvotes"
            type="number"
            min="0"
            value={parameters.min_upvotes}
            onChange={(e) => {
              const value = e.target.value === '' ? '' : parseInt(e.target.value) || 0;
              updateParameter('min_upvotes', value as any);
            }}
            onBlur={(e) => {
              if (e.target.value === '' || parseInt(e.target.value) < 0) {
                updateParameter('min_upvotes', 0);
              }
            }}
            error={errors.min_upvotes}
            helpText="Minimum upvotes required for comment inclusion"
            fullWidth
          />
          </div>
        </div>
      </div>

      {/* Estimated Collection Size */}
      <Card className="bg-hover-blue border-accent">
        <h4 className="font-subsection text-text-primary mb-3">
          Estimated Collection Size (Per Subreddit)
        </h4>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-semibold text-accent">
              {estimates.posts.toLocaleString()}
            </div>
            <div className="font-small text-text-secondary">Posts</div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-accent">
              ~{estimates.comments.toLocaleString()}
            </div>
            <div className="font-small text-text-secondary">Comments</div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-accent">
              {estimates.duration}-{estimates.duration * 2}
            </div>
            <div className="font-small text-text-secondary">Minutes</div>
          </div>
        </div>
        <p className="mt-3 font-small text-text-secondary text-center">
          Actual collection size may vary based on subreddit activity and content availability
        </p>
      </Card>
      </div>
  );
};

export default CollectionParametersForm;