import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiPost } from '../../lib/httpClient';
import { PenLine, ArrowLeft, Copy, Sparkles } from 'lucide-react-native';
import * as Clipboard from 'expo-clipboard';

const PLATFORMS = [
  { id: 'instagram', label: 'Instagram', color: '#E1306C' },
  { id: 'twitter', label: 'X (Twitter)', color: '#1DA1F2' },
  { id: 'linkedin', label: 'LinkedIn', color: '#0A66C2' },
  { id: 'tiktok', label: 'TikTok', color: '#000000' },
  { id: 'youtube', label: 'YouTube', color: '#FF0000' },
];

const TONES = [
  { id: 'professional', label_ar: 'احترافي', label_en: 'Professional' },
  { id: 'casual', label_ar: 'عادي', label_en: 'Casual' },
  { id: 'humorous', label_ar: 'فكاهي', label_en: 'Humorous' },
  { id: 'inspirational', label_ar: 'ملهم', label_en: 'Inspirational' },
];

export default function ContentCreator() {
  const insets = useSafeAreaInsets();
  const { lang } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const primary = '#6B21A8';

  const [topic, setTopic] = useState('');
  const [platform, setPlatform] = useState('instagram');
  const [tone, setTone] = useState('professional');
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState('');
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setReply('');
    try {
      const data = await apiPost('/api/features/content', { topic: topic.trim(), platform, tone, lang: isAr ? 'ar' : 'en' });
      setReply(data.reply);
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
    <View style={[st.container, { paddingTop: insets.top }]}>
      <View style={st.header}>
        <TouchableOpacity onPress={() => router.back()} style={st.backBtn}><ArrowLeft size={24} stroke={primary} /></TouchableOpacity>
        <Text style={st.headerTitle}>{t('كتابة محتوى', 'Content Creator')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={st.content} keyboardShouldPersistTaps="handled">
        <View style={st.card}>
          <PenLine size={32} stroke={primary} style={{ alignSelf: 'center', marginBottom: 16 }} />
          <Text style={st.label}>{t('اختر المنصة', 'Choose Platform')}</Text>
          <View style={st.platformRow}>
            {PLATFORMS.map((p) => (
              <TouchableOpacity key={p.id} style={[st.platformBtn, platform === p.id && { borderColor: p.color, backgroundColor: p.color + '15' }]} onPress={() => setPlatform(p.id)}>
                <Text style={[st.platformText, platform === p.id && { color: p.color, fontWeight: '700' }]}>{p.label}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={st.label}>{t('النبرة', 'Tone')}</Text>
          <View style={st.platformRow}>
            {TONES.map((tn) => (
              <TouchableOpacity key={tn.id} style={[st.platformBtn, tone === tn.id && { borderColor: primary, backgroundColor: primary + '15' }]} onPress={() => setTone(tn.id)}>
                <Text style={[st.platformText, tone === tn.id && { color: primary, fontWeight: '700' }]}>{isAr ? tn.label_ar : tn.label_en}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <TextInput style={[st.input, isAr && { textAlign: 'right' }]} placeholder={t('عن ماذا تريد الكتابة؟', 'What do you want to write about?')} placeholderTextColor="#7C6B99" value={topic} onChangeText={setTopic} multiline />
          <TouchableOpacity style={[st.btn, { opacity: topic.trim() ? 1 : 0.6 }]} onPress={handleGenerate} disabled={loading || !topic.trim()}>
            {loading ? <ActivityIndicator color="#FFF" /> : <><Sparkles size={18} stroke="#FFF" /><Text style={st.btnText}>{t('توليد المحتوى', 'Generate Content')}</Text></>}
          </TouchableOpacity>
        </View>

        {reply ? (
          <View style={st.resultCard}>
            <View style={st.resultHeader}>
              <Text style={st.resultTitle}>{t('المحتوى', 'Content')}</Text>
              <TouchableOpacity onPress={handleCopy}><Copy size={18} stroke={copied ? '#10B981' : primary} /></TouchableOpacity>
            </View>
            <Text style={st.resultText}>{reply}</Text>
          </View>
        ) : null}
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
  card: { backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  label: { fontSize: 14, fontWeight: '600', color: '#1A1226', marginBottom: 10, marginTop: 16 },
  platformRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 8 },
  platformBtn: { paddingHorizontal: 16, paddingVertical: 10, borderRadius: 20, borderWidth: 1.5, borderColor: '#EDE9F6' },
  platformText: { fontSize: 13, fontWeight: '500', color: '#7C6B99' },
  input: { backgroundColor: '#FFF', borderRadius: 16, padding: 16, fontSize: 15, color: '#1A1226', borderWidth: 1, borderColor: '#EDE9F6', minHeight: 80, textAlignVertical: 'top', marginTop: 12 },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#6B21A8', padding: 16, borderRadius: 16, marginTop: 16, gap: 8 },
  btnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  resultCard: { marginTop: 24, backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  resultHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  resultTitle: { fontSize: 16, fontWeight: '700', color: '#6B21A8' },
  resultText: { fontSize: 15, color: '#1A1226', lineHeight: 24 },
});
