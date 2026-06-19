import { SafeAreaView, View, Text, TouchableOpacity, StyleSheet, ScrollView, Animated, Alert, ActivityIndicator, TextInput, Modal } from 'react-native';
import { useState, useRef, useEffect } from 'react';
import { router } from 'expo-router';
import { useTwinStore, TwinGender } from '../store/useTwinStore';
import { completeOnboarding } from '../lib/httpClient';
import { Sparkles, ArrowLeft, ArrowRight, Check, Volume2 } from 'lucide-react-native';

const QUESTIONS = {
  ar: [
    { id:'1', q:'عندما تواجه مشكلة كبيرة، كيف تتعامل معها عادةً؟', options:['أحللها بهدوء','أثق بحدسي','أطلب المساعدة','أتجنبها مؤقتاً'] },
    { id:'2', q:'ما هو أكثر شيء يدفعك للاستمرار في الحياة؟', options:['تحقيق إنجاز','قضاء وقت مع الأحباء','النجاح المهني','تحقيق السلام الداخلي'] },
    { id:'3', q:'أي نوع من العلاقات تشعر أنه الأقرب لقلبك؟', options:['مستقرة وداعمة','مليئة بالمغامرات','مع العائلة والأصدقاء','أفضل الاعتماد على نفسي'] },
    { id:'4', q:'كيف تصف يومك المثالي؟', options:['منجزاً ومليئاً بالمهام','في الطبيعة أو أسترخي','مع العائلة والأصدقاء','أستمتع بها لكن أحتاج مساحتي'] },
    { id:'5', q:'ما هو أكبر خوف يراودك أحياناً؟', options:['الفشل في تحقيق أهدافي','أحياناً أقلق من فقدانهم','عدم تحقيق تأثير في العالم','أخشى فقدان استقلاليتي'] },
    { id:'6', q:'عندما تشعر بالضغط، ما هو أول شيء تفعله؟', options:['أبحث عن حل مباشر','أتحدث مع أحدهم','أشغل نفسي بشيء آخر','أبقى وحدي لأفكر'] },
    { id:'7', q:'ما هي القيمة الأكثر أهمية بالنسبة لك؟', options:['الذكاء والدهاء','السعادة العائلية','التأثير في العالم','الحرية الشخصية'] },
  ],
  en: [
    { id:'1', q:'When facing a big problem, how do you usually handle it?', options:['Analyze it calmly','Trust my intuition','Ask for help','Avoid it temporarily'] },
    { id:'2', q:'What drives you most to keep going in life?', options:['Achieving a goal','Spending time with loved ones','Professional success','Achieving inner peace'] },
    { id:'3', q:'Which type of relationship feels closest to your heart?', options:['Stable and supportive','Full of adventures','With family and friends','I prefer to rely on myself'] },
    { id:'4', q:'How would you describe your perfect day?', options:['Productive and full of tasks','In nature or relaxing','With family and friends','I enjoy them but need my space'] },
    { id:'5', q:'What is your biggest fear sometimes?', options:['Failure to achieve my goals','Sometimes I worry about losing them','Not making an impact on the world','Losing my independence'] },
    { id:'6', q:'When you feel stressed, what is the first thing you do?', options:['Look for a direct solution','Talk to someone','Distract myself with something else','Stay alone to think'] },
    { id:'7', q:'What is the most important value to you?', options:['Intelligence and cleverness','Family happiness','Making an impact on the world','Personal freedom'] },
  ],
};

