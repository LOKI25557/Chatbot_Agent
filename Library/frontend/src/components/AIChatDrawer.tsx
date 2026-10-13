import React, { useState, useRef, useEffect } from 'react';
import { Book, SearchResponse } from '../types';
import { api } from '../services/api';
import { X, Send, Sparkles, BookOpen, User, Bot, AlertTriangle, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  books?: Book[];
  similarBooks?: Book[];
  timestamp: string;
}

interface AIChatDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectBook: (book: Book) => void;
}

const SUGGESTED_FOLLOWUPS = [
  "Show me only available books",
  "Are there other books in Algorithms?",
  "Tell me about Clean Code",
  "Do you have books by R. K. Narayan?",
];

export const AIChatDrawer: React.FC<AIChatDrawerProps> = ({
  isOpen,
  onClose,
  onSelectBook,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: "Hello! I am your AI Library Assistant. Ask me about any title, author, topic, or shelf location in our collection. I answer strictly based on our genuine catalogue records.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMsg: Message = {
      id: String(Date.now()),
      sender: 'user',
      text: text.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setIsLoading(true);

    try {
      // Pass previous query as context
      const prevAssistantMsg = messages.filter((m) => m.sender === 'assistant').pop()?.text;
      const res: SearchResponse = await api.search(text.trim(), false, undefined, prevAssistantMsg);

      const assistantMsg: Message = {
        id: String(Date.now() + 1),
        sender: 'assistant',
        text: res.ai_explanation,
        books: res.books,
        similarBooks: res.similar_books,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: String(Date.now() + 1),
        sender: 'assistant',
        text: `I encountered an issue querying the catalogue: ${err.message || 'Server error'}. Please try asking with a title or author.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(inputQuery);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm"
        />

        {/* Drawer Panel */}
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 220 }}
          className="relative w-full max-w-md h-full bg-white dark:bg-library-darkCard border-l border-library-border dark:border-library-darkBorder shadow-2xl flex flex-col z-10"
        >
          {/* Header */}
          <div className="p-4 border-b border-library-border dark:border-library-darkBorder flex items-center justify-between bg-slate-50 dark:bg-slate-900">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-emerald-600 text-white">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-serif font-bold text-slate-900 dark:text-white leading-tight">
                  Library Assistant
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Factual, catalogue-grounded conversational search
                </p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
              aria-label="Close conversation drawer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Conversation Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'assistant' && (
                  <div className="w-7 h-7 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 flex items-center justify-center shrink-0 text-xs font-bold mt-1">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl p-3.5 text-sm ${
                    msg.sender === 'user'
                      ? 'bg-library-navy dark:bg-emerald-600 text-white rounded-br-none'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-bl-none border border-slate-200/60 dark:border-slate-700/60'
                  }`}
                >
                  <p className="leading-relaxed whitespace-pre-wrap">{msg.text}</p>

                  {/* Grounded Matching Books in Chat */}
                  {msg.books && msg.books.length > 0 && (
                    <div className="mt-3 space-y-2 pt-2 border-t border-slate-200 dark:border-slate-700">
                      <span className="text-[11px] font-semibold uppercase text-slate-500 dark:text-slate-400 block">
                        Verified Matches:
                      </span>
                      {msg.books.map((b) => (
                        <div
                          key={b.id}
                          onClick={() => onSelectBook(b)}
                          className="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-emerald-500 cursor-pointer transition-colors text-xs"
                        >
                          <div className="truncate pr-2">
                            <span className="font-semibold text-slate-900 dark:text-white block truncate">
                              {b.title}
                            </span>
                            <span className="text-slate-500 truncate block">
                              {b.author || 'Unknown'} · {b.available_copies}/{b.total_copies} avail
                            </span>
                          </div>
                          <ArrowRight className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Grounded Similar Books Suggestions */}
                  {msg.similarBooks && msg.similarBooks.length > 0 && (
                    <div className="mt-3 space-y-2 pt-2 border-t border-slate-200 dark:border-slate-700">
                      <span className="text-[11px] font-semibold uppercase text-amber-600 dark:text-amber-400 block">
                        Related Books in Catalogue:
                      </span>
                      {msg.similarBooks.slice(0, 3).map((b) => (
                        <div
                          key={b.id}
                          onClick={() => onSelectBook(b)}
                          className="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-amber-500 cursor-pointer transition-colors text-xs"
                        >
                          <div className="truncate pr-2">
                            <span className="font-semibold text-slate-900 dark:text-white block truncate">
                              {b.title}
                            </span>
                            <span className="text-slate-500 truncate block">
                              {b.author || 'Unknown'} ({b.category || 'General'})
                            </span>
                          </div>
                          <ArrowRight className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                        </div>
                      ))}
                    </div>
                  )}

                  <span
                    className={`text-[10px] block mt-1.5 ${
                      msg.sender === 'user' ? 'text-white/70 text-right' : 'text-slate-400'
                    }`}
                  >
                    {msg.timestamp}
                  </span>
                </div>

                {msg.sender === 'user' && (
                  <div className="w-7 h-7 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center justify-center shrink-0 text-xs font-bold mt-1">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-3 items-center text-xs text-slate-400">
                <div className="w-7 h-7 rounded-full bg-emerald-100 dark:bg-emerald-950 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-emerald-600" />
                </div>
                <div className="flex items-center gap-1.5 p-3 rounded-2xl bg-slate-100 dark:bg-slate-800">
                  <div className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce" />
                  <div className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce [animation-delay:0.2s]" />
                  <div className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce [animation-delay:0.4s]" />
                  <span className="ml-2 text-slate-500">Checking database catalogue...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Follow-ups */}
          <div className="p-3 bg-slate-50 dark:bg-slate-900/60 border-t border-library-border dark:border-library-darkBorder">
            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1.5">
              Quick Follow-ups:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {SUGGESTED_FOLLOWUPS.map((q, i) => (
                <button
                  key={i}
                  disabled={isLoading}
                  onClick={() => handleSendMessage(q)}
                  className="text-xs px-2.5 py-1 rounded-full bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-emerald-400 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Input Box */}
          <form
            onSubmit={handleSubmit}
            className="p-3 border-t border-library-border dark:border-library-darkBorder bg-white dark:bg-library-darkCard flex items-center gap-2"
          >
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask about books, authors, availability..."
              className="flex-1 py-2.5 px-3.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
            <button
              type="submit"
              disabled={isLoading || !inputQuery.trim()}
              className="p-2.5 rounded-xl bg-emerald-600 text-white disabled:opacity-50 hover:bg-emerald-500 transition-colors shrink-0"
              aria-label="Send message"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
