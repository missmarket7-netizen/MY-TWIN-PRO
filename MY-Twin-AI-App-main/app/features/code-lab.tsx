import { useState, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert, Animated, Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiPost } from '../../lib/httpClient';
import { ArrowLeft, Code2, Send, Copy, RefreshCw, Terminal, Bug, BookOpen, CheckCircle2 } from 'lucide-react-native';
import * as Clipboard from 'expo-clipboard';

const LANGUAGES = [
  { id: 'python', label: 'Python', color: '#3776AB' },
  { id: 'javascript', label: 'JavaScript', color: '#F7DF1E' },
  { id: 'typescript', label: 'TypeScript', color: '#3178C6' },
  { id: 'java', label: 'Java', color: '#ED8B00' },
  { id: 'cpp', label: 'C++', color: '#00599C' },
  { id: 'go', label: 'Go', color: '#00ADD8' },
  { id: 'rust', label: 'Rust', color: '#DEA584' },
  { id: 'swift', label: 'Swift', color: '#F05138' },
];

const ACTIONS = [
  { id: 'write', label_ar: 'كتابة كود', label_en: 'Write Code', icon: Code2, desc_ar: 'اكتب كود كامل للمهمة', desc_en: 'Write complete code' },
  { id: 'review', label_ar: 'مراجعة', label_en: 'Review', icon: CheckCircle2, desc_ar: 'راجع الكود وحسّنه', desc_en: 'Review and improve' },
  { id: 'explain', label_ar: 'شرح', label_en: 'Explain', icon: BookOpen, desc_ar: 'اشرح الكود خطوة بخطوة', desc_en: 'Explain step by step' },
  { id: 'debug', label_ar: 'تصحيح', label_en: 'Debug', icon: Bug, desc_ar: 'اكتشف الأخطاء وأصلحها', desc_en: 'Find and fix bugs' },
];

