'use client';

import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '@/app/services/api';
import type { ChatResponse, ChatCitation } from '@/app/types';
import { Send, Bot, User, FileText, TrendingUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  routing?: Record<string, unknown>;
  agents?: Record<string, unknown>;
  citations?: ChatCitation[];
  confidence?: number;
  session_id?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hello! I am your IntelliPlant AI assistant. How can I help you today? You can ask me about equipment inspections, RCA analysis, compliance, or lessons learned.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (message: string) => {
    if (!message.trim() || loading) return;

    const userMsg: Message = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const data: ChatResponse = await sendChatMessage(message, sessionId);
      const assistantMsg: Message = {
        role: 'assistant',
        content: data.response,
        routing: data.routing,
        agents: data.agents,
        citations: data.citations,
        confidence: (data.routing as Record<string, number>)?.confidence,
        session_id: data.session_id,
      };
      setMessages((prev) => [...prev, assistantMsg]);
      setSessionId(data.session_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(input);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-white">AI Chat</h1>
        <p className="text-slate-400 mt-1">Ask questions about your industrial equipment and documents</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center shrink-0">
                <Bot size={16} className="text-blue-400" />
              </div>
            )}
            <div className={`max-w-[75%] ${msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'}`}>
              <div className="px-4 py-3 text-sm leading-relaxed prose prose-invert max-w-none prose-sm">
                {msg.role === 'user' ? (
                  <p>{msg.content}</p>
                ) : (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                )}
              </div>
              {msg.role === 'assistant' && msg.routing && Object.keys(msg.routing).length > 0 && (
                <div className="px-4 pb-3 flex flex-wrap gap-1.5">
                  {Object.entries(msg.routing).map(([key, val]) => (
                    <span key={key} className="px-1.5 py-0.5 bg-slate-800 rounded text-[10px] text-slate-400">
                      {key}: {String(val)}
                    </span>
                  ))}
                </div>
              )}
              {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                <div className="px-4 pb-3 border-t border-slate-800/50 mt-1 pt-2">
                  <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                    <FileText size={10} />Sources
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {msg.citations.map((cite, idx) => (
                      <span key={idx} className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-500/10 border border-blue-500/20 rounded text-[10px] text-blue-400">
                        <FileText size={9} />
                        {cite.source}
                        {cite.relevance_score > 0 && (
                          <span className="text-blue-300/60 ml-0.5">({Math.round(cite.relevance_score * 100)}%)</span>
                        )}
                      </span>
                    ))}
                  </div>
                  {msg.confidence !== undefined && msg.confidence > 0 && (
                    <div className="mt-1.5 flex items-center gap-1.5">
                      <TrendingUp size={10} className="text-green-400" />
                      <span className="text-[10px] text-slate-500">
                        Confidence: <span className={msg.confidence > 0.7 ? 'text-green-400' : msg.confidence > 0.4 ? 'text-yellow-400' : 'text-red-400'}>
                          {Math.round(msg.confidence * 100)}%
                        </span>
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
                <User size={16} className="text-white" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center shrink-0">
              <Bot size={16} className="text-blue-400" />
            </div>
            <div className="chat-bubble-assistant px-4 py-3">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-slate-400 rounded-full loading-dot" />
                <span className="w-2 h-2 bg-slate-400 rounded-full loading-dot" />
                <span className="w-2 h-2 bg-slate-400 rounded-full loading-dot" />
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-sm text-red-400">
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-2 flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={loading}
          className="flex-1 bg-transparent px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none disabled:opacity-50"
        />
        <button
          onClick={() => handleSend(input)}
          disabled={!input.trim() || loading}
          className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
