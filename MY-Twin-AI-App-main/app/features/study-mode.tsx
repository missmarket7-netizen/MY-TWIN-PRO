import { useState, useRef, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert, Animated } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiPost } from '../../lib/httpClient';
import { ArrowLeft, BookOpen, Send, Clock, Target, Lightbulb, GraduationCap, Copy, RefreshCw } from 'lucide-react-native';
import * as Clipboard from 'expo-clipboard';
import Markdown from 'react-native-markdown-display';

const LEVELS = [
  { id: 'beginner', label_ar: 'مبتدئ', label_en: 'Beginner', icon: '🌱' },
  { id: 'intermediate', label_ar: 'متوسط', label_en: 'Intermediate', icon: '🌿' },
  { id: 'advanced', label_ar: 'متقدم', label_en: 'Advanced', icon: '🌳' },
  { id: 'expert', label_ar: 'خبير', label_en: 'Expert', icon: '🏆' },
];

const TYPES = [
  { id: 'explain', label_ar: 'شرح', label_en: 'Explain', icon: BookOpen, desc_ar: 'شرح مبسط للموضوع', desc_en: 'Simple explanation' },
  { id: 'summarize', label_ar: 'تلخيص', label_en: 'Summarize', icon: Target, desc_ar: 'ملخص مختصر ومفيد', desc_en: 'Concise summary' },
  { id: 'solve', label_ar: 'حل مسألة', label_en: 'Solve', icon: Lightbulb, desc_ar: 'حل خطوة بخطوة', desc_en: 'Step by step solution' },
  { id: 'plan', label_ar: 'خطة دراسية', label_en: 'Study Plan', icon: Clock, desc_ar: 'تنظيم الوقت والمذاكرة', desc_en: 'Time management plan' },
];

const RECENT_TOPICS_KEY = 'study_recent_topics';

