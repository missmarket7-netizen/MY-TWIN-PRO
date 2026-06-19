import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView, ScrollView, ActivityIndicator } from 'react-native';
import { useState } from 'react';
import { router } from 'expo-router';
import { useTwinStore } from '../store/useTwinStore';
import { streamChat } from '../lib/httpClient';
import {
  MessageSquare, Target, Heart, Music, Cloud, Newspaper,
  Sparkles, Zap
} from 'lucide-react-native';

const QUICK_STARTERS = [
  {
    id: 'chat',
    icon: MessageSquare,
    color: '#7C3AED',
    bgColor: '#7C3AED15',
    label_ar: 'دردشة حرة',
    label_en: 'Free Chat',
    message_ar: 'مرحباً! أنا مستعد للدردشة معك 💜',
    message_en: 'Hello! Ready to chat with you 💜',
  },
  {
    id: 'goals',
    icon: Target,
    color: '#F59E0B',
    bgColor: '#F59E0B15',
    label_ar: 'تحديد هدف',
    label_en: 'Set a Goal',
    message_ar: 'دعنا نخطط لأهدافك! ما الذي تريد تحقيقه؟ 🎯',
    message_en: "Let's plan your goals! What do you want to achieve? 🎯",
  },
  {
    id: 'support',
    icon: Heart,
    color: '#EC4899',
    bgColor: '#EC489915',
    label_ar: 'دعم نفسي',
    label_en: 'Emotional Support',
    message_ar: 'أنا هنا لدعمك والاستماع لك 🫶',
    message_en: "I'm here to support and listen to you 🫶",
  },
  {
    id: 'music',
    icon: Music,
    color: '#10B981',
    bgColor: '#10B98115',
    label_ar: 'موسيقى',
    label_en: 'Music',
    message_ar: 'ما نوع الموسيقى الذي يعجبك اليوم؟ 🎵',
    message_en: 'What kind of music do you like today? 🎵',
  },
  {
    id: 'weather',
    icon: Cloud,
    color: '#3B82F6',
    bgColor: '#3B82F615',
    label_ar: 'الطقس',
    label_en: 'Weather',
    message_ar: 'دعني أتحقق من الطقس لك ☀️',
    message_en: 'Let me check the weather for you ☀️',
  },
  {
    id: 'news',
    icon: Newspaper,
    color: '#6366F1',
    bgColor: '#6366F115',
    label_ar: 'أخبار',
    label_en: 'News',
    message_ar: 'هل تريد معرفة آخر الأخبار؟ 📰',
    message_en: 'Do you want to know the latest news? 📰',
  },
];

export default function HomeScreen() {
  const { theme, lang, twinName, addMessage } = useTwinStore();
  const isDark = theme === 'dark';
  const isAr = lang === 'ar';
  const [loading, setLoading] = useState<string | null>(null);

  const bg = isDark ? '#1A1A1A' : '#F8F6F2';
  const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#CCC' : '#666';
  const card = isDark ? '#2A2A2A' : '#FFF';
  const border = isDark ? '#444' : '#E5E5E5';

  const handleQuickStart = async (starter: typeof QUICK_STARTERS[0]) => {
    if (loading) return;
    setLoading(starter.id);
    try {
      const userMessage = isAr ? starter.message_ar : starter.message_en;
      
      addMessage({
        id: `user-${Date.now()}`,
        role: 'user',
        content: userMessage,
        timestamp: Date.now(),
      });

      const twinMsgId = `twin-${Date.now()}`;
      addMessage({
        id: twinMsgId,
        role: 'twin',
        content: '',
        timestamp: Date.now(),
      });

      router.push('/chat');
    } catch (error) {
      addMessage({
        id: `twin-${Date.now()}`,
        role: 'twin',
        content: isAr 
          ? 'أنا متحمس للبدء! 💜 ما الذي تريد التحدث عنه؟'
          : "I'm excited to start! 💜 What do you want to talk about?",
        timestamp: Date.now(),
        provider: 'local',
      });
      router.push('/chat');
    } finally {
      setLoading(null);
    }
  };

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Sparkles size={28} stroke="#7C3AED" />
          <Text style={[styles.title, { color: txt }]}>
            {isAr ? 'مرحباً بك في' : 'Welcome to'}
          </Text>
          <Text style={[styles.appName, { color: '#7C3AED' }]}>
            MyTwin
          </Text>
          <Text style={[styles.subtitle, { color: sub }]}>
            {isAr ? 'رفيقك الذكي - اختر كيف تريد أن تبدأ' : 'Your AI companion - choose how to start'}
          </Text>
        </View>

        {twinName && twinName !== 'توأمك' ? (
          <Text style={[styles.twinName, { color: sub }]}>
            {twinName} {isAr ? 'في انتظارك' : 'is waiting for you'} 💜
          </Text>
        ) : null}

        <View style={styles.grid}>
          {QUICK_STARTERS.map((starter) => {
            const Icon = starter.icon;
            const isLoading = loading === starter.id;
            return (
              <TouchableOpacity
                key={starter.id}
                style={[styles.card, { backgroundColor: card, borderColor: border }]}
                onPress={() => handleQuickStart(starter)}
                disabled={!!loading}
                activeOpacity={0.7}
              >
                <View style={[styles.iconWrap, { backgroundColor: starter.bgColor }]}>
                  {isLoading ? (
                    <ActivityIndicator size="small" color={starter.color} />
                  ) : (
                    <Icon size={32} stroke={starter.color} />
                  )}
                </View>
                <Text style={[styles.cardTitle, { color: txt }]}>
                  {isAr ? starter.label_ar : starter.label_en}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <TouchableOpacity
          style={[styles.directChat, { backgroundColor: '#7C3AED' }]}
          onPress={() => router.push('/chat')}
        >
          <Zap size={20} stroke="#FFF" />
          <Text style={styles.directChatText}>
            {isAr ? 'انتقل مباشرة للمحادثة' : 'Go directly to chat'}
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  content: { padding: 20, paddingTop: 60, paddingBottom: 40 },
  header: { alignItems: 'center', marginBottom: 8 },
  title: { fontSize: 22, fontWeight: '600', marginTop: 12 },
  appName: { fontSize: 36, fontWeight: '800', marginTop: 4 },
  subtitle: { fontSize: 15, marginTop: 8, textAlign: 'center' },
  twinName: { fontSize: 15, textAlign: 'center', marginTop: 12, marginBottom: 20 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', marginTop: 24 },
  card: {
    width: '48%',
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 14,
    alignItems: 'center',
  },
  iconWrap: {
    width: 60,
    height: 60,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardTitle: { fontSize: 16, fontWeight: '700', marginBottom: 6, textAlign: 'center' },
  directChat: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginTop: 10,
    padding: 16,
    borderRadius: 14,
  },
  directChatText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
});
