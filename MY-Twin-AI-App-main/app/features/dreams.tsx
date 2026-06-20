import { useState, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert, Animated } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiPost } from '../../lib/httpClient';
import { ArrowLeft, Moon, Send, Sparkles, BookOpen, Volume2 } from 'lucide-react-native';
import { FeatureErrorBoundary } from '../../components/FeatureErrorBoundary';
import { useFeatureColors } from '../../lib/useFeatureColors';
import { SkeletonCard } from '../../components/SkeletonLoader';
import { speakResponse } from '../../utils/voice_engine';

export default function DreamJournal() {
  const insets = useSafeAreaInsets();
  const { lang } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const colors = useFeatureColors();

  const [dream, setDream] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const handleAnalyze = async () => {
    if (!dream.trim()) return;
    setLoading(true);
    setResult(null);
    setError('');
    try {
      const data = await apiPost('/api/features/dream', { dream: dream.trim(), lang: isAr ? 'ar' : 'en' });
      setResult(data);
      Animated.timing(fadeAnim, { toValue: 1, duration: 500, useNativeDriver: true }).start();
    } catch (e: any) {
      setError(e.message || t('فشل التحليل', 'Analysis failed'));
    } finally { setLoading(false); }
  };

  const handleSpeak = () => {
    if (result?.interpretation) speakResponse(result.interpretation).catch(() => {});
  };

  return (
    <FeatureErrorBoundary featureName={t('تفسير الأحلام', 'Dream Journal')}>
      <View style={[st.container, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
        <View style={st.header}>
          <TouchableOpacity onPress={() => router.back()}><ArrowLeft size={24} stroke="#6B21A8" /></TouchableOpacity>
          <Text style={[st.headerTitle, { color: colors.text }]}>{t('تفسير الأحلام', 'Dream Journal')}</Text>
          <View style={{ width: 40 }} />
        </View>

        <ScrollView contentContainerStyle={st.content} keyboardShouldPersistTaps="handled">
          <View style={[st.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
            <Moon size={40} stroke="#6B21A8" style={{ alignSelf: 'center', marginBottom: 16 }} />
            <Text style={[st.label, { color: colors.text }]}>{t('احكِ لي حلمك', 'Tell me your dream')}</Text>
            <TextInput style={[st.input, { backgroundColor: colors.inputBg, color: colors.text, borderColor: colors.border }, isAr && { textAlign: 'right' }]} placeholder={t('اكتب حلمك هنا...', 'Write your dream here...')} placeholderTextColor={colors.subtext} value={dream} onChangeText={setDream} multiline numberOfLines={4} />
            <TouchableOpacity style={[st.btn, { opacity: dream.trim() ? 1 : 0.6 }]} onPress={handleAnalyze} disabled={loading || !dream.trim()}>
              {loading ? <ActivityIndicator color="#FFF" /> : <><Send size={18} stroke="#FFF" /><Text style={st.btnText}>{t('فسر حلمي', 'Interpret Dream')}</Text></>}
            </TouchableOpacity>
          </View>

          {loading && <SkeletonCard />}
          {error ? <View style={st.errorCard}><Text style={st.errorText}>{error}</Text></View> : null}

          {result && (
            <Animated.View style={[st.resultCard, { backgroundColor: colors.card, borderColor: colors.border, opacity: fadeAnim }]}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <Sparkles size={20} stroke="#6B21A8" />
                <TouchableOpacity onPress={handleSpeak}><Volume2 size={20} stroke="#6B21A8" /></TouchableOpacity>
              </View>
              <Text style={[st.interpretation, { color: colors.text }]}>{result.interpretation}</Text>
            </Animated.View>
          )}
        </ScrollView>
      </View>
    </FeatureErrorBoundary>
  );
}

const st = StyleSheet.create({
  container: { flex: 1 }, header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5, borderBottomColor: '#EDE9F6' },
  headerTitle: { fontSize: 18, fontWeight: '700' }, content: { padding: 20, paddingBottom: 40 },
  card: { borderRadius: 24, padding: 24, borderWidth: 1 }, label: { fontSize: 16, fontWeight: '600', marginBottom: 12, textAlign: 'center' },
  input: { borderRadius: 16, padding: 16, fontSize: 15, borderWidth: 1, minHeight: 120, textAlignVertical: 'top' },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#6B21A8', padding: 16, borderRadius: 16, marginTop: 16, gap: 8 },
  btnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  errorCard: { padding: 16, alignItems: 'center' }, errorText: { color: '#EF4444', fontSize: 14 },
  resultCard: { marginTop: 24, borderRadius: 24, padding: 24, borderWidth: 1 },
  interpretation: { fontSize: 16, lineHeight: 26 },
});