export default function CodeLab() {
  const insets = useSafeAreaInsets();
  const { lang } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const primary = '#6B21A8';

  const [task, setTask] = useState('');
  const [language, setLanguage] = useState('python');
  const [action, setAction] = useState('write');
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState('');
  const [copied, setCopied] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const handleGenerate = async () => {
    if (!task.trim()) return;
    setLoading(true);
    setReply('');
    try {
      const data = await apiPost('/api/features/code', { task: task.trim(), language, action, lang: isAr ? 'ar' : 'en' });
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

  // استخراج الكود من النص (للتنسيق)
  const extractCode = (text: string) => {
    const match = text.match(/```[\w]*\n([\s\S]*?)```/);
    return match ? match[1] : text;
  };

  const codeContent = extractCode(reply);

  return (
    <View style={[s.container, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}><ArrowLeft size={24} stroke={primary} /></TouchableOpacity>
        <Text style={s.headerTitle}>{t('مختبر البرمجة', 'Code Lab')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={s.content} keyboardShouldPersistTaps="handled">
        <View style={s.card}>
          <Terminal size={40} stroke={primary} style={{ alignSelf: 'center', marginBottom: 16 }} />
          
          <Text style={s.label}>{t('اختر اللغة', 'Choose Language')}</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.langScroll}>
            {LANGUAGES.map((lg) => (
              <TouchableOpacity key={lg.id} style={[s.langBtn, language === lg.id && { borderColor: lg.color, backgroundColor: lg.color + '15' }]} onPress={() => setLanguage(lg.id)}>
                <Text style={[s.langText, language === lg.id && { color: lg.color, fontWeight: '700' }]}>{lg.label}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          <Text style={s.label}>{t('الإجراء', 'Action')}</Text>
          <View style={s.actionsGrid}>
            {ACTIONS.map((ac) => {
              const Icon = ac.icon;
              const active = action === ac.id;
              return (
                <TouchableOpacity key={ac.id} style={[s.actionCard, active && { borderColor: primary, backgroundColor: '#F5F3FF' }]} onPress={() => setAction(ac.id)}>
                  <Icon size={24} stroke={active ? primary : '#7C6B99'} />
                  <Text style={[s.actionLabel, active && { color: primary, fontWeight: '700' }]}>{isAr ? ac.label_ar : ac.label_en}</Text>
                  <Text style={s.actionDesc}>{isAr ? ac.desc_ar : ac.desc_en}</Text>
                </TouchableOpacity>
              );
            })}
          </View>

          <TextInput style={[s.input, isAr && { textAlign: 'right' }]} placeholder={t('اكتب المهمة البرمجية...', 'Write the coding task...')} placeholderTextColor="#7C6B99" value={task} onChangeText={setTask} multiline numberOfLines={4} />

          <TouchableOpacity style={[s.btn, { opacity: task.trim() ? 1 : 0.6 }]} onPress={handleGenerate} disabled={loading || !task.trim()}>
            {loading ? <ActivityIndicator color="#FFF" /> : <><Code2 size={18} stroke="#FFF" /><Text style={s.btnText}>{t('تنفيذ', 'Execute')}</Text></>}
          </TouchableOpacity>
        </View>

        {reply ? (
          <Animated.View style={[s.resultCard, { opacity: fadeAnim }]}>
            <View style={s.resultHeader}>
              <Text style={s.resultTitle}>{t('النتيجة', 'Result')}</Text>
              <View style={{ flexDirection: 'row', gap: 8 }}>
                <TouchableOpacity onPress={handleCopy}><Copy size={18} stroke={copied ? '#10B981' : primary} /></TouchableOpacity>
                <TouchableOpacity onPress={handleGenerate}><RefreshCw size={18} stroke={primary} /></TouchableOpacity>
              </View>
            </View>
            {/* عرض النص العادي */}
            <Text style={s.resultText}>{reply}</Text>
            {/* عرض الكود في بطاقة خاصة إذا وجد */}
            {codeContent !== reply && (
              <View style={s.codeBlock}>
                <View style={s.codeHeader}>
                  <View style={{ flexDirection: 'row', gap: 6 }}>
                    <View style={[s.codeDot, { backgroundColor: '#FF5F57' }]} />
                    <View style={[s.codeDot, { backgroundColor: '#FEBC2E' }]} />
                    <View style={[s.codeDot, { backgroundColor: '#28C840' }]} />
                  </View>
                  <Text style={s.codeLang}>{language}</Text>
                </View>
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  <Text style={s.codeText} selectable>{codeContent}</Text>
                </ScrollView>
              </View>
            )}
          </Animated.View>
        ) : null}
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
  card: { backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  label: { fontSize: 14, fontWeight: '600', color: '#1A1226', marginBottom: 10, marginTop: 16 },
  langScroll: { marginBottom: 8 },
  langBtn: { paddingHorizontal: 18, paddingVertical: 10, borderRadius: 20, borderWidth: 1.5, borderColor: '#EDE9F6', marginRight: 8 },
  langText: { fontSize: 13, fontWeight: '500', color: '#7C6B99' },
  actionsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  actionCard: { width: '47%', padding: 16, borderRadius: 16, borderWidth: 1.5, borderColor: '#EDE9F6', alignItems: 'center', gap: 6 },
  actionLabel: { fontSize: 14, fontWeight: '600', color: '#1A1226' },
  actionDesc: { fontSize: 11, color: '#7C6B99', textAlign: 'center' },
  input: { backgroundColor: '#FFF', borderRadius: 16, padding: 16, fontSize: 15, color: '#1A1226', borderWidth: 1, borderColor: '#EDE9F6', minHeight: 100, textAlignVertical: 'top', marginTop: 12 },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#6B21A8', padding: 16, borderRadius: 16, marginTop: 20, gap: 8 },
  btnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  resultCard: { marginTop: 24, backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  resultHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  resultTitle: { fontSize: 16, fontWeight: '700', color: '#6B21A8' },
  resultText: { fontSize: 15, color: '#1A1226', lineHeight: 24 },
  codeBlock: { marginTop: 16, backgroundColor: '#1E1E2E', borderRadius: 14, overflow: 'hidden' },
  codeHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 14, paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.1)' },
  codeDot: { width: 10, height: 10, borderRadius: 5 },
  codeLang: { color: '#6C7086', fontSize: 11, fontWeight: '600' },
  codeText: { fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', fontSize: 13, color: '#CDD6F4', padding: 14, lineHeight: 22 },
});
