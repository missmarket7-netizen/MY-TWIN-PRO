import { View, Image, Text, StyleSheet, Animated } from 'react-native';
import { useEffect, useRef } from 'react';
import { router } from 'expo-router';

const LOGO = require('../assets/icon.png');

export default function Splash() {
  const logoOpacity = useRef(new Animated.Value(0)).current;
  const logoScale = useRef(new Animated.Value(0.5)).current;
  const appNameOpacity = useRef(new Animated.Value(0)).current;
  const appNameTranslateY = useRef(new Animated.Value(20)).current;
  const byOpacity = useRef(new Animated.Value(0)).current;
  const byTranslateY = useRef(new Animated.Value(15)).current;
  const copyOpacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const animationSequence = Animated.sequence([
      Animated.parallel([
        Animated.timing(logoOpacity, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.spring(logoScale, {
          toValue: 1,
          friction: 8,
          tension: 40,
          useNativeDriver: true,
        }),
      ]),
      Animated.parallel([
        Animated.timing(appNameOpacity, {
          toValue: 1,
          duration: 600,
          useNativeDriver: true,
        }),
        Animated.timing(appNameTranslateY, {
          toValue: 0,
          duration: 600,
          useNativeDriver: true,
        }),
      ]),
      Animated.parallel([
        Animated.timing(byOpacity, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(byTranslateY, {
          toValue: 0,
          duration: 500,
          useNativeDriver: true,
        }),
      ]),
      Animated.timing(copyOpacity, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }),
    ]);

    animationSequence.start();

    const timer = setTimeout(() => {
      Animated.timing(logoOpacity, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }).start(() => {
        router.replace('/login');
      });
    }, 4500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <View style={styles.container}>
      <Animated.Image 
        source={LOGO} 
        style={[
          styles.logo, 
          { 
            opacity: logoOpacity,
            transform: [{ scale: logoScale }]
          }
        ]} 
        resizeMode="contain" 
      />
      <Animated.Text style={[
        styles.appName,
        {
          opacity: appNameOpacity,
          transform: [{ translateY: appNameTranslateY }]
        }
      ]}>
        MyTwin
      </Animated.Text>
      <Animated.Text style={[
        styles.by,
        {
          opacity: byOpacity,
          transform: [{ translateY: byTranslateY }]
        }
      ]}>
        By SOULSYNC
      </Animated.Text>
      <Animated.Text style={[
        styles.copy,
        { opacity: copyOpacity }
      ]}>
        2026©
      </Animated.Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    justifyContent: 'center', 
    alignItems: 'center', 
    backgroundColor: '#0f0a1a' 
  },
  logo: { 
    width: 150, 
    height: 150, 
    marginBottom: 20 
  },
  appName: { 
    fontSize: 36, 
    fontWeight: '800', 
    color: '#D8B4FE', 
    marginBottom: 8 
  },
  by: { 
    fontSize: 16, 
    color: '#A78BFA', 
    marginBottom: 4 
  },
  copy: { 
    fontSize: 14, 
    color: '#7C3AED' 
  },
});
