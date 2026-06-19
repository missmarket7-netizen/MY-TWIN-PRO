import { View, Image, Text, StyleSheet, Animated, Dimensions } from 'react-native';
import { useEffect, useRef } from 'react';
import { router } from 'expo-router';
import { useTwinStore } from '../store/useTwinStore';

const LOGO = require('../assets/icon.png');
const { width, height } = Dimensions.get('window');

export default function Splash() {
  // قيم التحريك
  const logoScale = useRef(new Animated.Value(0.3)).current;
  const logoOpacity = useRef(new Animated.Value(0)).current;
  const titleOpacity = useRef(new Animated.Value(0)).current;
  const titleTranslateY = useRef(new Animated.Value(20)).current;
  const taglineOpacity = useRef(new Animated.Value(0)).current;
  const taglineTranslateY = useRef(new Animated.Value(15)).current;
  const byOpacity = useRef(new Animated.Value(0)).current;
  const copyOpacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // تسلسل ظهور احترافي
    const animationSequence = Animated.sequence([
      // 1. ظهور الأيقونة مع تكبير
      Animated.parallel([
        Animated.spring(logoScale, {
          toValue: 1,
          friction: 6,
          tension: 40,
          useNativeDriver: true,
        }),
        Animated.timing(logoOpacity, {
          toValue: 1,
          duration: 600,
          useNativeDriver: true,
        }),
      ]),
      // 2. ظهور الاسم
      Animated.parallel([
        Animated.timing(titleOpacity, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(titleTranslateY, {
          toValue: 0,
          duration: 500,
          useNativeDriver: true,
        }),
      ]),
      // 3. ظهور الجملة التسويقية
      Animated.parallel([
        Animated.timing(taglineOpacity, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        }),
        Animated.timing(taglineTranslateY, {
          toValue: 0,
          duration: 400,
          useNativeDriver: true,
        }),
      ]),
      // 4. ظهور باقي النصوص
      Animated.timing(byOpacity, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }),
      Animated.timing(copyOpacity, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
    ]);

    animationSequence.start();

    // الانتقال للشاشة التالية
    const timer = setTimeout(() => {
      const hasUser = useTwinStore.getState().userId;
      router.replace(hasUser ? '/welcome' : '/login');
    }, 4500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <View style={styles.container}>
      {/* الأيقونة بتأثير التوهج */}
      <Animated.View
        style={[
          styles.logoContainer,
          {
            transform: [{ scale: logoScale }],
            opacity: logoOpacity,
          },
        ]}
      >
        <View style={styles.glowEffect}>
          <Image source={LOGO} style={styles.logo} resizeMode="contain" />
        </View>
      </Animated.View>

      {/* اسم التطبيق */}
      <Animated.Text
        style={[
          styles.appName,
          {
            opacity: titleOpacity,
            transform: [{ translateY: titleTranslateY }],
          },
        ]}
      >
        My Twin
      </Animated.Text>

      {/* الجملة التسويقية */}
      <Animated.Text
        style={[
          styles.tagline,
          {
            opacity: taglineOpacity,
            transform: [{ translateY: taglineTranslateY }],
          },
        ]}
      >
        Your Twin AI ... Always There
      </Animated.Text>

      {/* الحقوق */}
      <Animated.Text style={[styles.by, { opacity: byOpacity }]}>
        By SOULSYNC
      </Animated.Text>
      <Animated.Text style={[styles.copy, { opacity: copyOpacity }]}>
        © 2026 SOULSYNC
      </Animated.Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  logoContainer: {
    marginBottom: 24,
  },
  glowEffect: {
    width: 140,
    height: 140,
    borderRadius: 70,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    shadowColor: '#7C3AED',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.7,
    shadowRadius: 25,
    elevation: 15,
  },
  logo: {
    width: 120,
    height: 120,
    borderRadius: 30,
  },
  appName: {
    fontSize: 36,
    fontWeight: '800',
    color: '#1A1226',
    letterSpacing: -0.5,
    marginBottom: 8,
  },
  tagline: {
    fontSize: 16,
    color: '#7C3AED',
    fontWeight: '500',
    marginBottom: 24,
    letterSpacing: 0.3,
  },
  by: {
    fontSize: 14,
    color: '#A78BFA',
    fontWeight: '600',
    letterSpacing: 1,
    marginBottom: 4,
  },
  copy: {
    fontSize: 13,
    color: '#C4B5FD',
    fontWeight: '400',
  },
});
