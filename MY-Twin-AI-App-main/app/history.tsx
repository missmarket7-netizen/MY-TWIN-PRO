import {
  SafeAreaView, View, Text, StyleSheet, FlatList, TouchableOpacity,
  ActivityIndicator, Alert, RefreshControl, TextInput
} from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { supabase } from '../lib/supabase';
import { router } from 'expo-router';
import { useState, useEffect, useCallback, useRef } from 'react';
import {
  MessageCircle, Clock, Trash2, Search, X,
  ChevronRight, ChevronLeft, ArrowLeft
} from 'lucide-react-native';

interface Conversation {
  id: number;
  user_id: string;
  title: string;
  summary: string | null;
  dominant_emotion: string;
  memory_count: number;
  message_count: number;
  created_at: string;
  updated_at: string;
}

const EMOTION_ICONS: Record<string, string> = {
  joy: '😊', sadness: '😔', anger: '😤', fear: '😨',
  love: '💕', surprise: '😮', neutral: '😐'
};

export default function History() {
  const { lang, theme, userId } = useTwinStore();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';
  const t = (ar: string, en: string) => isAr ? ar : en;

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const cancelledRef = useRef(false);

  const fetchConversations = useCallback(async (showRefresh = false) => {
    if (!userId) { setLoading(false); return; }
    if (showRefresh) setRefreshing(true); else setLoading(true);
    try {
      const { data } = await supabase
        .from('conversations')
        .select('*')
        .eq('user_id', userId)
        .order('updated_at', { ascending: false });
      if (!cancelledRef.current) setConversations(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      if (!cancelledRef.current) { setLoading(false); setRefreshing(false); }
    }
  }, [userId]);

  useEffect(() => {
    cancelledRef.current = false;
    fetchConversations();
    return () => { cancelledRef.current = true; };
  }, [fetchConversations]);

  const handleDelete = (convId: number) => {
    Alert.alert(
      t('حذف', 'Delete'),
      t('هل أنت متأكد؟', 'Are you sure?'),
      [
        { text: t('إلغاء', 'Cancel'), style: 'cancel' },
        {
          text: t('حذف', 'Delete'),
          style: 'destructive',
          onPress: async () => {
            await supabase.from('conversations').delete().eq('id', convId);
            setConversations(prev => prev.filter(c => c.id !== convId));
          }
        }
      ]
    );
  };

  const relativeTime = (iso: string) => {
    const now = new Date();
    const date = new Date(iso);
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    if (diffMins < 1) return t('الآن', 'Just now');
    if (diffMins < 60) return t(`قبل ${diffMins} د`, `${diffMins}m ago`);
    if (diffHours < 24) return t(`قبل ${diffHours} س`, `${diffHours}h ago`);
    if (diffDays === 1) return t('أمس', 'Yesterday');
    if (diffDays < 7) return t(`قبل ${diffDays} أيام`, `${diffDays}d ago`);
    return date.toLocaleDateString(isAr ? 'ar-EG' : 'en-US', { month: 'short', day: 'numeric' });
  };

  const filtered = searchQuery.trim()
    ? conversations.filter(c => c.title.toLowerCase().includes(searchQuery.toLowerCase()))
    : conversations;

  const openConversation = async (conv: Conversation) => {
    try {
      const { data: messages } = await supabase
        .from('conversation_messages')
        .select('*')
        .eq('conversation_id', conv.id)
        .order('created_at', { ascending: true });
      if (messages) {
        useTwinStore.getState().clearHistory();
        messages.forEach((msg: any) => {
          useTwinStore.getState().addMessage({
            role: msg.role,
            content: msg.content,
            id: msg.id?.toString() || Math.random().toString(36).substr(2, 9),
            timestamp: new Date(msg.created_at).getTime(),
          });
        });
      }
      router.push('/chat');
    } catch (e) {
      router.push('/chat');
    }
  };

  // ألوان المظهر
  const bg = isDark ? '#1A1A1A' : '#F8F6F2';
  const card = isDark ? '#2A2A2A' : '#FFF';
  const border = isDark ? '#444' : '#F0F0F0';
  const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#888' : '#666';

  if (loading) {
    return (
      <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
        <ActivityIndicator size="large" color="#6B21A8" style={{ marginTop: 80 }} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      {/* Header احترافي */}
      <View style={[styles.header, { borderBottomColor: border }]}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <ArrowLeft size={24} stroke={txt} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: txt }]}>
          {t('المحادثات 💬', 'Conversations 💬')}
        </Text>
        <View style={styles.backBtn} />
      </View>

      <View style={styles.container}>
        <View style={[styles.searchRow, { backgroundColor: card, borderColor: border }]}>
          <Search size={18} stroke={sub} />
          <TextInput
            style={[styles.searchInput, { color: txt }]}
            placeholder={t('بحث...', 'Search...')}
            placeholderTextColor={sub}
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <X size={18} stroke={sub} />
            </TouchableOpacity>
          )}
        </View>

        <FlatList
          data={filtered}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={{ paddingBottom: 40 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => fetchConversations(true)}
              colors={['#6B21A8']}
            />
          }
          ListEmptyComponent={
            <View style={{ alignItems: 'center', marginTop: 60 }}>
              <MessageCircle size={48} stroke={sub} />
              <Text style={{ color: sub, fontSize: 17, fontWeight: '600', marginTop: 16 }}>
                {t('لا توجد محادثات', 'No conversations')}
              </Text>
            </View>
          }
          renderItem={({ item }) => {
            const emotionIcon = EMOTION_ICONS[item.dominant_emotion] || '😐';
            return (
              <TouchableOpacity
                style={[styles.card, { backgroundColor: card, borderColor: border }]}
                onPress={() => openConversation(item)}
                onLongPress={() => handleDelete(item.id)}
              >
                <View style={[styles.cardRow, isAr && { flexDirection: 'row-reverse' }]}>
                  <View style={styles.emotionBadge}>
                    <Text style={{ fontSize: 20 }}>{emotionIcon}</Text>
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={[styles.cardTitle, { color: txt }]} numberOfLines={1}>
                      {item.title}
                    </Text>
                    <View style={styles.metaRow}>
                      <Text style={[styles.metaText, { color: sub }]}>
                        {relativeTime(item.updated_at)}
                      </Text>
                      <Text style={[styles.metaText, { color: sub }]}>
                        {item.message_count} {t('رسالة', 'msgs')}
                      </Text>
                    </View>
                  </View>
                  {isAr ? (
                    <ChevronLeft size={20} stroke={sub} />
                  ) : (
                    <ChevronRight size={20} stroke={sub} />
                  )}
                </View>
              </TouchableOpacity>
            );
          }}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
  backBtn: { width: 36, height: 36, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { fontSize: 20, fontWeight: '700', textAlign: 'center', flex: 1 },
  container: { flex: 1, padding: 20 },
  searchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 16,
    gap: 8,
  },
  searchInput: { flex: 1, fontSize: 15 },
  card: { padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 10 },
  cardRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  emotionBadge: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#F3F0FF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardTitle: { fontSize: 16, fontWeight: '600', marginBottom: 4 },
  metaRow: { flexDirection: 'row', gap: 8 },
  metaText: { fontSize: 12 },
});
