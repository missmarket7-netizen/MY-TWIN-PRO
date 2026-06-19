/**
 * MyTwin – HTTP Client (Frontend)
 * يتواصل مع الـ Backend الجديد. لا يستدعي Supabase.
 */
import { getToken, removeToken } from './auth';
import { Platform } from 'react-native';
import * as Application from 'expo-application';

const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 
  (Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000');

let requestCounter = 0;
function generateRequestId(): string {
  requestCounter++;
  return `${Date.now().toString(36)}-${requestCounter.toString(36)}-${Math.random().toString(36).substring(2, 7)}`;
}

async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = await getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Request-ID': generateRequestId(),
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) {
    await removeToken();
    throw new Error('SESSION_EXPIRED');
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response;
}

// ========== دوال عامة ==========
export async function apiGet<T = any>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${BASE_URL}${path}`);
  if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  const response = await authFetch(url.toString());
  return response.json();
}

export async function apiPost<T = any>(path: string, body?: any): Promise<T> {
  const response = await authFetch(`${BASE_URL}${path}`, {
    method: 'POST',
    body: body ? JSON.stringify(body) : undefined,
  });
  return response.json();
}

export async function apiPut<T = any>(path: string, body?: any): Promise<T> {
  const response = await authFetch(`${BASE_URL}${path}`, {
    method: 'PUT',
    body: body ? JSON.stringify(body) : undefined,
  });
  return response.json();
}

export async function apiDelete<T = any>(path: string): Promise<T> {
  const response = await authFetch(`${BASE_URL}${path}`, { method: 'DELETE' });
  return response.json();
}

// ========== دوال متخصصة ==========
export async function login(email: string, password: string): Promise<{ token: string; user_id: string }> {
  return apiPost('/api/auth/login', { email, password });
}

export async function signup(email: string, password: string): Promise<{ token: string; user_id: string }> {
  return apiPost('/api/auth/signup', { email, password });
}

export async function getProfile(): Promise<any> {
  return apiGet('/api/profile');
}

export async function updateProfile(data: any): Promise<any> {
  return apiPut('/api/profile', data);
}

export async function getMemories(): Promise<any[]> {
  return apiGet('/api/memories');
}

export async function getMoods(): Promise<any[]> {
  return apiGet('/api/moods');
}

export async function addMood(mood: string): Promise<any> {
  return apiPost('/api/moods', { mood });
}

export async function getFeedback(): Promise<any[]> {
  return apiGet('/api/feedback');
}

export async function getGoals(): Promise<any[]> {
  return apiGet('/api/goals');
}

export async function addGoal(title: string): Promise<any> {
  return apiPost('/api/goals', { title });
}

export async function deleteGoal(goalId: string): Promise<void> {
  return apiDelete(`/api/goals/${goalId}`);
}

export async function generateReferralCode(): Promise<{ code: string }> {
  return apiPost('/api/referral/generate');
}

export async function activateReferralCode(code: string): Promise<any> {
  return apiPost('/api/referral/activate', { code });
}

export async function getReferralStats(): Promise<any> {
  return apiGet('/api/referral/stats');
}

export async function completeOnboarding(data: any): Promise<any> {
  return apiPost('/api/onboarding', data);
}

export async function deleteAccount(): Promise<void> {
  return apiDelete('/api/account');
}

export async function exportData(): Promise<any> {
  return apiGet('/api/me/export');
}

export async function updatePushToken(token: string, platform: string): Promise<void> {
  return apiPut('/api/push-token', { token, platform });
}

export async function verifyReceipt(receipt: string, productId: string): Promise<{ valid: boolean }> {
  return apiPost('/api/billing/verify', { receipt, productId, platform: Platform.OS });
}

export async function getUsageStats(): Promise<any> {
  return apiGet('/api/stats');
}

export async function getAdStatus(): Promise<any> {
  return apiGet('/api/ads/status');
}

export async function claimAdReward(): Promise<any> {
  return apiPost('/api/ads/reward', { ad_type: 'rewarded' });
}

export async function getTodayTasks(): Promise<any[]> {
  return apiGet('/api/tasks/today');
}

export async function getCalendarEvents(): Promise<any> {
  return apiGet('/api/calendar/all');
}

// ========== تدفق المحادثة ==========
export async function streamChat(
  message: string,
  history: any[] = [],
  lang: string = 'ar',
  onChunk: (text: string) => void,
  signal?: AbortSignal,
): Promise<string> {
  const url = `${BASE_URL}/api/chat/stream`;
  const token = await getToken();

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
      'Authorization': token ? `Bearer ${token}` : '',
      'X-Request-ID': generateRequestId(),
    },
    body: JSON.stringify({ message, history, lang }),
    signal,
  });

  if (!response.ok) {
    if (response.status === 401) { await removeToken(); throw new Error('SESSION_EXPIRED'); }
    throw new Error(`Stream error: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let fullText = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split('\n');
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6).trim();
        if (data === '[DONE]') continue;
        fullText += data;
        onChunk(data);
      }
    }
  }
  return fullText;
}
