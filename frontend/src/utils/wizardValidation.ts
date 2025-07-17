/**
 * Wizard Validation Logic
 * Centralized validation functions for all wizard steps
 */

import type { WizardFormData } from '@/hooks/useWizardState';

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
  warnings?: Record<string, string>;
}

export interface StepValidationRules {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => string | null;
}

// Individual field validation
export const validateResearchQuestion = (value: string): ValidationResult => {
  const errors: Record<string, string> = {};
  
  // Research question is optional, but if provided, should be meaningful
  if (value.trim() && value.trim().length < 10) {
    errors.researchQuestion = 'Research question should be at least 10 characters if provided';
  }
  
  if (value.length > 500) {
    errors.researchQuestion = 'Research question should not exceed 500 characters';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

export const validateKeywords = (keywords: string[]): ValidationResult => {
  const errors: Record<string, string> = {};
  
  if (keywords.length === 0) {
    errors.keywords = 'At least one keyword is required';
  }
  
  if (keywords.length > 20) {
    errors.keywords = 'Maximum 20 keywords allowed';
  }
  
  // Check for duplicate keywords
  const duplicates = keywords.filter((item, index) => keywords.indexOf(item) !== index);
  if (duplicates.length > 0) {
    errors.keywords = `Duplicate keywords found: ${duplicates.join(', ')}`;
  }
  
  // Check individual keyword length
  const longKeywords = keywords.filter(keyword => keyword.length > 50);
  if (longKeywords.length > 0) {
    errors.keywords = `Keywords too long (max 50 characters): ${longKeywords.join(', ')}`;
  }
  
  // Check for empty keywords
  const emptyKeywords = keywords.filter(keyword => keyword.trim().length === 0);
  if (emptyKeywords.length > 0) {
    errors.keywords = 'Empty keywords are not allowed';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

export const validateCollections = (collectionIds: string[]): ValidationResult => {
  const errors: Record<string, string> = {};
  
  if (collectionIds.length === 0) {
    errors.collections = 'At least one collection must be selected';
  }
  
  if (collectionIds.length > 10) {
    errors.collections = 'Maximum 10 collections allowed';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

export const validateConfiguration = (formData: WizardFormData): ValidationResult => {
  const errors: Record<string, string> = {};
  
  // Project name validation
  if (!formData.projectName.trim()) {
    errors.projectName = 'Project name is required';
  }
  
  if (formData.projectName.length > 100) {
    errors.projectName = 'Project name should not exceed 100 characters';
  }
  
  // Context window validation
  if (formData.contextWindow < 50) {
    errors.contextWindow = 'Context window should be at least 50 words';
  }
  
  if (formData.contextWindow > 500) {
    errors.contextWindow = 'Context window should not exceed 500 words';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Main step validation function
export const validateStep = (step: number, formData: WizardFormData): ValidationResult => {
  switch (step) {
    case 1:
      return validateResearchQuestion(formData.researchQuestion);
    
    case 2:
      return validateKeywords(formData.keywords);
    
    case 3:
      return validateCollections(formData.selectedCollections);
    
    case 4:
      return validateConfiguration(formData);
    
    default:
      return { isValid: false, errors: { general: 'Invalid step' } };
  }
};

// Validate entire form
export const validateAllSteps = (formData: WizardFormData): ValidationResult => {
  const allErrors: Record<string, string> = {};
  
  // Validate each step
  for (let step = 1; step <= 4; step++) {
    const stepResult = validateStep(step, formData);
    Object.assign(allErrors, stepResult.errors);
  }
  
  return {
    isValid: Object.keys(allErrors).length === 0,
    errors: allErrors,
  };
};

// Validation utilities
export const isValidKeyword = (keyword: string): boolean => {
  return keyword.trim().length > 0 && keyword.length <= 50;
};

export const sanitizeKeyword = (keyword: string): string => {
  return keyword.trim().toLowerCase();
};

export const isValidProjectName = (name: string): boolean => {
  return name.trim().length > 0 && name.length <= 100;
};

// Business logic validation
export const validateKeywordBusinessLogic = (keywords: string[]): ValidationResult => {
  const errors: Record<string, string> = {};
  const warnings: Record<string, string> = {};
  
  // Check for very common words that might not be useful
  const commonWords = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'];
  const foundCommonWords = keywords.filter(keyword => 
    commonWords.includes(keyword.toLowerCase())
  );
  
  if (foundCommonWords.length > 0) {
    warnings.keywords = `Common words detected: ${foundCommonWords.join(', ')}. Consider more specific keywords.`;
  }
  
  // Check for single character keywords
  const singleCharKeywords = keywords.filter(keyword => keyword.trim().length === 1);
  if (singleCharKeywords.length > 0) {
    errors.keywords = `Single character keywords are not recommended: ${singleCharKeywords.join(', ')}`;
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    warnings,
  };
};

// Error message formatting
export const formatValidationError = (field: string, error: string): string => {
  return `${field.charAt(0).toUpperCase() + field.slice(1)}: ${error}`;
};

export const getFieldErrorMessage = (errors: Record<string, string>, field: string): string | undefined => {
  return errors[field];
};

export const hasFieldError = (errors: Record<string, string>, field: string): boolean => {
  return !!errors[field];
};