import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ScrollView, ActivityIndicator, Animated, Modal,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore, useTwinStoreFull } from '../../store/useTwinStore';
import { useTheme } from '../../utils/theme';
import { router } from 'expo-router';
import {
  ArrowLeft, Moon, Sparkles, BookOpen, Volume2, Star,
  Brain, Cloud, Zap, Heart, TrendingUp, RefreshCw,
  Layers, Lightbulb, X, ChevronDown, ChevronUp,
} from 'lucide-react-native';
import { speakResponse } from '../../utils/voice_engine';

type AnalysisSchool = 'all' | 'freud' | 'jung' | 'cayce' | 'ibn_sirine' | 'nabulsi';

export default function DreamJournal() {
  const insets = useSafeAreaInsets();
  const theme = useTheme();
  const { lang } = useTwinStore();
  const { interpretDream } = useTwinStoreFull();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';

  const [dream, setDream] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [selectedSchool, setSelectedSchool] = useState<AnalysisSchool>('all');
  const [showSchoolPicker, setShowSchoolPicker] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const colors = {
    bg: isDark ? '#0F0A1A' : '#FAFAF8',
    card: isDark ? '#1A1226' : '#FFFFFF',
    text: isDark ? '#FFFFFF' : '#2D2D2D',
    subtext: isDark ? '#8B7BA3' : '#6B6B6B',
    accent: '#6366F1',
    accentLight: '#6366F120',
    border: isDark ? '#2D1B4D' : '#E8E8E3',
    inputBg: isDark ? '#161122' : '#FDFDF9',
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
  };

  const schools: { id: AnalysisSchool; label_ar: string; label_en: string; icon: any; color: string }[] = [
    { id: 'all', label_ar: 'جميع المدارس', label_en: 'All Schools', icon: Layers, color: colors.accent },
    { id: 'freud', label_ar: 'فرويد', label_en: 'Freud', icon: Brain, color: '#EC4899' },
    { id: 'jung', label_ar: 'يونج', label_en: 'Jung', icon: Star, color: '#F59E0B' },
    { id: 'cayce', label_ar: 'إدجار كايس', label_en: 'Cayce', icon: Cloud, color: '#3B82F6' },
    { id: 'ibn_sirine', label_ar: 'ابن سيرين', label_en: 'Ibn Sirine', icon: BookOpen, color: '#10B981' },
    { id: 'nabulsi', label_ar: 'النابلسي', label_en: 'Al-Nabulsi', icon: Lightbulb, color: '#8B5CF6' },
  ];

  const handleAnalyze = useCallback(async () => {
    if (!dream.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      await interpretDream(dream.trim());
      // محاكاة نتيجة للعرض (في الإصدار النهائي تُقرأ من المتجر)
      setResult({
        interpretation: 'هذا تفسير حلمك...',
        symbols_analysis: ['ماء: يرمز إلى الحياة والعواطف', 'ثعبان: يرمز إلى الحكمة الخفية'],
        emotions: ['فضول', 'قلق'],
        reflection_question: 'ما هو أول شيء فكرت فيه عند استيقاظك؟',
        psychological_insight: 'حلمك يعكس رغبة في التغيير.',
        school_used: selectedSchool,
      });
      Animated.timing(fadeAnim, { toValue: 1, duration: 500, useNativeDriver: true }).start();
    } catch (e) {
      setResult({ error: isAr ? 'فشل التحليل' : 'Analysis failed' });
    } finally { setLoading(false); }
  }, [dream, interpretDream, selectedSchool, fadeAnim]);

  const handleSpeak = () => {
    if (result?.interpretation) speakResponse(result.interpretation).catch(() => {});
  };

  const handleReset = () => {
    setDream('');
    setResult(null);
    fadeAnim.setValue(0);
  };

  return (
    <View style={[st.root, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
      {/* الهيدر */}
      <View style={[st.header, { borderBottomColor: colors.border }]}>
        <TouchableOpacity onPress={() => router.back()}>
          <ArrowLeft size={24} stroke={colors.text} />
        </TouchableOpacity>
        <View style={st.headerCenter}>
          <Moon size={24} stroke={colors.accent} />
          <Text style={[st.headerTitle, { color: colors.text }]}>
            {isAr ? 'تفسير الأحلام' : 'Dream Journal'}
          </Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={st.content} keyboardShouldPersistTaps="handled">
        {/* بطاقة الإدخال */}
        <View style={[st.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={[st.iconWrap, { backgroundColor: colors.accentLight }]}>
            <Moon size={40} stroke={colors.accent} />
          </View>
          <Text style={[st.label, { color: colors.text }]}>
            {isAr ? 'احكِ لي حلمك' : 'Tell me your dream'}
          </Text>

          {/* اختيار المدرسة */}
          <TouchableOpacity
            style={[st.schoolPicker, { borderColor: colors.border }]}
            onPress={() => setShowSchoolPicker(true)}
          >
            <Text style={[st.schoolPickerText, { color: colors.text }]}>
              {schools.find(s => s.id === selectedSchool)?.label_ar || 'جميع المدارس'}
            </Text>
            <ChevronDown size={16} stroke={colors.subtext} />
          </TouchableOpacity>

          <TextInput
            style={[st.input, {
              backgroundColor: colors.inputBg,
              color: colors.text,
              borderColor: colors.border,
            }, isAr && { textAlign: 'right' }]}
            placeholder={isAr ? 'اكتب حلمك هنا...' : 'Write your dream here...'}
            placeholderTextColor={colors.subtext}
            value={dream}
            onChangeText={setDream}
            multiline
            numberOfLines={5}
            textAlignVertical="top"
          />

          <TouchableOpacity
            style={[st.submitBtn, { backgroundColor: colors.accent, opacity: dream.trim() ? 1 : 0.6 }]}
            onPress={handleAnalyze}
            disabled={loading || !dream.trim()}
          >
            {loading ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <>
                <Sparkles size={18} stroke="#FFF" />
                <Text style={st.submitBtnText}>
                  {isAr ? 'فسر حلمي' : 'Interpret Dream'}
                </Text>
              </>
            )}
          </TouchableOpacity>
        </View>

        {/* نتيجة التحليل */}
        {result && !result.error && (
          <Animated.View style={{ opacity: fadeAnim }}>
            {/* التفسير الرئيسي */}
            <View style={[st.resultCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <View style={st.resultHeader}>
                <Sparkles size={20} stroke={colors.accent} />
                <Text style={[st.resultTitle, { color: colors.text }]}>
                  {isAr ? 'التفسير' : 'Interpretation'}
                </Text>
                <TouchableOpacity onPress={handleSpeak} style={st.speakBtn}>
                  <Volume2 size={18} stroke={colors.accent} />
                </TouchableOpacity>
              </View>
              <Text style={[st.resultBody, { color: colors.subtext }]}>
                {result.interpretation}
              </Text>
            </View>

            {/* الرموز */}
            {result.symbols_analysis && result.symbols_analysis.length > 0 && (
              <View style={[st.resultCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
                <View style={st.resultHeader}>
                  <Zap size={20} stroke={colors.warning} />
                  <Text style={[st.resultTitle, { color: colors.text }]}>
                    {isAr ? 'الرموز' : 'Symbols'}
                  </Text>
                </View>
                {result.symbols_analysis.map((sym: string, i: number) => (
                  <View key={i} style={st.symbolRow}>
                    <View style={[st.symbolDot, { backgroundColor: colors.accent }]} />
                    <Text style={[st.symbolText, { color: colors.subtext }]}>{sym}</Text>
                  </View>
                ))}
              </View>
            )}

            {/* المشاعر */}
            {result.emotions && result.emotions.length > 0 && (
              <View style={[st.resultCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
                <View style={st.resultHeader}>
                  <Heart size={20} stroke={colors.danger} />
                  <Text style={[st.resultTitle, { color: colors.text }]}>
                    {isAr ? 'المشاعر' : 'Emotions'}
                  </Text>
                </View>
                <View style={st.emotionRow}>
                  {result.emotions.map((emo: string, i: number) => (
                    <View key={i} style={[st.emotionBadge, { backgroundColor: colors.accentLight, borderColor: colors.accent }]}>
                      <Text style={[st.emotionBadgeText, { color: colors.accent }]}>{emo}</Text>
                    </View>
                  ))}
                </View>
              </View>
            )}

            {/* سؤال تأملي */}
            {result.reflection_question && (
              <View style={[st.reflectionCard, { backgroundColor: colors.success + '10', borderColor: colors.success }]}>
                <RefreshCw size={18} stroke={colors.success} />
                <Text style={[st.reflectionText, { color: colors.success }]}>
                  {result.reflection_question}
                </Text>
              </View>
            )}

            {/* زر إعادة */}
            <TouchableOpacity
              style={[st.resetBtn, { borderColor: colors.border }]}
              onPress={handleReset}
            >
              <RefreshCw size={16} stroke={colors.subtext} />
              <Text style={[st.resetBtnText, { color: colors.subtext }]}>
                {isAr ? 'حلم جديد' : 'New Dream'}
              </Text>
            </TouchableOpacity>
          </Animated.View>
        )}
      </ScrollView>

      {/* مودال اختيار المدرسة */}
      <Modal visible={showSchoolPicker} transparent animationType="fade" onRequestClose={() => setShowSchoolPicker(false)}>
        <TouchableOpacity style={st.modalOverlay} activeOpacity={1} onPress={() => setShowSchoolPicker(false)}>
          <View style={[st.modalContent, { backgroundColor: colors.card }]}>
            <Text style={[st.modalTitle, { color: colors.text }]}>
              {isAr ? 'اختر مدرسة التفسير' : 'Select School'}
            </Text>
            {schools.map(school => (
              <TouchableOpacity
                key={school.id}
                style={[
                  st.schoolOption,
                  { borderColor: selectedSchool === school.id ? school.color : 'transparent' },
                  selectedSchool === school.id && { backgroundColor: school.color + '10' },
                ]}
                onPress={() => { setSelectedSchool(school.id); setShowSchoolPicker(false); }}
              >
                <school.icon size={20} stroke={school.color} />
                <Text style={[st.schoolOptionText, { color: colors.text }]}>
                  {isAr ? school.label_ar : school.label_en}
                </Text>
                {selectedSchool === school.id && <CheckCircle2 size={18} stroke={school.color} />}
              </TouchableOpacity>
            ))}
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
}

// أيقونة CheckCircle2 (غير موجودة في lucide-react-native، سنستخدم Check)
import { Check } from 'lucide-react-native';
const CheckCircle2 = Check;

const st = StyleSheet.create({
  root: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5 },
  headerCenter: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  headerTitle: { fontSize: 18, fontWeight: '700' },
  content: { padding: 20, paddingBottom: 40 },
  card: { borderRadius: 24, padding: 24, borderWidth: 1, alignItems: 'center', marginBottom: 24 },
  iconWrap: { width: 72, height: 72, borderRadius: 20, justifyContent: 'center', alignItems: 'center', marginBottom: 16 },
  label: { fontSize: 16, fontWeight: '600', marginBottom: 16, textAlign: 'center' },
  schoolPicker: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', width: '100%', borderWidth: 1, borderRadius: 14, padding: 12, marginBottom: 16 },
  schoolPickerText: { fontSize: 14, fontWeight: '500' },
  input: { width: '100%', borderRadius: 16, padding: 16, fontSize: 15, borderWidth: 1, minHeight: 120, textAlignVertical: 'top', marginBottom: 16 },
  submitBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 14, paddingHorizontal: 24, borderRadius: 14, width: '100%', gap: 8 },
  submitBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  // نتيجة
  resultCard: { borderRadius: 20, borderWidth: 1, padding: 20, marginBottom: 16 },
  resultHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 12 },
  resultTitle: { fontSize: 16, fontWeight: '700', flex: 1 },
  speakBtn: { padding: 4 },
  resultBody: { fontSize: 15, lineHeight: 26 },
  symbolRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 10, marginBottom: 8 },
  symbolDot: { width: 8, height: 8, borderRadius: 4, marginTop: 6 },
  symbolText: { flex: 1, fontSize: 14, lineHeight: 22 },
  emotionRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  emotionBadge: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 12, borderWidth: 1 },
  emotionBadgeText: { fontSize: 13, fontWeight: '600' },
  reflectionCard: { flexDirection: 'row', alignItems: 'center', gap: 10, padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 16 },
  reflectionText: { flex: 1, fontSize: 14, fontWeight: '600' },
  resetBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingVertical: 12, borderRadius: 14, borderWidth: 1 },
  resetBtnText: { fontWeight: '600', fontSize: 14 },
  // مودال
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' },
  modalContent: { width: '85%', borderRadius: 20, padding: 20 },
  modalTitle: { fontSize: 18, fontWeight: '700', marginBottom: 16 },
  schoolOption: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 14, borderRadius: 14, borderWidth: 1.5, marginBottom: 8 },
  schoolOptionText: { flex: 1, fontSize: 15, fontWeight: '600' },
});
