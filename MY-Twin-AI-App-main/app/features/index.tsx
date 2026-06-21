import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, RefreshControl, Dimensions,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore, useTwinStoreFull } from '../../store/useTwinStore';
import { useTheme } from '../../utils/theme';
import { router } from 'expo-router';
import {
  ArrowLeft, GraduationCap, Code2, TrendingUp, Heart,
  ImageIcon, Moon, PenLine, Sparkles, Zap, MessageSquare,
  Home, CheckSquare, Brain, Lightbulb, BarChart3,
} from 'lucide-react-native';

const { width: SCREEN_W } = Dimensions.get('window');
const CARD_WIDTH = (SCREEN_W - 56) / 2; // عرض البطاقة في شبكة ثنائية

export default function FeaturesHub() {
  const insets = useSafeAreaInsets();
  const theme = useTheme();
  const { lang } = useTwinStore();
  const { getUserStats } = useTwinStoreFull();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';

  const [usageStats, setUsageStats] = useState<any>(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const colors = {
    bg: isDark ? '#0F0A1A' : '#FAFAF8',
    card: isDark ? '#1A1226' : '#FFFFFF',
    text: isDark ? '#FFFFFF' : '#2D2D2D',
    subtext: isDark ? '#8B7BA3' : '#6B6B6B',
    accent: '#7C3AED',
    border: isDark ? '#2D1B4D' : '#E8E8E3',
  };

  const features = [
    { id: 'study', icon: GraduationCap, label_ar: 'المذاكرة الذكية', label_en: 'Smart Study', route: '/features/study-mode', color: '#3B82F6', desc_ar: 'شرح، تلخيص، حل مسائل', desc_en: 'Explain, summarize, solve' },
    { id: 'code', icon: Code2, label_ar: 'مختبر البرمجة', label_en: 'Code Lab', route: '/features/code-lab', color: '#10B981', desc_ar: 'كتابة، مراجعة، تصحيح', desc_en: 'Write, review, debug' },
    { id: 'business', icon: TrendingUp, label_ar: 'تحليل الأعمال', label_en: 'Business Analyzer', route: '/features/business-analyzer', color: '#F59E0B', desc_ar: 'تحليل مالي، تسويقي', desc_en: 'Financial, marketing' },
    { id: 'coach', icon: Heart, label_ar: 'مدرب الحياة', label_en: 'Life Coach', route: '/features/life-coach', color: '#EC4899', desc_ar: 'دعم نفسي، اجتماعي', desc_en: 'Psychological support' },
    { id: 'image', icon: ImageIcon, label_ar: 'إنشاء الصور', label_en: 'Image Creator', route: '/features/image-creator', color: '#8B5CF6', desc_ar: 'توليد صور بالذكاء', desc_en: 'AI image generation' },
    { id: 'dreams', icon: Moon, label_ar: 'تفسير الأحلام', label_en: 'Dream Journal', route: '/features/dreams', color: '#6366F1', desc_ar: 'تفسير برؤى متعددة', desc_en: 'Multi-school interpretation' },
    { id: 'content', icon: PenLine, label_ar: 'كتابة المحتوى', label_en: 'Content Creator', route: '/features/content-creator', color: '#D946EF', desc_ar: 'محتوى للمنصات', desc_en: 'Social media content' },
    { id: 'smart_home', icon: Home, label_ar: 'المنزل الذكي', label_en: 'Smart Home', route: '/features/smart-home', color: '#06B6D4', desc_ar: 'تحكم بالإضاءة', desc_en: 'Light control' },
    { id: 'tasks', icon: CheckSquare, label_ar: 'المساعد الشخصي', label_en: 'P.A.S.S.', route: '/features/task-manager', color: '#F97316', desc_ar: 'مهام، تقويم، طقس', desc_en: 'Tasks, Calendar, Weather' },
    { id: 'ai_trainer', icon: Brain, label_ar: 'تدريب الذكاء', label_en: 'AI Trainer', route: '/features/ai-trainer', color: '#A855F7', desc_ar: 'تدريب نموذجك الخاص', desc_en: 'Train your own model' },
  ];

  const fetchStats = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true); else setLoadingStats(true);
    try {
      await getUserStats();
      const store = useTwinStore.getState();
      setUsageStats(store.userStats || {});
    } catch (e) {
      setUsageStats(null);
    } finally {
      setLoadingStats(false);
      setRefreshing(false);
    }
  }, [getUserStats]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  if (loadingStats) {
    return (
      <View style={[st.root, { paddingTop: insets.top, backgroundColor: colors.bg, justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={colors.accent} />
      </View>
    );
  }

  return (
    <View style={[st.root, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
      {/* الهيدر */}
      <View style={[st.header, { borderBottomColor: colors.border }]}>
        <TouchableOpacity onPress={() => router.back()}>
          <ArrowLeft size={24} stroke={colors.text} />
        </TouchableOpacity>
        <Text style={[st.headerTitle, { color: colors.text }]}>
          {isAr ? 'قدرات توأمك' : 'Twin Powers'}
        </Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView
        contentContainerStyle={st.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => fetchStats(true)} colors={[colors.accent]} />
        }
      >
        {/* بطاقة الترحيب */}
        <View style={[st.heroCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <Sparkles size={36} stroke={colors.accent} style={{ alignSelf: 'center', marginBottom: 12 }} />
          <Text style={[st.heroTitle, { color: colors.text }]}>
            {isAr ? 'ماذا يستطيع توأمك أن يفعل؟' : 'What can your Twin do?'}
          </Text>
          <Text style={[st.heroSub, { color: colors.subtext }]}>
            {isAr ? 'اختر أياً من هذه القدرات ودع توأمك يساعدك' : 'Choose any power and let your Twin help you'}
          </Text>
        </View>

        {/* إحصائيات سريعة */}
        {usageStats && (
          <View style={[st.statsRow, { backgroundColor: colors.card, borderColor: colors.border }]}>
            <View style={st.statItem}>
              <MessageSquare size={20} stroke={colors.accent} />
              <Text style={[st.statValue, { color: colors.text }]}>
                {usageStats?.usage?.messages?.used || 0}
              </Text>
              <Text style={[st.statLabel, { color: colors.subtext }]}>
                {isAr ? 'طلبات اليوم' : 'Today'}
              </Text>
            </View>
            <View style={st.statItem}>
              <Zap size={20} stroke="#F59E0B" />
              <Text style={[st.statValue, { color: colors.text }]}>
                {usageStats?.subscription?.twin_energy || 100}%
              </Text>
              <Text style={[st.statLabel, { color: colors.subtext }]}>
                {isAr ? 'الطاقة' : 'Energy'}
              </Text>
            </View>
            <View style={st.statItem}>
              <Lightbulb size={20} stroke="#10B981" />
              <Text style={[st.statValue, { color: colors.text }]}>
                {usageStats?.tcma?.total_insights || 0}
              </Text>
              <Text style={[st.statLabel, { color: colors.subtext }]}>
                {isAr ? 'استنتاجات' : 'Insights'}
              </Text>
            </View>
          </View>
        )}

        {/* شبكة الميزات */}
        <Text style={[st.sectionTitle, { color: colors.text }]}>
          {isAr ? '🚀 جميع القدرات' : '🚀 All Powers'}
        </Text>
        <View style={st.grid}>
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <TouchableOpacity
                key={feature.id}
                style={[
                  st.card,
                  {
                    backgroundColor: colors.card,
                    borderColor: colors.border,
                    width: CARD_WIDTH,
                  },
                ]}
                onPress={() => router.push(feature.route as any)}
                activeOpacity={0.85}
              >
                <View style={[st.cardIcon, { backgroundColor: feature.color + '15' }]}>
                  <Icon size={28} stroke={feature.color} />
                </View>
                <Text style={[st.cardTitle, { color: colors.text }]} numberOfLines={1}>
                  {isAr ? feature.label_ar : feature.label_en}
                </Text>
                <Text style={[st.cardDesc, { color: colors.subtext }]} numberOfLines={2}>
                  {isAr ? feature.desc_ar : feature.desc_en}
                </Text>
                <View style={[st.cardBottom, { backgroundColor: feature.color + '10' }]}>
                  <Text style={[st.cardAction, { color: feature.color }]}>
                    {isAr ? 'ابدأ' : 'Start'} →
                  </Text>
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
  root: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5 },
  headerTitle: { fontSize: 18, fontWeight: '700' },
  content: { padding: 16, paddingBottom: 40 },
  heroCard: { borderRadius: 24, padding: 28, marginBottom: 20, borderWidth: 1, alignItems: 'center' },
  heroTitle: { fontSize: 20, fontWeight: '800', marginBottom: 8, textAlign: 'center' },
  heroSub: { fontSize: 14, textAlign: 'center', lineHeight: 22 },
  statsRow: { flexDirection: 'row', borderRadius: 20, padding: 18, marginBottom: 20, borderWidth: 1, justifyContent: 'space-around' },
  statItem: { alignItems: 'center', gap: 6 },
  statValue: { fontSize: 20, fontWeight: '800' },
  statLabel: { fontSize: 11, fontWeight: '600' },
  sectionTitle: { fontSize: 18, fontWeight: '700', marginBottom: 16 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, justifyContent: 'space-between' },
  card: { borderRadius: 20, padding: 16, borderWidth: 1, marginBottom: 4 },
  cardIcon: { width: 50, height: 50, borderRadius: 16, justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  cardTitle: { fontSize: 15, fontWeight: '700', marginBottom: 4 },
  cardDesc: { fontSize: 12, lineHeight: 18, marginBottom: 12 },
  cardBottom: { paddingVertical: 8, paddingHorizontal: 12, borderRadius: 10 },
  cardAction: { fontSize: 12, fontWeight: '600' },
});
