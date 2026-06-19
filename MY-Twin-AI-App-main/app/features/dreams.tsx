import { useState, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Animated, ActivityIndicator, Alert } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiPost } from '../../lib/httpClient';
import { Moon, Sparkles, ArrowLeft, Send, BookOpen } from 'lucide-react-native';

export default function DreamJournal() {
  const insets = useSafeAreaInsets();
  const { lang, theme } = useTwinStore();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';
  const t = (ar: string, en: string) => isAr ? ar : en;

  const [dream, setDream] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const primary = '#6B21A8';

  const handleAnalyze = async () => {
    if (!dream.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await apiPost('/api/features/dream', { dream: dream.trim(), lang: isAr ? 'ar' : 'en' });
      setResult(data);
      Animated.timing(fadeAnim, { toValue: 1, duration: 500, useNativeDriver: true }).start();
    } catch (e: any) {
      Alert.alert(t('خطأ', 'Error'), e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={[s.container, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}>
          <ArrowLeft size={24} stroke={primary} />
        </TouchableOpacity>
        <Text style={s.headerTitle}>{t('تفسير الأحلام', 'Dream Journal')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={s.content} keyboardShouldPersistTaps="handled">
        <View style={s.inputCard}>
          <Moon size={40} stroke={primary} style={{ alignSelf: 'center', marginBottom: 16 }} />
          <Text style={s.label}>{t('احكِ لي حلمك', 'Tell me your dream')}</Text>
          <TextInput
            style={[s.input, isAr && { textAlign: 'right' }]}
            placeholder={t('اكتب حلمك هنا...', 'Write your dream here...')}
            placeholderTextColor="#7C6B99"
            value={dream}
            onChangeText={setDream}
            multiline
            numberOfLines={4}
          />
          <TouchableOpacity style={[s.btn, { opacity: dream.trim() ? 1 : 0.6 }]} onPress={handleAnalyze} disabled={loading || !dream.trim()}>
            {loading ? <ActivityIndicator color="#FFF" /> : <><Send size={18} stroke="#FFF" /><Text style={s.btnText}>{t('فسر حلمي', 'Interpret Dream')}</Text></>}
          </TouchableOpacity>
        </View>

        {result && (
          <Animated.View style={[s.resultCard, { opacity: fadeAnim }]}>
            <Sparkles size={24} stroke={primary} style={{ alignSelf: 'center', marginBottom: 16 }} />
            <Text style={s.interpretation}>{result.interpretation}</Text>
            {result.symbols?.length > 0 && (
              <View style={s.symbolsRow}>
                <BookOpen size={16} stroke={primary} />
                <Text style={s.symbolsTitle}>{t('الرموز', 'Symbols')}: </Text>
                {result.symbols.map((sym: string, i: number) => (
                  <View key={i} style={s.symbolBadge}><Text style={s.symbolText}>{sym}</Text></View>
                ))}
              </View>
            )}
            {result.emotions?.length > 0 && (
              <View style={s.emotionsRow}>
                {result.emotions.map((emo: string, i: number) => (
                  <View key={i} style={s.emotionBadge}><Text style={s.emotionText}>{emo}</Text></View>
                ))}
              </View>
            )}
            {result.reflection_question && (
              <View style={s.questionCard}>
                <Text style={s.questionText}>{result.reflection_question}</Text>
              </View>
            )}
          </Animated.View>
        )}
      </ScrollView>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5, borderBottomColor: '#EDE9F6' },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'flex-start' },
  headerTitle: { fontSize: 18, fontWeight: '700', color: '#6B21A8' },
  content: { padding: 20, paddingBottom: 40 },
  inputCard: { backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  label: { fontSize: 16, fontWeight: '600', color: '#1A1226', marginBottom: 12, textAlign: 'center' },
  input: { backgroundColor: '#FFF', borderRadius: 16, padding: 16, fontSize: 15, color: '#1A1226', borderWidth: 1, borderColor: '#EDE9F6', minHeight: 120, textAlignVertical: 'top' },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#6B21A8', padding: 16, borderRadius: 16, marginTop: 16, gap: 8 },
  btnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  resultCard: { marginTop: 24, backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  interpretation: { fontSize: 16, color: '#1A1226', lineHeight: 26, textAlign: 'center', marginBottom: 16 },
  symbolsRow: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', gap: 8, marginBottom: 12 },
  symbolsTitle: { fontSize: 14, fontWeight: '600', color: '#6B21A8' },
  symbolBadge: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 12, backgroundColor: '#F5F3FF' },
  symbolText: { fontSize: 13, color: '#6B21A8', fontWeight: '500' },
  emotionsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 12, justifyContent: 'center' },
  emotionBadge: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 12, backgroundColor: '#FFF' },
  emotionText: { fontSize: 16 },
  questionCard: { backgroundColor: '#FFF', padding: 16, borderRadius: 16, borderLeftWidth: 4, borderLeftColor: '#6B21A8' },
  questionText: { fontSize: 15, color: '#1A1226', fontStyle: 'italic', lineHeight: 22 },
});
