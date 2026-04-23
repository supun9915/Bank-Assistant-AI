import React from 'react';
import { motion } from 'framer-motion';
interface MessageBubbleProps {
  sender: 'user' | 'bot';
  text: string;
  timestamp: string;
}
export function MessageBubble({ sender, text, timestamp }: MessageBubbleProps) {
  const isUser = sender === 'user';
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 10
      }}
      animate={{
        opacity: 1,
        y: 0
      }}
      className={`flex flex-col w-full ${isUser ? 'items-end' : 'items-start'} mb-4`}>
      
      <div
        className={`max-w-[80%] px-4 py-2.5 text-sm shadow-sm ${isUser ? 'bg-blue-600 text-white rounded-2xl rounded-br-sm' : 'bg-white text-gray-800 border border-gray-100 rounded-2xl rounded-bl-sm'}`}>
        
        {text}
      </div>
      <span className="text-[10px] text-gray-400 mt-1 px-1 font-medium">
        {timestamp}
      </span>
    </motion.div>);

}