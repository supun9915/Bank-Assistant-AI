import React, { useState } from 'react';
import { Send } from 'lucide-react';
interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}
const QUICK_ACTIONS = ['Check Balance', 'Transactions', 'Loan Info'];
export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };
  return (
    <div className="bg-white border-t border-gray-200 p-3 rounded-b-2xl z-10">
      {/* Quick Actions */}
      <div className="flex overflow-x-auto space-x-2 mb-3 pb-1 scrollbar-hide">
        {QUICK_ACTIONS.map((action) =>
        <button
          key={action}
          onClick={() => onSend(action)}
          disabled={disabled}
          className="whitespace-nowrap px-3 py-1.5 text-xs font-medium text-blue-600 bg-white border border-blue-200 rounded-full hover:bg-blue-600 hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm">
          
            {action}
          </button>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="flex items-center space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={disabled}
          className="flex-1 bg-gray-50 border border-gray-200 text-sm rounded-full px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 disabled:opacity-50 transition-all" />
        
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="w-10 h-10 flex items-center justify-center bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm shrink-0">
          
          <Send size={18} className="ml-0.5" />
        </button>
      </form>
    </div>);

}