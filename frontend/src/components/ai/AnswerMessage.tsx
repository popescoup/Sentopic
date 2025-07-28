/**
 * Answer Message Component
 * Displays AI responses with simplified metadata
 * Cleaned up version without search type, discussions found, and source/data buttons
 */

import React from 'react';
import type { ChatResponse } from '@/types/api';

interface AnswerMessageProps {
  response?: ChatResponse; // Made optional to handle historical messages
  timestamp: string;
  content?: string; // Add content prop for fallback when response is undefined
}

const AnswerMessage: React.FC<AnswerMessageProps> = ({
  response,
  timestamp,
  content
}) => {
  // Handle case where response is undefined (historical messages)
  const messageContent = response?.message || content || 'Message content unavailable';
  const tokensUsed = response?.tokens_used || 0;
  const costEstimate = response?.cost_estimate || 0;

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
      {/* AI Response Bubble */}
      <div className="flex justify-start">
        <div className="max-w-[85%]">
          {/* AI Avatar/Icon */}
          <div className="flex items-start space-x-3">
          <div className="flex-shrink-0 w-6 h-6 bg-text-primary rounded-full flex items-center justify-center">
            <span className="text-xs font-bold text-white">AI</span>
          </div>

            <div className="flex-1">
              {/* Response Content */}
              <div className="bg-panel border border-border-primary px-4 py-3 rounded-input rounded-tl-sm">
                <p className="font-body text-sm text-text-primary leading-relaxed whitespace-pre-wrap">
                  {messageContent}
                </p>
              </div>

              <div className="flex items-center justify-between mt-1">
                {/* Cost Information (if available) - moved to right side */}
                {response && costEstimate > 0 && (
                  <div className="text-xs text-text-tertiary">
                    ${costEstimate.toFixed(4)} • {tokensUsed} tokens
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnswerMessage;