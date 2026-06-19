import { SafeAreaView, View, Text, StyleSheet, FlatList, ActivityIndicator, RefreshControl, TouchableOpacity } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { getMemories } from '../lib/httpClient';
import { useState, useEffect, useCallback, useRef } from 'react';
import Header from '../components/Header';
import { Stack } from 'expo-router';
import { BrainCircuit, Clock, Layers, Sparkles, Target, Heart, Star, MessageCircle } from 'lucide-react-native';

const MEMORY_CATEGORIES: Record<string, { icon: any; color: string; label_ar: string; label_en: string }> = {
  core: { icon: Sparkles, color: '#F59E0B', label_ar: 'أساسية', label_en: 'Core' },
  goal: { icon: Target, color: '#10B981', label_ar: 'هدف', label_en: 'Goal' },
  emotional: { icon: Heart, color: '#EC4899', label_ar: 'عاطفية', label_en: 'Emotional' },
  fact: { icon: BrainCircuit, color: '#3B82F6', label_ar: 'معلومة', label_en: 'Fact' },
  preference: { icon: Star, color: '#8B5CF6', label_ar: 'تفضيل', label_en: 'Preference' },
  daily: { icon: MessageCircle, color: '#6366F1', label_ar: 'يومية', label_en: 'Daily' },
};

export default function MemoriesScreen() {
  const { lang, theme } = useTwinStore();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';
  const t = (ar: string, en: string) => isAr ? ar : en;

  const [memories, setMemories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true); else setLoading(true);
    try {
      const data = await getMemories();
      setMemories(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const bg = isDark ? '#1A1A1A' : '#F8F6F2';
  const card = isDark ? '#2A2A2A' : '#FFF';
  const border = isDark ? '#444' : '#F0F0F0';
  const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#888' : '#666';
  const primary = isDark ? '#D8B4FE' : '#6B21A8';

  if (loading) {
    return (
      <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
        <ActivityIndicator size="large" color={primary} style={{ marginTop: 80 }} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header />

      <FlatList
        data={memories}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => fetchData(true)} colors={[primary]} />}
        ListEmptyComponent={<View style={styles.empty}><BrainCircuit size={48} stroke={sub} /><Text style={[styles.emptyText, { color: sub }]}>{t('لا توجد ذكريات', 'No memories yet')}</Text></View>}
        renderItem={({ item }) => {
          const cat = MEMORY_CATEGORIES[item.memory_type] || MEMORY_CATEGORIES.daily;
          const Icon = cat.icon;
          return (
            <View style={[styles.memoryCard, { backgroundColor: card, borderColor: border }]}>
              <View style={[styles.memoryIcon, { backgroundColor: cat.color + '20' }]}><Icon size={16} color={cat.color} /></View>
              <View style={styles.memoryBody}>
                <Text style={[styles.memoryContent, { color: txt }]}>{item.content}</Text>
                <Text style={[styles.memoryDate, { color: sub }]}>{new Date(item.created_at).toLocaleDateString(isAr ? 'ar-EG' : 'en-US', { month: 'short', day: 'numeric' })}</Text>
              </View>
            </View>
          );
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  listContent: { padding: 16, paddingBottom: 40 },
  empty: { alignItems: 'center', marginTop: 60 },
  emptyText: { fontSize: 17, fontWeight: '600', marginTop: 16 },
  memoryCard: { flexDirection: 'row', alignItems: 'flex-start', padding: 14, borderRadius: 14, borderWidth: 1, marginBottom: 10, gap: 12 },
  memoryIcon: { width: 36, height: 36, borderRadius: 10, justifyContent: 'center', alignItems: 'center' },
  memoryBody: { flex: 1 },
  memoryContent: { fontSize: 15, lineHeight: 22, marginBottom: 6 },
  memoryDate: { fontSize: 11 },
});
