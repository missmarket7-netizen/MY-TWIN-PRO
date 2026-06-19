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
      if (abortRef.current) {
        abortRef.current.abort();
      }

      const controller = new AbortController();
      abortRef.current = controller;

      setState({ isStreaming: true, error: null });
      setThinking(true);
      setThinkingStage('thinking');

      const userMsgId = `msg_${Date.now().toString(36)}_user`;
      addMessage({
        id: userMsgId,
        role: 'user',
        content: message,
        timestamp: Date.now(),
        image,
      });

      const twinMsgId = `msg_${Date.now().toString(36)}_twin`;
      addMessage({
        id: twinMsgId,
        role: 'twin',
        content: '',
        timestamp: Date.now(),
        thinkingStage: 'thinking',
      });

      setStreamingText('');
      setThinkingStage('generating');

      try {
        const store = useTwinStore.getState();
        const fullText = await streamChat(
          message,
          store.chatHistory.slice(-10).map((h) => ({
            role: h.role,
            content: h.content,
          })),
          store.lang,
          (chunk: string) => {
            setStreamingText((prev: string) => prev + chunk);
          },
          controller.signal
        );

        setThinking(false);
        setThinkingStage('complete');
        setStreamingText('');

        useTwinStore.setState((s) => ({
          chatHistory: s.chatHistory.map((msg) =>
            msg.id === twinMsgId
              ? { ...msg, content: fullText, thinkingStage: 'complete', provider: 'gemini' }
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

        const errorMsg =
          error.message === 'SESSION_EXPIRED'
            ? 'انتهت الجلسة، الرجاء تسجيل الدخول مجدداً'
            : 'حدث خطأ في الاتصال';

        useTwinStore.setState((s) => ({
          chatHistory: s.chatHistory.map((msg) =>
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
