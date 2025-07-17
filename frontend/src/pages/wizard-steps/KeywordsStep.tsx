/**
 * Keywords Step Component
 * Step 2: Keywords selection and management
 */

import React, { useState } from 'react';
import KeywordsManager from '@/components/projects/KeywordsManager';
import Button from '@/components/ui/Button';
import { useAIStatus } from '@/hooks/useApi';
import { api } from '@/api/client';
import type { WizardFormData } from '@/hooks/useWizardState';

export interface KeywordsStepProps {
  /** Current form data */
  formData: WizardFormData;
  /** Function to update form data */
  updateFormData: (updates: Partial<WizardFormData>) => void;
  /** Validation errors */
  errors: Record<string, string>;
}

export const KeywordsStep: React.FC<KeywordsStepProps> = ({
  formData,
  updateFormData,
  errors
}) => {
  const { data: aiStatus } = useAIStatus();
  const [isGeneratingKeywords, setIsGeneratingKeywords] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  const handleKeywordsChange = (keywords: string[]) => {
    updateFormData({ keywords });
  };

  const handleAIKeywordSuggestion = async () => {
    if (!formData.researchQuestion.trim()) {
      setAiError('Please enter a research question first to get AI keyword suggestions');
      return;
    }

    setIsGeneratingKeywords(true);
    setAiError(null);

    try {
      const response = await api.suggestKeywords({
        research_description: formData.researchQuestion,
        max_keywords: 10
      });

      // Merge AI suggestions with existing keywords, avoiding duplicates
      const existingKeywords = formData.keywords.map(k => k.toLowerCase());
      const newKeywords = response.keywords.filter(
        keyword => !existingKeywords.includes(keyword.toLowerCase())
      );

      const combinedKeywords = [...formData.keywords, ...newKeywords];
      updateFormData({ keywords: combinedKeywords });

    } catch (error) {
      setAiError('Failed to generate keyword suggestions. Please try again.');
      console.error('AI keyword suggestion error:', error);
    } finally {
      setIsGeneratingKeywords(false);
    }
  };

  const isAIAvailable = aiStatus?.ai_available && aiStatus?.features?.keyword_suggestion;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Step Introduction */}
      <div className="mb-8">
        <h3 className="font-subsection text-text-primary mb-3">
          Select Keywords for Analysis
        </h3>
        <p className="font-body text-text-secondary">
          Keywords help identify relevant discussions in your selected collections. 
          Choose terms that are likely to appear in posts and comments related to your research.
        </p>
      </div>

      {/* AI Keyword Suggestion */}
      {isAIAvailable && (
        <div className="mb-6 p-4 bg-panel rounded-input border border-border-primary">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="font-subsection text-text-primary mb-2">
                AI Keyword Suggestions
              </h4>
              <p className="font-body text-text-secondary mb-3">
                Get AI-powered keyword suggestions based on your research question.
              </p>
              
              {aiError && (
                <div className="mb-3 p-2 bg-red-50 border border-danger rounded-input">
                  <p className="font-body text-danger text-sm">{aiError}</p>
                </div>
              )}
            </div>
            
            <Button
              variant="outline"
              onClick={handleAIKeywordSuggestion}
              disabled={!formData.researchQuestion.trim() || isGeneratingKeywords}
              loading={isGeneratingKeywords}
              className="ml-4"
            >
              {isGeneratingKeywords ? 'Generating...' : 'Suggest Keywords'}
            </Button>
          </div>
          
          {!formData.researchQuestion.trim() && (
            <div className="mt-3 p-2 bg-yellow-50 border border-warning rounded-input">
              <p className="font-body text-text-secondary text-sm">
                💡 Add a research question in the previous step to get personalized keyword suggestions
              </p>
            </div>
          )}
        </div>
      )}

      {/* Keywords Manager */}
      <div className="mb-8">
        <KeywordsManager
          keywords={formData.keywords}
          onKeywordsChange={handleKeywordsChange}
          error={errors.keywords}
          maxKeywords={20}
          placeholder="Enter keywords related to your research..."
        />
      </div>

      {/* Keywords Strategy Guide */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="p-4 bg-panel rounded-input border border-border-primary">
          <h4 className="font-subsection text-text-primary mb-3">
            Keyword Strategy
          </h4>
          <div className="space-y-3">
            <div>
              <h5 className="font-body text-text-primary mb-1 font-medium">
                Broad Keywords
              </h5>
              <p className="font-small text-text-secondary">
                General terms that cast a wide net (e.g., "remote work", "productivity")
              </p>
            </div>
            
            <div>
              <h5 className="font-body text-text-primary mb-1 font-medium">
                Specific Keywords
              </h5>
              <p className="font-small text-text-secondary">
                Targeted terms for specific aspects (e.g., "zoom fatigue", "home office")
              </p>
            </div>
            
            <div>
              <h5 className="font-body text-text-primary mb-1 font-medium">
                Synonyms & Variations
              </h5>
              <p className="font-small text-text-secondary">
                Alternative terms (e.g., "WFH", "work from home", "telecommuting")
              </p>
            </div>
          </div>
        </div>

        <div className="p-4 bg-panel rounded-input border border-border-primary">
          <h4 className="font-subsection text-text-primary mb-3">
            Analysis Features
          </h4>
          <div className="space-y-3">
            <div>
              <h5 className="font-body text-text-primary mb-1 font-medium">
                Keyword Matching
              </h5>
              <p className="font-small text-text-secondary">
                Find posts and comments containing your keywords
              </p>
            </div>
            
            <div>
              <h5 className="font-body text-text-primary mb-1 font-medium">
                Sentiment Analysis
              </h5>
              <p className="font-small text-text-secondary">
                Analyze positive/negative sentiment around each keyword
              </p>
            </div>
            
            <div>
              <h5 className="font-body text-text-primary mb-1 font-medium">
                Co-occurrence Analysis
              </h5>
              <p className="font-small text-text-secondary">
                Discover which keywords appear together frequently
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Keyword Examples by Domain */}
      <div className="mt-6 p-4 bg-panel rounded-input border border-border-primary">
        <h4 className="font-subsection text-text-primary mb-3">
          Keyword Examples by Research Domain
        </h4>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <div className="p-3 bg-content rounded-input border border-border-secondary">
            <h5 className="font-body text-text-primary mb-2 font-medium">
              Technology
            </h5>
            <div className="flex flex-wrap gap-1">
              {['AI', 'machine learning', 'blockchain', 'privacy', 'security', 'automation'].map(keyword => (
                <span key={keyword} className="px-2 py-1 bg-hover-blue text-accent text-xs rounded">
                  {keyword}
                </span>
              ))}
            </div>
          </div>
          
          <div className="p-3 bg-content rounded-input border border-border-secondary">
            <h5 className="font-body text-text-primary mb-2 font-medium">
              Health & Wellness
            </h5>
            <div className="flex flex-wrap gap-1">
              {['mental health', 'exercise', 'diet', 'sleep', 'stress', 'meditation'].map(keyword => (
                <span key={keyword} className="px-2 py-1 bg-hover-blue text-accent text-xs rounded">
                  {keyword}
                </span>
              ))}
            </div>
          </div>
          
          <div className="p-3 bg-content rounded-input border border-border-secondary">
            <h5 className="font-body text-text-primary mb-2 font-medium">
              Business & Finance
            </h5>
            <div className="flex flex-wrap gap-1">
              {['investment', 'startup', 'cryptocurrency', 'savings', 'inflation', 'job market'].map(keyword => (
                <span key={keyword} className="px-2 py-1 bg-hover-blue text-accent text-xs rounded">
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Validation Requirements */}
      <div className="mt-6 p-4 bg-hover-blue rounded-input border border-accent">
        <h4 className="font-subsection text-text-primary mb-2">
          Requirements for Next Step:
        </h4>
        <ul className="space-y-1 text-sm text-text-secondary">
          <li>• At least 1 keyword is required</li>
          <li>• Keywords should be relevant to your research question</li>
          <li>• Maximum 20 keywords per project</li>
          <li>• Keywords are case-insensitive</li>
        </ul>
      </div>
    </div>
  );
};

export default KeywordsStep;