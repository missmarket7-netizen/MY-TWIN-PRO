import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { Platform } from 'react-native';
import * as Application from 'expo-application';
import { supabase } from './supabase';
import { useTwinStore, RelationshipDims } from '../store/useTwinStore';
import { jwtDecode } from 'jwt-decode';

// ==================== تكوين البيئة ====================
// في الإنتاج: استخدم المتغير البيئي EXPO_PUBLIC_API_URL
// في التطوير: استخدم localhost كاحتياطي فقط
const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 
  (Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000');

const APP_VERSION = Application.nativeApplicationVersion ?? '1.0.0';
const PLATFORM = Platform.OS;

// ==================== أدوات مساعدة ====================
let requestCounter = 0;
function generateRequestId(): string { 
  requestCounter++; 
  return `${Date.now().toString(36)}-${requestCounter.toString(36)}-${Math.random().toString(36).substring(2, 7)}`; 
}

function sanitizeTwinGender(gender: string | undefined): 'male' | 'female' {
  if (gender === 'male' || gender === 'female') return gender;
  return 'female';
}

// ==================== إنشاء عميل Axios ====================
export const API = axios.create({ 
  baseURL: BASE_URL, 
  timeout: 45000, 
  headers: { 'Content-Type': 'application/json' } 
});

// ==================== إدارة التوكن (Token Management) ====================
let _token = '';
let _tokenRefreshing = false;
let _tokenPromise: Promise<string> | null = null;
let _refreshSubscribers: Array<(token: string) => void> = [];

// ✅ إضافة مشترك جديد في قائمة انتظار التحديث
function addRefreshSubscriber(callback: (token: string) => void) {
  _refreshSubscribers.push(callback);
}

// ✅ إزالة مشترك من القائمة (يمنع تسرب الذاكرة)
function removeRefreshSubscriber(callback: (token: string) => void) {
  _refreshSubscribers = _refreshSubscribers.filter(cb => cb !== callback);
}

// ✅ إعلام جميع المشتركين بأن التوكن تجدد
function onTokenRefreshed(token: string) {
  _refreshSubscribers.forEach(callback => callback(token));
  _refreshSubscribers = [];
}

export function setToken(token: string) { _token = token; }
export function getToken() { return _token; }

// ✅ دالة جلب التوكن بشكل آمن (مع فحص تاريخ الصلاحية بـ jwtDecode)
async function getFreshToken(): Promise<string> {
  // إذا كان التوكن موجوداً ولم تنته صلاحيته، أرجعه فوراً
  if (_token) {
    try {
      const decoded = jwtDecode<{ exp: number }>(_token);
      const expiresAt = decoded.exp * 1000;
      // إذا تبقى أكثر من 60 ثانية على انتهاء الصلاحية
      if (Date.now() < expiresAt - 60000) return _token;
    } catch {
      // إذا فشل فك التشفير، نتجاهل ونحاول تجديده
    }
  }

  // إذا كانت هناك عملية تحديث جارية، أعد وعدها
  if (_tokenRefreshing && _tokenPromise) return _tokenPromise;
  
  _tokenRefreshing = true;
  _tokenPromise = (async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) { 
        _token = session.access_token; 
        return _token;
      }
    } catch (e) { 
      console.error('getSession error:', e); 
    }
    return '';
  })();
  
  try {
    const token = await _tokenPromise;
    onTokenRefreshed(token);
    return token;
  } finally {
    _tokenRefreshing = false;
    _tokenPromise = null;
  }
}

// ==================== اعتراضات (Interceptors) ====================

// ✅ اعتراض الطلبات: إضافة التوكن ورؤوس التطبيق
API.interceptors.request.use(async (config) => {
  if (!config.headers['X-Request-ID']) config.headers['X-Request-ID'] = generateRequestId();
  config.headers['X-App-Version'] = APP_VERSION; 
  config.headers['X-Platform'] = PLATFORM;
  
  try { 
    const store = useTwinStore.getState(); 
    if (store.twinGender) {
      config.headers['X-Twin-Gender'] = sanitizeTwinGender(store.twinGender);
    }
  } catch (e) {}
  
  const token = await getFreshToken(); 
  if (token) config.headers['Authorization'] = `Bearer ${token}`;
  return config;
});

// ✅ اعتراض الردود: تجديد التوكن عند 401 وإعادة المحاولة
interface RetryConfig extends InternalAxiosRequestConfig { 
  _retry?: boolean; 
  _retryCount?: number; 
}

