import React, { useState, useEffect } from "react";
import { ChatContainer } from "./components/ChatContainer";
import { AccountPanel, AccountInfo } from "./components/AccountPanel";

const STORAGE_KEY = "bank_session_account";

export function App() {
  const [accountInfo, setAccountInfo] = useState<AccountInfo | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  // Clear any previous session on every page load
  useEffect(() => {
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const handleAccountVerified = (info: AccountInfo) => {
    setAccountInfo(info);
  };

  const handleAccountCleared = () => {
    setAccountInfo(null);
    setIsPanelOpen(false);
  };

  return (
    <div className="flex w-full min-h-screen justify-center items-center bg-gradient-to-br from-blue-900 via-blue-800 to-slate-900 p-4">
      {/* Decorative blobs */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-32 -left-32 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl" />
        <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-4xl">
        {/* Bank branding above chat */}
        <div className="flex items-center justify-center space-x-2 mb-4">
          <div className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center">
            <span className="text-white text-xs font-bold">SB</span>
          </div>
          <span className="text-white/80 text-sm font-semibold tracking-wide">
            SmartBank AI
          </span>
        </div>

        <ChatContainer
          accountInfo={accountInfo}
          onOpenAccountPanel={() => setIsPanelOpen(true)}
        />

        <p className="text-center text-white/40 text-[11px] mt-3">
          Secured with 256-bit encryption &middot; Powered by AI
        </p>
      </div>

      <AccountPanel
        isOpen={isPanelOpen}
        onClose={() => setIsPanelOpen(false)}
        accountInfo={accountInfo}
        onAccountVerified={handleAccountVerified}
        onAccountCleared={handleAccountCleared}
      />
    </div>
  );
}
