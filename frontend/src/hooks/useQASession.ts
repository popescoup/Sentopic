/**
 * useQASession Hook
 * Manages Q&A session lifecycle, message history, and question submission
 */

import { useState, useCallback, useRef } from 'react';
import { api } from '@/api/client';
import type { ChatMessage, ChatResponse, ChatMessageCreate } from '@/types/api';

// Extract the search type from ChatMessageCreate for reuse
type SearchType = NonNullable<ChatMessageCreate['search_type']>;

interface QAMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  response?: ChatResponse; // For assistant messages
  searchType?: SearchType; // For user messages - now properly typed
}

interface UseQASessionReturn {
  sessionId: string | null;
  messages: QAMessage[];
  isLoading: boolean;
  error: string | null;
  sendQuestion: (question: string, searchType: SearchType) => Promise<void>; // Now properly typed
  initializeSession: () => Promise<void>;
  clearSession: () => void;
}

export const useQASession = (projectId: string): UseQASessionReturn => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<QAMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messageIdCounter = useRef(1);

  // Initialize a new chat session
  const initializeSession = useCallback(async () => {
    try {
      setError(null);
      const response = await api.startChatSession(projectId);
      setSessionId(response.session_id);
      
      // Load existing chat history if any
      if (response.session_id) {
        try {
          const history = await api.getChatHistory(response.session_id);
          const formattedMessages: QAMessage[] = history.messages.map((msg: ChatMessage) => ({
            id: msg.id,
            role: msg.role,
            content: msg.content,
            timestamp: msg.timestamp,
            // Note: We don't have access to original response data or searchType from history
            // This is a limitation of the current backend design
          }));
          setMessages(formattedMessages);
          
          // Update counter to avoid ID conflicts
          if (formattedMessages.length > 0) {
            messageIdCounter.current = Math.max(...formattedMessages.map(m => m.id)) + 1;
          }
        } catch (historyError) {
          console.warn('Failed to load chat history:', historyError);
          // Continue without history - not critical
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to initialize session';
      setError(errorMessage);
      console.error('Failed to initialize Q&A session:', err);
    }
  }, [projectId]);

  // Send a question and get AI response
  const sendQuestion = useCallback(async (question: string, searchType: SearchType) => {
    if (!sessionId) {
      throw new Error('No active session. Please initialize session first.');
    }

    if (!question.trim()) {
      throw new Error('Question cannot be empty');
    }

    setIsLoading(true);
    setError(null);

    try {
      // Add user message immediately for better UX
      const userMessage: QAMessage = {
        id: messageIdCounter.current++,
        role: 'user',
        content: question.trim(),
        timestamp: new Date().toISOString(),
        searchType
      };
      
      setMessages(prev => [...prev, userMessage]);

      // Send question to AI
      const response = await api.sendChatMessage(sessionId, {
        message: question.trim(),
        search_type: searchType // Now properly typed
      });

      // Add AI response
      const assistantMessage: QAMessage = {
        id: messageIdCounter.current++,
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        response: response
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send question';
      setError(errorMessage);
      
      // Remove the user message that was optimistically added
      setMessages(prev => prev.slice(0, -1));
      
      throw err; // Re-throw so caller can handle if needed
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  // Clear the current session and messages
  const clearSession = useCallback(() => {
    setSessionId(null);
    setMessages([]);
    setError(null);
    setIsLoading(false);
    messageIdCounter.current = 1;
  }, []);

  return {
    sessionId,
    messages,
    isLoading,
    error,
    sendQuestion,
    initializeSession,
    clearSession
  };
};