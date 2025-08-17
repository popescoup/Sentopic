/**
 * Wizard State Management Hook
 * Complex state management for multi-step form with validation
 */

import { useState, useCallback, useMemo } from 'react';

export interface WizardFormData {
  // Step 1: Research Question
  researchQuestion: string;
  
  // Step 2: Keywords
  keywords: string[];
  
  // Step 3: Collections
  selectedCollections: string[];
  
  // Step 4: Configuration
  projectName: string;
  partialMatching: boolean;
  contextWindow: number;
  generateSummary: boolean;
}

export interface WizardState {
  currentStep: number;
  formData: WizardFormData;
  stepCompletionStatus: Record<number, boolean>;
  visitedSteps: Set<number>;
}

const initialFormData: WizardFormData = {
  researchQuestion: '',
  keywords: [],
  selectedCollections: [],
  projectName: '',
  partialMatching: true,
  contextWindow: 110,
  generateSummary: true,
};

const initialState: WizardState = {
  currentStep: 1,
  formData: initialFormData,
  stepCompletionStatus: {},
  visitedSteps: new Set([1]),
};

export const useWizardState = () => {
  const [state, setState] = useState<WizardState>(initialState);

  // Update form data
  const updateFormData = useCallback((updates: Partial<WizardFormData>) => {
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

  // Step completion validation (must be defined before canGoNext)
  const isStepComplete = useCallback((step: number): boolean => {
    const { formData } = state;
    
    switch (step) {
      case 1: // Research Question - optional, always complete
        return true;
      
      case 2: // Keywords - at least 1 keyword required
        return formData.keywords.length > 0;
      
      case 3: // Collections - at least 1 collection required
        return formData.selectedCollections.length > 0;
      
      case 4: // Configuration - project name required
        return formData.projectName.trim().length > 0;
      
      default:
        return false;
    }
  }, [state.formData]);

  // Navigation helpers
  const canGoBack = useMemo(() => state.currentStep > 1, [state.currentStep]);
  
  // FIXED: Updated logic to handle final step correctly
  const canGoNext = useMemo(() => {
    // For steps 1-3, check if we can advance to next step
    // For step 4 (final), check if current step is complete for submission
    if (state.currentStep === 4) {
      return isStepComplete(state.currentStep); // Can submit if step 4 is complete
    }
    return state.currentStep < 4 && isStepComplete(state.currentStep); // Can advance if not final step and current step complete
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

  // Auto-generate project name if not provided
  const getProjectName = useCallback(() => {
    if (state.formData.projectName.trim()) {
      return state.formData.projectName.trim();
    }
    
    // Auto-generate based on research question or keywords
    if (state.formData.researchQuestion.trim()) {
      const words = state.formData.researchQuestion.trim().split(' ').slice(0, 3);
      return words.join(' ');
    }
    
    if (state.formData.keywords.length > 0) {
      return state.formData.keywords.slice(0, 2).join(' & ');
    }
    
    return `Project ${new Date().toLocaleDateString()}`;
  }, [state.formData]);

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
    getProjectName,
  };
};