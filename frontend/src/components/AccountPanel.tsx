import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  Mail,
  CreditCard,
  Hash,
  ShieldCheck,
  RefreshCw,
  CheckCircle,
  Trash2,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { sendOtp, verifyOtp } from "../api";

export interface AccountInfo {
  email: string;
  account_holder: string;
  account_number: string;
  account_type: string;
  user_id: number;
}

interface AccountPanelProps {
  isOpen: boolean;
  onClose: () => void;
  accountInfo: AccountInfo | null;
  onAccountVerified: (info: AccountInfo) => void;
  onAccountCleared: () => void;
}

type Step = "form" | "otp" | "verified";

const STORAGE_KEY = "bank_session_account";

export function AccountPanel({
  isOpen,
  onClose,
  accountInfo,
  onAccountVerified,
  onAccountCleared,
}: AccountPanelProps) {
  const [step, setStep] = useState<Step>(accountInfo ? "verified" : "form");

  // Form state
  const [email, setEmail] = useState("");
  const [idNumber, setIdNumber] = useState("");
  const [accountNumber, setAccountNumber] = useState("");

  // OTP state
  const [otp, setOtp] = useState("");
  const [otpTimer, setOtpTimer] = useState(300); // 5 min
  const [timerActive, setTimerActive] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Sync step when accountInfo changes externally
  useEffect(() => {
    setStep(accountInfo ? "verified" : "form");
  }, [accountInfo]);

  // OTP countdown
  useEffect(() => {
    if (!timerActive) return;
    if (otpTimer <= 0) {
      setTimerActive(false);
      return;
    }
    const id = setInterval(() => setOtpTimer((t) => t - 1), 1000);
    return () => clearInterval(id);
  }, [timerActive, otpTimer]);

  const formatTime = (s: number) =>
    `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!email.trim() || !idNumber.trim() || !accountNumber.trim()) {
      setError("All fields are required.");
      return;
    }
    setLoading(true);
    try {
      await sendOtp({
        email: email.trim(),
        id_number: idNumber.trim(),
        account_number: accountNumber.trim(),
      });
      setStep("otp");
      setOtpTimer(300);
      setTimerActive(true);
      setSuccessMsg(`OTP sent to ${email.trim()}`);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Failed to send OTP. Check your details and try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!otp.trim() || otp.trim().length !== 6) {
      setError("Please enter the 6-digit OTP.");
      return;
    }
    setLoading(true);
    try {
      const data = await verifyOtp({ email: email.trim(), otp: otp.trim() });
      const info: AccountInfo = {
        email: email.trim(),
        account_holder: data.account_holder ?? "Account Holder",
        account_number: data.account_number ?? accountNumber.trim(),
        account_type: data.account_type ?? "savings",
        user_id: data.user_id ?? 1,
      };
      // Save to localStorage
      localStorage.setItem(STORAGE_KEY, JSON.stringify(info));
      onAccountVerified(info);
      setStep("verified");
      setSuccessMsg("");
      setTimerActive(false);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Invalid or expired OTP. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    if (timerActive && otpTimer > 0) return;
    setError("");
    setLoading(true);
    try {
      await sendOtp({
        email: email.trim(),
        id_number: idNumber.trim(),
        account_number: accountNumber.trim(),
      });
      setOtpTimer(300);
      setTimerActive(true);
      setSuccessMsg(`OTP resent to ${email.trim()}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Failed to resend OTP.");
    } finally {
      setLoading(false);
    }
  };

  const handleClearAccount = () => {
    localStorage.removeItem(STORAGE_KEY);
    setEmail("");
    setIdNumber("");
    setAccountNumber("");
    setOtp("");
    setError("");
    setSuccessMsg("");
    setStep("form");
    onAccountCleared();
  };

  const maskedAccount = (num: string) =>
    num.length > 4 ? `••••${num.slice(-4)}` : num;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          />

          {/* Panel */}
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, y: 40, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 40, scale: 0.96 }}
              transition={{ type: "spring", stiffness: 300, damping: 28 }}
              className="w-full max-w-lg pointer-events-auto"
            >
              <div className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200">
                {/* Header */}
                <div className="bg-gradient-to-r from-blue-700 to-blue-600 px-6 py-5 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center">
                      <ShieldCheck size={18} className="text-white" />
                    </div>
                    <div>
                      <h2 className="text-white font-bold text-base">
                        Account Verification
                      </h2>
                      <p className="text-blue-200 text-xs">
                        Secure identity check
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={onClose}
                    className="w-8 h-8 rounded-full bg-white/15 flex items-center justify-center text-white hover:bg-white/25 transition-colors"
                  >
                    <X size={16} />
                  </button>
                </div>

                <div className="p-6">
                  {/* Step indicator */}
                  {step !== "verified" && (
                    <div className="flex items-center space-x-2 mb-6">
                      {["Details", "OTP", "Done"].map((label, i) => {
                        const active =
                          (step === "form" && i === 0) ||
                          (step === "otp" && i === 1);
                        const done = step === "otp" && i === 0;
                        return (
                          <React.Fragment key={label}>
                            <div className="flex items-center space-x-1.5">
                              <div
                                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                              ${done ? "bg-green-500 text-white" : active ? "bg-blue-600 text-white" : "bg-slate-200 text-slate-400"}`}
                              >
                                {done ? "✓" : i + 1}
                              </div>
                              <span
                                className={`text-xs font-medium ${active ? "text-blue-700" : done ? "text-green-600" : "text-slate-400"}`}
                              >
                                {label}
                              </span>
                            </div>
                            {i < 2 && (
                              <div
                                className={`flex-1 h-px ${done ? "bg-green-300" : "bg-slate-200"}`}
                              />
                            )}
                          </React.Fragment>
                        );
                      })}
                    </div>
                  )}

                  {/* Error / Success messages */}
                  {error && (
                    <div className="flex items-start space-x-2 bg-red-50 border border-red-200 rounded-xl px-4 py-3 mb-4 text-sm text-red-700">
                      <AlertCircle size={16} className="shrink-0 mt-0.5" />
                      <span>{error}</span>
                    </div>
                  )}
                  {successMsg && !error && (
                    <div className="flex items-center space-x-2 bg-green-50 border border-green-200 rounded-xl px-4 py-3 mb-4 text-sm text-green-700">
                      <CheckCircle size={16} />
                      <span>{successMsg}</span>
                    </div>
                  )}

                  {/* ── Step 1: Details form ── */}
                  {step === "form" && (
                    <form onSubmit={handleSendOtp} className="space-y-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1.5">
                          Email Address
                        </label>
                        <div className="relative">
                          <Mail
                            size={15}
                            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                          />
                          <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="your@email.com"
                            required
                            className="w-full pl-9 pr-4 py-2.5 text-sm border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 transition-all"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1.5">
                          National ID Number
                        </label>
                        <div className="relative">
                          <Hash
                            size={15}
                            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                          />
                          <input
                            type="text"
                            value={idNumber}
                            onChange={(e) => setIdNumber(e.target.value)}
                            placeholder="e.g. 199912345678"
                            required
                            className="w-full pl-9 pr-4 py-2.5 text-sm border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 transition-all"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1.5">
                          Account Number
                        </label>
                        <div className="relative">
                          <CreditCard
                            size={15}
                            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                          />
                          <input
                            type="text"
                            value={accountNumber}
                            onChange={(e) => setAccountNumber(e.target.value)}
                            placeholder="e.g. ACC001"
                            required
                            className="w-full pl-9 pr-4 py-2.5 text-sm border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 transition-all"
                          />
                        </div>
                      </div>

                      <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 bg-blue-600 text-white text-sm font-semibold rounded-xl hover:bg-blue-700 active:scale-[0.98] transition-all disabled:opacity-50 flex items-center justify-center space-x-2 mt-2"
                      >
                        {loading ? (
                          <Loader2 size={16} className="animate-spin" />
                        ) : (
                          <Mail size={16} />
                        )}
                        <span>
                          {loading ? "Sending OTP..." : "Send OTP to Email"}
                        </span>
                      </button>
                    </form>
                  )}

                  {/* ── Step 2: OTP entry ── */}
                  {step === "otp" && (
                    <form onSubmit={handleVerifyOtp} className="space-y-4">
                      <p className="text-sm text-slate-600">
                        Enter the 6-digit code sent to <strong>{email}</strong>
                      </p>

                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1.5">
                          One-Time Password
                        </label>
                        <input
                          type="text"
                          inputMode="numeric"
                          pattern="[0-9]{6}"
                          maxLength={6}
                          value={otp}
                          onChange={(e) =>
                            setOtp(
                              e.target.value.replace(/\D/g, "").slice(0, 6),
                            )
                          }
                          placeholder="• • • • • •"
                          required
                          className="w-full text-center tracking-[0.6em] text-xl font-bold py-3 border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 transition-all"
                        />
                      </div>

                      <div className="flex items-center justify-between text-xs text-slate-500">
                        <span>
                          {otpTimer > 0 ? (
                            <>
                              ⏱ Expires in{" "}
                              <strong>{formatTime(otpTimer)}</strong>
                            </>
                          ) : (
                            <span className="text-red-500">OTP expired</span>
                          )}
                        </span>
                        <button
                          type="button"
                          onClick={handleResendOtp}
                          disabled={loading || (timerActive && otpTimer > 0)}
                          className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 disabled:opacity-40 font-medium"
                        >
                          <RefreshCw size={12} />
                          <span>Resend OTP</span>
                        </button>
                      </div>

                      <button
                        type="submit"
                        disabled={loading || otp.length !== 6}
                        className="w-full py-3 bg-blue-600 text-white text-sm font-semibold rounded-xl hover:bg-blue-700 active:scale-[0.98] transition-all disabled:opacity-50 flex items-center justify-center space-x-2"
                      >
                        {loading ? (
                          <Loader2 size={16} className="animate-spin" />
                        ) : (
                          <ShieldCheck size={16} />
                        )}
                        <span>
                          {loading
                            ? "Verifying..."
                            : "Verify & Connect Account"}
                        </span>
                      </button>

                      <button
                        type="button"
                        onClick={() => {
                          setStep("form");
                          setError("");
                          setOtp("");
                          setTimerActive(false);
                        }}
                        className="w-full py-2.5 text-sm text-slate-500 hover:text-slate-700 transition-colors"
                      >
                        ← Back to details
                      </button>
                    </form>
                  )}

                  {/* ── Step 3: Verified ── */}
                  {step === "verified" && accountInfo && (
                    <div className="space-y-4">
                      <div className="flex items-center space-x-3 bg-green-50 border border-green-200 rounded-2xl p-4">
                        <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center text-white shrink-0">
                          <CheckCircle size={20} />
                        </div>
                        <div>
                          <p className="font-semibold text-slate-800">
                            {accountInfo.account_holder}
                          </p>
                          <p className="text-xs text-slate-500">
                            {accountInfo.email}
                          </p>
                        </div>
                      </div>

                      <div className="bg-slate-50 rounded-2xl p-4 space-y-3">
                        <div className="flex justify-between text-sm">
                          <span className="text-slate-500">Account Number</span>
                          <span className="font-semibold text-slate-800 font-mono">
                            {maskedAccount(accountInfo.account_number)}
                          </span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-slate-500">Account Type</span>
                          <span className="font-semibold text-slate-800 capitalize">
                            {accountInfo.account_type}
                          </span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-slate-500">Status</span>
                          <span className="text-green-600 font-semibold flex items-center space-x-1">
                            <span className="w-2 h-2 rounded-full bg-green-500 inline-block" />
                            <span>Verified</span>
                          </span>
                        </div>
                      </div>

                      <p className="text-xs text-slate-400 text-center">
                        You can now ask about your balance, transactions, and
                        account details.
                      </p>

                      <button
                        onClick={handleClearAccount}
                        className="w-full py-2.5 flex items-center justify-center space-x-2 text-sm font-medium text-red-600 bg-red-50 border border-red-200 rounded-xl hover:bg-red-100 transition-colors"
                      >
                        <Trash2 size={15} />
                        <span>Clear Account Details</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
