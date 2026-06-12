import { SafeAreaView, ScrollView, Text, StyleSheet, View, ActivityIndicator, TouchableOpacity, Modal, TextInput, Alert, RefreshControl, Platform, KeyboardAvoidingView } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { supabase } from '../lib/supabase';
import { useState, useEffect, useCallback, useRef } from 'react';
import { HeartPulse, Plus, X, TrendingUp, TrendingDown, Minus, Heart, Shield, Star } from 'lucide-react-native';
import EmotionalAvatar from '../components/EmotionalAvatar';

const MOOD_OPTIONS = [
  { emoji:'😊', label_ar:'سعيد', label_en:'Happy', value:'joy', color:'#F59E0B' },
  { emoji:'😌', label_ar:'هادئ', label_en:'Calm', value:'neutral', color:'#3B82F6' },
  { emoji:'😢', label_ar:'حزين', label_en:'Sad', value:'sadness', color:'#60A5FA' },
  { emoji:'😤', label_ar:'غاضب', label_en:'Angry', value:'anger', color:'#EF4444' },
  { emoji:'😨', label_ar:'قلق', label_en:'Anxious', value:'fear', color:'#A78BFA' },
  { emoji:'💕', label_ar:'محب', label_en:'Loving', value:'love', color:'#EC4899' },
  { emoji:'😴', label_ar:'متعب', label_en:'Tired', value:'sadness', color:'#8B5CF6' },
];

