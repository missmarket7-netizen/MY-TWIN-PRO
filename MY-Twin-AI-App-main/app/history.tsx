import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Header from '../components/Header';
import { useTwinStore } from '../store/useTwinStore';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export default function History() {
  const insets = useSafeAreaInsets();
  const theme = useTwinStore(s => s.theme);
  const isDark = theme === 'dark';

  return (
    <View style={[styles.container, { paddingTop: insets.top, backgroundColor: isDark ? '#0f0a1a' : '#fff' }]}>
      <Header title="سجل المحادثات" onMenuPress={() => useTwinStore.getState().openMenu()} />
      <View style={styles.content}>
        <Text style={{ color: isDark ? '#fff' : '#000' }}>سجل المحادثات السابقة يظهر هنا.</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { flex: 1, justifyContent: 'center', alignItems: 'center' },
});