export default function Onboarding() {
  const { userId, twinName, twinGender, setTwinName, setTwinGender, addMessage, lang, theme } = useTwinStore();
  const isAr = lang === 'ar'; const isDark = theme === 'dark';
  const questions = QUESTIONS[lang as keyof typeof QUESTIONS] || QUESTIONS['ar'];
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [userName, setUserName] = useState('');
  const [freeInfo, setFreeInfo] = useState('');
  const [newTwinName, setNewTwinName] = useState(twinName || (isAr ? 'توأمك' : 'Your Twin'));
  const [newTwinGender, setNewTwinGender] = useState<TwinGender>(twinGender || 'female');
  const [loading, setLoading] = useState(false);
  const fadeAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => { Animated.timing(fadeAnim, { toValue: 1, duration: 200, useNativeDriver: true }).start(); }, [step]);

  const handleAnswer = (qId: string, opt: string) => {
    setAnswers(prev => ({ ...prev, [qId]: opt }));
    if (step < questions.length - 1) {
      Animated.timing(fadeAnim, { toValue: 0, duration: 100, useNativeDriver: true }).start(() => setStep(prev => prev + 1));
    }
  };

  const handleBack = () => { if (step > 0) { Animated.timing(fadeAnim, { toValue: 0, duration: 100, useNativeDriver: true }).start(() => setStep(prev => prev - 1)); } };
  const handleSkip = () => setStep(questions.length - 1);

  const handleFinalSubmit = async () => {
    if (!userName.trim()) { Alert.alert(isAr ? 'تنبيه' : 'Notice', isAr ? 'من فضلك أدخل اسمك' : 'Please enter your name'); return; }
    setLoading(true);
    try {
      await completeOnboarding({
        answers,
        lang,
        userName: userName.trim(),
        twinName: newTwinName.trim(),
        twinGender: newTwinGender,
        freeInfo,
      });
      setTwinName(newTwinName.trim() || (isAr ? 'توأمك' : 'Your Twin'));
      setTwinGender(newTwinGender);
      addMessage({ role: 'twin', content: isAr ? `🎯 مرحباً ${userName.trim()}!\n\nأنا ${newTwinName.trim() || 'توأمك'} 💜` : `🎯 Welcome ${userName.trim()}!\n\nI'm ${newTwinName.trim() || 'Your Twin'} 💜`, id: Date.now().toString(), timestamp: Date.now() });
      router.replace('/chat');
    } catch (e: any) { Alert.alert(isAr ? 'خطأ' : 'Error', e.message); }
    finally { setLoading(false); }
  };

  const currentQ = questions[step];
  const isLastStep = step === questions.length - 1;

  return (
    <SafeAreaView style={[styles.safe, isDark && { backgroundColor: '#1A1A1A' }]}>
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <Animated.View style={[styles.card, isDark && { backgroundColor: '#2A2A2A', borderColor: '#444' }, { opacity: fadeAnim }]}>
          <View style={styles.headerRow}>
            <View style={styles.progressBar}>{questions.map((_, i) => (<View key={i} style={[styles.dot, i <= step && styles.dotActive]} />))}</View>
            {!isLastStep && (<TouchableOpacity onPress={handleSkip} style={styles.skipBtn}><Text style={[styles.skipText, isDark && { color: '#D8B4FE' }]}>{isAr ? 'تخطي' : 'Skip'}</Text><ArrowRight size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} /></TouchableOpacity>)}
          </View>
          {!isLastStep ? (<>
            <Sparkles size={40} stroke={isDark ? '#D8B4FE' : '#6B21A8'} style={{ alignSelf:'center', marginBottom:20 }} />
            <Text style={[styles.question, isDark && { color:'#FFF' }]}>{currentQ.q}</Text>
            {currentQ.options.map((opt, i) => (<TouchableOpacity key={i} style={[styles.option, answers[currentQ.id]===opt && styles.selectedOption, isDark && { borderColor:'#444' }]} onPress={() => handleAnswer(currentQ.id, opt)}><Text style={[styles.optionText, isDark && { color:'#CCC' }]}>{opt}</Text></TouchableOpacity>))}
            {step > 0 && (<TouchableOpacity style={styles.backBtn} onPress={handleBack}><ArrowLeft size={18} stroke={isDark ? '#D8B4FE' : '#6B21A8'} /><Text style={[styles.backText, isDark && { color: '#D8B4FE' }]}>{isAr ? 'رجوع' : 'Back'}</Text></TouchableOpacity>)}
          </>) : (<>
            <Sparkles size={48} stroke={isDark ? '#D8B4FE' : '#6B21A8'} style={{ alignSelf:'center', marginBottom:20 }} />
            <Text style={[styles.title, isDark && { color:'#FFF' }]}>{isAr ? 'خطوة أخيرة!' : 'Final Step!'}</Text>
            <Text style={[styles.label, isDark && { color:'#CCC' }]}>{isAr ? 'ما اسمك؟' : 'What is your name?'}</Text>
            <TextInput style={[styles.input, isDark && { backgroundColor:'#333', color:'#FFF', borderColor:'#444' }]} placeholder={isAr ? 'أدخل اسمك' : 'Enter your name'} placeholderTextColor="#999" value={userName} onChangeText={setUserName} />
            <Text style={[styles.label, isDark && { color:'#CCC' }]}>{isAr ? 'ماذا تريد أن تسمي توأمك؟' : 'What would you name your Twin?'}</Text>
            <TextInput style={[styles.input, isDark && { backgroundColor:'#333', color:'#FFF', borderColor:'#444' }]} placeholder={isAr ? 'اسم التوأم' : 'Twin name'} placeholderTextColor="#999" value={newTwinName} onChangeText={setNewTwinName} />
            <Text style={[styles.label, isDark && { color:'#CCC' }]}>{isAr ? 'اختر صوت توأمك' : 'Choose Twin Voice'}</Text>
            <View style={styles.genderRow}>
              <TouchableOpacity style={[styles.genderBtn, newTwinGender==='female' && styles.genderBtnActive]} onPress={() => setNewTwinGender('female')}><Text style={styles.genderEmoji}>♀️</Text><Volume2 size={20} stroke={newTwinGender==='female' ? '#6B21A8' : '#999'} /><Text style={[styles.genderText, newTwinGender==='female' && styles.genderTextActive]}>{isAr ? 'أنثى' : 'Female'}</Text></TouchableOpacity>
              <TouchableOpacity style={[styles.genderBtn, newTwinGender==='male' && styles.genderBtnActive]} onPress={() => setNewTwinGender('male')}><Text style={styles.genderEmoji}>♂️</Text><Volume2 size={20} stroke={newTwinGender==='male' ? '#6B21A8' : '#999'} /><Text style={[styles.genderText, newTwinGender==='male' && styles.genderTextActive]}>{isAr ? 'ذكر' : 'Male'}</Text></TouchableOpacity>
            </View>
            <Text style={[styles.label, isDark && { color:'#CCC' }]}>{isAr ? 'أخبرني عن نفسك (اختياري)' : 'Tell me about yourself (optional)'}</Text>
            <TextInput style={[styles.textArea, isDark && { backgroundColor:'#333', color:'#FFF', borderColor:'#444' }]} placeholder={isAr ? 'اكتب بحرية...' : 'Write freely...'} placeholderTextColor="#999" value={freeInfo} onChangeText={setFreeInfo} multiline numberOfLines={4} />
            <TouchableOpacity style={[styles.submitBtn, (!userName.trim() || loading) && { opacity:0.6 }]} onPress={handleFinalSubmit} disabled={!userName.trim() || loading}>
              {loading ? <ActivityIndicator color="#FFF" /> : (<><Check size={20} stroke="#FFF" /><Text style={styles.submitText}>{isAr ? 'ابدأ رحلتك' : 'Start Your Journey'}</Text></>)}
            </TouchableOpacity>
          </>)}
        </Animated.View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 }, scroll: { flexGrow: 1, justifyContent: 'center', padding: 20 },
  card: { backgroundColor: '#FFF', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#F0F0F0', elevation: 2 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  progressBar: { flexDirection: 'row', gap: 6 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#E0D9F5' },
  dotActive: { backgroundColor: '#6B21A8', width: 24 },
  skipBtn: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  skipText: { color: '#6B21A8', fontWeight: '600', fontSize: 14 },
  question: { fontSize: 18, fontWeight: '700', color: '#1A1A1A', textAlign: 'center', marginBottom: 20 },
  option: { padding: 16, borderRadius: 12, borderWidth: 1.5, borderColor: '#E0D9F5', marginBottom: 10 },
  selectedOption: { borderColor: '#6B21A8', backgroundColor: '#F3F0FF' },
  optionText: { fontSize: 15, color: '#1A1A1A', textAlign: 'center' },
  backBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginTop: 16, gap: 6 },
  backText: { color: '#6B21A8', fontWeight: '600' },
  title: { fontSize: 22, fontWeight: '800', color: '#1A1A1A', textAlign: 'center', marginBottom: 16 },
  label: { fontSize: 14, fontWeight: '600', color: '#666', marginBottom: 8, marginTop: 12 },
  input: { backgroundColor: '#F8F6F2', borderRadius: 12, padding: 14, fontSize: 15, color: '#1A1A1A', borderWidth: 1, borderColor: '#E0D9F5', marginBottom: 8 },
  genderRow: { flexDirection: 'row', gap: 12, marginBottom: 8 },
  genderBtn: { flex: 1, padding: 16, borderRadius: 12, borderWidth: 1.5, borderColor: '#E0D9F5', alignItems: 'center', gap: 8 },
  genderBtnActive: { borderColor: '#6B21A8', backgroundColor: '#F3F0FF' },
  genderEmoji: { fontSize: 24 },
  genderText: { fontSize: 15, fontWeight: '600', color: '#666' },
  genderTextActive: { color: '#6B21A8' },
  textArea: { backgroundColor: '#F8F6F2', borderRadius: 12, padding: 14, fontSize: 15, color: '#1A1A1A', borderWidth: 1, borderColor: '#E0D9F5', minHeight: 100, textAlignVertical: 'top', marginBottom: 20 },
  submitBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#6B21A8', padding: 16, borderRadius: 12, gap: 8 },
  submitText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
});
