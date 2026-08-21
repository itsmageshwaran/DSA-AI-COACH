import { useState, useEffect, useRef, useCallback } from 'react';
import { WS_BASE } from '../../services/api';

type Message = {
  id: string;
  sender: 'ai' | 'user';
  text: string;
};

export function useTutorWebSocket(problemId: string) {
  const token = localStorage.getItem('access_token');
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [isStreaming, setIsStreaming] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const currentAiMessageRef = useRef<string>('');

  const connect = useCallback(() => {
    if (!token) return;
    
    setStatus('connecting');
    const wsUrl = `${WS_BASE}/tutor?token=${token}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('connected');
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: 'ai',
        text: 'Connection established. How can I help you with this problem?'
      }]);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.error) {
          setIsStreaming(false);
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            sender: 'ai',
            text: `⚠️ **Notice**: ${data.error}`
          }]);
          return;
        }

        if (data.event === "stream_start") {
          setIsStreaming(true);
          currentAiMessageRef.current = '';
          const msgId = Date.now().toString();
          setMessages(prev => [...prev, { id: msgId, sender: 'ai', text: '' }]);
        } else if (data.event === "token") {
          currentAiMessageRef.current += data.chunk;
          const updatedText = currentAiMessageRef.current;
          setMessages(prev => {
            if (prev.length === 0) return prev;
            const newMessages = [...prev];
            const lastMsg = newMessages[newMessages.length - 1];
            if (lastMsg && lastMsg.sender === 'ai') {
              newMessages[newMessages.length - 1] = {
                ...lastMsg,
                text: updatedText
              };
            }
            return newMessages;
          });
        } else if (data.event === "stream_end") {
          currentAiMessageRef.current = '';
          setIsStreaming(false);
        } else if (data.message) {
          setIsStreaming(false);
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            sender: 'ai',
            text: data.message
          }]);
        }
      } catch (e) {
        console.error("Failed to parse WS message:", event.data);
      }
    };

    ws.onclose = () => {
      setStatus('disconnected');
      setIsStreaming(false);
    };

    ws.onerror = (err) => {
      console.error("WS Error:", err);
      setStatus('error');
      setIsStreaming(false);
    };
  }, [token, problemId]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  const sendMessage = useCallback((action: string, payload: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        action,
        ...payload
      }));
    } else {
      console.warn("WebSocket is not connected.");
    }
  }, []);

  const requestReview = useCallback((code: string, context?: any, difficulty?: string, concept?: string, promptText?: string) => {
    // Add user message to UI immediately for better perceived performance
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      sender: 'user',
      text: promptText || "Please review my code."
    }]);
    setIsStreaming(true); // show waiting indicator
    sendMessage("socratic_guide", { code, execution_result: context, ast_analysis: null, difficulty, concept });
  }, [sendMessage]);

  const askAction = useCallback((action: 'socratic_guide' | 'code_auditor' | 'complexity_analyst', code: string, label: string, context?: any) => {
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      sender: 'user',
      text: label
    }]);
    setIsStreaming(true);
    sendMessage(action, { code, execution_result: context, ast_analysis: null });
  }, [sendMessage]);

  return {
    messages,
    status,
    isStreaming,
    requestReview,
    askAction,
    sendMessage
  };
}
