import React, { useEffect, useState, useRef } from "react";
import { Header } from "./Header";
import { MessageBubble } from "./MessageBubble";
import { ChatInput } from "./ChatInput";
import { TypingIndicator } from "./TypingIndicator";
import { sendChatMessage } from "../api";

interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
  timestamp: string;
  intent?: string;
  confidence?: number;
}

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "bot",
      text: "👋 Hello! I am your Smart Banking Assistant. How can I help you today?\n\nYou can ask me about your balance, transactions, loans, fixed deposits, and more.",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const lastIntentRef = useRef<string | undefined>(undefined);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const data = await sendChatMessage({
        message: text,
        last_intent: lastIntentRef.current,
      });

      if (data.intent) lastIntentRef.current = data.intent;
      setIsOnline(true);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text:
          data.reply ||
          "I received your message, but couldn't process the reply.",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        intent: data.intent,
        confidence: data.confidence,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch {
      setIsOnline(false);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text: "⚠️ I'm having trouble connecting to the server right now. Please ensure the backend is running and try again.",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col w-full max-w-lg h-[700px] max-h-[92vh] bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden">
      <Header isOnline={isOnline} />

      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-1 scrollbar-hide bg-gradient-to-b from-slate-50 to-blue-50/30">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            sender={msg.sender}
            text={msg.text}
            timestamp={msg.timestamp}
            intent={msg.intent}
            confidence={msg.confidence}
          />
        ))}

        {isTyping && (
          <div className="mb-2">
            <TypingIndicator />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSend={handleSendMessage} disabled={isTyping} />
    </div>
  );
}
