import { SafeAreaView, View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, Modal, Alert, ActivityIndicator, RefreshControl, Platform, KeyboardAvoidingView } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { supabase } from '../lib/supabase';
import { useState, useEffect, useCallback, useRef } from 'react';
import { Target, Plus, Trash2, X, Sparkles } from 'lucide-react-native';

interface Goal { id: string; title: string; status: string; progress: number; category: string; deadline: string|null; created_at: string; }

const CATEGORIES: Record<string,{icon:string;color:string;label_ar:string;label_en:string}> = {
  health:{icon:'❤️',color:'#EF4444',label_ar:'صحة',label_en:'Health'},
  learning:{icon:'📚',color:'#3B82F6',label_ar:'تعلم',label_en:'Learning'},
  finance:{icon:'💰',color:'#10B981',label_ar:'مال',label_en:'Finance'},
  relationships:{icon:'👥',color:'#EC4899',label_ar:'علاقات',label_en:'Relationships'},
  personal:{icon:'🧠',color:'#8B5CF6',label_ar:'تطوير ذات',label_en:'Personal'},
  career:{icon:'💼',color:'#F59E0B',label_ar:'عمل',label_en:'Career'},
  creative:{icon:'🎨',color:'#6366F1',label_ar:'إبداع',label_en:'Creative'},
  other:{icon:'🎯',color:'#6B21A8',label_ar:'أخرى',label_en:'Other'},
};

