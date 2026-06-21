import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  ActivityIndicator, StyleSheet, Animated, Dimensions,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore, useTwinStoreFull } from '../../store/useTwinStore';
import { useTheme, getEmotionColor, getBondColor } from '../../utils/theme';
import {
  Brain, Sparkles, Target, Zap, ArrowLeft, ArrowRight,
  Check, X, RotateCcw, BookOpen, Lightbulb, Layers,
  MessageCircle, TrendingUp, Award,
} from 'lucide-react-native';

const { width: SCREEN_W } = Dimensions.get('window');

type SessionState = 'idle' | 'explaining' | 'questioning' | 'reviewing';

export default function StudyMode() {
  const insets = useSafeAreaInsets();
  const theme = useTheme();
  const { lang, userId } = useTwinStore();
  const { startStudySession, answerStudyQuestion, endStudySession } = useTwinStoreFull();
  const isRTL = lang === 'ar';
  const isDark = theme === 'dark';

  // حالة الجلسة
  const [concept, setConcept] = useState('');
  const [sessionState, setSessionState] = useState<SessionState>('idle');
  const [loading, setLoading] = useState(false);
  const [explanation, setExplanation] = useState<any>(null);
  const [currentQuestion, setCurrentQuestion] = useState<string>('');
  const [userAnswer, setUserAnswer] = useState('');
  const [answerResult, setAnswerResult] = useState<any>(null);
  const [sessionStats, setSessionStats] = useState({
    depth: 0, questionsAsked: 0, correctAnswers: 0, accuracy: '0%',
  });

  // ألوان
  const colors = {
    bg: isDark ? '#0F0A1A' : '#FAFAF8',
    card: isDark ? '#1A1226' : '#FFFFFF',
    text: isDark ? '#FFFFFF' : '#2D2D2D',
    subtext: isDark ? '#8B7BA3' : '#6B6B6B',
    accent: '#3B82F6',
    accentLight: '#3B82F620',
    success: '#10B981',
    danger: '#EF4444',
    warning: '#F59E0B',
    border: isDark ? '#2D1B4D' : '#E8E8E3',
    inputBg: isDark ? '#161122' : '#FDFDF9',
  };

  // بدء الجلسة
  const handleStartSession = useCallback(async () => {
    if (!concept.trim()) return;
    setLoading(true);
    setSessionState('explaining');
    try {
      await startStudySession(concept);
      // جلب الشرح (محاكاة - في الإصدار النهائي يُقرأ من المتجر)
      setExplanation({
        simplified: 'هذا شرح مبسط للمفهوم...',
        analogy: 'تخيل أن المفهوم مثل...',
        fragments: ['الجزء الأول', 'الجزء الثاني', 'الجزء الثالث'],
        check_question: 'هل فهمت الشرح؟',
        layers_applied: 5,
      });
      setSessionStats(prev => ({ ...prev, depth: 1 }));
    } catch (e) {
      setExplanation({ error: 'تعذر بدء الجلسة' });
    }
    setLoading(false);
  }, [concept, startStudySession]);

  // الإجابة على سؤال
  const handleAnswer = useCallback(async () => {
    if (!userAnswer.trim()) return;
    setLoading(true);
    try {
      const result = await answerStudyQuestion(userAnswer);
      setAnswerResult(result);
      setSessionStats(prev => ({
        ...prev,
        questionsAsked: prev.questionsAsked + 1,
        correctAnswers: prev.correctAnswers + (result?.is_correct ? 1 : 0),
        accuracy: prev.questionsAsked > 0
          ? `${Math.round(((prev.correctAnswers + (result?.is_correct ? 1 : 0)) / (prev.questionsAsked + 1)) * 100)}%`
          : (result?.is_correct ? '100%' : '0%'),
        depth: result?.current_depth || prev.depth,
      }));
      if (result?.next_question) {
        setCurrentQuestion(result.next_question);
      }
      setUserAnswer('');
    } catch (e) {
      setAnswerResult({ error: 'تعذر تقييم الإجابة' });
    }
    setLoading(false);
  }, [userAnswer, answerStudyQuestion]);

  // إنهاء الجلسة
  const handleEndSession = useCallback(async () => {
    setLoading(true);
    try {
      await endStudySession();
      setSessionState('reviewing');
    } catch (e) {}
    setLoading(false);
  }, [endStudySession]);

  // إعادة تعيين
  const handleReset = () => {
    setConcept('');
    setSessionState('idle');
    setExplanation(null);
    setCurrentQuestion('');
    setUserAnswer('');
    setAnswerResult(null);
    setSessionStats({ depth: 0, questionsAsked: 0, correctAnswers: 0, accuracy: '0%' });
  };

  return (
    <View style={[styles.root, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
      {/* الهيدر */}
      <View style={[styles.header, { borderBottomColor: colors.border }]}>
        <TouchableOpacity onPress={handleReset} style={styles.backBtn}>
          <ArrowLeft size={22} stroke={colors.text} />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Brain size={24} stroke={colors.accent} />
          <Text style={[styles.headerTitle, { color: colors.text }]}>
            {lang === 'ar' ? 'مساعد الدراسة' : 'Study Assistant'}
          </Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        {/* مرحلة الإدخال */}
        {sessionState === 'idle' && (
          <View style={styles.idleContainer}>
            <View style={[styles.iconWrap, { backgroundColor: colors.accentLight }]}>
              <BookOpen size={48} stroke={colors.accent} />
            </View>
            <Text style={[styles.idleTitle, { color: colors.text }]}>
              {lang === 'ar' ? 'ماذا تريد أن تتعلم اليوم؟' : 'What do you want to learn today?'}
            </Text>
            <TextInput
              style={[styles.conceptInput, { backgroundColor: colors.inputBg, borderColor: colors.border, color: colors.text }]}
              placeholder={lang === 'ar' ? 'مثلاً: الجاذبية، التفاضل...' : 'e.g., Gravity, Calculus...'}
              placeholderTextColor={colors.subtext}
              value={concept}
              onChangeText={setConcept}
              multiline
            />
            <TouchableOpacity
              style={[styles.startBtn, { backgroundColor: concept.trim() ? colors.accent : colors.border }]}
              onPress={handleStartSession}
              disabled={!concept.trim() || loading}
            >
              {loading ? <ActivityIndicator color="#FFF" /> : <Sparkles size={20} stroke="#FFF" />}
              <Text style={styles.startBtnText}>
                {lang === 'ar' ? 'ابدأ التعلم' : 'Start Learning'}
              </Text>
            </TouchableOpacity>
          </View>
        )}

        {/* مرحلة الشرح */}
        {sessionState === 'explaining' && explanation && (
          <View style={styles.explanationContainer}>
            {/* شريط التقدم */}
            <View style={[styles.progressBar, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <View style={styles.progressItem}>
                <Target size={16} stroke={colors.accent} />
                <Text style={[styles.progressText, { color: colors.subtext }]}>
                  {lang === 'ar' ? `العمق: ${sessionStats.depth}/6` : `Depth: ${sessionStats.depth}/6`}
                </Text>
              </View>
              <View style={styles.progressItem}>
                <TrendingUp size={16} stroke={colors.success} />
                <Text style={[styles.progressText, { color: colors.subtext }]}>
                  {lang === 'ar' ? `الدقة: ${sessionStats.accuracy}` : `Accuracy: ${sessionStats.accuracy}`}
                </Text>
              </View>
            </View>

            {/* الشرح المبسط */}
            <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <View style={styles.cardHeader}>
                <Lightbulb size={20} stroke={colors.warning} />
                <Text style={[styles.cardTitle, { color: colors.text }]}>
                  {lang === 'ar' ? 'الشرح المبسط' : 'Simplified'}
                </Text>
              </View>
              <Text style={[styles.cardBody, { color: colors.subtext }]}>
                {explanation.simplified || explanation.error || 'جاري التحميل...'}
              </Text>
            </View>

            {/* التشبيه */}
            {explanation.analogy && (
              <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
                <View style={styles.cardHeader}>
                  <Zap size={20} stroke={colors.warning} />
                  <Text style={[styles.cardTitle, { color: colors.text }]}>
                    {lang === 'ar' ? 'تشبيه' : 'Analogy'}
                  </Text>
                </View>
                <Text style={[styles.cardBody, { color: colors.subtext }]}>{explanation.analogy}</Text>
              </View>
            )}

            {/* الأجزاء */}
            {explanation.fragments && (
              <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
                <View style={styles.cardHeader}>
                  <Layers size={20} stroke={colors.accent} />
                  <Text style={[styles.cardTitle, { color: colors.text }]}>
                    {lang === 'ar' ? 'الأجزاء' : 'Fragments'}
                  </Text>
                </View>
                {explanation.fragments.map((frag: string, i: number) => (
                  <View key={i} style={styles.fragmentRow}>
                    <View style={[styles.fragmentDot, { backgroundColor: colors.accent }]} />
                    <Text style={[styles.fragmentText, { color: colors.subtext }]}>{frag}</Text>
                  </View>
                ))}
              </View>
            )}

            {/* أزرار الإجراءات */}
            <View style={styles.actionRow}>
              <TouchableOpacity
                style={[styles.actionBtn, { backgroundColor: colors.accent }]}
                onPress={() => setSessionState('questioning')}
              >
                <MessageCircle size={18} stroke="#FFF" />
                <Text style={styles.actionBtnText}>
                  {lang === 'ar' ? 'اختبر فهمي' : 'Test Me'}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.actionBtn, { backgroundColor: colors.danger }]}
                onPress={handleEndSession}
              >
                <X size={18} stroke="#FFF" />
                <Text style={styles.actionBtnText}>
                  {lang === 'ar' ? 'إنهاء' : 'End'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* مرحلة الأسئلة */}
        {sessionState === 'questioning' && (
          <View style={styles.questionContainer}>
            <Text style={[styles.questionText, { color: colors.text }]}>
              {currentQuestion || explanation?.check_question || 'ما هو فهمك للمفهوم؟'}
            </Text>
            <TextInput
              style={[styles.answerInput, { backgroundColor: colors.inputBg, borderColor: colors.border, color: colors.text }]}
              placeholder={lang === 'ar' ? 'اكتب إجابتك...' : 'Write your answer...'}
              placeholderTextColor={colors.subtext}
              value={userAnswer}
              onChangeText={setUserAnswer}
              multiline
            />
            <TouchableOpacity
              style={[styles.submitBtn, { backgroundColor: userAnswer.trim() ? colors.accent : colors.border }]}
              onPress={handleAnswer}
              disabled={!userAnswer.trim() || loading}
            >
              {loading ? <ActivityIndicator color="#FFF" /> : <Check size={20} stroke="#FFF" />}
              <Text style={styles.submitBtnText}>
                {lang === 'ar' ? 'إرسال الإجابة' : 'Submit Answer'}
              </Text>
            </TouchableOpacity>

            {/* نتيجة الإجابة */}
            {answerResult && (
              <View style={[styles.resultCard, {
                backgroundColor: answerResult.is_correct ? colors.success + '15' : colors.danger + '15',
                borderColor: answerResult.is_correct ? colors.success : colors.danger,
              }]}>
                <View style={styles.resultHeader}>
                  {answerResult.is_correct ? (
                    <Check size={24} stroke={colors.success} />
                  ) : (
                    <X size={24} stroke={colors.danger} />
                  )}
                  <Text style={[styles.resultTitle, {
                    color: answerResult.is_correct ? colors.success : colors.danger,
                  }]}>
                    {answerResult.is_correct
                      ? (lang === 'ar' ? 'إجابة صحيحة! 🎉' : 'Correct! 🎉')
                      : (lang === 'ar' ? 'حاول مرة أخرى 💪' : 'Try again 💪')}
                  </Text>
                </View>
                {answerResult.next_question && (
                  <TouchableOpacity
                    style={[styles.nextBtn, { backgroundColor: colors.accent + '20' }]}
                    onPress={() => {
                      setCurrentQuestion(answerResult.next_question || '');
                      setAnswerResult(null);
                    }}
                  >
                    <ArrowRight size={16} stroke={colors.accent} />
                    <Text style={[styles.nextBtnText, { color: colors.accent }]}>
                      {lang === 'ar' ? 'السؤال التالي' : 'Next Question'}
                    </Text>
                  </TouchableOpacity>
                )}
              </View>
            )}

            <TouchableOpacity
              style={[styles.backToExplainBtn, { borderColor: colors.border }]}
              onPress={() => {
                setSessionState('explaining');
                setAnswerResult(null);
              }}
            >
              <RotateCcw size={16} stroke={colors.subtext} />
              <Text style={[styles.backToExplainText, { color: colors.subtext }]}>
                {lang === 'ar' ? 'العودة للشرح' : 'Back to Explanation'}
              </Text>
            </TouchableOpacity>
          </View>
        )}

        {/* مرحلة المراجعة */}
        {sessionState === 'reviewing' && (
          <View style={styles.reviewContainer}>
            <View style={[styles.iconWrap, { backgroundColor: colors.success + '15' }]}>
              <Award size={48} stroke={colors.success} />
            </View>
            <Text style={[styles.reviewTitle, { color: colors.text }]}>
              {lang === 'ar' ? 'أحسنت! 🎉' : 'Well Done! 🎉'}
            </Text>
            <View style={[styles.statsCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <View style={styles.statRow}>
                <Text style={[styles.statLabel, { color: colors.subtext }]}>
                  {lang === 'ar' ? 'الأسئلة' : 'Questions'}
                </Text>
                <Text style={[styles.statValue, { color: colors.text }]}>{sessionStats.questionsAsked}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={[styles.statLabel, { color: colors.subtext }]}>
                  {lang === 'ar' ? 'الإجابات الصحيحة' : 'Correct'}
                </Text>
                <Text style={[styles.statValue, { color: colors.success }]}>{sessionStats.correctAnswers}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={[styles.statLabel, { color: colors.subtext }]}>
                  {lang === 'ar' ? 'الدقة' : 'Accuracy'}
                </Text>
                <Text style={[styles.statValue, { color: colors.accent }]}>{sessionStats.accuracy}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={[styles.statLabel, { color: colors.subtext }]}>
                  {lang === 'ar' ? 'العمق' : 'Depth'}
                </Text>
                <Text style={[styles.statValue, { color: colors.warning }]}>{sessionStats.depth}/6</Text>
              </View>
            </View>
            <TouchableOpacity
              style={[styles.startBtn, { backgroundColor: colors.accent }]}
              onPress={handleReset}
            >
              <RotateCcw size={20} stroke="#FFF" />
              <Text style={styles.startBtnText}>
                {lang === 'ar' ? 'مفهوم جديد' : 'New Concept'}
              </Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5 },
  backBtn: { padding: 6 },
  headerCenter: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  headerTitle: { fontSize: 18, fontWeight: '700' },
  content: { padding: 20, paddingBottom: 40 },
  // خامل
  idleContainer: { alignItems: 'center', paddingVertical: 40 },
  iconWrap: { width: 80, height: 80, borderRadius: 24, justifyContent: 'center', alignItems: 'center', marginBottom: 20 },
  idleTitle: { fontSize: 20, fontWeight: '700', marginBottom: 20, textAlign: 'center' },
  conceptInput: { width: '100%', borderWidth: 1, borderRadius: 16, padding: 16, fontSize: 16, marginBottom: 20, minHeight: 80 },
  startBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingHorizontal: 24, paddingVertical: 14, borderRadius: 14 },
  startBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  // شرح
  explanationContainer: { gap: 16 },
  progressBar: { flexDirection: 'row', justifyContent: 'space-around', padding: 12, borderRadius: 12, borderWidth: 1 },
  progressItem: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  progressText: { fontSize: 13, fontWeight: '600' },
  card: { borderRadius: 16, borderWidth: 1, padding: 16 },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 10 },
  cardTitle: { fontSize: 16, fontWeight: '700' },
  cardBody: { fontSize: 15, lineHeight: 24 },
  fragmentRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 10, marginBottom: 8 },
  fragmentDot: { width: 8, height: 8, borderRadius: 4, marginTop: 6 },
  fragmentText: { flex: 1, fontSize: 14, lineHeight: 22 },
  actionRow: { flexDirection: 'row', gap: 12, marginTop: 8 },
  actionBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingVertical: 14, borderRadius: 14 },
  actionBtnText: { color: '#FFF', fontWeight: '700', fontSize: 15 },
  // أسئلة
  questionContainer: { gap: 16 },
  questionText: { fontSize: 18, fontWeight: '600', lineHeight: 28 },
  answerInput: { borderWidth: 1, borderRadius: 16, padding: 16, fontSize: 16, minHeight: 100 },
  submitBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingVertical: 14, borderRadius: 14 },
  submitBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  resultCard: { borderRadius: 16, borderWidth: 1, padding: 16 },
  resultHeader: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 12 },
  resultTitle: { fontSize: 18, fontWeight: '700' },
  nextBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingVertical: 12, borderRadius: 12, marginTop: 12 },
  nextBtnText: { fontWeight: '600', fontSize: 14 },
  backToExplainBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingVertical: 12, borderRadius: 12, borderWidth: 1 },
  backToExplainText: { fontWeight: '600', fontSize: 14 },
  // مراجعة
  reviewContainer: { alignItems: 'center', paddingVertical: 40 },
  reviewTitle: { fontSize: 24, fontWeight: '800', marginBottom: 20 },
  statsCard: { width: '100%', borderRadius: 16, borderWidth: 1, padding: 20, marginBottom: 24 },
  statRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  statLabel: { fontSize: 15, fontWeight: '500' },
  statValue: { fontSize: 17, fontWeight: '700' },
});
