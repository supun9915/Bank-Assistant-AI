import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { Header } from './Header';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  timestamp: string;
}
export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([
  {
    id: '1',
    sender: 'bot',
    text: 'Hello! I am your Smart Banking Assistant. How can I help you today?',
    timestamp: new Date().toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    })
  }]
  );
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth'
    });
  };
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);
  const handleSendMessage = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
      })
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);
    try {
      // Simulate network delay for better UX
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const response = await axios.post('http://localhost:8000/chat', {
        message: text
      });
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text:
        response.data.reply ||
        "I received your message, but couldn't process the reply.",
        timestamp: new Date().toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit'
        })
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      // Fallback for when the API is not running
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: "I'm having trouble connecting to the server right now. Please try again later.",
        timestamp: new Date().toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit'
        })
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };
  return (
    <div className="flex flex-col w-full max-w-md h-[600px] max-h-[90vh] bg-slate-50 rounded-2xl shadow-xl border border-gray-200 relative overflow-hidden">
      <Header />

      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-slate-50/95 bg-blend-overlay">
        {messages.map((msg) =>
        <MessageBubble
          key={msg.id}
          sender={msg.sender}
          text={msg.text}
          timestamp={msg.timestamp} />

        )}

        {isTyping &&
        <div className="mb-4">
            <TypingIndicator />
          </div>
        }
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSend={handleSendMessage} disabled={isTyping} />
    </div>);

}