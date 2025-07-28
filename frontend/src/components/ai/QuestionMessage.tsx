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
          
        </div>
      </div>
    </div>
  );
};

export default QuestionMessage;