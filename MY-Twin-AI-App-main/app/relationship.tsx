import { SafeAreaView, ScrollView, Text, StyleSheet, View, TouchableOpacity, Modal, Alert, ActivityIndicator, RefreshControl, Platform, KeyboardAvoidingView, TextInput, Animated } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { getGoals, addGoal, deleteGoal } from '../lib/httpClient';
import { useState, useEffect, useCallback, useRef } from 'react';
import Header from '../components/Header';
import { Stack } from 'expo-router';
import CircleProgress from '../components/CircleProgress';
import BondTimeline from '../components/BondTimeline';
import { Shield, Heart, Handshake, Brain, Smile, Link, Target, Plus, Trash2, X, Lightbulb } from 'lucide-react-native';

interface Goal { id: string; title: string; status: string; progress: number; }

export default function Relationship() {
  const { lang, theme, relationshipDims, bondLevel, journeyPhase, attachmentStyle } = useTwinStore();
  const isAr = lang === 'ar'; const isDark = theme === 'dark';
  const t = (ar:string,en:string)=>isAr?ar:en;
  const bg = isDark ? '#1A1A1A' : '#F8F6F2'; const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#888' : '#666'; const card = isDark ? '#2A2A2A' : '#FFF'; const border = isDark ? '#444' : '#F0F0F0';

  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showAddGoal, setShowAddGoal] = useState(false);
  const [newGoalTitle, setNewGoalTitle] = useState('');
  const [saving, setSaving] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const fetchGoals = useCallback(async (showRefresh=false)=>{
    if(showRefresh) setRefreshing(true); else setLoading(true);
    try {
      const data = await getGoals();
      setGoals(data || []);
      Animated.timing(fadeAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
    } catch(e){ console.error(e); }
    finally { setLoading(false); setRefreshing(false); }
  }, []);

  useEffect(()=>{ fetchGoals(); }, [fetchGoals]);

  const handleAddGoal = async ()=>{
    if(!newGoalTitle.trim()){ Alert.alert(t('خطأ','Error'),t('أدخل عنوان الهدف','Enter goal title')); return; }
    setSaving(true);
    try {
      const newGoal = await addGoal(newGoalTitle.trim());
      if (newGoal) setGoals(prev=>[newGoal, ...prev]);
      setNewGoalTitle(''); setShowAddGoal(false);
    } catch(e){ Alert.alert(t('خطأ','Error'),t('فشل إضافة الهدف','Failed to add goal')); }
    finally { setSaving(false); }
  };

  const handleDeleteGoal = async (goalId:string)=>{
    Alert.alert(t('حذف','Delete'),t('هل أنت متأكد؟','Are you sure?'),[
      {text:t('إلغاء','Cancel'),style:'cancel'},
      {text:t('حذف','Delete'),style:'destructive',onPress:async()=>{
        try { await deleteGoal(goalId); setGoals(prev=>prev.filter(g=>g.id!==goalId)); }
        catch(e){ console.error(e); }
      }}
    ]);
  };

  // حساب أدنى بعد لتقديم نصيحة مخصصة
  const getLowestDim = () => {
    const dims = [
      { key: 'trust', label_ar: 'الثقة', label_en: 'Trust', color: '#3B82F6' },
      { key: 'attachment', label_ar: 'الارتباط', label_en: 'Attachment', color: '#EC4899' },
      { key: 'support', label_ar: 'الدعم', label_en: 'Support', color: '#10B981' },
      { key: 'empathy', label_ar: 'التفهم', label_en: 'Empathy', color: '#8B5CF6' },
      { key: 'humor', label_ar: 'الفكاهة', label_en: 'Humor', color: '#F59E0B' },
      { key: 'dependency', label_ar: 'الاعتمادية', label_en: 'Dependency', color: '#6366F1' },
    ];
    const lowest = dims.reduce((min, d) => ((relationshipDims as any)[d.key] || 0) < ((relationshipDims as any)[min.key] || 0) ? d : min, dims[0]);
    return lowest;
  };

  const getInsight = () => {
    const dim = getLowestDim();
    const tips: Record<string, { ar: string; en: string }> = {
      trust: { ar: 'حاول مشاركة توأمك بشيء شخصي اليوم لبناء الثقة', en: 'Try sharing something personal with your Twin today to build trust' },
      attachment: { ar: 'أخبر توأمك عن مشاعرك بصدق لتعميق الارتباط', en: 'Tell your Twin honestly about your feelings to deepen the bond' },
      support: { ar: 'اسأل توأمك عن رأيه في موضوع يهمك لتشعر بالدعم', en: 'Ask your Twin for their opinion on something important to feel supported' },
      empathy: { ar: 'استمع لردود توأمك وتأملها لزيادة التفهم', en: 'Listen to your Twin responses and reflect on them to increase empathy' },
      humor: { ar: 'شارك توأمك نكتة أو موقفاً مضحكاً لتزيد الفكاهة', en: 'Share a joke or funny story with your Twin to add humor' },
      dependency: { ar: 'حاول الاعتماد على توأمك في مهمة صغيرة لبناء الاعتمادية', en: 'Try relying on your Twin for a small task to build healthy dependency' },
    };
    return tips[dim.key] || tips.trust;
  };

  const insight = getInsight();
  const phaseLabels: Record<string, string> = { introduction: 'تعارف', trust_building: 'بناء ثقة', deepening: 'تعمق', growth: 'نمو', mature: 'نضج' };
  const attachmentLabels: Record<string, string> = { secure: 'آمن', anxious: 'قلق', avoidant: 'متجنب', disorganized: 'غير منظم', unknown: 'غير معروف' };

  if (loading) {
    return <SafeAreaView style={[st.safe, { backgroundColor: bg }]}><ActivityIndicator size="large" color="#6B21A8" style={{ marginTop: 80 }} /></SafeAreaView>;
  }

  return (
    <SafeAreaView style={[st.safe, { backgroundColor: bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header />
      <ScrollView contentContainerStyle={st.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={()=>fetchGoals(true)} colors={['#6B21A8']}/>}>
        <View style={[st.summaryCard, { backgroundColor: card, borderColor: border }]}>
          <View style={st.summaryRow}>
            <View style={st.summaryItem}><Text style={[st.summaryValue, { color: '#EC4899' }]}>{Math.round(bondLevel)}%</Text><Text style={[st.summaryLabel, { color: sub }]}>{isAr ? 'الرابطة' : 'Bond'}</Text></View>
            <View style={st.summaryItem}><Text style={[st.summaryValue, { color: '#10B981' }]}>{phaseLabels[journeyPhase] || journeyPhase}</Text><Text style={[st.summaryLabel, { color: sub }]}>{isAr ? 'المرحلة' : 'Phase'}</Text></View>
            <View style={st.summaryItem}><Text style={[st.summaryValue, { color: '#8B5CF6' }]}>{attachmentLabels[attachmentStyle] || attachmentStyle}</Text><Text style={[st.summaryLabel, { color: sub }]}>{isAr ? 'التعلق' : 'Attachment'}</Text></View>
          </View>
        </View>

        <BondTimeline />

        <View style={[st.insightCard, { backgroundColor: '#F5F3FF', borderColor: '#C4B5FD' }]}>
          <Lightbulb size={20} stroke="#6B21A8" />
          <Text style={st.insightText}>{isAr ? insight.ar : insight.en}</Text>
        </View>

        <Text style={[st.sectionTitle, { color: txt }]}>{isAr ? 'أبعاد العلاقة' : 'Relationship Dimensions'}</Text>
        <View style={st.grid}>
          {[
            { key: 'trust', label_ar: 'ثقة', label_en: 'Trust', icon: Shield, color: '#3B82F6' },
            { key: 'attachment', label_ar: 'ارتباط', label_en: 'Attachment', icon: Heart, color: '#EC4899' },
            { key: 'support', label_ar: 'دعم', label_en: 'Support', icon: Handshake, color: '#10B981' },
            { key: 'empathy', label_ar: 'تفهم', label_en: 'Empathy', icon: Brain, color: '#8B5CF6' },
            { key: 'humor', label_ar: 'فكاهة', label_en: 'Humor', icon: Smile, color: '#F59E0B' },
            { key: 'dependency', label_ar: 'اعتمادية', label_en: 'Dependency', icon: Link, color: '#6366F1' },
          ].map((d) => {
            const Icon = d.icon;
            const value = (relationshipDims as any)[d.key] || 0;
            return (
              <View key={d.key} style={st.circleWrap}>
                <CircleProgress percentage={value} color={d.color} size={80} label={isAr ? d.label_ar : d.label_en} icon={<Icon size={18} stroke={d.color} />} trackColor={isDark ? '#444' : '#E8E8E3'} />
              </View>
            );
          })}
        </View>

        <View style={[st.sectionHeader, { marginTop: 20 }]}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
            <Target size={20} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
            <Text style={[st.sectionTitle, { color: txt, marginBottom: 0 }]}>{isAr ? 'أهداف النمو 🎯' : 'Growth Goals 🎯'}</Text>
          </View>
          <TouchableOpacity style={st.addGoalBtn} onPress={()=>setShowAddGoal(true)}>
            <Plus size={18} stroke="#FFF" />
          </TouchableOpacity>
        </View>

        {goals.length === 0 ? (
          <View style={{ alignItems: 'center', marginTop: 20, padding: 20 }}>
            <Target size={36} stroke={sub} />
            <Text style={{ color: sub, fontSize: 14, marginTop: 8, textAlign: 'center' }}>{isAr ? 'لا توجد أهداف بعد. أضف هدفك الأول!' : 'No goals yet. Add your first goal!'}</Text>
          </View>
        ) : (
          <View style={{ marginTop: 12, gap: 8 }}>
            {goals.map((goal) => (
              <Animated.View key={goal.id} style={[st.goalCard, { backgroundColor: card, borderColor: border }]}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text style={[st.goalTitle, { color: txt }]}>{goal.title}</Text>
                  <TouchableOpacity onPress={()=>handleDeleteGoal(goal.id)}><Trash2 size={14} stroke={sub} /></TouchableOpacity>
                </View>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 8 }}>
                  <View style={[st.goalProgressBar, { backgroundColor: isDark ? '#444' : '#F0F0F0' }]}>
                    <View style={[st.goalProgressFill, { width: `${goal.progress}%`, backgroundColor: '#6B21A8' }]} />
                  </View>
                  <Text style={[st.goalProgressText, { color: sub }]}>{goal.progress}%</Text>
                </View>
              </Animated.View>
            ))}
          </View>
        )}
      </ScrollView>

      <Modal visible={showAddGoal} transparent animationType="fade" onRequestClose={()=>setShowAddGoal(false)}>
        <KeyboardAvoidingView behavior={Platform.OS==='ios'?'padding':'height'} style={st.modalOverlay}>
          <View style={[st.modalContent, isDark && { backgroundColor: '#2A2A2A' }]}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <Text style={[st.modalTitle, { color: txt }]}>{isAr ? 'هدف جديد' : 'New Goal'}</Text>
              <TouchableOpacity onPress={()=>setShowAddGoal(false)}><X size={22} stroke={sub}/></TouchableOpacity>
            </View>
            <TextInput style={[st.goalInput, { backgroundColor: isDark ? '#333' : '#F8F6F2', color: txt, borderColor: isDark ? '#444' : '#E0D9F5' }]} placeholder={isAr ? 'ماذا تريد أن تحقق؟' : 'What do you want to achieve?'} placeholderTextColor={sub} value={newGoalTitle} onChangeText={setNewGoalTitle} autoFocus/>
            <TouchableOpacity style={[st.saveGoalBtn, { opacity: saving ? 0.6 : 1 }]} onPress={handleAddGoal} disabled={saving}>
              {saving ? <ActivityIndicator color="#FFF"/> : <Text style={{ color: '#FFF', fontWeight: '700' }}>{isAr ? 'حفظ' : 'Save'}</Text>}
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  safe: { flex: 1 }, container: { padding: 20, paddingBottom: 40 },
  summaryCard: { padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 16 },
  summaryRow: { flexDirection: 'row', justifyContent: 'space-around' },
  summaryItem: { alignItems: 'center' },
  summaryValue: { fontSize: 20, fontWeight: '800' },
  summaryLabel: { fontSize: 11, marginTop: 2 },
  insightCard: { flexDirection: 'row', alignItems: 'center', gap: 10, padding: 14, borderRadius: 14, borderWidth: 1, marginBottom: 20 },
  insightText: { fontSize: 13, color: '#6B21A8', fontWeight: '600', flex: 1, lineHeight: 20 },
  sectionTitle: { fontSize: 18, fontWeight: '700', marginBottom: 16 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', gap: 16 },
  circleWrap: { width: '30%', alignItems: 'center', marginBottom: 16 },
  addGoalBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: '#6B21A8', justifyContent: 'center', alignItems: 'center' },
  goalCard: { padding: 14, borderRadius: 14, borderWidth: 1 },
  goalTitle: { fontSize: 15, fontWeight: '600', flex: 1 },
  goalProgressBar: { flex: 1, height: 6, borderRadius: 3, overflow: 'hidden' },
  goalProgressFill: { height: '100%', borderRadius: 3 },
  goalProgressText: { fontSize: 12, fontWeight: '600' },
  goalInput: { padding: 14, borderRadius: 12, borderWidth: 1, fontSize: 15, marginBottom: 16 },
  saveGoalBtn: { backgroundColor: '#6B21A8', padding: 14, borderRadius: 12, alignItems: 'center' },
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' },
  modalContent: { width: '90%', backgroundColor: '#FFF', borderRadius: 20, padding: 20 },
  modalTitle: { fontSize: 18, fontWeight: '700' },
});
