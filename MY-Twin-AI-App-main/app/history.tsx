import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, SafeAreaView,
  FlatList, Alert, ActivityIndicator,
} from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { Stack, router } from 'expo-router';
import Header from '../components/Header';
import { supabase } from '../lib/supabase';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Pin, Trash2, MessageSquare } from 'lucide-react-native';

interface Session {
  id: string;
  created_at: string;
  messages: any[];
}

export default function History() {
  const { theme, lang, userId } = useTwinStore();
  const isDark = theme === 'dark';
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;

  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [pinnedIds, setPinnedIds] = useState<string[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const colors = {
    bg: isDark ? '#1A1A1A' : '#F8F6F2',
    card: isDark ? '#2A2A2A' : '#FFFFFF',
    text: isDark ? '#FFF' : '#1A1A1A',
    subtext: isDark ? '#CCC' : '#666',
    primary: '#7C3AED',
    border: isDark ? '#333' : '#E5E5E5',
    pinColor: '#F59E0B',
  };

  // تحميل الجلسات
  const fetchSessions = useCallback(async () => {
    if (!userId) return;
    try {
      const { data, error } = await supabase
        .from('chat_sessions')
        .select('id, created_at, messages')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) {
        console.warn('Error fetching sessions:', error.message);
        setSessions([]);
      } else {
        setSessions(data || []);
      }
    } catch (e) {
      console.warn(e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [userId]);

  // تحميل المثبتة
  useEffect(() => {
    const loadPinned = async () => {
      try {
        const stored = await AsyncStorage.getItem('pinnedSessions');
        if (stored) setPinnedIds(JSON.parse(stored));
      } catch {}
    };
    loadPinned();
  }, []);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchSessions();
  };

  const togglePin = async (sessionId: string) => {
    let updated: string[];
    if (pinnedIds.includes(sessionId)) {
      updated = pinnedIds.filter(id => id !== sessionId);
    } else {
      updated = [sessionId, ...pinnedIds];
    }
    setPinnedIds(updated);
    await AsyncStorage.setItem('pinnedSessions', JSON.stringify(updated));
  };

  const deleteSession = async (sessionId: string) => {
    Alert.alert(
      t('حذف المحادثة', 'Delete Chat'),
      t('هل أنت متأكد من حذف هذه المحادثة نهائياً؟', 'Are you sure you want to permanently delete this chat?'),
      [
        { text: t('إلغاء', 'Cancel'), style: 'cancel' },
        {
          text: t('حذف', 'Delete'),
          style: 'destructive',
          onPress: async () => {
            try {
              await supabase.from('chat_sessions').delete().eq('id', sessionId);
              setSessions(prev => prev.filter(s => s.id !== sessionId));
              if (pinnedIds.includes(sessionId)) {
                const updated = pinnedIds.filter(id => id !== sessionId);
                setPinnedIds(updated);
                await AsyncStorage.setItem('pinnedSessions', JSON.stringify(updated));
              }
            } catch (e) {
              Alert.alert(t('خطأ', 'Error'), t('فشل حذف المحادثة', 'Failed to delete chat'));
            }
          },
        },
      ]
    );
  };

  const handleLongPress = (session: Session) => {
    const isPinned = pinnedIds.includes(session.id);
    Alert.alert(
      t('خيارات المحادثة', 'Chat Options'),
      '',
      [
        {
          text: isPinned ? t('إلغاء التثبيت', 'Unpin') : t('تثبيت', 'Pin'),
          onPress: () => togglePin(session.id),
        },
        {
          text: t('حذف', 'Delete'),
          style: 'destructive',
          onPress: () => deleteSession(session.id),
        },
        { text: t('إلغاء', 'Cancel'), style: 'cancel' },
      ]
    );
  };

  const getPreview = (messages: any[]) => {
    if (!messages || messages.length === 0) return t('محادثة فارغة', 'Empty chat');
    const firstUserMsg = messages.find((m: any) => m.role === 'user');
    return firstUserMsg ? firstUserMsg.content.substring(0, 80) + (firstUserMsg.content.length > 80 ? '...' : '') : t('محادثة', 'Chat');
  };

  const sortedSessions = [...sessions].sort((a, b) => {
    const aPinned = pinnedIds.includes(a.id) ? 1 : 0;
    const bPinned = pinnedIds.includes(b.id) ? 1 : 0;
    if (aPinned !== bPinned) return bPinned - aPinned; // المثبتة أولاً
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  const renderItem = ({ item }: { item: Session }) => {
    const isPinned = pinnedIds.includes(item.id);
    const date = new Date(item.created_at);
    const dateStr = date.toLocaleDateString(isAr ? 'ar-EG' : 'en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    const timeStr = date.toLocaleTimeString(isAr ? 'ar-EG' : 'en-US', { hour: '2-digit', minute: '2-digit' });

    return (
      <TouchableOpacity
        style={[styles.sessionCard, { backgroundColor: colors.card, borderColor: colors.border }]}
        onPress={() => router.push({ pathname: '/chat', params: { sessionId: item.id } })}
        onLongPress={() => handleLongPress(item)}
        activeOpacity={0.7}
      >
        <View style={styles.sessionLeft}>
          <MessageSquare size={20} stroke={colors.primary} />
          <View style={{ flex: 1, marginLeft: 12 }}>
            <Text style={[styles.sessionDate, { color: colors.text }]} numberOfLines={1}>
              {dateStr} {timeStr}
            </Text>
            <Text style={[styles.sessionPreview, { color: colors.subtext }]} numberOfLines={1}>
              {getPreview(item.messages)}
            </Text>
          </View>
        </View>
        {isPinned && <Pin size={16} stroke={colors.pinColor} fill={colors.pinColor} />}
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header title={t('سجل المحادثات', 'Chat History')} />
      
      {loading ? (
        <View style={styles.centered}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : sortedSessions.length === 0 ? (
        <View style={styles.centered}>
          <MessageSquare size={48} stroke={colors.subtext} />
          <Text style={[styles.emptyText, { color: colors.subtext }]}>
            {t('لا توجد محادثات سابقة', 'No previous chats')}
          </Text>
          <TouchableOpacity style={[styles.newChatBtn, { backgroundColor: colors.primary }]} onPress={() => router.push('/chat')}>
            <Text style={styles.newChatBtnText}>{t('ابدأ محادثة جديدة', 'Start New Chat')}</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={sortedSessions}
          keyExtractor={item => item.id}
          renderItem={renderItem}
          contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
          refreshing={refreshing}
          onRefresh={handleRefresh}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  emptyText: { fontSize: 16, marginTop: 16, textAlign: 'center' },
  newChatBtn: { marginTop: 20, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 12 },
  newChatBtnText: { color: '#FFF', fontWeight: '600', fontSize: 16 },
  sessionCard: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    padding: 16, borderRadius: 12, borderWidth: 1, marginBottom: 10,
  },
  sessionLeft: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  sessionDate: { fontSize: 15, fontWeight: '600', marginBottom: 4 },
  sessionPreview: { fontSize: 13 },
});
