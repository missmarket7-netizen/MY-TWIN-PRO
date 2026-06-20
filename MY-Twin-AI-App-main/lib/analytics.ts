import PostHog from 'posthog-react-native';
import { Platform } from 'react-native';

// ── أنواع البيانات ──────────────────────────────
interface AnalyticsConfig {
  apiKey: string;
  host: string;
  enabled: boolean;
}

interface TrackProperties {
  [key: string]: string | number | boolean | null | undefined;
}

// ── Logger مركزي ────────────────────────────────
const logger = {
  info: (msg: string) => {
    if (__DEV__) console.log(`[Analytics] ${msg}`);
  },
  warn: (msg: string, err?: unknown) => {
    if (__DEV__) console.warn(`[Analytics] ${msg}`, err || '');
  },
  error: (msg: string, err?: unknown) => {
    // في الإنتاج يمكن إرسال الخطأ إلى Sentry
    console.error(`[Analytics] ${msg}`, err || '');
  },
};

// ── الحالة الداخلية ─────────────────────────────
let posthog: PostHog | null = null;
let config: Readonly<AnalyticsConfig> | null = null;
let isInitialized = false;
let privacyConsent = false; // GDPR/CCPA
let initPromise: Promise<boolean> | null = null;

// ── التحقق من صحة اسم الحدث ─────────────────────
function isValidEventName(event: string): boolean {
  if (!event || typeof event !== 'string') return false;
  const trimmed = event.trim();
  // اسم الحدث يجب أن يكون بين 1 و 100 حرف
  return trimmed.length > 0 && trimmed.length <= 100;
}

// ── تنظيف الخصائص (إزالة القيم غير المدعومة) ────
function sanitizeProperties(props?: TrackProperties): Record<string, any> | undefined {
  if (!props) return undefined;
  const clean: Record<string, any> = {};
  for (const [key, value] of Object.entries(props)) {
    if (value === undefined || value === null) continue;
    if (typeof value === 'object') {
      try {
        clean[key] = JSON.stringify(value);
      } catch {
        // تجاهل القيم غير القابلة للتحويل
      }
    } else {
      clean[key] = value;
    }
  }
  return Object.keys(clean).length > 0 ? clean : undefined;
}

// ── التهيئة ──────────────────────────────────────
export async function initAnalytics(): Promise<boolean> {
  // منع التهيئة المزدوجة
  if (isInitialized && posthog) {
    logger.info('Already initialized');
    return true;
  }

  // إذا كانت التهيئة جارية، ننتظر نتيجتها
  if (initPromise) {
    return await initPromise;
  }

  initPromise = (async (): Promise<boolean> => {
    try {
      const apiKey = process.env.EXPO_PUBLIC_POSTHOG_KEY;
      if (!apiKey) {
        logger.info('PostHog key not set, analytics disabled');
        config = { apiKey: '', host: '', enabled: false };
        return false;
      }

      const host = process.env.EXPO_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com';

      // تدمير العميل القديم إن وُجد
      if (posthog) {
        try {
          posthog.shutdown();
        } catch {
          // تجاهل أخطاء الإغلاق
        }
        posthog = null;
      }

      // إنشاء العميل الجديد
      posthog = new PostHog(apiKey, {
        host,
        // إعدادات إضافية للخصوصية
        flushAt: 5,
        flushInterval: 5000,
      });

      // انتظار جاهزية PostHog
      if (typeof (posthog as any).setup === 'function') {
        await (posthog as any).setup();
      }

      config = Object.freeze({ apiKey, host, enabled: true });
      isInitialized = true;
      logger.info('✅ PostHog initialized');
      return true;
    } catch (e) {
      logger.error('PostHog init failed:', e);
      config = { apiKey: '', host: '', enabled: false };
      isInitialized = false;
      posthog = null;
      return false;
    } finally {
      initPromise = null;
    }
  })();

  return await initPromise;
}

// ── الموافقة على الخصوصية ────────────────────────
export function setPrivacyConsent(consent: boolean): void {
  privacyConsent = consent;
  if (!consent && posthog) {
    // حذف جميع البيانات المحلية عند سحب الموافقة
    try {
      posthog.reset();
    } catch {
      // تجاهل
    }
  }
}

// ── تتبع حدث ─────────────────────────────────────
export function track(event: string, properties?: TrackProperties): void {
  if (!posthog || !config?.enabled) return;

  // التحقق من الموافقة
  if (!privacyConsent) {
    logger.warn('Cannot track event: privacy consent not given');
    return;
  }

  // التحقق من صحة الحدث
  if (!isValidEventName(event)) {
    logger.warn(`Invalid event name: "${event}"`);
    return;
  }

  try {
    const cleanProps = sanitizeProperties(properties);
    posthog.capture(event.trim(), cleanProps);
  } catch (e) {
    logger.error(`Failed to track event "${event}":`, e);
  }
}

// ── تتبع شاشة ─────────────────────────────────────
export function screen(screenName: string, properties?: TrackProperties): void {
  if (!posthog || !config?.enabled || !privacyConsent) return;

  if (!screenName || typeof screenName !== 'string' || !screenName.trim()) {
    logger.warn('Invalid screen name');
    return;
  }

  try {
    const cleanProps = sanitizeProperties(properties);
    posthog.screen(screenName.trim(), cleanProps);
  } catch (e) {
    logger.error(`Failed to track screen "${screenName}":`, e);
  }
}

// ── تعريف المستخدم ───────────────────────────────
export function identify(userId: string, traits?: TrackProperties): void {
  if (!posthog || !config?.enabled) return;

  if (!privacyConsent) {
    logger.warn('Cannot identify user: privacy consent not given');
    return;
  }

  if (!userId || typeof userId !== 'string' || !userId.trim()) {
    logger.warn('Invalid userId for identify');
    return;
  }

  try {
    const cleanTraits = sanitizeProperties(traits);
    posthog.identify(userId.trim(), cleanTraits);
  } catch (e) {
    logger.error(`Failed to identify user "${userId}":`, e);
  }
}

// ── إعادة تعيين المستخدم (تسجيل الخروج) ──────────
export function resetUser(): void {
  if (!posthog) return;

  try {
    posthog.reset();
    logger.info('User reset successfully');
  } catch (e) {
    logger.error('Failed to reset user:', e);
  }
}

// ── تفريغ الأحداث قبل إغلاق التطبيق ──────────────
export function flush(): void {
  if (!posthog) return;

  try {
    posthog.flush();
    logger.info('Events flushed');
  } catch (e) {
    logger.error('Failed to flush events:', e);
  }
}

// ── إغلاق التحليلات نهائياً ──────────────────────
export function shutdown(): void {
  if (!posthog) return;

  try {
    posthog.flush();
    posthog.shutdown();
    posthog = null;
    isInitialized = false;
    config = null;
    logger.info('Analytics shutdown complete');
  } catch (e) {
    logger.error('Failed to shutdown analytics:', e);
  }
}

// ── التحقق من حالة التهيئة ───────────────────────
export function isAnalyticsReady(): boolean {
  return isInitialized && posthog !== null && config?.enabled === true;
}

// ── الحصول على الإعدادات الحالية ──────────────────
export function getAnalyticsConfig(): Readonly<AnalyticsConfig> | null {
  return config;
}
