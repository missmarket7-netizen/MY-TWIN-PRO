import { useEffect, useRef, useState } from 'react';
import {
  View, StyleSheet, Animated, ActivityIndicator, Text, Dimensions, SafeAreaView
} from 'react-native';
import { router } from 'expo-router';
import { supabase } from '../lib/supabase';
import { useTwinStore } from '../store/useTwinStore';
import { setToken } from '../lib/api';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

export default function SplashScreen() {
  const { setAuth, theme } = useTwinStore();
  const isDark = theme === 'dark';

  const scaleAnim = useRef(new Animated.Value(0.3)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;
  const textOpacity = useRef(new Animated.Value(0)).current;
  const subTextOpacity = useRef(new Animated.Value(0)).current;
  const [loadingText, setLoadingText] = useState('');
  const animRef = useRef<Animated.CompositeAnimation | null>(null);
  const [routeReady, setRouteReady] = useState(false);
  const targetRoute = useRef('/login');

  useEffect(() => {
    // بدء الأنيميشن
    animRef.current = Animated.sequence([
      Animated.parallel([
        Animated.spring(scaleAnim, {
          toValue: 1,
          tension: 8,
          friction: 3,
          useNativeDriver: true,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        }),
      ]),
      Animated.parallel([
        Animated.timing(textOpacity, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(subTextOpacity, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        }),
      ]),
    ]);
    animRef.current.start();

    // بدء التحقق من الجلسة فوراً بالتوازي
    const isAr = useTwinStore.getState().lang === 'ar';
    const texts = {
      checking: isAr ? 'جارٍ الاتصال بتوأمك...' : 'Connecting to your Twin...',
      loading: isAr ? 'تحميل البيانات...' : 'Loading data...',
    };

    const bootPromise = (async () => {
      try {
        setLoadingText(texts.checking);
        const { data: { session } } = await supabase.auth.getSession();

        if (!session) {
          targetRoute.current = '/login';
          return;
        }

        setAuth(session.user.id);
        setToken(session.access_token);
        setLoadingText(texts.loading);

        // جلب ملف المستخدم
        const { data: profile, error: profileError } = await supabase
          .from('profiles')
          .select('onboarded')
          .eq('id', session.user.id)
          .maybeSingle();

        if (profileError) {
          console.error('Profile fetch error:', profileError);
          targetRoute.current = '/login';
          return;
        }

        // إذا لم يكن هناك صف أو لم يكمل الـ onboarding
        if (!profile || !profile.onboarded) {
          targetRoute.current = '/onboarding';
          return;
        }

        targetRoute.current = '/chat';
      } catch (e) {
        console.error('Boot error:', e);
        targetRoute.current = '/login';
      } finally {
        setRouteReady(true);
      }
    })();

    // انتظر على الأقل مدة الأنيميشن (2.8 ثانية) مع التحقق
    const minTime = new Promise(resolve => setTimeout(resolve, 2800));

    Promise.all([bootPromise, minTime]).then(() => {
      if (!routeReady) setRouteReady(true);
    });

    return () => {
      animRef.current?.stop();
    };
  }, []);

  // الانتقال عند الجاهزية
  useEffect(() => {
    if (routeReady) {
      router.replace(targetRoute.current as any);
    }
  }, [routeReady]);

  return (
    <SafeAreaView style={[styles.safe, isDark && { backgroundColor: '#1A1A1A' }]}>
      <View style={[styles.container, isDark && { backgroundColor: '#1A1A1A' }]}>
        <View style={styles.group}>
          <Animated.Image
            source={require('../assets/logo.png')}
            style={[
              styles.logo,
              {
                transform: [{ scale: scaleAnim }],
                opacity: opacityAnim,
              },
            ]}
            resizeMode="contain"
          />
          <Animated.Text style={[styles.appName, { opacity: textOpacity }, isDark && { color: '#D8B4FE' }]}>
            MyTwin
          </Animated.Text>
          <Animated.Text style={[styles.tagline, { opacity: subTextOpacity }, isDark && { color: '#A78BFA' }]}>
            {useTwinStore.getState().lang === 'ar' ? 'رفيقك الذكي دائماً 💜' : 'Your AI Companion Always 💜'}
          </Animated.Text>
          <Animated.Text style={[styles.company, { opacity: textOpacity }, isDark && { color: '#9B7FC7' }]}>
            BY SOULSYNC
          </Animated.Text>
          <Animated.Text style={[styles.copyright, { opacity: subTextOpacity }, isDark && { color: '#9B7FC7' }]}>
            2026©
          </Animated.Text>
        </View>

        <View style={styles.loadingRow}>
          <ActivityIndicator size="small" color={isDark ? '#D8B4FE' : '#6B21A8'} />
          <Text style={[styles.loadingText, isDark && { color: '#D8B4FE' }]}>
            {loadingText}
          </Text>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  group: { alignItems: 'center' },
  logo: {
    width: Math.min(SCREEN_WIDTH * 0.5, 240),
    height: Math.min(SCREEN_WIDTH * 0.5, 240),
    marginBottom: 16,
  },
  appName: {
    fontSize: 32,
    fontWeight: '800',
    color: '#6B21A8',
    letterSpacing: 2,
    marginBottom: 6,
  },
  tagline: {
    fontSize: 15,
    color: '#9B7FC7',
    marginBottom: 16,
    fontWeight: '500',
  },
  company: {
    fontSize: 16,
    fontWeight: '700',
    color: '#6B21A8',
    letterSpacing: 2,
    marginBottom: 4,
  },
  copyright: { fontSize: 12, color: '#9B7FC7', letterSpacing: 1 },
  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 24,
  },
  loadingText: {
    fontSize: 13,
    color: '#6B21A8',
    fontWeight: '500',
  },
});
