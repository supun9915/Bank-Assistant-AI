import React from "react";
import { Bot, Shield, Wifi, WifiOff } from "lucide-react";

interface HeaderProps {
  isOnline?: boolean;
}

export function Header({ isOnline = true }: HeaderProps) {
  return (
    <div className="relative flex items-center justify-between px-5 py-4 bg-gradient-to-r from-blue-700 to-blue-600 z-10">
      {/* Left: avatar + title */}
      <div className="flex items-center space-x-3">
        <div className="relative">
          <div className="w-11 h-11 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white shadow-inner">
            <Bot size={24} />
          </div>
          <div
            className={`absolute bottom-0 right-0 w-3 h-3 border-2 border-blue-600 rounded-full ${
              isOnline ? "bg-green-400 animate-pulse" : "bg-red-400"
            }`}
          />
        </div>
        <div>
          <h1 className="text-sm font-bold text-white tracking-wide">
            Smart Banking Assistant
          </h1>
          <div className="flex items-center space-x-1 mt-0.5">
            {isOnline ? (
              <>
                <Wifi size={10} className="text-green-300" />
                <span className="text-[11px] text-green-300 font-medium">
                  Connected
                </span>
              </>
            ) : (
              <>
                <WifiOff size={10} className="text-red-300" />
                <span className="text-[11px] text-red-300 font-medium">
                  Disconnected
                </span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Right: secure badge */}
      <div className="flex items-center space-x-1.5 bg-white/15 rounded-full px-3 py-1.5">
        <Shield size={13} className="text-green-300" />
        <span className="text-[11px] text-white/90 font-medium">Secure</span>
      </div>
    </div>
  );
}
