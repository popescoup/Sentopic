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

  // Initialize or resume a chat session
const initializeSession = useCallback(async () => {
    try {
      setError(null);
      console.log(`🔍 Initializing session for project: ${projectId}`);
      
      // First, check if any existing chat sessions exist for this project
      console.log('🔍 Checking for existing chat sessions...');
      const existingSessions = await api.getChatSessions(projectId);
      console.log('🔍 Existing sessions response:', existingSessions);
      console.log('🔍 Number of existing sessions:', existingSessions.sessions.length);
      
      let selectedSessionId: string;
      
      if (existingSessions.sessions.length > 0) {
        // Use the most recent session (by last_active timestamp)
        console.log('🔍 Found existing sessions, selecting most recent...');
        const mostRecentSession = existingSessions.sessions.reduce((latest, current) => {
          const latestTime = new Date(latest.last_active).getTime();
          const currentTime = new Date(current.last_active).getTime();
          console.log(`🔍 Comparing sessions: ${current.session_id} (${currentTime}) vs ${latest.session_id} (${latestTime})`);
          return currentTime > latestTime ? current : latest;
        });
        
        selectedSessionId = mostRecentSession.session_id;
        console.log(`✅ Resuming existing chat session: ${selectedSessionId}`);
        console.log('🔍 Selected session details:', mostRecentSession);
      } else {
        // No existing sessions, create a new one
        console.log('🔍 No existing sessions found, creating new session...');
        const response = await api.startChatSession(projectId);
        selectedSessionId = response.session_id;
        console.log(`✅ Created new chat session: ${selectedSessionId}`);
      }
      
      // Set the session ID
      setSessionId(selectedSessionId);
      
      // Load chat history from the selected session
      try {
        console.log(`🔍 Loading chat history for session: ${selectedSessionId}`);
        const history = await api.getChatHistory(selectedSessionId);
        console.log('🔍 Chat history response:', history);
        console.log('🔍 Number of messages in history:', history.messages.length);
        
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
        
        console.log(`✅ Loaded ${formattedMessages.length} messages from chat history`);
      } catch (historyError) {
        console.warn('Failed to load chat history:', historyError);
        // Continue without history - not critical for UX
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to initialize session';
      setError(errorMessage);
      console.error('❌ Failed to initialize Q&A session:', err);
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