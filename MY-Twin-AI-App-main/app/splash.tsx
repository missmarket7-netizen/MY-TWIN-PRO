import { View, Image, Text, StyleSheet } from 'react-native';
import { useEffect } from 'react';
import { router } from 'expo-router';

const LOGO = require('../assets/icon.png'); // استبدلها بشعارك

export default function Splash() {
  useEffect(() => {
    const timer = setTimeout(() => {
      router.replace('/login');
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <View style={styles.container}>
      <Image source={LOGO} style={styles.logo} resizeMode="contain" />
      <Text style={styles.appName}>MyTwin</Text>
      <Text style={styles.by}>By SOULSYNC</Text>
      <Text style={styles.copy}>2026©</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0f0a1a' },
  logo: { width: 150, height: 150, marginBottom: 20 },
  appName: { fontSize: 36, fontWeight: '800', color: '#D8B4FE', marginBottom: 8 },
  by: { fontSize: 16, color: '#A78BFA', marginBottom: 4 },
  copy: { fontSize: 14, color: '#7C3AED' },
});