API.interceptors.response.use((r) => r, async (error: AxiosError) => {
  const config = error.config as RetryConfig | undefined; 
  if (!config) return Promise.reject(error);
  
  // ✅ معالجة 401 مع كسر حلقة التحديث اللانهائية
  if (error.response?.status === 401 && !config._retry) {
    // إذا كانت هناك عملية تحديث جارية، اشترك في انتظارها
    if (_tokenRefreshing) {
      return new Promise((resolve) => {
        const subscriber = (token: string) => {
          if (config.headers) config.headers['Authorization'] = `Bearer ${token}`;
          removeRefreshSubscriber(subscriber); // تنظيف بعد الاستخدام
          resolve(API(config));
        };
        addRefreshSubscriber(subscriber);
      });
    }

    config._retry = true; // ✅ كسر الحلقة: نمنع إعادة المحاولة أكثر من مرة
    _tokenRefreshing = true;
    try {
      const { data: { session } } = await supabase.auth.refreshSession();
      if (session?.access_token) {
        _token = session.access_token;
        if (config.headers) config.headers['Authorization'] = `Bearer ${_token}`;
        return API(config);
      }
      // ✅ إذا فشل refresh، جرب getSession مرة أخيرة
      const { data: { session: currentSession } } = await supabase.auth.getSession();
      if (currentSession?.access_token) {
        _token = currentSession.access_token;
        if (config.headers) config.headers['Authorization'] = `Bearer ${_token}`;
        return API(config);
      }
    } catch (refreshError) { 
      console.error('Token refresh failed:', refreshError); 
    } finally {
      _tokenRefreshing = false;
      _tokenPromise = null;
      _refreshSubscribers = [];
    }
    // ✅ فشل كل شيء: تسجيل خروج صامت
    try {
      await supabase.auth.signOut();
      useTwinStore.getState().logout();
    } catch (e) {}
    return Promise.reject(new Error('SESSION_EXPIRED'));
  }
  
  // ✅ إعادة محاولة عند أخطاء الشبكة أو الخادم
  const shouldRetry = !error.response || error.response.status >= 502 || error.code === 'ECONNABORTED';
  if (shouldRetry) {
    config._retryCount = config._retryCount ?? 0;
    if (config._retryCount < 3) {
      config._retryCount++;
      await new Promise((resolve) => setTimeout(resolve, Math.pow(2, config._retryCount!) * 1000));
      return API(config);
    }
  }
  return Promise.reject(error);
});

// ==================== الواجهات (Interfaces) ====================

export interface TwinResponse {
  reply: string; 
  new_bond?: number; 
  twin_gender?: 'male' | 'female'; 
  voice_personality?: string;
  emotion?: { 
    primary: string; secondary: string; intensity: number; 
    valence: number; arousal: number; trend?: string; riskLevel?: string 
  };
  relationship_dims?: Record<string, number>; 
  relationship_stage?: string; 
  journey_phase?: string; 
  journey_day?: number;
  attachment_style?: string; 
  consciousness?: { last_thought?: string; active_goals?: string[] };
  memory_used?: boolean; 
  thinking_stage?: string; 
  dialect?: string; 
  latency_ms?: number; 
  energy?: number; 
  provider?: string;
}

export interface TwinRequest {
  message: string; twinName: string; bondLevel: number; relationshipDims: RelationshipDims;
  chatHistory?: Array<{ role: string; content: string }>; 
  journeyPhase?: string; attachmentStyle?: string;
  twinStyle?: string; replyStyle?: string; 
  lang?: string; image?: string; calmMode?: boolean; twinGender?: 'male' | 'female';
}

// ==================== دوال مساعدة ====================

function toSafeRecord(dims: RelationshipDims | Record<string, any>): Record<string, number> {
  const out: Record<string, number> = {};
  if (dims && typeof dims === 'object') {
    for (const [k, v] of Object.entries(dims)) {
      if (typeof v === 'number') out[k] = v;
    }
  }
  return out;
}

// ==================== دوال API الأساسية (مع دعم AbortSignal) ====================

export const askTwin = async (req: TwinRequest, signal?: AbortSignal): Promise<TwinResponse> => {
  const store = useTwinStore.getState(); 
  const g = sanitizeTwinGender(req.twinGender || store.twinGender);
  const safeDims = toSafeRecord(req.relationshipDims || {});
  
  const payload = {
    message: req.message,
    twin_name: req.twinName || 'توأمك',
    bond_level: req.bondLevel || 0,
    relationship_dims: safeDims,
    history: req.chatHistory?.slice(-10) || [],
    journey_phase: req.journeyPhase || 'introduction',
    attachment_style: req.attachmentStyle || 'unknown',
    twin_style: req.twinStyle || 'supportive',
    reply_style: req.replyStyle || 'medium',
    lang: req.lang || 'ar',
    image: req.image,
    calm_mode: req.calmMode || false,
    twin_gender: g,
  };
  
  const { data } = await API.post('/api/chat', payload, {
    headers: { 'X-Calm-Mode': String(req.calmMode || false), 'X-Twin-Gender': g },
    signal, // ✅ دعم إلغاء الطلب
  });
  
  return {
    reply: data.reply, new_bond: data.new_bond, emotion: data.emotion,
    relationship_dims: data.relationship_dims, relationship_stage: data.relationship_stage,
    journey_phase: data.journey_phase, journey_day: data.journey_day,
    attachment_style: data.attachment_style, consciousness: data.consciousness,
    memory_used: data.memory_used, thinking_stage: data.thinking_stage,
    dialect: data.dialect, latency_ms: data.latency_ms, energy: data.energy,
    provider: data.provider, twin_gender: data.twin_gender || g,
    voice_personality: data.voice_personality,
  };
};

export const sendChatFromStore = async (message: string, image?: string, signal?: AbortSignal): Promise<TwinResponse> => {
  const s = useTwinStore.getState();
  return askTwin({
    message, twinName: s.twinName, bondLevel: s.bondLevel,
    relationshipDims: s.relationshipDims, chatHistory: s.chatHistory.slice(-10),
    journeyPhase: s.journeyPhase, attachmentStyle: s.attachmentStyle,
    twinStyle: s.twinStyle, replyStyle: s.replyStyle, lang: s.lang,
    image, calmMode: s.calmMode, twinGender: sanitizeTwinGender(s.twinGender),
  }, signal);
};

export const updateStoreFromResponse = (r: TwinResponse) => {
  const s = useTwinStore.getState();
  if (r.new_bond !== undefined) s.updateBond(r.new_bond);
  if (r.relationship_dims) s.updateRelationshipDims(r.relationship_dims);
  if (r.energy !== undefined) s.setTwinEnergy(r.energy || 100);
  if (r.journey_phase) s.setJourneyPhase(r.journey_phase as any);
  if (r.attachment_style) s.setAttachmentStyle(r.attachment_style as any);
  if (r.emotion) s.setEmotionState(r.emotion as any);
  if (r.thinking_stage) { 
    s.setThinkingStage(r.thinking_stage); 
    s.setThinking(r.thinking_stage !== 'complete');
  }
  if (r.twin_gender) s.setTwinGender(r.twin_gender);
  s.setTotalMessages(s.totalMessages + 1);
};

// ==================== خدمات الأدوات (مع دعم AbortSignal) ====================

export const fetchWeather = async (city: string = 'Cairo', signal?: AbortSignal) => {
  let params: any = {};
  if (city.includes(',')) {
    const [lat, lon] = city.split(',');
    params = { lat, lon };
  } else {
    params = { city };
  }
  const { data } = await API.get('/api/services/weather', { params, signal });
  return data;
};

export const fetchYouTube = async (query: string, lang: string = 'ar', signal?: AbortSignal) => {
  const { data } = await API.get('/api/services/youtube', { params: { query, lang }, signal });
  return data;
};

export const fetchSpotify = async (query: string, signal?: AbortSignal) => {
  const { data } = await API.get('/api/services/spotify', { params: { query }, signal });
  return data;
};

export const fetchGoogleSearch = async (query: string, signal?: AbortSignal) => {
  const { data } = await API.get('/api/services/google', { params: { query }, signal });
  return data;
};

export const fetchCalendarEvents = async (signal?: AbortSignal) => {
  const { data } = await API.get('/api/services/calendar', { signal });
  return data;
};

export const fetchNews = async (country: string = 'sa', signal?: AbortSignal) => {
  const { data } = await API.get('/api/services/news', { params: { country }, signal });
  return data;
};

export const fetchMaps = async (query: string, signal?: AbortSignal) => {
  const { data } = await API.get('/api/services/maps', { params: { query }, signal });
  return data;
};

export const fetchLocationInfo = async (lat: number, lon: number, signal?: AbortSignal) => {
  const { data } = await API.get('/api/services/location', { params: { lat, lon }, signal });
  return data;
};

export const fetchCurrency = async (base: string = 'USD', signal?: AbortSignal) => {
  const { data } = await API.get('/api/services/currency', { params: { base }, signal });
  return data;
};

export const sendHomeAssistantCommand = async (command: string, entity_id?: string, signal?: AbortSignal) => {
  const { data } = await API.post('/api/services/homeassistant', { command, entity_id }, { signal });
  return data;
};

export const sendEmail = async (to: string, subject: string, body: string, signal?: AbortSignal) => {
  const { data } = await API.post('/api/services/email', { to, subject, body }, { signal });
  return data;
};

export const sendTelegram = async (chatId: string, message: string, signal?: AbortSignal) => {
  const { data } = await API.post('/api/services/telegram', { chat_id: chatId, message }, { signal });
  return data;
};

export const fetchNotes = async (signal?: AbortSignal) => {
  const { data } = await API.get('/api/services/notes', { signal });
  return data;
};

export const createNote = async (content: string, signal?: AbortSignal) => {
  const { data } = await API.post('/api/services/notes', { content }, { signal });
  return data;
};

export const fetchTasks = async (signal?: AbortSignal) => {
  const { data } = await API.get('/api/services/tasks', { signal });
  return data;
};

export const createTask = async (title: string, due?: string, signal?: AbortSignal) => {
  const { data } = await API.post('/api/services/tasks', { title, due }, { signal });
  return data;
};

export default API;
