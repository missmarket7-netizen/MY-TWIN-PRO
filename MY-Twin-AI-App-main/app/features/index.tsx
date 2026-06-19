import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiGet } from '../../lib/httpClient';
import { useState, useEffect } from 'react';
import {
  ArrowLeft, GraduationCap, Code2, TrendingUp, Heart,
  Image as ImageIcon, Moon, PenLine, Sparkles, Zap, MessageSquare,
} from 'lucide-react-native';

const FEATURES = [
  { id: 'study', icon: GraduationCap, label_ar: 'المذاكرة الذكية', label_en: 'Smart Study', route: '/features/study-mode', color: '#3B82F6', desc_ar: 'شرح، تلخيص، حل مسائل، خطط دراسية', desc_en: 'Explain, summarize, solve, study plans' },
  { id: 'code', icon: Code2, label_ar: 'مختبر البرمجة', label_en: 'Code Lab', route: '/features/code-lab', color: '#10B981', desc_ar: 'كتابة، مراجعة، شرح، تصحيح أكواد', desc_en: 'Write, review, explain, debug code' },
  { id: 'business', icon: TrendingUp, label_ar: 'تحليل الأعمال', label_en: 'Business Analyzer', route: '/features/business-analyzer', color: '#F59E0B', desc_ar: 'تحليل مالي، تسويقي، استراتيجي', desc_en: 'Financial, marketing, strategic analysis' },
  { id: 'coach', icon: Heart, label_ar: 'مدرب الحياة', label_en: 'Life Coach', route: '/features/life-coach', color: '#EC4899', desc_ar: 'دعم نفسي، اجتماعي، عملي، شخصي', desc_en: 'Psychological, social, professional support' },
  { id: 'image', icon: ImageIcon, label_ar: 'إنشاء الصور', label_en: 'Image Creator', route: '/features/image-creator', color: '#8B5CF6', desc_ar: 'توليد صور بالذكاء الاصطناعي', desc_en: 'AI image generation' },
  { id: 'dreams', icon: Moon, label_ar: 'تفسير الأحلام', label_en: 'Dream Journal', route: '/features/dreams', color: '#6366F1', desc_ar: 'تفسير أحلامك برؤى متعددة', desc_en: 'Dream interpretation with multiple insights' },
  { id: 'content', icon: PenLine, label_ar: 'كتابة المحتوى', label_en: 'Content Creator', route: '/features/content-creator', color: '#D946EF', desc_ar: 'محتوى لمنصات التواصل الاجتماعي', desc_en: 'Content for social media platforms' },
];

export default function FeaturesHub() {
  const insets = useSafeAreaInsets();
  const { lang, theme } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const primary = '#6B21A8';

  const [usageStats, setUsageStats] = useState<any>(null);
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    apiGet('/api/stats')
      .then(data => {
        setUsageStats(data);
        setLoadingStats(false);
      })
      .catch(() => setLoadingStats(false));
  }, []);

  return (
    <View style={[st.container, { paddingTop: insets.top }]}>
      <View style={st.header}>
        <TouchableOpacity onPress={() => router.back()} style={st.backBtn}>
          <ArrowLeft size={24} stroke={primary} />
        </TouchableOpacity>
        <Text style={st.headerTitle}>{t('قدرات توأمك', 'Your Twin Powers')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={st.content}>
        <View style={st.heroCard}>
          <Sparkles size={36} stroke={primary} style={{ alignSelf: 'center', marginBottom: 12 }} />
          <Text style={st.heroTitle}>{t('ماذا يستطيع توأمك أن يفعل؟', 'What can your Twin do?')}</Text>
          <Text style={st.heroSub}>{t('اختر أياً من هذه القدرات ودع توأمك يساعدك', 'Choose any of these powers and let your Twin help you')}</Text>
        </View>

        {/* بطاقة إحصائيات الاستخدام */}
        {usageStats && (
          <View style={[st.statsCard, { borderColor: '#EDE9F6' }]}>
            <View style={st.statItem}>
              <MessageSquare size={20} stroke="#7C3AED" />
              <Text style={st.statValue}>{usageStats.daily_requests || 0}</Text>
              <Text style={st.statLabel}>{t('طلبات اليوم', 'Today Requests')}</Text>
            </View>
            <View style={st.statItem}>
              <Zap size={20} stroke="#F59E0B" />
              <Text style={st.statValue}>{usageStats.limits?.messages?.remaining || 0}</Text>
              <Text style={st.statLabel}>{t('متبقية', 'Remaining')}</Text>
            </View>
          </View>
        )}

        <View style={st.grid}>
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <TouchableOpacity
                key={feature.id}
                style={[st.card, { borderColor: feature.color + '30' }]}
                onPress={() => router.push(feature.route as any)}
                activeOpacity={0.85}
              >
                <View style={[st.iconWrap, { backgroundColor: feature.color + '15' }]}>
                  <Icon size={32} stroke={feature.color} />
                </View>
                <Text style={[st.cardTitle, { color: '#1A1226' }]}>{isAr ? feature.label_ar : feature.label_en}</Text>
                <Text style={st.cardDesc}>{isAr ? feature.desc_ar : feature.desc_en}</Text>
                <View style={[st.cardBottom, { backgroundColor: feature.color + '10' }]}>
                  <Text style={[st.cardAction, { color: feature.color }]}>{t('ابدأ الآن', 'Start Now')} →</Text>
                </View>
              </TouchableOpacity>
            );
          })}
        </View>
      </ScrollView>
    </View>
  );
}

const st = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5, borderBottomColor: '#EDE9F6' },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'flex-start' },
  headerTitle: { fontSize: 18, fontWeight: '700', color: '#6B21A8' },
  content: { padding: 20, paddingBottom: 40 },
  heroCard: { backgroundColor: '#FAFAFE', borderRadius: 24, padding: 28, marginBottom: 20, borderWidth: 1, borderColor: '#EDE9F6' },
  heroTitle: { fontSize: 20, fontWeight: '800', color: '#1A1226', textAlign: 'center', marginBottom: 8 },
  heroSub: { fontSize: 14, color: '#7C6B99', textAlign: 'center', lineHeight: 22 },
  statsCard: { flexDirection: 'row', backgroundColor: '#FAFAFE', borderRadius: 20, padding: 20, marginBottom: 20, borderWidth: 1, justifyContent: 'space-around' },
  statItem: { alignItems: 'center', gap: 6 },
  statValue: { fontSize: 22, fontWeight: '800', color: '#1A1226' },
  statLabel: { fontSize: 12, color: '#7C6B99', fontWeight: '600' },
  grid: { gap: 14 },
  card: { backgroundColor: '#FAFAFE', borderRadius: 20, padding: 20, borderWidth: 1, borderColor: '#EDE9F6' },
  iconWrap: { width: 56, height: 56, borderRadius: 18, justifyContent: 'center', alignItems: 'center', marginBottom: 14 },
  cardTitle: { fontSize: 17, fontWeight: '700', marginBottom: 6 },
  cardDesc: { fontSize: 13, color: '#7C6B99', lineHeight: 20, marginBottom: 14 },
  cardBottom: { paddingVertical: 10, paddingHorizontal: 14, borderRadius: 12 },
  cardAction: { fontSize: 13, fontWeight: '600' },
});
