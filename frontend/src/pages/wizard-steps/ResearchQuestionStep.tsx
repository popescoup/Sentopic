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
          Define your research question to guide the analysis. This field is optional but helps 
          focus the analysis and provides context for AI-generated insights.
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
          helpText="Describe what you want to understand from the Reddit discussions"
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

      {/* Examples Section */}
      <div className="mb-8 p-4 bg-panel rounded-input border border-border-primary">
        <h4 className="font-subsection text-text-primary mb-3">
          Research Question Examples
        </h4>
        <div className="space-y-3">
          <div className="p-3 bg-content rounded-input border border-border-secondary">
            <p className="font-body text-text-primary mb-1">
              "How do users discuss the pros and cons of different programming languages?"
            </p>
            <p className="font-small text-text-tertiary">
              Keywords: programming, languages, python, javascript, comparison
            </p>
          </div>
          
          <div className="p-3 bg-content rounded-input border border-border-secondary">
            <p className="font-body text-text-primary mb-1">
              "What are the main concerns people have about electric vehicles?"
            </p>
            <p className="font-small text-text-tertiary">
              Keywords: electric vehicles, EV, battery, charging, range anxiety
            </p>
          </div>
          
          <div className="p-3 bg-content rounded-input border border-border-secondary">
            <p className="font-body text-text-primary mb-1">
              "How has the pandemic affected small business operations?"
            </p>
            <p className="font-small text-text-tertiary">
              Keywords: pandemic, small business, covid, operations, challenges
            </p>
          </div>
        </div>
      </div>

      {/* Guidelines */}
      <div className="p-4 bg-panel rounded-input border border-border-primary">
        <h4 className="font-subsection text-text-primary mb-3">
          Tips for Effective Research Questions
        </h4>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <h5 className="font-body text-text-primary mb-2 font-medium">
              ✅ Good practices:
            </h5>
            <ul className="space-y-1 text-sm text-text-secondary">
              <li>• Be specific and focused</li>
              <li>• Include key concepts you want to explore</li>
              <li>• Consider multiple perspectives</li>
              <li>• Think about what insights you need</li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-body text-text-primary mb-2 font-medium">
              ❌ Avoid:
            </h5>
            <ul className="space-y-1 text-sm text-text-secondary">
              <li>• Overly broad questions</li>
              <li>• Yes/no questions</li>
              <li>• Questions with obvious answers</li>
              <li>• Multiple unrelated topics</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Impact on Analysis */}
      <div className="mt-6 p-4 bg-hover-blue rounded-input border border-accent">
        <h4 className="font-subsection text-text-primary mb-2">
          How this helps your analysis:
        </h4>
        <ul className="space-y-1 text-sm text-text-secondary">
          <li>• <strong>AI Summary:</strong> Provides focused insights relevant to your question</li>
          <li>• <strong>Keyword Suggestions:</strong> AI can suggest related terms based on your research focus</li>
          <li>• <strong>Result Interpretation:</strong> Analysis results are contextualized to your research goal</li>
          <li>• <strong>Project Organization:</strong> Helps you remember the purpose of each analysis</li>
        </ul>
      </div>
    </div>
  );
};

export default ResearchQuestionStep;