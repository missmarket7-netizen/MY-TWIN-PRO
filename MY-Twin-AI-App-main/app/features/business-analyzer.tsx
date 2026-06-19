import { useState, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert, Animated } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiPost } from '../../lib/httpClient';
import { ArrowLeft, TrendingUp, Send, Copy, RefreshCw, BarChart3, DollarSign, Target, PieChart } from 'lucide-react-native';
import * as Clipboard from 'expo-clipboard';
import Markdown from 'react-native-markdown-display';

const ANALYSIS_TYPES = [
  { id: 'general', label_ar: 'تحليل عام', label_en: 'General', icon: BarChart3, desc_ar: 'رؤى شاملة', desc_en: 'Comprehensive insights' },
  { id: 'financial', label_ar: 'تحليل مالي', label_en: 'Financial', icon: DollarSign, desc_ar: 'أرقام وإحصائيات', desc_en: 'Numbers & stats' },
  { id: 'marketing', label_ar: 'تسويق', label_en: 'Marketing', icon: Target, desc_ar: 'استراتيجيات التسويق', desc_en: 'Marketing strategies' },
  { id: 'strategy', label_ar: 'استراتيجي', label_en: 'Strategy', icon: PieChart, desc_ar: 'خطط وتوصيات', desc_en: 'Plans & recommendations' },
];

export default function BusinessAnalyzer() {
  const insets = useSafeAreaInsets();
  const { lang } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const primary = '#6B21A8';

  const [text, setText] = useState('');
  const [analysisType, setAnalysisType] = useState('general');
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState('');
  const [copied, setCopied] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setReply('');
    try {
      const data = await apiPost('/api/features/business', { text: text.trim(), analysis_type: analysisType, lang: isAr ? 'ar' : 'en' });
      setReply(data.reply);
      Animated.timing(fadeAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
    } catch (e: any) {
      Alert.alert(t('خطأ', 'Error'), e.message);
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
        <Text style={s.headerTitle}>{t('تحليل الأعمال', 'Business Analyzer')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={s.content} keyboardShouldPersistTaps="handled">
        <View style={s.card}>
          <TrendingUp size={40} stroke={primary} style={{ alignSelf: 'center', marginBottom: 16 }} />
          
          <Text style={s.label}>{t('نوع التحليل', 'Analysis Type')}</Text>
          <View style={s.typesGrid}>
            {ANALYSIS_TYPES.map((at) => {
              const Icon = at.icon;
              const active = analysisType === at.id;
              return (
                <TouchableOpacity key={at.id} style={[s.typeCard, active && { borderColor: primary, backgroundColor: '#F5F3FF' }]} onPress={() => setAnalysisType(at.id)}>
                  <Icon size={28} stroke={active ? primary : '#7C6B99'} />
                  <Text style={[s.typeLabel, active && { color: primary, fontWeight: '700' }]}>{isAr ? at.label_ar : at.label_en}</Text>
                  <Text style={s.typeDesc}>{isAr ? at.desc_ar : at.desc_en}</Text>
                </TouchableOpacity>
              );
            })}
          </View>

          <Text style={s.label}>{t('النص للتحليل', 'Text to Analyze')}</Text>
          <TextInput style={[s.input, isAr && { textAlign: 'right' }]} placeholder={t('الصق النص هنا...', 'Paste text here...')} placeholderTextColor="#7C6B99" value={text} onChangeText={setText} multiline numberOfLines={5} />

          <TouchableOpacity style={[s.btn, { opacity: text.trim() ? 1 : 0.6 }]} onPress={handleAnalyze} disabled={loading || !text.trim()}>
            {loading ? <ActivityIndicator color="#FFF" /> : <><Send size={18} stroke="#FFF" /><Text style={s.btnText}>{t('حلل', 'Analyze')}</Text></>}
          </TouchableOpacity>
        </View>

        {reply ? (
          <Animated.View style={[s.resultCard, { opacity: fadeAnim }]}>
            <View style={s.resultHeader}>
              <Text style={s.resultTitle}>{t('نتيجة التحليل', 'Analysis Result')}</Text>
              <View style={{ flexDirection: 'row', gap: 8 }}>
                <TouchableOpacity onPress={handleCopy}><Copy size={18} stroke={copied ? '#10B981' : primary} /></TouchableOpacity>
                <TouchableOpacity onPress={handleAnalyze}><RefreshCw size={18} stroke={primary} /></TouchableOpacity>
              </View>
            </View>
            <Markdown style={markdownStyles}>{reply}</Markdown>
          </Animated.View>
        ) : null}
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

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5, borderBottomColor: '#EDE9F6' },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'flex-start' },
  headerTitle: { fontSize: 18, fontWeight: '700', color: '#6B21A8' },
  content: { padding: 20, paddingBottom: 40 },
  card: { backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  label: { fontSize: 14, fontWeight: '600', color: '#1A1226', marginBottom: 10, marginTop: 16 },
  typesGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  typeCard: { width: '47%', padding: 16, borderRadius: 16, borderWidth: 1.5, borderColor: '#EDE9F6', alignItems: 'center', gap: 6 },
  typeLabel: { fontSize: 14, fontWeight: '600', color: '#1A1226' },
  typeDesc: { fontSize: 11, color: '#7C6B99', textAlign: 'center' },
  input: { backgroundColor: '#FFF', borderRadius: 16, padding: 16, fontSize: 15, color: '#1A1226', borderWidth: 1, borderColor: '#EDE9F6', minHeight: 130, textAlignVertical: 'top', marginTop: 12 },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#6B21A8', padding: 16, borderRadius: 16, marginTop: 20, gap: 8 },
  btnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  resultCard: { marginTop: 24, backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  resultHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  resultTitle: { fontSize: 16, fontWeight: '700', color: '#6B21A8' },
});