export default function Goals() {
  const { lang, theme, userId } = useTwinStore();
  const isAr = lang==='ar'; const isDark = theme==='dark';
  const t = (ar:string,en:string)=>isAr?ar:en;
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [saving, setSaving] = useState(false);
  const cancelledRef = useRef(false);

  const fetchGoals = useCallback(async (showRefresh=false)=>{
    if(!userId){ setLoading(false); return; }
    if(showRefresh) setRefreshing(true); else setLoading(true);
    try {
      const { data, error } = await supabase.from('goals').select('*').eq('user_id',userId).order('created_at',{ascending:false});
      if(cancelledRef.current) return;
      if(error) throw error;
      setGoals(data||[]);
    } catch(e){ console.error('Goals error:',e); }
    finally { if(!cancelledRef.current){ setLoading(false); setRefreshing(false); } }
  },[userId]);

  useEffect(()=>{ cancelledRef.current=false; fetchGoals(); return ()=>{cancelledRef.current=true;}; },[fetchGoals]);

  const handleAddGoal = async ()=>{
    if(!newTitle.trim()){ Alert.alert(t('خطأ','Error'),t('أدخل عنوان الهدف','Enter goal title')); return; }
    setSaving(true);
    try {
      const { data, error } = await supabase.from('goals').insert({user_id:userId,title:newTitle.trim(),status:'active',progress:0}).select().single();
      if(error) throw error;
      if(data) setGoals(prev=>[data,...prev]);
      setNewTitle(''); setShowAddModal(false);
    } catch(e){ Alert.alert(t('خطأ','Error'),t('فشل إضافة الهدف','Failed to add goal')); }
    finally { setSaving(false); }
  };

  const deleteGoal = async (goalId:string)=>{
    Alert.alert(t('حذف','Delete'),t('هل أنت متأكد؟','Are you sure?'),[ {text:t('إلغاء','Cancel'),style:'cancel'}, {text:t('حذف','Delete'),style:'destructive',onPress:async()=>{ await supabase.from('goals').delete().eq('id',goalId); setGoals(prev=>prev.filter(g=>g.id!==goalId)); }} ]);
  };

  const bg = isDark?'#1A1A1A':'#F8F6F2', card = isDark?'#2A2A2A':'#FFF', border = isDark?'#444':'#F0F0F0', txt = isDark?'#FFF':'#1A1A1A', sub = isDark?'#888':'#666';
  if(loading) return <SafeAreaView style={[s.safe,{backgroundColor:bg}]}><ActivityIndicator size="large" color="#6B21A8" style={{marginTop:80}}/></SafeAreaView>;

  return (
    <SafeAreaView style={[s.safe,{backgroundColor:bg}]}>
      <View style={[s.container,{backgroundColor:bg}]}>
        <View style={[s.headerRow,isAr&&{flexDirection:'row-reverse'}]}>
          <Text style={[s.title,{color:txt}]}>{t('أهدافي 🎯','My Goals 🎯')}</Text>
          <TouchableOpacity style={s.addBtn} onPress={()=>setShowAddModal(true)}><Plus size={20} stroke="#FFF"/></TouchableOpacity>
        </View>
        <FlatList
          data={goals} keyExtractor={(item)=>item.id}
          contentContainerStyle={{paddingBottom:40}}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={()=>fetchGoals(true)} colors={['#6B21A8']}/>}
          ListEmptyComponent={<View style={{alignItems:'center',marginTop:60}}><Target size={48} stroke={sub}/><Text style={{color:sub,fontSize:17,fontWeight:'600',marginTop:16}}>{t('لا توجد أهداف','No goals yet')}</Text><Text style={{color:sub,fontSize:14,marginTop:6,textAlign:'center'}}>{t('أضف هدفك الأول','Add your first goal')}</Text></View>}
          renderItem={({item})=>(
            <View style={[s.card,{backgroundColor:card,borderColor:border}]}>
              <View style={[s.cardHeader,isAr&&{flexDirection:'row-reverse'}]}>
                <Text style={[s.cardTitle,{color:txt,textDecorationLine:item.status==='completed'?'line-through':'none'}]}>{item.title}</Text>
                <TouchableOpacity onPress={()=>deleteGoal(item.id)}><Trash2 size={16} stroke={sub}/></TouchableOpacity>
              </View>
              <View style={s.progressSection}>
                <View style={[s.progressBar,{backgroundColor:isDark?'#444':'#F0F0F0'}]}><View style={[s.progressFill,{width:`${item.progress}%`,backgroundColor:'#6B21A8'}]}/></View>
                <Text style={[s.progressText,{color:sub}]}>{item.progress}%</Text>
              </View>
            </View>
          )}
        />
      </View>

      <Modal visible={showAddModal} transparent animationType="fade" onRequestClose={()=>setShowAddModal(false)}>
        <KeyboardAvoidingView behavior={Platform.OS==='ios'?'padding':'height'} style={s.modalOverlay}>
          <View style={[s.modalContent,isDark&&{backgroundColor:'#2A2A2A'}]}>
            <View style={[s.modalHeader,isAr&&{flexDirection:'row-reverse'}]}>
              <Text style={[s.modalTitle,{color:txt}]}>{t('هدف جديد','New Goal')}</Text>
              <TouchableOpacity onPress={()=>setShowAddModal(false)}><X size={22} stroke={sub}/></TouchableOpacity>
            </View>
            <TextInput style={[s.input,{backgroundColor:isDark?'#333':'#F8F6F2',color:txt,borderColor:isDark?'#444':'#E0D9F5'}]} placeholder={t('ماذا تريد أن تحقق؟','What do you want to achieve?')} placeholderTextColor={sub} value={newTitle} onChangeText={setNewTitle} autoFocus/>
            <TouchableOpacity style={[s.saveBtn,{opacity:saving?0.6:1}]} onPress={handleAddGoal} disabled={saving}>
              {saving?<ActivityIndicator color="#FFF"/>:<Text style={s.saveBtnText}>{t('حفظ','Save')}</Text>}
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe:{flex:1}, container:{flex:1,padding:20}, headerRow:{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginBottom:20},
  title:{fontSize:24,fontWeight:'800'}, addBtn:{width:40,height:40,borderRadius:20,backgroundColor:'#6B21A8',justifyContent:'center',alignItems:'center'},
  card:{padding:16,borderRadius:16,borderWidth:1,marginBottom:12},
  cardHeader:{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginBottom:8},
  cardTitle:{fontSize:16,fontWeight:'600'},
  progressSection:{flexDirection:'row',alignItems:'center',gap:10},
  progressBar:{flex:1,height:8,borderRadius:4,overflow:'hidden'}, progressFill:{height:'100%',borderRadius:4},
  progressText:{fontSize:13,fontWeight:'600'},
  modalOverlay:{flex:1,justifyContent:'center',alignItems:'center',backgroundColor:'rgba(0,0,0,0.5)'},
  modalContent:{width:'90%',backgroundColor:'#FFF',borderRadius:20,padding:20},
  modalHeader:{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginBottom:16},
  modalTitle:{fontSize:18,fontWeight:'700'},
  input:{padding:14,borderRadius:12,borderWidth:1,fontSize:15,marginBottom:16},
  saveBtn:{backgroundColor:'#6B21A8',padding:14,borderRadius:12,alignItems:'center'},
  saveBtnText:{color:'#FFF',fontWeight:'700',fontSize:16},
});
