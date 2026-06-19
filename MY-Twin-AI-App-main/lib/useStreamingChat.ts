import { useState, useRef, useCallback } from 'react';
import { streamChat } from './httpClient';
import { useTwinStore } from '../store/useTwinStore';

interface StreamingState {
  isStreaming: boolean;
  error: string | null;
}

export function useStreamingChat() {
  const [state, setState] = useState<StreamingState>({
    isStreaming: false,
    error: null,
  });
  
  const abortRef = useRef<AbortController | null>(null);
  const { addMessage, setStreamingText, setThinking, setThinkingStage } = useTwinStore();

  const sendStreamingMessage = useCallback(
    async (message: string, image?: string) => {
      // Abort any existing stream
      if (abortRef.current) {
        abortRef.current.abort();
      }

      const controller = new AbortController();
      abortRef.current = controller;

      setState({ isStreaming: true, error: null });
      setThinking(true);
      setThinkingStage('thinking');

      // Add user message to store immediately
      const userMsgId = `msg_${Date.now().toString(36)}_user`;
      addMessage({
        id: userMsgId,
        role: 'user',
        content: message,
        timestamp: Date.now(),
        image,
      });

      // Create a placeholder for the twin's response
      const twinMsgId = `msg_${Date.now().toString(36)}_twin`;
      addMessage({
        id: twinMsgId,
        role: 'twin',
        content: '',
        timestamp: Date.now(),
        thinkingStage: 'thinking',
      });

      // Initialize streaming text for this message
      setStreamingText('');
      setThinkingStage('generating');

      try {
        const store = useTwinStore.getState();
        
        const fullText = await streamChat(
          '/api/chat/stream',
          {
            message,
            twin_name: store.twinName,
            bond_level: store.bondLevel,
            relationship_dims: store.relationshipDims,
            history: store.chatHistory.slice(-10).map((h) => ({
              role: h.role,
              content: h.content,
            })),
            lang: store.lang,
            twin_gender: store.twinGender,
            calm_mode: store.calmMode,
          },
          (chunk: string) => {
            // Update streaming text chunk by chunk
            setStreamingText((prev) => prev + chunk);
          },
          controller.signal
        );

        // Update the placeholder message with full text
        setThinking(false);
        setThinkingStage('complete');
        setStreamingText(''); // Clear streaming state
        
        // Update message in store with full content
        useTwinStore.setState((state) => ({
          chatHistory: state.chatHistory.map((msg) =>
            msg.id === twinMsgId
              ? {
                  ...msg,
                  content: fullText,
                  thinkingStage: 'complete',
                  provider: 'gemini',
                }
              : msg
          ),
        }));

        setState({ isStreaming: false, error: null });
        return fullText;
      } catch (error: any) {
        if (error.name === 'AbortError') {
          setState({ isStreaming: false, error: null });
          return '';
        }
        
        setThinking(false);
        setThinkingStage('complete');
        setStreamingText('');
        
        const errorMsg = error.message === 'SESSION_EXPIRED'
          ? 'انتهت الجلسة، الرجاء تسجيل الدخول مجدداً'
          : 'حدث خطأ في الاتصال';
        
        // Update placeholder with error
        useTwinStore.setState((state) => ({
          chatHistory: state.chatHistory.map((msg) =>
            msg.id === twinMsgId
              ? { ...msg, content: errorMsg, failed: true, thinkingStage: 'complete' }
              : msg
          ),
        }));

        setState({ isStreaming: false, error: errorMsg });
        return '';
      }
    },
    [addMessage, setStreamingText, setThinking, setThinkingStage]
  );

  const cancelStream = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setState({ isStreaming: false, error: null });
    setThinking(false);
    setStreamingText('');
  }, [setThinking, setStreamingText]);

  return {
    sendStreamingMessage,
    cancelStream,
    isStreaming: state.isStreaming,
    error: state.error,
  };
}
