import axios from "axios";

const BASE_URL = "http://localhost:8000";

export interface ChatApiRequest {
  message: string;
  user_id?: string;
  last_intent?: string;
}

export interface ChatApiResponse {
  reply: string;
  intent?: string;
  confidence?: number;
  data?: Record<string, unknown>;
}

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function sendChatMessage(
  payload: ChatApiRequest,
): Promise<ChatApiResponse> {
  const response = await apiClient.post<ChatApiResponse>("/api/chat", payload);
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