export default function Mood() {
  const { lang, theme, userId, relationshipDims } = useTwinStore();
  const isAr = lang==='ar'; const isDark = theme==='dark';
  const t = (ar:string,en:string)=>isAr?ar:en;
  const [recentMoods, setRecentMoods] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedMood, setSelectedMood] = useState('joy');
  const [saving, setSaving] = useState(false);
  const cancelledRef = useRef(false);

  const fetchMoods = useCallback(async (showRefresh=false)=>{
    if(!userId){ setLoading(false); return; }
    if(showRefresh) setRefreshing(true); else setLoading(true);
    try {
      const { data } = await supabase.from('emotional_timeline').select('*').eq('user_id',userId).order('created_at',{ascending:false}).limit(7);
      if(!cancelledRef.current) setRecentMoods(data||[]);
    } catch(e){ console.error('Mood fetch error:',e); }
    finally { if(!cancelledRef.current){ setLoading(false); setRefreshing(false); } }
  },[userId]);

  useEffect(()=>{ cancelledRef.current=false; fetchMoods(); return ()=>{cancelledRef.current=true;}; },[fetchMoods]);

  const handleAddMood = async ()=>{
    if(!userId) return;
    setSaving(true);
    try {
      const { error } = await supabase.from('emotional_timeline').insert({
        user_id:userId, primary_emotion:selectedMood, intensity:0.7,
        valence: selectedMood==='joy'||selectedMood==='love'?0.8: selectedMood==='sadness'||selectedMood==='anger'?-0.5:0.2,
      });
      if(error) throw error;
      setShowAddModal(false);
      fetchMoods(true);
    } catch(e:any){
      Alert.alert(t('خطأ','Error'), e.message || t('فشل تسجيل المشاعر','Failed to log mood'));
    } finally { setSaving(false); }
  };

  const bg = isDark?'#1A1A1A':'#F8F6F2', card = isDark?'#2A2A2A':'#FFF', border = isDark?'#444':'#F0F0F0', txt = isDark?'#FFF':'#1A1A1A', sub = isDark?'#888':'#666';
  if(loading) return <SafeAreaView style={[s.safe,{backgroundColor:bg}]}><ActivityIndicator size="large" color="#6B21A8" style={{marginTop:80}}/></SafeAreaView>;

  return (
    <SafeAreaView style={[s.safe,{backgroundColor:bg}]}>
      <ScrollView contentContainerStyle={[s.container]} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={()=>fetchMoods(true)} colors={['#6B21A8']}/>}>
        <View style={[s.headerRow,isAr&&{flexDirection:'row-reverse'}]}>
          <Text style={[s.title,{color:txt}]}>{t('لوحة المشاعر','Mood Board')}</Text>
          <TouchableOpacity style={s.addBtn} onPress={()=>setShowAddModal(true)}><Plus size={20} stroke="#FFF"/></TouchableOpacity>
        </View>

        <View style={[s.relationshipCard,{backgroundColor:card,borderColor:border}]}>
          <View style={[s.sectionHeader,isAr&&{flexDirection:'row-reverse'}]}><Heart size={20} stroke="#EC4899"/><Text style={[s.sectionTitle,{color:txt}]}>{t('مشاعر العلاقة','Relationship Mood')}</Text></View>
          <View style={s.relGrid}>
            {[
              {label:t('ثقة','Trust'),value:relationshipDims.trust ?? 0,color:'#3B82F6',icon:Shield},
              {label:t('ارتباط','Attachment'),value:relationshipDims.affection ?? 0,color:'#EC4899',icon:Heart},
              {label:t('راحة','Comfort'),value:relationshipDims.empathy ?? 0,color:'#10B981',icon:Star}
            ].map((item,i)=>(
              <View key={i} style={s.relItem}>
                <item.icon size={16} stroke={item.color}/>
                <View style={[s.relBar,{backgroundColor:isDark?'#444':'#F0F0F0'}]}>
                  <View style={[s.relFill,{width:`${Math.min(item.value,100)}%`,backgroundColor:item.color}]}/>
                </View>
                <Text style={[s.relLabel,{color:sub}]}>{item.label}</Text>
              </View>
            ))}
          </View>
        </View>

        <Text style={[s.sectionTitle,{color:txt}]}>{t('آخر المشاعر','Recent Moods')}</Text>
        {recentMoods.length===0?<Text style={[s.empty,{color:sub}]}>{t('لا توجد بيانات بعد','No data yet')}</Text>:
          recentMoods.map((entry,i)=>{
            const moodInfo = MOOD_OPTIONS.find(m=>m.value===entry.primary_emotion)||MOOD_OPTIONS[1];
            return (
              <View key={i} style={[s.moodRow,{backgroundColor:card,borderColor:border}]}>
                <EmotionalAvatar mood={moodInfo.value} size={28} animated={false}/>
                <View style={{flex:1}}><Text style={[s.moodLabel,{color:txt}]}>{isAr?moodInfo.label_ar:moodInfo.label_en}</Text><Text style={[s.moodTime,{color:sub}]}>{new Date(entry.created_at).toLocaleDateString(isAr?'ar-EG':'en-US',{weekday:'long',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})}</Text></View>
                <View style={[s.intensityDot,{backgroundColor:moodInfo.color,width:12+entry.intensity*12,height:12+entry.intensity*12,borderRadius:6+entry.intensity*6}]}/>
              </View>
            );
          })
        }
      </ScrollView>

      <Modal visible={showAddModal} transparent animationType="fade" onRequestClose={()=>setShowAddModal(false)}>
        <KeyboardAvoidingView behavior={Platform.OS==='ios'?'padding':'height'} style={s.modalOverlay}>
          <View style={[s.modalContent,isDark&&{backgroundColor:'#2A2A2A'}]}>
            <View style={[s.modalHeader,isAr&&{flexDirection:'row-reverse'}]}><Text style={[s.modalTitle,{color:txt}]}>{t('كيف تشعر؟','How do you feel?')}</Text><TouchableOpacity onPress={()=>setShowAddModal(false)}><X size={22} stroke={sub}/></TouchableOpacity></View>
            <View style={s.moodGrid}>
              {MOOD_OPTIONS.map((mood)=>(
                <TouchableOpacity key={mood.value} style={[s.moodOption,{borderColor:selectedMood===mood.value?mood.color:border,backgroundColor:selectedMood===mood.value?mood.color+'20':'transparent'}]} onPress={()=>setSelectedMood(mood.value)}>
                  <Text style={s.moodOptionEmoji}>{mood.emoji}</Text>
                  <Text style={[s.moodOptionLabel,{color:selectedMood===mood.value?mood.color:sub}]}>{isAr?mood.label_ar:mood.label_en}</Text>
                </TouchableOpacity>
              ))}
            </View>
            <TouchableOpacity style={[s.saveBtn,{opacity:saving?0.6:1}]} onPress={handleAddMood} disabled={saving}>
              {saving?<ActivityIndicator color="#FFF"/>:<Text style={s.saveBtnText}>{t('تسجيل','Log Mood')}</Text>}
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe:{flex:1}, container:{padding:20,paddingBottom:40},
  headerRow:{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginBottom:20},
  title:{fontSize:24,fontWeight:'800'}, addBtn:{width:40,height:40,borderRadius:20,backgroundColor:'#6B21A8',justifyContent:'center',alignItems:'center'},
  relationshipCard:{padding:20,borderRadius:20,borderWidth:1,marginBottom:20},
  sectionHeader:{flexDirection:'row',alignItems:'center',gap:8,marginBottom:16},
  sectionTitle:{fontSize:17,fontWeight:'700'},
  relGrid:{gap:10},
  relItem:{flexDirection:'row',alignItems:'center',gap:10},
  relBar:{flex:1,height:6,borderRadius:3,overflow:'hidden'}, relFill:{height:'100%',borderRadius:3},
  relLabel:{fontSize:12,minWidth:40,textAlign:'right'},
  empty:{textAlign:'center',fontSize:15,marginTop:20},
  moodRow:{flexDirection:'row',alignItems:'center',padding:14,borderRadius:14,borderWidth:1,marginBottom:8,gap:12},
  moodLabel:{fontSize:15,fontWeight:'600'}, moodTime:{fontSize:12,marginTop:2},
  intensityDot:{},
  modalOverlay:{flex:1,justifyContent:'center',alignItems:'center',backgroundColor:'rgba(0,0,0,0.5)'},
  modalContent:{width:'90%',backgroundColor:'#FFF',borderRadius:20,padding:20},
  modalHeader:{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginBottom:16},
  modalTitle:{fontSize:18,fontWeight:'700'},
  moodGrid:{flexDirection:'row',flexWrap:'wrap',gap:10,marginBottom:16},
  moodOption:{alignItems:'center',padding:12,borderRadius:14,borderWidth:1.5,width:'30%'},
  moodOptionEmoji:{fontSize:28,marginBottom:4},
  moodOptionLabel:{fontSize:12,fontWeight:'500'},
  saveBtn:{backgroundColor:'#6B21A8',padding:14,borderRadius:12,alignItems:'center'},
  saveBtnText:{color:'#FFF',fontWeight:'700',fontSize:16},
});
