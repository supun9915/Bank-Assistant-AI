import { motion } from "framer-motion";
import { Bot, User } from "lucide-react";

interface MessageBubbleProps {
  sender: "user" | "bot";
  text: string;
  timestamp: string;
  intent?: string;
  confidence?: number;
}

export function MessageBubble({ sender, text, timestamp }: MessageBubbleProps) {
  const isUser = sender === "user";

  // Format text: replace \n with line breaks
  const lines = text.split("\n");

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-3`}
    >
      {/* Bot avatar */}
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white shrink-0 mr-2 mt-1 shadow">
          <Bot size={14} />
        </div>
      )}

      <div
        className={`flex flex-col ${isUser ? "items-end" : "items-start"} max-w-[78%]`}
      >
        <div
          className={`px-4 py-3 text-sm leading-relaxed shadow-sm ${
            isUser
              ? "bg-blue-600 text-white rounded-2xl rounded-br-sm"
              : "bg-white text-gray-800 border border-gray-100 rounded-2xl rounded-bl-sm"
          }`}
        >
          {lines.map((line, i) =>
            line === "" ? (
              <br key={i} />
            ) : (
              <p key={i} className={i > 0 ? "mt-1" : ""}>
                {line}
              </p>
            ),
          )}
        </div>

        <div className="flex items-center gap-2 mt-1 px-1">
          <span className="text-[10px] text-gray-400 font-medium">
            {timestamp}
          </span>
        </div>
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center text-white shrink-0 ml-2 mt-1 shadow">
          <User size={14} />
        </div>
      )}
    </motion.div>
  );
}
