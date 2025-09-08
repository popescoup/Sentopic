/**
 * Collection Wizard Validation Utilities
 * Validation functions for collection wizard form data
 */

import type { CollectionWizardFormData } from '@/hooks/useCollectionWizardState';

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

/**
 * Validate a specific wizard step
 */
export const validateCollectionStep = (step: number, formData: CollectionWizardFormData): ValidationResult => {
  const errors: Record<string, string> = {};

  switch (step) {
    case 1: // Subreddit Selection
      if (formData.subreddits.length === 0) {
        errors.subreddits = 'At least one subreddit is required';
      } else if (formData.subreddits.length > 10) {
        errors.subreddits = 'Maximum 10 subreddits allowed';
      }
      break;

    case 2: // Parameters
      const params = formData.parameters;
      
      if (params.posts_count < 1 || params.posts_count > 1000) {
        errors.posts_count = 'Posts count must be between 1 and 1000';
      }

      if (params.root_comments < 0 || params.root_comments > 100) {
        errors.root_comments = 'Root comments must be between 0 and 100';
      }

      if (params.replies_per_root < 0 || params.replies_per_root > 50) {
        errors.replies_per_root = 'Replies per root must be between 0 and 50';
      }

      if (params.min_upvotes < 0) {
        errors.min_upvotes = 'Minimum upvotes cannot be negative';
      }

      if (['top', 'controversial'].includes(params.sort_method) && !params.time_period) {
        errors.time_period = 'Time period is required for top/controversial sorts';
      }
      break;

    case 3: // Review
      // Validate all previous steps
      const step1Validation = validateCollectionStep(1, formData);
      const step2Validation = validateCollectionStep(2, formData);
      
      Object.assign(errors, step1Validation.errors, step2Validation.errors);
      break;

    case 4: // Progress
      // No validation needed for progress step
      break;

    default:
      errors.general = 'Invalid step';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Validate entire form data
 */
export const validateEntireCollectionForm = (formData: CollectionWizardFormData): ValidationResult => {
  const errors: Record<string, string> = {};

  // Validate all steps
  for (let step = 1; step <= 3; step++) {
    const stepValidation = validateCollectionStep(step, formData);
    Object.assign(errors, stepValidation.errors);
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Validate subreddit name format
 */
export const validateSubredditName = (name: string): string | null => {
  if (!name.trim()) {
    return 'Subreddit name cannot be empty';
  }

  // Remove r/ prefix if present
  const cleanName = name.startsWith('r/') ? name.slice(2) : name;

  if (cleanName.length < 1) {
    return 'Subreddit name is too short';
  }

  if (cleanName.length > 21) {
    return 'Subreddit name is too long (max 21 characters)';
  }

  // Basic format validation (letters, numbers, underscores, hyphens)
  if (!/^[a-zA-Z0-9_-]+$/.test(cleanName)) {
    return 'Subreddit name contains invalid characters';
  }

  return null;
};