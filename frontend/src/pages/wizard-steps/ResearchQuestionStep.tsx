/**
 * Research Question Step Component
 * Step 1: Research question input interface
 */

import React from 'react';
import { Textarea } from '@/components/ui/Input';
import type { WizardFormData } from '@/hooks/useWizardState';

export interface ResearchQuestionStepProps {
  /** Current form data */
  formData: WizardFormData;
  /** Function to update form data */
  updateFormData: (updates: Partial<WizardFormData>) => void;
  /** Validation errors */
  errors: Record<string, string>;
}

export const ResearchQuestionStep: React.FC<ResearchQuestionStepProps> = ({
  formData,
  updateFormData,
  errors
}) => {
  const handleResearchQuestionChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    updateFormData({ researchQuestion: event.target.value });
  };

  const characterCount = formData.researchQuestion.length;
  const maxCharacters = 500;
  const isNearLimit = characterCount > maxCharacters * 0.8;

  return (
    <div className="max-w-3xl mx-auto">
      {/* Step Introduction */}
      <div className="mb-8">
        <h3 className="font-subsection text-text-primary mb-3">
          What would you like to research?
        </h3>
        <p className="font-body text-text-secondary">
        This helps AI suggest better keywords in the next step and generates more relevant insights from your analysis.
        </p>
      </div>

      {/* Research Question Input */}
      <div className="mb-6">
        <Textarea
          label="Research Question"
          value={formData.researchQuestion}
          onChange={handleResearchQuestionChange}
          placeholder="e.g., How do users discuss the impact of remote work on productivity and work-life balance?"
          rows={4}
          error={errors.researchQuestion}
          fullWidth
          resize="vertical"
        />
        
        {/* Character Count */}
        <div className="mt-2 flex justify-between items-center">
          <div className="font-body text-text-tertiary text-sm">
            {characterCount === 0 ? 'Optional field' : 'Your research question will guide the analysis'}
          </div>
          <div className={`font-body text-sm ${
            isNearLimit ? 'text-warning' : 'text-text-tertiary'
          }`}>
            {characterCount}/{maxCharacters} characters
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResearchQuestionStep;