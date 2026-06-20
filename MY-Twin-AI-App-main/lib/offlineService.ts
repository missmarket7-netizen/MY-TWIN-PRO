/**
 * Offline Service – manages offline message queue and cache.
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiPost } from './httpClient';

const OFFLINE_QUEUE_KEY = 'mytwin_offline_queue';
const RESPONSE_CACHE_KEY = 'mytwin_response_cache';
const MAX_CACHED_RESPONSES = 50;

interface QueuedMessage {
  id: string;
  message: string;
  timestamp: number;
  retries: number;
}

// ========== Response Cache ==========

export async function cacheResponse(message: string, reply: string): Promise<void> {
  try {
    const cached = await getCachedResponses();
    const hash = simpleHash(message);
    cached[hash] = { reply, timestamp: Date.now() };
    // Keep only last N responses
    const keys = Object.keys(cached);
    if (keys.length > MAX_CACHED_RESPONSES) {
      const oldest = keys.sort((a, b) => cached[a].timestamp - cached[b].timestamp)[0];
      delete cached[oldest];
    }
    await AsyncStorage.setItem(RESPONSE_CACHE_KEY, JSON.stringify(cached));
  } catch {}
}

export async function getCachedResponse(message: string): Promise<string | null> {
  try {
    const cached = await getCachedResponses();
    const hash = simpleHash(message);
    return cached[hash]?.reply || null;
  } catch {
    return null;
  }
}

async function getCachedResponses(): Promise<Record<string, { reply: string; timestamp: number }>> {
  try {
    const raw = await AsyncStorage.getItem(RESPONSE_CACHE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function simpleHash(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(36);
}

// ========== Offline Queue ==========

export async function addToOfflineQueue(message: string): Promise<void> {
  try {
    const queue = await getOfflineQueue();
    queue.push({
      id: Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      message,
      timestamp: Date.now(),
      retries: 0,
    });
    await AsyncStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
  } catch {}
}

export async function getOfflineQueue(): Promise<QueuedMessage[]> {
  try {
    const raw = await AsyncStorage.getItem(OFFLINE_QUEUE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export async function clearOfflineQueue(): Promise<void> {
  await AsyncStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify([]));
}

export async function processOfflineQueue(): Promise<number> {
  const queue = await getOfflineQueue();
  if (queue.length === 0) return 0;

  let processed = 0;
  const remaining: QueuedMessage[] = [];

  for (const item of queue) {
    try {
      await apiPost('/api/chat', { message: item.message, lang: 'ar' });
      processed++;
    } catch {
      // Keep in queue for retry
      if (item.retries < 3) {
        remaining.push({ ...item, retries: item.retries + 1 });
      }
    }
  }

  await AsyncStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(remaining));
  return processed;
}

// ========== Network Status ==========

type NetworkCallback = (isOnline: boolean) => void;
const listeners: NetworkCallback[] = [];
let isOnline = true;

export function onNetworkChange(callback: NetworkCallback): () => void {
  listeners.push(callback);
  return () => {
    const index = listeners.indexOf(callback);
    if (index > -1) listeners.splice(index, 1);
  };
}

export function setNetworkStatus(online: boolean): void {
  if (isOnline !== online) {
    isOnline = online;
    listeners.forEach(cb => cb(online));
    // Process queue when back online
    if (online) {
      processOfflineQueue().catch(() => {});
    }
  }
}

export function getNetworkStatus(): boolean {
  return isOnline;
}
