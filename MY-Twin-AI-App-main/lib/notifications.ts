/**
 * MyTwin – Push Notifications Service v1.0
 * - تسجيل الجهاز للحصول على Push Token
 * - معالجة الإشعارات الواردة (Foreground + Background)
 * - التنقل الذكي عند الضغط على الإشعار
 */
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform, Alert } from 'react-native';
import { supabase } from './supabase';
import { router } from 'expo-router';

// ✅ تكوين معالج الإشعارات الأمامية (Foreground)
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
    priority: Notifications.AndroidNotificationPriority.HIGH,
  }),
});

/**
 * تسجيل الجهاز للحصول على Push Token وتخزينه في Supabase
 */
export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    console.log('⚠️ الإشعارات تحتاج جهازاً حقيقياً');
    return null;
  }

  // طلب الصلاحيات
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.log('❌ المستخدم رفض صلاحية الإشعارات');
    return null;
  }

  // الحصول على Push Token
  try {
    const projectId = 'b5e2baa3-6015-40a5-9f31-115298d3b0c9'; // من app.json
    const token = await Notifications.getExpoPushTokenAsync({ projectId });
    console.log('✅ Push Token:', token.data);

    // تخزين التوكن في Supabase
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.user) {
      await supabase.from('profiles').update({
        push_token: token.data,
        device_platform: Platform.OS,
        push_token_updated_at: new Date().toISOString(),
      }).eq('id', session.user.id);
    }

    return token.data;
  } catch (e) {
    console.error('❌ فشل الحصول على Push Token:', e);
    return null;
  }
}

/**
 * معالجة الإشعارات الواردة والتنقل عند الضغط
 */
export function setupNotificationHandlers() {
  // ✅ عند الضغط على إشعار (التطبيق في الخلفية أو مغلق)
  Notifications.addNotificationResponseReceivedListener(response => {
    const data = response.notification.request.content.data;
    console.log('📩 تم الضغط على إشعار:', data);

    // التنقل حسب نوع الإشعار
    if (data?.type === 'proactive') {
      router.push('/chat');
    } else if (data?.type === 'bond_update') {
      router.push('/relationship');
    } else if (data?.type === 'goal_reminder') {
      router.push('/relationship');
    } else {
      router.push('/chat');
    }
  });

  // ✅ عند استلام إشعار في الأمام (Foreground)
  Notifications.addNotificationReceivedListener(notification => {
    console.log('📬 إشعار في الأمام:', notification.request.content.title);
  });
}

/**
 * إعداد قنوات الإشعارات (Android)
 */
export async function setupAndroidChannels() {
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('mytwin_proactive', {
      name: 'رسائل استباقية',
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#6B21A8',
    });

    await Notifications.setNotificationChannelAsync('mytwin_default', {
      name: 'عام',
      importance: Notifications.AndroidImportance.DEFAULT,
      vibrationPattern: [0, 100, 100, 100],
      lightColor: '#6B21A8',
    });
  }
}
