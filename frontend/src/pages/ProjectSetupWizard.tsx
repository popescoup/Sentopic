/**
 * Project Setup Wizard Page
 * Comprehensive 4-step guided wizard for project creation
 * 
 * Phase 2.2: Full multi-step wizard with form validation
 */

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import WizardLayout from '@/components/wizard/WizardLayout';
import ResearchQuestionStep from '@/pages/wizard-steps/ResearchQuestionStep';
import KeywordsStep from '@/pages/wizard-steps/KeywordsStep';
import CollectionsStep from '@/pages/wizard-steps/CollectionsStep';
import ConfigurationStep from '@/pages/wizard-steps/ConfigurationStep';
import { useWizardState } from '@/hooks/useWizardState';
import { useCreateProject, useStartAnalysis } from '@/hooks/useApi';
import { validateStep } from '@/utils/wizardValidation';
import { getErrorMessage } from '@/api/client';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';

const ProjectSetupWizard: React.FC = () => {
  const navigate = useNavigate();
  const createProjectMutation = useCreateProject();
  const startAnalysisMutation = useStartAnalysis();

  const {
    currentStep,
    formData,
    updateFormData,
    goToStep,
    canGoBack,
    canGoNext,
    isStepComplete,
    resetWizard
  } = useWizardState();

  // Step configuration
  const steps = [
    {
      id: 1,
      title: 'Research Question',
      component: ResearchQuestionStep,
      description: 'Define your research focus'
    },
    {
      id: 2,
      title: 'Keywords',
      component: KeywordsStep,
      description: 'Select relevant keywords'
    },
    {
      id: 3,
      title: 'Collections',
      component: CollectionsStep,
      description: 'Choose data sources'
    },
    {
      id: 4,
      title: 'Configuration',
      component: ConfigurationStep,
      description: 'Review and configure'
    }
  ];

  const currentStepConfig = steps.find(step => step.id === currentStep);
  const CurrentStepComponent = currentStepConfig?.component;

  // Navigation handlers
  const handlePrevious = () => {
    if (canGoBack) {
      goToStep(currentStep - 1);
    }
  };

  const handleNext = async () => {
    // Validate current step
    const validation = validateStep(currentStep, formData);
    if (!validation.isValid) {
      // Handle validation errors (will be implemented with validation utils)
      console.error('Validation failed:', validation.errors);
      return;
    }

    if (currentStep < steps.length) {
      goToStep(currentStep + 1);
    } else {
      // Final step - submit project
      await handleSubmit();
    }
  };

  const handleCancel = () => {
    resetWizard();
    navigate('/');
  };

  // Project submission
  const handleSubmit = async () => {
    try {
      // Create project
      const projectData = {
        name: formData.projectName || `Project ${new Date().toLocaleDateString()}`,
        research_question: formData.researchQuestion || undefined,
        keywords: formData.keywords,
        collection_ids: formData.selectedCollections,
        partial_matching: formData.partialMatching,
        context_window_words: formData.contextWindow,
        generate_summary: formData.generateSummary
      };

      const newProject = await createProjectMutation.mutateAsync(projectData);

      // Start analysis
      await startAnalysisMutation.mutateAsync(newProject.id);

      // Navigate to analysis progress
      navigate(`/projects/${newProject.id}/progress`);
    } catch (error) {
      console.error('Failed to create project:', error);
      // Error handling will be enhanced with proper error UI
    }
  };

  // Loading state
  const isSubmitting = createProjectMutation.isLoading || startAnalysisMutation.isLoading;

  return (
    <MainLayout title="Create New Project">
      {/* Breadcrumb Navigation */}
      <div className="mb-6">
        <nav className="flex items-center space-x-2 font-body text-text-secondary">
          <Link 
            to="/" 
            className="hover:text-text-primary transition-colors duration-150"
          >
            Projects
          </Link>
          <span>→</span>
          <span className="text-text-primary">New Project</span>
        </nav>
      </div>

      {/* Page Header */}
      <div className="mb-8">
        <h1 className="font-page-title text-text-primary mb-3">
          Create New Project
        </h1>
        <p className="font-body text-text-secondary max-w-2xl">
          Set up a new research project to analyze Reddit discussions. Follow the guided 
          steps to define your research question, select keywords, and choose data collections.
        </p>
      </div>

      {/* Wizard Container */}
      <div className="max-w-4xl mx-auto">
        <WizardLayout
          steps={steps}
          currentStep={currentStep}
          onStepClick={goToStep}
          canGoBack={canGoBack}
          canGoNext={canGoNext && isStepComplete(currentStep)}
          onPrevious={handlePrevious}
          onNext={handleNext}
          onCancel={handleCancel}
          isSubmitting={isSubmitting}
          submitText={currentStep === steps.length ? 'Create Project' : 'Next'}
        >
          {/* Step Content */}
          {CurrentStepComponent && (
            <CurrentStepComponent
              formData={formData}
              updateFormData={updateFormData}
              errors={validateStep(currentStep, formData).errors}
            />
          )}
        </WizardLayout>
      </div>

      {/* Error Display */}
      {(createProjectMutation.error || startAnalysisMutation.error) && (
        <div className="mt-6 max-w-4xl mx-auto">
          <Card className="border-danger bg-red-50">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-danger" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="font-subsection text-danger">
                  Project Creation Failed
                </h3>
                <p className="font-body text-text-secondary mt-1">
                  {getErrorMessage(createProjectMutation.error) || getErrorMessage(startAnalysisMutation.error) || 'An unexpected error occurred'}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Development Info - Remove in production */}
      <div className="mt-12 bg-panel rounded-default p-6 border border-border-primary max-w-4xl mx-auto">
        <h2 className="font-section-header text-text-primary mb-3">
          Phase 2.2 Development Status
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              Current Step Data
            </h3>
            <pre className="font-technical text-text-secondary bg-content p-3 rounded-default border border-border-secondary text-xs overflow-auto">
              {JSON.stringify({ currentStep, formData }, null, 2)}
            </pre>
          </div>
          <div>
            <h3 className="font-subsection text-text-primary mb-2">
              Step Validation
            </h3>
            <pre className="font-technical text-text-secondary bg-content p-3 rounded-default border border-border-secondary text-xs overflow-auto">
              {JSON.stringify(validateStep(currentStep, formData), null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default ProjectSetupWizard;