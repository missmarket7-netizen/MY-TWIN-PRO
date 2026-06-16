import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { ChevronLeft } from 'lucide-react-native';
import { router } from 'expo-router';
import { useTwinStore } from '../store/useTwinStore';

export default function Header({ title }: { title: string }) {
  const theme = useTwinStore(s => s.theme);
  const isDark = theme === 'dark';
  const primary = isDark ? '#D8B4FE' : '#7C3AED';
  const textColor = isDark ? '#FFF' : '#1A1A1A';
  const borderColor = isDark ? '#333' : '#E5E5E5';

  return (
    <View style={[styles.container, { borderBottomColor: borderColor }]}>
      <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
        <ChevronLeft size={24} stroke={primary} />
      </TouchableOpacity>
      <Text style={[styles.title, { color: textColor }]} numberOfLines={1}>{title}</Text>
      <View style={{ width: 40 }} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 0.5,
  },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  title: { flex: 1, textAlign: 'center', fontSize: 18, fontWeight: '700' },
});
