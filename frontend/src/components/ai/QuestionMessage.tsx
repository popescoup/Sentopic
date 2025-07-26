/**
 * Question Message Component
 * Displays user questions in the Q&A interface
 */

import React from 'react';

interface QuestionMessageProps {
  content: string;
  timestamp: string;
  searchType: string;
}

const QuestionMessage: React.FC<QuestionMessageProps> = ({
  content,
  timestamp,
  searchType
}) => {
  // Format timestamp for display
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.abs(now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      const minutes = Math.floor(diffInHours * 60);
      return minutes <= 1 ? 'Just now' : `${minutes}m ago`;
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  // Get search type display label
  const getSearchTypeLabel = (type: string) => {
    switch (type) {
      case 'keyword':
        return 'Keyword';
      case 'local_semantic':
        return 'Semantic (Local)';
      case 'cloud_semantic':
        return 'Semantic (Cloud)';
      case 'analytics_driven':
        return 'Analytics';
      default:
        return 'Auto';
    }
  };

  return (
    <div className="mb-4">
      {/* Question Bubble */}
      <div className="flex justify-end">
        <div className="max-w-[85%]">
          <div className="bg-accent text-white px-4 py-2 rounded-input rounded-br-sm">
            <p className="font-body text-sm leading-relaxed whitespace-pre-wrap">
              {content}
            </p>
          </div>
          
          {/* Metadata */}
          <div className="flex items-center justify-end mt-1 space-x-2 text-xs text-text-tertiary">
            <span className="px-2 py-0.5 bg-panel rounded-sm border border-border-primary">
              {getSearchTypeLabel(searchType)}
            </span>
            <span>{formatTime(timestamp)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionMessage;