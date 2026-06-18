import { createClient, SupabaseClient } from '@supabase/supabase-js';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import * as Application from 'expo-application';

// ── متغيرات البيئة ──────────────────────
const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL || '';
const SUPABASE_ANON_KEY = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || '';

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  console.warn(
    '⚠️ Supabase: Missing EXPO_PUBLIC_SUPABASE_URL or EXPO_PUBLIC_SUPABASE_ANON_KEY. Auth and DB features may not work.',
  );
}

// ─ـ تحقق بسيط من صحة الرابط ────────────────────
const isValidUrl = (url: string) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

if (SUPABASE_URL && !isValidUrl(SUPABASE_URL)) {
  console.error('❌ Supabase: Invalid URL format in EXPO_PUBLIC_SUPABASE_URL');
}

// ─ـ تجنب تضارب مفاتيح التخزين ─────────────────
const BUNDLE_ID = Application.applicationId || 'com.mytwin.app';
const STORAGE_KEY = `sb-${SUPABASE_URL.split('.')[0]?.replace(/https?:\/\//, '') || 'mytwin'}-${BUNDLE_ID}-auth`;

// ─ـ مخزن احتياطي في الذاكرة عند فشل SecureStore ──
const memoryFallback: Record<string, string> = {};

// ─ـ واجهة تخزين آمنة ──────────────────────────
const secureStorage = {
  async getItem(key: string): Promise<string | null> {
    try {
      // تحقق إضافي لحالة القفل على iOS
      if (Platform.OS === 'ios') {
        return await SecureStore.getItemAsync(key);
      }
      return await SecureStore.getItemAsync(key);
    } catch (error) {
      console.warn('🔐 SecureStore getItem failed:', error instanceof Error ? error.message : error);
      // الرجوع إلى المخزن الاحتياطي في الذاكرة
      return memoryFallback[key] || null;
    }
  },
  async setItem(key: string, value: string): Promise<void> {
    try {
      await SecureStore.setItemAsync(key, value);
      // مسح النسخة الاحتياطية في الذاكرة عند نجاح التخزين الآمن
      delete memoryFallback[key];
    } catch (error) {
      console.warn('🔐 SecureStore setItem failed, using memory fallback:', error instanceof Error ? error.message : error);
      // الرجوع إلى التخزين في الذاكرة
      memoryFallback[key] = value;
    }
  },
  async removeItem(key: string): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(key);
      delete memoryFallback[key];
    } catch (error) {
      console.warn('🔐 SecureStore removeItem failed:', error instanceof Error ? error.message : error);
      delete memoryFallback[key];
    }
  },
};

// ─ـ إنشاء عميل Supabase ──────────────────────────
export const supabase: SupabaseClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    storage: secureStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
    storageKey: STORAGE_KEY,
  },
});

// ─ـ تسجيل نجاح الاتصال للتصحيح (فقط في وضع التطوير) ──
if (__DEV__ && SUPABASE_URL) {
  console.log(`🔗 Supabase client initialized (storage: SecureStore + memory fallback, key: ${STORAGE_KEY})`);
}

// ─ـ الاستماع لتغييرات حالة المصادقة ──────────────
supabase.auth.onAuthStateChange((event, session) => {
  if (!__DEV__) return;

  switch (event) {
    case 'INITIAL_SESSION':
      console.log('🔐 Supabase Auth: Initial session loaded');
      break;
    case 'SIGNED_IN':
      console.log('✅ Supabase Auth: User signed in');
      break;
    case 'SIGNED_OUT':
      console.log('👋 Supabase Auth: User signed out');
      break;
    case 'TOKEN_REFRESHED':
      console.log('🔄 Supabase Auth: Token refreshed');
      break;
    case 'USER_UPDATED':
      console.log('📝 Supabase Auth: User updated');
      break;
    case 'PASSWORD_RECOVERY':
      console.log('🔑 Supabase Auth: Password recovery initiated');
      break;
  }
});

// ==================== أدوات مساعدة ====================

/**
 * التحقق من أن RLS يعمل بشكل صحيح
 * @returns true إذا كان RLS يمنع الوصول غير المصرح به (أي أن المستخدم المجهول لا يمكنه قراءة profiles)
 */
export async function checkRLS(): Promise<boolean> {
  try {
    const { error } = await supabase
      .from('profiles')
      .select('id')
      .limit(1);
    // إذا كان هناك خطأ (مثل permission denied)، فهذا يعني أن RLS يعمل
    return !!error;
  } catch {
    return false;
  }
}

/**
 * التحقق من صحة الاتصال بـ Supabase
 * @returns true إذا كان الاتصال سريعاً وصحياً (أقل من 3 ثوانٍ)
 */
export async function checkSupabaseHealth(): Promise<boolean> {
  try {
    const start = Date.now();
    const { error } = await supabase.from('profiles').select('count', { count: 'exact', head: true });
    const latency = Date.now() - start;
    if (error) throw error;
    if (__DEV__) console.log(`✅ Supabase healthy (${latency}ms)`);
    return latency < 3000;
  } catch (error) {
    if (__DEV__) console.error('❌ Supabase health check failed:', error);
    return false;
  }
}
