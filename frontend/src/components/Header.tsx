import { Bot, Shield, Wifi, WifiOff, UserCheck, UserX } from "lucide-react";
import { AccountInfo } from "./AccountPanel";

interface HeaderProps {
  isOnline?: boolean;
  accountInfo?: AccountInfo | null;
  onOpenAccountPanel?: () => void;
}

export function Header({
  isOnline = true,
  accountInfo,
  onOpenAccountPanel,
}: HeaderProps) {
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

      {/* Right: account button + secure badge */}
      <div className="flex items-center space-x-2">
        <button
          onClick={onOpenAccountPanel}
          title={
            accountInfo
              ? `Account: ${accountInfo.account_holder}`
              : "Connect your account"
          }
          className={`flex items-center space-x-1.5 rounded-full px-3 py-1.5 transition-colors ${
            accountInfo
              ? "bg-green-500/30 hover:bg-green-500/50 border border-green-400/40"
              : "bg-white/15 hover:bg-white/25 border border-white/20"
          }`}
        >
          {accountInfo ? (
            <>
              <UserCheck size={13} className="text-green-300" />
              <span className="text-[11px] text-green-200 font-medium max-w-[80px] truncate">
                {accountInfo.account_holder.split(" ")[0]}
              </span>
            </>
          ) : (
            <>
              <UserX size={13} className="text-white/70" />
              <span className="text-[11px] text-white/70 font-medium">
                My Account
              </span>
            </>
          )}
        </button>

        <div className="flex items-center space-x-1.5 bg-white/15 rounded-full px-3 py-1.5">
          <Shield size={13} className="text-green-300" />
          <span className="text-[11px] text-white/90 font-medium">Secure</span>
        </div>
      </div>
    </div>
  );
}
