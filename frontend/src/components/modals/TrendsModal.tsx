/**
 * Trends Analysis Modal
 * Advanced trends visualization with interactive controls
 * Features D3-powered line charts with toggle between mention frequency and sentiment trends
 */

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { LoadingState } from '@/components/layout/LoadingSpinner';
import { TrendsChart } from '@/components/visualizations';
import { useTrends } from '@/hooks/useApi';
import type { ProjectResponse } from '@/types/api';

interface TrendsModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Function to call when modal should close */
  onClose: () => void;
  /** Project data for trends analysis */
  project: ProjectResponse;
}

export const TrendsModal: React.FC<TrendsModalProps> = ({
  isOpen,
  onClose,
  project
}) => {
  // State for interactive controls
  const [chartType, setChartType] = useState<'mentions' | 'sentiment'>('mentions');
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const [timePeriod, setTimePeriod] = useState<'daily' | 'weekly' | 'monthly'>('weekly');

  // Initialize with first 3 keywords when modal opens
  useEffect(() => {
    if (isOpen && project.keywords.length > 0) {
      const initialKeywords = project.keywords.slice(0, Math.min(3, project.keywords.length));
      setSelectedKeywords(initialKeywords);
    }
  }, [isOpen, project.keywords]);

  // API call for trends data
  const { 
    data: trendsData, 
    isLoading, 
    error,
    refetch 
  } = useTrends(project.id, selectedKeywords, timePeriod, isOpen && selectedKeywords.length > 0);

  // Convert error to string for display
  const errorMessage = error instanceof Error ? error.message : 
                      error ? String(error) : 'An unexpected error occurred';

  // Handle keyword selection
  const handleKeywordToggle = (keyword: string) => {
    setSelectedKeywords(prev => {
      if (prev.includes(keyword)) {
        return prev.filter(k => k !== keyword);
      } else if (prev.length < 5) {
        return [...prev, keyword];
      }
      return prev; // Don't add if already at limit
    });
  };

  // Chart type options
  const chartTypeOptions = [
    { value: 'mentions', label: 'Mention Frequency', description: 'Number of times keywords appear' },
    { value: 'sentiment', label: 'Sentiment Trends', description: 'Average sentiment over time' }
  ];

  // Time period options
  const timePeriodOptions = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' }
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Trends Analysis"
      size="xl"
      className="max-h-[90vh]"
    >
      <div className="max-h-[75vh] overflow-y-auto pr-1">
        {/* Interactive Controls */}
        <div className="border-b border-border-primary pb-6 mb-6">
          {/* Chart Type Toggle */}
          <div className="mb-6">
            <label className="block font-medium text-text-primary mb-3">
              Chart Type
            </label>
            <div className="grid gap-3 md:grid-cols-2">
              {chartTypeOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => setChartType(option.value as 'mentions' | 'sentiment')}
                  className={`p-4 rounded-default border text-left transition-all duration-150 ${
                    chartType === option.value
                      ? 'border-accent bg-hover-blue text-text-primary'
                      : 'border-border-secondary bg-content text-text-secondary hover:border-border-emphasis hover:text-text-primary'
                  }`}
                >
                  <div className="font-medium">{option.label}</div>
                  <div className="text-sm mt-1">{option.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Keyword Selection */}
          <div className="mb-6">
            <label className="block font-medium text-text-primary mb-3">
              Keywords to Analyze (Max 5)
            </label>
            <div className="grid gap-2 md:grid-cols-3 lg:grid-cols-4">
              {project.keywords.map(keyword => (
                <label
                  key={keyword}
                  className="flex items-center space-x-2 cursor-pointer p-2 rounded-input hover:bg-hover-blue transition-colors duration-150"
                >
                  <input
                    type="checkbox"
                    checked={selectedKeywords.includes(keyword)}
                    onChange={() => handleKeywordToggle(keyword)}
                    disabled={!selectedKeywords.includes(keyword) && selectedKeywords.length >= 5}
                    className="rounded border-border-secondary focus:border-accent focus:ring-accent"
                  />
                  <span className={`text-sm ${
                    selectedKeywords.includes(keyword) 
                      ? 'text-text-primary font-medium' 
                      : 'text-text-secondary'
                  }`}>
                    {keyword}
                  </span>
                </label>
              ))}
            </div>
            {selectedKeywords.length === 5 && (
              <p className="text-small text-text-tertiary mt-2">
                Maximum of 5 keywords can be selected for performance.
              </p>
            )}
          </div>

          {/* Time Period Selection */}
          <div className="mb-6">
            <label className="block font-medium text-text-primary mb-3">
              Time Period
            </label>
            <div className="flex space-x-2">
              {timePeriodOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => setTimePeriod(option.value as 'daily' | 'weekly' | 'monthly')}
                  className={`px-4 py-2 rounded-input border font-medium transition-all duration-150 ${
                    timePeriod === option.value
                      ? 'border-accent bg-accent text-white'
                      : 'border-border-secondary bg-content text-text-secondary hover:border-border-emphasis hover:text-text-primary'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Chart Visualization */}
        <div>
          {/* Chart Header */}
          <div className="mb-4">
            <h3 className="font-section-header text-text-primary mb-2">
              {chartType === 'mentions' ? 'Mention Frequency Trends' : 'Sentiment Trends'}
            </h3>
            {selectedKeywords.length > 0 && (
              <p className="font-body text-text-secondary">
                Showing {chartType === 'mentions' ? 'mention counts' : 'average sentiment'} over time for: {selectedKeywords.join(', ')}
              </p>
            )}
          </div>

          {/* Chart Content */}
          <div>
            {/* Loading State */}
            {isLoading && (
              <LoadingState 
                title="Loading Trends..."
                description="Analyzing keyword trends over time."
              />
            )}

            {/* Error State */}
            {!!error && (
              <div className="text-center py-8">
                <div className="text-danger mb-4">
                  <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="font-subsection text-text-primary mb-2">Error Loading Trends</h3>
                <p className="font-body text-text-secondary mb-4">
                  {errorMessage}
                </p>
                <Button variant="outline" onClick={() => refetch()}>
                  Try Again
                </Button>
              </div>
            )}

            {/* No Keywords Selected */}
            {selectedKeywords.length === 0 && !isLoading && (
              <div className="text-center py-12">
                <div className="text-text-tertiary mb-4">
                  <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="font-subsection text-text-primary mb-2">
                  Select Keywords
                </h3>
                <p className="font-body text-text-secondary mb-4 max-w-md mx-auto">
                  Choose one or more keywords from your project to see their trends over time.
                </p>
              </div>
            )}

            {/* Trends Chart */}
            {trendsData && selectedKeywords.length > 0 && !isLoading && (
              <div className="mb-6">
                <TrendsChart
                  data={trendsData.chart_data}
                  keywords={selectedKeywords}
                  chartType={chartType}
                  width={800}
                  height={400}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default TrendsModal;