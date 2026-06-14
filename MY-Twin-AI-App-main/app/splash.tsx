import { useEffect, useRef, useState } from 'react';
import { View, StyleSheet, Animated, Dimensions, SafeAreaView, Text } from 'react-native';
import { router } from 'expo-router';
import { supabase } from '../lib/supabase';
import { useTwinStore } from '../store/useTwinStore';
import { setToken } from '../lib/api';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

export default function SplashScreen() {
  const { setAuth, theme } = useTwinStore();
  const isDark = theme === 'dark';

  // قيم الأنيميشن
  const logoScale = useRef(new Animated.Value(0.4)).current;
  const logoOpacity = useRef(new Animated.Value(0)).current;
  const titleOpacity = useRef(new Animated.Value(0)).current;
  const subtitleOpacity = useRef(new Animated.Value(0)).current;
  const taglineOpacity = useRef(new Animated.Value(0)).current;
  const copyrightOpacity = useRef(new Animated.Value(0)).current;
  const gradientOpacity = useRef(new Animated.Value(0)).current;

  const [routeReady, setRouteReady] = useState(false);
  const targetRoute = useRef('/login');

  useEffect(() => {
    // أنيميشن متسلسل احترافي
    const animation = Animated.sequence([
      // المرحلة 1: ظهور الشعار مع نبضة
      Animated.parallel([
        Animated.spring(logoScale, {
          toValue: 1,
          tension: 6,
          friction: 3,
          useNativeDriver: true,
        }),
        Animated.timing(logoOpacity, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ]),
      // المرحلة 2: ظهور التدرج اللوني الخلفي
      Animated.timing(gradientOpacity, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
      // المرحلة 3: ظهور اسم التطبيق
      Animated.timing(titleOpacity, {
        toValue: 1,
        duration: 500,
        useNativeDriver: true,
      }),
      // المرحلة 4: ظهور الشعار الثانوي
      Animated.parallel([
        Animated.timing(subtitleOpacity, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        }),
        Animated.timing(taglineOpacity, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        }),
      ]),
      // المرحلة 5: ظهور حقوق النشر
      Animated.timing(copyrightOpacity, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }),
    ]);

    animation.start();

    // التحقق من الجلسة
    const bootPromise = (async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
          targetRoute.current = '/login';
          return;
        }
        setAuth(session.user.id);
        setToken(session.access_token);
        const { data: profile } = await supabase
          .from('profiles')
          .select('onboarded')
          .eq('id', session.user.id)
          .maybeSingle();
        if (!profile || !profile.onboarded) {
          targetRoute.current = '/onboarding';
          return;
        }
        targetRoute.current = '/chat';
      } catch (e) {
        targetRoute.current = '/login';
      } finally {
        setRouteReady(true);
      }
    })();

    // ضمان وقت أدنى للشاشة (3.5 ثواني)
    const minTime = new Promise(resolve => setTimeout(resolve, 3500));
    Promise.all([bootPromise, minTime]).then(() => {
      if (!routeReady) setRouteReady(true);
    });

    return () => {
      animation.stop();
    };
  }, []);

  // الانتقال للصفحة المناسبة
  useEffect(() => {
    if (routeReady) {
      setTimeout(() => {
        router.replace(targetRoute.current);
      }, 200);
    }
  }, [routeReady]);

  const bg = isDark ? '#1A1A1A' : '#FFFFFF';
  const textColor = isDark ? '#FFF' : '#1A1A1A';
  const accentColor = '#7C3AED';

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      <View style={[styles.container, { backgroundColor: bg }]}>
        {/* خلفية دائرية متوهجة خلف الشعار */}
        <Animated.View
          style={[
            styles.glowCircle,
            {
              backgroundColor: accentColor + '10',
              opacity: gradientOpacity,
            },
          ]}
        />

        {/* مجموعة المحتوى الرئيسية */}
        <View style={styles.contentGroup}>
          {/* شعار التطبيق */}
          <Animated.Image
            source={require('../assets/icon.png')}
            style={[
              styles.logo,
              {
                transform: [{ scale: logoScale }],
                opacity: logoOpacity,
              },
            ]}
            resizeMode="contain"
          />

          {/* اسم التطبيق */}
          <Animated.Text
            style={[
              styles.title,
              { color: textColor, opacity: titleOpacity },
            ]}
          >
            MyTwin
          </Animated.Text>

          {/* الشعار الثانوي */}
          <Animated.Text
            style={[
              styles.subtitle,
              { color: accentColor, opacity: subtitleOpacity },
            ]}
          >
            رفيقك الذكي
          </Animated.Text>

          {/* سطر وصفي */}
          <Animated.Text
            style={[
              styles.tagline,
              { color: isDark ? '#CCC' : '#666', opacity: taglineOpacity },
            ]}
          >
            ذكاء اصطناعي يفهمك ويتطور معك
          </Animated.Text>
        </View>

        {/* حقوق النشر في الأسفل */}
        <Animated.View
          style={[
            styles.footer,
            { opacity: copyrightOpacity },
          ]}
        >
          <Text style={[styles.brandText, { color: accentColor }]}>
            By SOULSYNC
          </Text>
          <Text style={[styles.copyrightText, { color: isDark ? '#888' : '#A78BFA' }]}>
            © 2026
          </Text>
        </Animated.View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  glowCircle: {
    position: 'absolute',
    width: SCREEN_WIDTH * 1.2,
    height: SCREEN_WIDTH * 1.2,
    borderRadius: SCREEN_WIDTH * 0.6,
    top: SCREEN_HEIGHT * 0.15,
  },
  contentGroup: {
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  logo: {
    width: Math.min(SCREEN_WIDTH * 0.5, 240),
    height: Math.min(SCREEN_WIDTH * 0.5, 240),
    marginBottom: 20,
    borderRadius: 40,
  },
  title: {
    fontSize: 40,
    fontWeight: '800',
    letterSpacing: 2,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    fontWeight: '600',
    letterSpacing: 1,
    marginBottom: 12,
  },
  tagline: {
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 22,
  },
  footer: {
    position: 'absolute',
    bottom: 50,
    alignItems: 'center',
  },
  brandText: {
    fontSize: 18,
    fontWeight: '800',
    letterSpacing: 4,
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  copyrightText: {
    fontSize: 12,
    letterSpacing: 2,
  },
});
