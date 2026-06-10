import { useEffect, useRef, useState } from 'react';
import { View, StyleSheet, Animated, Dimensions, SafeAreaView } from 'react-native';
import { router } from 'expo-router';
import { supabase } from '../lib/supabase';
import { useTwinStore } from '../store/useTwinStore';
import { setToken } from '../lib/api';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

export default function SplashScreen() {
  const { setAuth, theme } = useTwinStore();
  const isDark = theme === 'dark';

  // ✅ النوع الصحيح لـ Ref
  const logoScale = useRef(new Animated.Value(0.3)).current;
  const logoOpacity = useRef(new Animated.Value(0)).current;
  const brandTextOpacity = useRef(new Animated.Value(0)).current;
  const copyrightOpacity = useRef(new Animated.Value(0)).current;
  const animRef = useRef<Animated.CompositeAnimation | null>(null);
  
  const [routeReady, setRouteReady] = useState(false);
  const targetRoute = useRef('/login');

  useEffect(() => {
    animRef.current = Animated.sequence([
      Animated.parallel([
        Animated.spring(logoScale, { toValue: 1, tension: 8, friction: 3, useNativeDriver: true }),
        Animated.timing(logoOpacity, { toValue: 1, duration: 800, useNativeDriver: true }),
      ]),
      Animated.timing(brandTextOpacity, { toValue: 1, duration: 600, useNativeDriver: true }),
      Animated.timing(copyrightOpacity, { toValue: 1, duration: 400, useNativeDriver: true }),
    ]);
    // ✅ Optional Chaining
    animRef.current?.start();

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

    const minTime = new Promise(resolve => setTimeout(resolve, 3500));
    Promise.all([bootPromise, minTime]).then(() => {
      if (!routeReady) setRouteReady(true);
    });

    return () => {
      // ✅ Optional Chaining
      animRef.current?.stop();
    };
  }, []);

  useEffect(() => {
    if (routeReady) router.replace(targetRoute.current);
  }, [routeReady]);

  return (
    <SafeAreaView style={[styles.safe, isDark && { backgroundColor: '#1A1A1A' }]}>
      <View style={[styles.container, isDark && { backgroundColor: '#1A1A1A' }]}>
        <View style={styles.contentGroup}>
          <Animated.Image
            source={require('../assets/logo.png')}
            style={[styles.logo, { transform: [{ scale: logoScale }], opacity: logoOpacity }]}
            resizeMode="contain"
          />
          <Animated.Text style={[styles.brandText, { opacity: brandTextOpacity }]}>
            By SOULSYNC
          </Animated.Text>
          <Animated.Text style={[styles.copyrightText, { opacity: copyrightOpacity }]}>
            ©2026
          </Animated.Text>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  container: { flex: 1, backgroundColor: '#FFFFFF', alignItems: 'center', justifyContent: 'center' },
  contentGroup: { alignItems: 'center' },
  logo: { width: Math.min(SCREEN_WIDTH * 0.55, 280), height: Math.min(SCREEN_WIDTH * 0.55, 280), marginBottom: 24 },
  brandText: { fontSize: 22, fontWeight: '800', color: '#7C3AED', letterSpacing: 4, textTransform: 'uppercase', marginBottom: 8 },
  copyrightText: { fontSize: 14, color: '#A78BFA', letterSpacing: 2 },
});
