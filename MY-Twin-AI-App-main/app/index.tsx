import { Redirect } from 'expo-router';
import { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, Image, StyleSheet } from 'react-native';
import { supabase } from '../lib/supabase';
import { useTwinStore } from '../store/useTwinStore';

export default function Index() {
  const { setAuth, lang } = useTwinStore();
  const [route, setRoute] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const boot = async () => {
      try {
        // 1. تحقق من وجود جلسة نشطة
        const { data: { session } } = await supabase.auth.getSession();

        if (!session) {
          if (!cancelled) setRoute('/login');
          return;
        }

        // حفظ معرف المستخدم في المتجر
        setAuth(session.user.id);

        // 2. تحقق من وجود ملف المستخدم وإعداداته
        const { data: profile, error: profileError } = await supabase
          .from('profiles')
          .select('id, onboarded, tier')
          .eq('id', session.user.id)
          .maybeSingle();

        if (profileError || !profile) {
          // إذا لم يوجد ملف شخصي، هذا مستخدم جديد يحتاج لإعداد الحساب
          if (!cancelled) setRoute('/onboarding');
          return;
        }

        // 3. إذا لم يكمل الـ onboarding بعد
        if (!profile.onboarded) {
          if (!cancelled) setRoute('/onboarding');
          return;
        }

        // 4. التحقق من الاشتراك (اختياري - إذا كانت الباقة منتهية)
        // يمكن إضافة منطق أكثر تعقيداً هنا حسب الحاجة

        // 5. كل شيء جاهز، انتقل إلى المحادثة
        if (!cancelled) setRoute('/chat');
      } catch (e) {
        console.error('Boot error:', e);
        if (!cancelled) setRoute('/login');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    boot();

    return () => { cancelled = true; };
  }, []);

  if (loading || !route) {
    return (
      <View style={styles.container}>
        <Image
          source={require('../assets/icon.png')}
          style={styles.logo}
          resizeMode="contain"
        />
        <ActivityIndicator size="large" color="#6B21A8" style={{ marginTop: 20 }} />
      </View>
    );
  }

  return <Redirect href={route as any} />;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  logo: {
    width: 120,
    height: 120,
  },
});
