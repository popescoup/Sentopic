/**
 * Collection Wizard State Management Hook
 * State management for multi-step collection creation form
 */

import { useState, useCallback, useMemo } from 'react';
import type { CollectionParams } from '@/types/api';

export interface CollectionWizardFormData {
  // Step 1: Subreddit Selection
  subreddits: string[];
  
  // Step 2: Parameters
  parameters: CollectionParams;
}

export interface CollectionWizardState {
  currentStep: number;
  formData: CollectionWizardFormData;
  stepCompletionStatus: Record<number, boolean>;
  visitedSteps: Set<number>;
}

const defaultParameters: CollectionParams = {
  sort_method: 'hot',
  time_period: undefined,
  posts_count: 50,
  root_comments: 10,
  replies_per_root: 3,
  min_upvotes: 1
};

const initialFormData: CollectionWizardFormData = {
  subreddits: [],
  parameters: defaultParameters,
};

const initialState: CollectionWizardState = {
  currentStep: 1,
  formData: initialFormData,
  stepCompletionStatus: {},
  visitedSteps: new Set([1]),
};

export const useCollectionWizardState = () => {
  const [state, setState] = useState<CollectionWizardState>(initialState);

  // Update form data
  const updateFormData = useCallback((updates: Partial<CollectionWizardFormData>) => {
    setState(prev => ({
      ...prev,
      formData: { ...prev.formData, ...updates },
    }));
  }, []);

  // Navigate to specific step
  const goToStep = useCallback((step: number) => {
    setState(prev => ({
      ...prev,
      currentStep: step,
      visitedSteps: new Set([...prev.visitedSteps, step]),
    }));
  }, []);

  // Step completion validation
  const isStepComplete = useCallback((step: number): boolean => {
    const { formData } = state;
    
    switch (step) {
      case 1: // Subreddit Selection - at least 1 subreddit required
        return formData.subreddits.length > 0;
      
      case 2: // Parameters - validate parameter ranges
        const params = formData.parameters;
        return (
          params.posts_count >= 1 && params.posts_count <= 1000 &&
          params.root_comments >= 0 && params.root_comments <= 100 &&
          params.replies_per_root >= 0 && params.replies_per_root <= 50 &&
          params.min_upvotes >= 0 &&
          // Time period required for top/controversial sorts
          (!['top', 'controversial'].includes(params.sort_method) || !!params.time_period)
        );
      
      case 3: // Review - check all previous steps are complete
        return isStepComplete(1) && isStepComplete(2);
      
      case 4: // Progress - always accessible once reached
        return true;
      
      default:
        return false;
    }
  }, [state.formData]);

  // Navigation helpers
  const canGoBack = useMemo(() => state.currentStep > 1, [state.currentStep]);
  
  const canGoNext = useMemo(() => {
    // For steps 1-2, check if we can advance to next step
    // For step 3, check if current step is complete for submission
    // For step 4, no next button needed
    if (state.currentStep === 4) {
      return false; // No next button on progress step
    }
    return isStepComplete(state.currentStep);
  }, [state.currentStep, isStepComplete]);

  // Mark step as complete
  const markStepComplete = useCallback((step: number, isComplete: boolean) => {
    setState(prev => ({
      ...prev,
      stepCompletionStatus: {
        ...prev.stepCompletionStatus,
        [step]: isComplete,
      },
    }));
  }, []);

  // Get step completion status
  const getStepStatus = useCallback((step: number) => {
    const isComplete = isStepComplete(step);
    const isVisited = state.visitedSteps.has(step);
    const isCurrent = state.currentStep === step;
    
    return {
      isComplete,
      isVisited,
      isCurrent,
      isAccessible: step <= state.currentStep || isVisited,
    };
  }, [state.currentStep, state.visitedSteps, isStepComplete]);

  // Calculate overall progress
  const progress = useMemo(() => {
    const completedSteps = [1, 2, 3, 4].filter(step => isStepComplete(step));
    return {
      completedSteps: completedSteps.length,
      totalSteps: 4,
      percentage: (completedSteps.length / 4) * 100,
    };
  }, [isStepComplete]);

  // Reset wizard
  const resetWizard = useCallback(() => {
    setState(initialState);
  }, []);

  return {
    // State
    currentStep: state.currentStep,
    formData: state.formData,
    visitedSteps: state.visitedSteps,
    progress,
    
    // Actions
    updateFormData,
    goToStep,
    markStepComplete,
    resetWizard,
    
    // Helpers
    canGoBack,
    canGoNext,
    isStepComplete,
    getStepStatus,
  };
};