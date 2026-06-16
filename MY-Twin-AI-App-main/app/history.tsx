import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, FlatList, ActivityIndicator } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { Stack, router } from 'expo-router';
import Header from '../components/Header';
import { MessageSquare } from 'lucide-react-native';

export default function History() {
  const { theme, lang, userId, chatHistory } = useTwinStore();
  const isDark = theme === 'dark'; const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const [loading, setLoading] = useState(true);

  const colors = { bg: isDark ? '#1A1A1A' : '#F8F6F2', card: isDark ? '#2A2A2A' : '#FFFFFF', text: isDark ? '#FFF' : '#1A1A1A', subtext: isDark ? '#CCC' : '#666', primary: '#7C3AED', border: isDark ? '#333' : '#E5E5E5' };

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  const localSessions = chatHistory && chatHistory.length > 0
    ? [{ id: 'current', created_at: new Date().toISOString(), messages: chatHistory }]
    : [];

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header title={t('سجل المحادثات', 'Chat History')} />
      
      {loading ? (
        <View style={styles.centered}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : localSessions.length === 0 ? (
        <View style={styles.centered}>
          <MessageSquare size={48} stroke={colors.subtext} />
          <Text style={[styles.emptyText, { color: colors.subtext }]}>
            {t('لا توجد محادثات سابقة', 'No previous chats')}
          </Text>
          <TouchableOpacity style={[styles.newChatBtn, { backgroundColor: colors.primary }]} onPress={() => router.push('/chat')}>
            <Text style={{ color: '#FFF', fontWeight: '600' }}>{t('ابدأ محادثة جديدة', 'Start New Chat')}</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={localSessions}
          keyExtractor={item => item.id}
          contentContainerStyle={{ padding: 16 }}
          renderItem={({ item }) => {
            // ✅ معاينة ذكية: أول رسالة من المستخدم
            const firstUserMsg = item.messages.find((m: any) => m.role === 'user');
            const preview = firstUserMsg 
              ? firstUserMsg.content.substring(0, 80) + (firstUserMsg.content.length > 80 ? '...' : '')
              : t('محادثة فارغة', 'Empty chat');
            
            return (
              <TouchableOpacity
                style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}
                onPress={() => router.push('/chat')}
              >
                <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
                  <MessageSquare size={20} stroke={colors.primary} />
                  <View style={{ flex: 1, marginLeft: 12 }}>
                    <Text style={[styles.date, { color: colors.text }]}>
                      {t('المحادثة الحالية', 'Current Chat')}
                    </Text>
                    <Text style={[styles.preview, { color: colors.subtext }]} numberOfLines={1}>
                      {preview}
                    </Text>
                  </View>
                </View>
              </TouchableOpacity>
            );
          }}
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
  card: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 16, borderRadius: 12, borderWidth: 1, marginBottom: 10 },
  date: { fontSize: 15, fontWeight: '600', marginBottom: 4 },
  preview: { fontSize: 13 },
});
