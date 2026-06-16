import { SafeAreaView, ScrollView, Text, StyleSheet, View, FlatList, TouchableOpacity, TextInput, Modal, Alert, ActivityIndicator, RefreshControl, Platform, KeyboardAvoidingView } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { supabase } from '../lib/supabase';
import { useState, useEffect, useCallback, useRef } from 'react';
import Header from '../components/Header';
import { Stack } from 'expo-router';
import CircleProgress from '../components/CircleProgress';
import BondTimeline from '../components/BondTimeline';
import { Shield, Heart, Handshake, Brain, Smile, Link, Target, Plus, Trash2, X } from 'lucide-react-native';

interface Goal { id: string; title: string; status: string; progress: number; category: string; deadline: string|null; created_at: string; }

export default function Relationship() {
  const { lang, theme, relationshipDims, bondLevel, journeyPhase, attachmentStyle, userId } = useTwinStore();
  const isAr = lang === 'ar'; const isDark = theme === 'dark';
  const t = (ar:string,en:string)=>isAr?ar:en;
  const bg = isDark ? '#1A1A1A' : '#F8F6F2'; const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#888' : '#666'; const card = isDark ? '#2A2A2A' : '#FFF'; const border = isDark ? '#444' : '#F0F0F0';

  const [goals, setGoals] = useState<Goal[]>([]);
  const [goalsLoading, setGoalsLoading] = useState(true);
  const [goalsRefreshing, setGoalsRefreshing] = useState(false);
  const [showAddGoal, setShowAddGoal] = useState(false);
  const [newGoalTitle, setNewGoalTitle] = useState('');
  const [saving, setSaving] = useState(false);
  const cancelledRef = useRef(false);

  const fetchGoals = useCallback(async (showRefresh=false)=>{
    if(!userId){ setGoalsLoading(false); return; }
    if(showRefresh) setGoalsRefreshing(true); else setGoalsLoading(true);
    try {
      const { data, error } = await supabase.from('goals').select('*').eq('user_id',userId).order('created_at',{ascending:false});
      if(cancelledRef.current) return;
      if(error) throw error;
      setGoals(data||[]);
    } catch(e){ console.error('Goals error:',e); }
    finally { if(!cancelledRef.current){ setGoalsLoading(false); setGoalsRefreshing(false); } }
  },[userId]);

  useEffect(()=>{ cancelledRef.current=false; fetchGoals(); return ()=>{cancelledRef.current=true;}; },[fetchGoals]);

  const handleAddGoal = async ()=>{
    if(!newGoalTitle.trim()){ Alert.alert(t('خطأ','Error'),t('أدخل عنوان الهدف','Enter goal title')); return; }
    setSaving(true);
    try {
      const { data, error } = await supabase.from('goals').insert({user_id:userId,title:newGoalTitle.trim(),status:'active',progress:0}).select().single();
      if(error) throw error;
      if(data) setGoals(prev=>[data,...prev]);
      setNewGoalTitle(''); setShowAddGoal(false);
    } catch(e){ Alert.alert(t('خطأ','Error'),t('فشل إضافة الهدف','Failed to add goal')); }
    finally { setSaving(false); }
  };

  const deleteGoal = async (goalId:string)=>{
    Alert.alert(t('حذف','Delete'),t('هل أنت متأكد؟','Are you sure?'),[ {text:t('إلغاء','Cancel'),style:'cancel'}, {text:t('حذف','Delete'),style:'destructive',onPress:async()=>{ await supabase.from('goals').delete().eq('id',goalId); setGoals(prev=>prev.filter(g=>g.id!==goalId)); }} ]);
  };

  const dimensions = [
    { key: 'trust', label_ar: 'ثقة', label_en: 'Trust', icon: Shield, color: '#3B82F6' },
    { key: 'affection', label_ar: 'مودة', label_en: 'Affection', icon: Heart, color: '#EC4899' },
    { key: 'support', label_ar: 'دعم', label_en: 'Support', icon: Handshake, color: '#10B981' },
    { key: 'empathy', label_ar: 'تفهم', label_en: 'Empathy', icon: Brain, color: '#8B5CF6' },
    { key: 'humor', label_ar: 'فكاهة', label_en: 'Humor', icon: Smile, color: '#F59E0B' },
    { key: 'dependency', label_ar: 'اعتمادية', label_en: 'Dependency', icon: Link, color: '#6366F1' },
  ];

  const phaseLabels: Record<string, string> = { introduction: 'تعارف', trust_building: 'بناء ثقة', deepening: 'تعمق', growth: 'نمو', mature: 'نضج' };
  const attachmentLabels: Record<string, string> = { secure: 'آمن', anxious: 'قلق', avoidant: 'متجنب', disorganized: 'غير منظم', unknown: 'غير معروف' };

  return (
    <SafeAreaView style={[s.safe, { backgroundColor: bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header />
      
      <ScrollView contentContainerStyle={s.container} refreshControl={<RefreshControl refreshing={goalsRefreshing} onRefresh={()=>fetchGoals(true)} colors={['#6B21A8']}/>}>
        {/* ملخص العلاقة */}
        <View style={[s.summaryCard, { backgroundColor: card, borderColor: border }]}>
          <View style={s.summaryRow}>
            <View style={s.summaryItem}><Text style={[s.summaryValue, { color: '#EC4899' }]}>{Math.round(bondLevel)}%</Text><Text style={[s.summaryLabel, { color: sub }]}>{isAr ? 'الرابطة' : 'Bond'}</Text></View>
            <View style={s.summaryItem}><Text style={[s.summaryValue, { color: '#10B981' }]}>{phaseLabels[journeyPhase] || journeyPhase}</Text><Text style={[s.summaryLabel, { color: sub }]}>{isAr ? 'المرحلة' : 'Phase'}</Text></View>
            <View style={s.summaryItem}><Text style={[s.summaryValue, { color: '#8B5CF6' }]}>{attachmentLabels[attachmentStyle] || attachmentStyle}</Text><Text style={[s.summaryLabel, { color: sub }]}>{isAr ? 'التعلق' : 'Attachment'}</Text></View>
          </View>
        </View>

        <BondTimeline />

        {/* أبعاد العلاقة */}
        <Text style={[s.sectionTitle, { color: txt }]}>{isAr ? 'أبعاد العلاقة' : 'Relationship Dimensions'}</Text>
        <View style={s.grid}>
          {dimensions.map((d) => {
            const Icon = d.icon;
            const value = (relationshipDims as any)[d.key] || 0;
            return (
              <View key={d.key} style={s.circleWrap}>
                <CircleProgress percentage={value} color={d.color} size={80} label={isAr ? d.label_ar : d.label_en} icon={<Icon size={18} stroke={d.color} />} trackColor={isDark ? '#444' : '#E8E8E3'} />
              </View>
            );
          })}
        </View>

        {/* قسم الأهداف */}
        <View style={[s.sectionHeader, { marginTop: 20 }]}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
            <Target size={20} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
            <Text style={[s.sectionTitle, { color: txt, marginBottom: 0 }]}>{isAr ? 'أهداف النمو 🎯' : 'Growth Goals 🎯'}</Text>
          </View>
          <TouchableOpacity style={s.addGoalBtn} onPress={()=>setShowAddGoal(true)}>
            <Plus size={18} stroke="#FFF" />
          </TouchableOpacity>
        </View>

        {goalsLoading ? <ActivityIndicator size="small" color="#6B21A8" style={{ marginTop: 20 }} /> :
          goals.length === 0 ? (
            <View style={{ alignItems: 'center', marginTop: 20, padding: 20 }}>
              <Target size={36} stroke={sub} />
              <Text style={{ color: sub, fontSize: 14, marginTop: 8, textAlign: 'center' }}>{isAr ? 'لا توجد أهداف بعد. أضف هدفك الأول!' : 'No goals yet. Add your first goal!'}</Text>
            </View>
          ) : (
            <View style={{ marginTop: 12, gap: 8 }}>
              {goals.map((goal) => (
                <View key={goal.id} style={[s.goalCard, { backgroundColor: card, borderColor: border }]}>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text style={[s.goalTitle, { color: txt }]}>{goal.title}</Text>
                    <TouchableOpacity onPress={()=>deleteGoal(goal.id)}><Trash2 size={14} stroke={sub} /></TouchableOpacity>
                  </View>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 8 }}>
                    <View style={[s.goalProgressBar, { backgroundColor: isDark ? '#444' : '#F0F0F0' }]}>
                      <View style={[s.goalProgressFill, { width: `${goal.progress}%`, backgroundColor: '#6B21A8' }]} />
                    </View>
                    <Text style={[s.goalProgressText, { color: sub }]}>{goal.progress}%</Text>
                  </View>
                </View>
              ))}
            </View>
          )
        }
      </ScrollView>

      {/* Modal إضافة هدف */}
      <Modal visible={showAddGoal} transparent animationType="fade" onRequestClose={()=>setShowAddGoal(false)}>
        <KeyboardAvoidingView behavior={Platform.OS==='ios'?'padding':'height'} style={s.modalOverlay}>
          <View style={[s.modalContent, isDark && { backgroundColor: '#2A2A2A' }]}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <Text style={[s.modalTitle, { color: txt }]}>{isAr ? 'هدف جديد' : 'New Goal'}</Text>
              <TouchableOpacity onPress={()=>setShowAddGoal(false)}><X size={22} stroke={sub}/></TouchableOpacity>
            </View>
            <TextInput style={[s.goalInput, { backgroundColor: isDark ? '#333' : '#F8F6F2', color: txt, borderColor: isDark ? '#444' : '#E0D9F5' }]} placeholder={isAr ? 'ماذا تريد أن تحقق؟' : 'What do you want to achieve?'} placeholderTextColor={sub} value={newGoalTitle} onChangeText={setNewGoalTitle} autoFocus/>
            <TouchableOpacity style={[s.saveGoalBtn, { opacity: saving ? 0.6 : 1 }]} onPress={handleAddGoal} disabled={saving}>
              {saving ? <ActivityIndicator color="#FFF"/> : <Text style={{ color: '#FFF', fontWeight: '700' }}>{isAr ? 'حفظ' : 'Save'}</Text>}
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1 }, container: { padding: 20, paddingBottom: 40 },
  summaryCard: { padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 16 },
  summaryRow: { flexDirection: 'row', justifyContent: 'space-around' },
  summaryItem: { alignItems: 'center' },
  summaryValue: { fontSize: 20, fontWeight: '800' },
  summaryLabel: { fontSize: 11, marginTop: 2 },
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
