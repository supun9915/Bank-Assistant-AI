import axios from "axios";

const BASE_URL = "http://localhost:8000";

export interface ChatApiRequest {
  message: string;
  user_id?: number;
  last_intent?: string;
  account_number?: string;
}

export interface ChatApiResponse {
  reply: string;
  intent?: string;
  confidence?: number;
  data?: Record<string, unknown>;
}

export interface SendOtpRequest {
  email: string;
  id_number: string;
  account_number: string;
}

export interface VerifyOtpRequest {
  email: string;
  otp: string;
}

export interface VerifyOtpResponse {
  success: boolean;
  message: string;
  account_holder?: string;
  account_number?: string;
  account_type?: string;
  user_id?: number;
}

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

export async function sendChatMessage(
  payload: ChatApiRequest,
): Promise<ChatApiResponse> {
  const response = await apiClient.post<ChatApiResponse>("/api/chat", payload);
  return response.data;
}

export async function sendOtp(
  payload: SendOtpRequest,
): Promise<{ success: boolean; message: string }> {
  const response = await apiClient.post("/api/account/send-otp", payload);
  return response.data;
}

export async function verifyOtp(
  payload: VerifyOtpRequest,
): Promise<VerifyOtpResponse> {
  const response = await apiClient.post<VerifyOtpResponse>(
    "/api/account/verify-otp",
    payload,
  );
  return response.data;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await apiClient.get("/health");
    return response.data?.status === "healthy";
  } catch {
    return false;
  }
}