export default function StudyMode() {
  const insets = useSafeAreaInsets();
  const { lang, theme } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const primary = '#6B21A8';

  const [topic, setTopic] = useState('');
  const [level, setLevel] = useState('intermediate');
  const [studyType, setStudyType] = useState('explain');
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState('');
  const [recentTopics, setRecentTopics] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setReply('');
    try {
      const data = await apiPost('/api/features/study', { topic: topic.trim(), level, type: studyType, lang: isAr ? 'ar' : 'en' });
      setReply(data.reply);
      Animated.timing(fadeAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
      setRecentTopics(prev => {
        const updated = [topic.trim(), ...prev.filter(x => x !== topic.trim())].slice(0, 5);
        return updated;
      });
    } catch (e: any) {
      Alert.alert(t('خطأ', 'Error'), e.message || t('فشل', 'Failed'));
    } finally { setLoading(false); }
  };

  const handleCopy = async () => {
    await Clipboard.setStringAsync(reply);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <View style={[s.container, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}><ArrowLeft size={24} stroke={primary} /></TouchableOpacity>
        <Text style={s.headerTitle}>{t('المذاكرة الذكية', 'Smart Study')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={s.content} keyboardShouldPersistTaps="handled">
        {/* بطاقة الإدخال */}
        <View style={s.card}>
          <GraduationCap size={40} stroke={primary} style={{ alignSelf: 'center', marginBottom: 16 }} />
          
          <Text style={s.label}>{t('ما الموضوع الذي تريد مذاكرته؟', 'What subject do you want to study?')}</Text>
          <TextInput style={[s.input, isAr && { textAlign: 'right' }]} placeholder={t('اكتب الموضوع هنا...', 'Write the topic here...')} placeholderTextColor="#7C6B99" value={topic} onChangeText={setTopic} />

          <Text style={s.label}>{t('المستوى', 'Level')}</Text>
          <View style={s.optionsRow}>
            {LEVELS.map((lv) => (
              <TouchableOpacity key={lv.id} style={[s.optionBtn, level === lv.id && { borderColor: primary, backgroundColor: '#F5F3FF' }]} onPress={() => setLevel(lv.id)}>
                <Text style={[s.optionText, level === lv.id && { color: primary, fontWeight: '700' }]}>{lv.icon} {isAr ? lv.label_ar : lv.label_en}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={s.label}>{t('نوع المساعدة', 'Type of Help')}</Text>
          <View style={s.typesGrid}>
            {TYPES.map((tp) => {
              const Icon = tp.icon;
              const active = studyType === tp.id;
              return (
                <TouchableOpacity key={tp.id} style={[s.typeCard, active && { borderColor: primary, backgroundColor: '#F5F3FF' }]} onPress={() => setStudyType(tp.id)}>
                  <Icon size={28} stroke={active ? primary : '#7C6B99'} />
                  <Text style={[s.typeLabel, active && { color: primary, fontWeight: '700' }]}>{isAr ? tp.label_ar : tp.label_en}</Text>
                  <Text style={s.typeDesc}>{isAr ? tp.desc_ar : tp.desc_en}</Text>
                </TouchableOpacity>
              );
            })}
          </View>

          <TouchableOpacity style={[s.btn, { opacity: topic.trim() ? 1 : 0.6 }]} onPress={handleGenerate} disabled={loading || !topic.trim()}>
            {loading ? <ActivityIndicator color="#FFF" /> : <><Send size={18} stroke="#FFF" /><Text style={s.btnText}>{t('ابدأ المذاكرة', 'Start Studying')}</Text></>}
          </TouchableOpacity>
        </View>

        {/* النتيجة */}
        {reply ? (
          <Animated.View style={[s.resultCard, { opacity: fadeAnim }]}>
            <View style={s.resultHeader}>
              <Text style={s.resultTitle}>{t('النتيجة', 'Result')}</Text>
              <View style={{ flexDirection: 'row', gap: 8 }}>
                <TouchableOpacity onPress={handleCopy}><Copy size={18} stroke={copied ? '#10B981' : primary} /></TouchableOpacity>
                <TouchableOpacity onPress={handleGenerate}><RefreshCw size={18} stroke={primary} /></TouchableOpacity>
              </View>
            </View>
            <Markdown style={markdownStyles}>{reply}</Markdown>
          </Animated.View>
        ) : null}

        {/* المواضيع السابقة */}
        {recentTopics.length > 0 && !reply && (
          <View style={s.recentCard}>
            <Clock size={18} stroke={primary} />
            <Text style={s.recentTitle}>{t('آخر المواضيع', 'Recent Topics')}</Text>
            {recentTopics.map((tp, i) => (
              <TouchableOpacity key={i} style={s.recentItem} onPress={() => setTopic(tp)}>
                <Text style={s.recentText}>{tp}</Text>
              </TouchableOpacity>
            ))}
          </View>
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
  code_inline: { backgroundColor: '#F5F3FF', color: '#6B21A8', paddingHorizontal: 6, borderRadius: 4 },
  code_block: { backgroundColor: '#1E1E2E', color: '#CDD6F4', padding: 12, borderRadius: 10, marginVertical: 10 },
  fence: { backgroundColor: '#1E1E2E', color: '#CDD6F4', padding: 12, borderRadius: 10, marginVertical: 10 },
  bullet_list: { marginBottom: 8 },
  ordered_list: { marginBottom: 8 },
  list_item: { marginBottom: 4 },
  blockquote: { borderLeftWidth: 4, borderLeftColor: '#6B21A8', paddingLeft: 12, marginVertical: 8, backgroundColor: '#FAFAFE', padding: 10, borderRadius: 8 },
};

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5, borderBottomColor: '#EDE9F6' },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'flex-start' },
  headerTitle: { fontSize: 18, fontWeight: '700', color: '#6B21A8' },
  content: { padding: 20, paddingBottom: 40 },
  card: { backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  label: { fontSize: 14, fontWeight: '600', color: '#1A1226', marginBottom: 10, marginTop: 16 },
  input: { backgroundColor: '#FFF', borderRadius: 16, padding: 16, fontSize: 15, color: '#1A1226', borderWidth: 1, borderColor: '#EDE9F6' },
  optionsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 8 },
  optionBtn: { paddingHorizontal: 16, paddingVertical: 10, borderRadius: 20, borderWidth: 1.5, borderColor: '#EDE9F6' },
  optionText: { fontSize: 13, fontWeight: '500', color: '#7C6B99' },
  typesGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  typeCard: { width: '47%', padding: 16, borderRadius: 16, borderWidth: 1.5, borderColor: '#EDE9F6', alignItems: 'center', gap: 6 },
  typeLabel: { fontSize: 14, fontWeight: '600', color: '#1A1226' },
  typeDesc: { fontSize: 11, color: '#7C6B99', textAlign: 'center' },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#6B21A8', padding: 16, borderRadius: 16, marginTop: 20, gap: 8 },
  btnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  resultCard: { marginTop: 24, backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  resultHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  resultTitle: { fontSize: 16, fontWeight: '700', color: '#6B21A8' },
  recentCard: { marginTop: 24, backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6', gap: 10 },
  recentTitle: { fontSize: 14, fontWeight: '600', color: '#1A1226' },
  recentItem: { padding: 12, borderRadius: 12, backgroundColor: '#FFF' },
  recentText: { fontSize: 14, color: '#6B21A8' },
});
