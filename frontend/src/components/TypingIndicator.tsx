import React from 'react';
import { motion } from 'framer-motion';
export function TypingIndicator() {
  return (
    <div className="flex items-center space-x-1 p-3 bg-white border border-gray-100 shadow-sm rounded-2xl rounded-bl-sm w-16 h-10">
      <motion.div
        className="w-2 h-2 bg-gray-400 rounded-full"
        animate={{
          y: [0, -5, 0]
        }}
        transition={{
          repeat: Infinity,
          duration: 0.6,
          ease: 'easeInOut'
        }} />
      
      <motion.div
        className="w-2 h-2 bg-gray-400 rounded-full"
        animate={{
          y: [0, -5, 0]
        }}
        transition={{
          repeat: Infinity,
          duration: 0.6,
          ease: 'easeInOut',
          delay: 0.2
        }} />
      
      <motion.div
        className="w-2 h-2 bg-gray-400 rounded-full"
        animate={{
          y: [0, -5, 0]
        }}
        transition={{
          repeat: Infinity,
          duration: 0.6,
          ease: 'easeInOut',
          delay: 0.4
        }} />
      
    </div>);

}