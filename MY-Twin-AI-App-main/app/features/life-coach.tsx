import { useState, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert, Animated } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiPost } from '../../lib/httpClient';
import { ArrowLeft, Heart, Brain, Users, Briefcase, Sparkles, Send, Copy, RefreshCw, Calendar } from 'lucide-react-native';
import * as Clipboard from 'expo-clipboard';
import Markdown from 'react-native-markdown-display';

const DOMAINS = [
  { id: 'psychological', label_ar: 'نفسي', label_en: 'Psychological', icon: Brain, desc_ar: 'الصحة النفسية والعاطفية', desc_en: 'Mental & emotional health' },
  { id: 'social', label_ar: 'اجتماعي', label_en: 'Social', icon: Users, desc_ar: 'العلاقات والتواصل', desc_en: 'Relationships & communication' },
  { id: 'professional', label_ar: 'عملي', label_en: 'Professional', icon: Briefcase, desc_ar: 'المهنة والطموح', desc_en: 'Career & ambition' },
  { id: 'personal', label_ar: 'شخصي', label_en: 'Personal', icon: Sparkles, desc_ar: 'النمو والتطوير الذاتي', desc_en: 'Personal growth' },
];

export default function LifeCoach() {
  const insets = useSafeAreaInsets();
  const { lang } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const primary = '#6B21A8';

  const [goal, setGoal] = useState('');
  const [domain, setDomain] = useState('psychological');
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState('');
  const [weeklyPlan, setWeeklyPlan] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const handleCoach = async () => {
    if (!goal.trim()) return;
    setLoading(true);
    setReply('');
    try {
      const data = await apiPost('/api/features/coach', { topic: goal.trim(), domain, lang: isAr ? 'ar' : 'en' });
      setReply(data.reply);
      Animated.timing(fadeAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
    } catch (e: any) { Alert.alert(t('خطأ', 'Error'), e.message); }
    finally { setLoading(false); }
  };

  const handleWeeklyPlan = async () => {
    setLoading(true);
    try {
      const data = await apiPost('/api/features/coach/weekly', { domain, lang: isAr ? 'ar' : 'en' });
      setWeeklyPlan(data.plan);
      Animated.timing(fadeAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
    } catch (e: any) { Alert.alert(t('خطأ', 'Error'), e.message); }
    finally { setLoading(false); }
  };

  const handleCopy = async () => {
    await Clipboard.setStringAsync(reply || weeklyPlan || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <View style={[st.container, { paddingTop: insets.top }]}>
      <View style={st.header}>
        <TouchableOpacity onPress={() => router.back()} style={st.backBtn}><ArrowLeft size={24} stroke={primary} /></TouchableOpacity>
        <Text style={st.headerTitle}>{t('مدرب الحياة', 'Life Coach')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={st.content} keyboardShouldPersistTaps="handled">
        <View style={st.heroCard}>
          <Heart size={48} stroke="#EC4899" fill="#EC489920" style={{ alignSelf: 'center', marginBottom: 16 }} />
          <Text style={st.heroTitle}>{t('أنا هنا لأجلك', "I'm here for you")}</Text>
          <Text style={st.heroSub}>{t('شاركني ما يشغل بالك وسأساعدك', 'Share what is on your mind and I will help')}</Text>
        </View>

        <View style={st.card}>
          <Text style={st.label}>{t('اختر المجال', 'Choose Domain')}</Text>
          <View style={st.domainsGrid}>
            {DOMAINS.map((dm) => {
              const Icon = dm.icon;
              const active = domain === dm.id;
              return (
                <TouchableOpacity key={dm.id} style={[st.domainCard, active && { borderColor: primary, backgroundColor: '#F5F3FF' }]} onPress={() => setDomain(dm.id)}>
                  <Icon size={28} stroke={active ? primary : '#7C6B99'} />
                  <Text style={[st.domainLabel, active && { color: primary, fontWeight: '700' }]}>{isAr ? dm.label_ar : dm.label_en}</Text>
                </TouchableOpacity>
              );
            })}
          </View>

          <Text style={st.label}>{t('ما الذي تريد التحدث عنه؟', 'What do you want to talk about?')}</Text>
          <TextInput style={[st.input, isAr && { textAlign: 'right' }]} placeholder={t('اكتب هنا...', 'Write here...')} placeholderTextColor="#7C6B99" value={goal} onChangeText={setGoal} multiline numberOfLines={4} />

          <TouchableOpacity style={[st.btn, { opacity: goal.trim() ? 1 : 0.6 }]} onPress={handleCoach} disabled={loading || !goal.trim()}>
            {loading ? <ActivityIndicator color="#FFF" /> : <><Send size={18} stroke="#FFF" /><Text style={st.btnText}>{t('اطلب النصيحة', 'Ask for Advice')}</Text></>}
          </TouchableOpacity>

          <TouchableOpacity style={st.weeklyBtn} onPress={handleWeeklyPlan} disabled={loading}>
            <Calendar size={18} stroke={primary} />
            <Text style={st.weeklyBtnText}>{t('خطة أسبوعية', 'Weekly Plan')}</Text>
          </TouchableOpacity>
        </View>

        {reply ? (
          <Animated.View style={[st.resultCard, { opacity: fadeAnim }]}>
            <View style={st.resultHeader}>
              <Text style={st.resultTitle}>{t('النصيحة', 'Advice')}</Text>
              <View style={{ flexDirection: 'row', gap: 8 }}>
                <TouchableOpacity onPress={handleCopy}><Copy size={18} stroke={copied ? '#10B981' : primary} /></TouchableOpacity>
                <TouchableOpacity onPress={handleCoach}><RefreshCw size={18} stroke={primary} /></TouchableOpacity>
              </View>
            </View>
            <Markdown style={markdownStyles}>{reply}</Markdown>
          </Animated.View>
        ) : null}

        {weeklyPlan && (
          <Animated.View style={[st.resultCard, { opacity: fadeAnim, marginTop: 16 }]}>
            <View style={st.resultHeader}>
              <Text style={st.resultTitle}>{t('الخطة الأسبوعية', 'Weekly Plan')}</Text>
              <TouchableOpacity onPress={handleCopy}><Copy size={18} stroke={copied ? '#10B981' : primary} /></TouchableOpacity>
            </View>
            <Markdown style={markdownStyles}>{weeklyPlan}</Markdown>
          </Animated.View>
        )}
      </ScrollView>
    </View>
  );
}

const markdownStyles = {
  body: { color: '#1A1226', fontSize: 15, lineHeight: 26 },
  heading1: { fontSize: 20, fontWeight: '800', color: '#6B21A8', marginBottom: 10, marginTop: 16 },
  heading2: { fontSize: 17, fontWeight: '700', color: '#6B21A8', marginBottom: 8, marginTop: 14 },
  heading3: { fontSize: 15, fontWeight: '600', color: '#6B21A8', marginBottom: 6, marginTop: 12 },
  bullet_list: { marginBottom: 8 },
  ordered_list: { marginBottom: 8 },
  list_item: { marginBottom: 4 },
  blockquote: { borderLeftWidth: 4, borderLeftColor: '#6B21A8', paddingLeft: 12, marginVertical: 8, backgroundColor: '#FAFAFE', padding: 10, borderRadius: 8 },
};

const st = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5, borderBottomColor: '#EDE9F6' },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'flex-start' },
  headerTitle: { fontSize: 18, fontWeight: '700', color: '#6B21A8' },
  content: { padding: 20, paddingBottom: 40 },
  heroCard: { backgroundColor: '#FFF5F8', borderRadius: 24, padding: 28, marginBottom: 20, borderWidth: 1, borderColor: '#FCE7F3' },
  heroTitle: { fontSize: 22, fontWeight: '800', color: '#1A1226', textAlign: 'center', marginBottom: 8 },
  heroSub: { fontSize: 14, color: '#7C6B99', textAlign: 'center' },
  card: { backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  label: { fontSize: 14, fontWeight: '600', color: '#1A1226', marginBottom: 10, marginTop: 16 },
  domainsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  domainCard: { width: '47%', padding: 16, borderRadius: 16, borderWidth: 1.5, borderColor: '#EDE9F6', alignItems: 'center', gap: 6 },
  domainLabel: { fontSize: 14, fontWeight: '600', color: '#1A1226' },
  input: { backgroundColor: '#FFF', borderRadius: 16, padding: 16, fontSize: 15, color: '#1A1226', borderWidth: 1, borderColor: '#EDE9F6', minHeight: 100, textAlignVertical: 'top', marginTop: 12 },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#6B21A8', padding: 16, borderRadius: 16, marginTop: 20, gap: 8 },
  btnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  weeklyBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 14, borderRadius: 16, borderWidth: 1.5, borderColor: primary, marginTop: 10 },
  weeklyBtnText: { fontSize: 14, fontWeight: '600', color: primary },
  resultCard: { marginTop: 24, backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  resultHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  resultTitle: { fontSize: 16, fontWeight: '700', color: '#6B21A8' },
});
