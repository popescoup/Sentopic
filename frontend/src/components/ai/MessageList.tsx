/**
 * Message List Component
 * Container for Q&A history with proper scrolling and loading states
 * Fixed to handle messages without response data
 */

import React, { useEffect, useRef } from 'react';
import QuestionMessage from './QuestionMessage';
import AnswerMessage from './AnswerMessage';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  response?: any; // For assistant messages with full response data
  searchType?: string; // For user messages
}

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Modified to only scroll within the chat container, not the entire page
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'nearest',  // Don't scroll the page, just the nearest scrollable container
      inline: 'nearest'
    });
  }, [messages, isLoading]);

  return (
    <div className="space-y-3">
      {/* Empty State */}
      {messages.length === 0 && !isLoading && (
        <div className="text-center py-8">
          <div className="text-text-tertiary mb-3">
            <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h4 className="font-medium text-text-primary mb-1 text-sm">
            Ready to Answer Questions
          </h4>
          <p className="text-xs text-text-secondary">
            Ask questions about your analysis data and get AI-powered insights
          </p>
        </div>
      )}

      {/* Message History */}
      {messages.map((message) => (
        message.role === 'user' ? (
          <QuestionMessage
            key={message.id}
            content={message.content}
            timestamp={message.timestamp}
            searchType={message.searchType || 'keyword'}
          />
        ) : (
          <AnswerMessage
            key={message.id}
            response={message.response} // This might be undefined for historical messages
            content={message.content}   // Pass content as fallback
            timestamp={message.timestamp}
          />
        )
      ))}

      {/* Loading State */}
      {isLoading && (
        <div className="mb-4">
          <div className="flex justify-start">
            <div className="max-w-[85%]">
              <div className="flex items-start space-x-3">
                {/* AI Avatar */}
                <div className="flex-shrink-0 w-6 h-6 bg-text-primary rounded-full flex items-center justify-center">
                  <span className="text-xs font-bold text-white">AI</span>
                </div>

                <div className="flex-1">
                  {/* Typing Indicator */}
                  <div className="bg-panel border border-border-primary px-4 py-3 rounded-input rounded-tl-sm">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-text-tertiary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-text-tertiary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-text-tertiary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                      <span className="text-sm text-text-secondary">
                        Analyzing question...
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;