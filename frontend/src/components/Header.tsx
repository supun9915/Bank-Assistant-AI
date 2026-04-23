import React from 'react';
import { Bot, MoreVertical } from 'lucide-react';
export function Header() {
  return (
    <div className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 rounded-t-2xl z-10 shadow-sm">
      <div className="flex items-center space-x-3">
        <div className="relative">
          <div className="w-10 h-10 bg-blue-50 border border-blue-100 rounded-full flex items-center justify-center text-blue-600">
            <Bot size={22} />
          </div>
          <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
        </div>
        <div>
          <h1 className="text-sm font-semibold text-gray-800">
            Banking Assistant
          </h1>
          <p className="text-xs text-green-600 font-medium">Online</p>
        </div>
      </div>
      <button className="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-full hover:bg-gray-50">
        <MoreVertical size={20} />
      </button>
    </div>);

}