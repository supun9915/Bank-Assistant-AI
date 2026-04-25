import React, { useState, useRef } from "react";
import { Send, Mic } from "lucide-react";

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

const QUICK_ACTIONS = [
  { label: "💰 Check Balance", value: "What is my account balance?" },
  { label: "📊 Transactions", value: "Show my recent transactions" },
  { label: "🏦 Loan Info", value: "Tell me about loan options" },
  { label: "💳 Fixed Deposit", value: "What are fixed deposit rates?" },
  { label: "🔒 Account Info", value: "Show my account details" },
];

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput("");
      inputRef.current?.focus();
    }
  };

  const handleQuickAction = (value: string) => {
    if (!disabled) {
      onSend(value);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="bg-white border-t border-gray-100 p-3">
      {/* Quick Actions */}
      <div className="flex overflow-x-auto space-x-2 mb-3 pb-1 scrollbar-hide">
        {QUICK_ACTIONS.map((action) => (
          <button
            key={action.label}
            onClick={() => handleQuickAction(action.value)}
            disabled={disabled}
            className="whitespace-nowrap px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-100 rounded-full hover:bg-blue-600 hover:text-white hover:border-blue-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {action.label}
          </button>
        ))}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="flex items-center space-x-2">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything about banking..."
          disabled={disabled}
          className="flex-1 bg-slate-50 border border-slate-200 text-sm rounded-2xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 disabled:opacity-50 transition-all placeholder:text-slate-400"
        />
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="w-10 h-10 flex items-center justify-center bg-blue-600 text-white rounded-full hover:bg-blue-700 active:scale-95 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow shrink-0"
        >
          <Send size={17} className="ml-0.5" />
        </button>
      </form>
    </div>
  );
}
