import { SafeAreaView, View, Text, StyleSheet, FlatList, ActivityIndicator, RefreshControl, Alert, TouchableOpacity } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { supabase } from '../lib/supabase';
import { useState, useEffect, useCallback, useRef } from 'react';
import { BrainCircuit, Heart, Star, Lightbulb, Trash2 } from 'lucide-react-native';
import type { LucideIcon } from 'lucide-react-native';

interface Memory { id: string; user_id: string; content: string; created_at: string; category?: string; importance_score?: number; emotional_tag?: string; }

const CATEGORY_ICONS: Record<string, LucideIcon> = { pref: Heart, dream: Star, fact: Lightbulb, default: BrainCircuit };
const CATEGORY_COLORS: Record<string, string> = { pref: '#EC4899', dream: '#F59E0B', fact: '#3B82F6', default: '#6B21A8' };

export default function Memories() {
  const { lang, theme, userId } = useTwinStore();
  const isAr = lang==='ar'; const isDark = theme==='dark';
  const t = (ar:string,en:string)=>isAr?ar:en;
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string|null>(null);
  const cancelledRef = useRef(false);

  const fetchMemories = useCallback(async (showRefresh=false)=>{
    if(!userId){ setLoading(false); return; }
    if(showRefresh) setRefreshing(true); else setLoading(true);
    setError(null);
    try {
      const { data, error:fetchError } = await supabase.from('memories').select('*').eq('user_id',userId).order('created_at',{ascending:false});
      if(cancelledRef.current) return;
      if(fetchError) throw fetchError;
      setMemories(data||[]);
    } catch(e){ if(!cancelledRef.current) setError(t('فشل تحميل الذكريات','Failed to load memories')); }
    finally { if(!cancelledRef.current){ setLoading(false); setRefreshing(false); } }
  },[userId,isAr]);

  useEffect(()=>{ cancelledRef.current=false; fetchMemories(); return ()=>{cancelledRef.current=true;}; },[fetchMemories]);

  const handleDelete = (memoryId:string)=>{ Alert.alert(t('حذف','Delete'),t('هل أنت متأكد؟','Are you sure?'),[ {text:t('إلغاء','Cancel'),style:'cancel'}, {text:t('حذف','Delete'),style:'destructive',onPress:async()=>{ await supabase.from('memories').delete().eq('id',memoryId); setMemories(prev=>prev.filter(m=>m.id!==memoryId)); }} ]); };

  const bg = isDark?'#1A1A1A':'#F8F6F2', card = isDark?'#2A2A2A':'#FFF', border = isDark?'#444':'#F0F0F0', txt = isDark?'#FFF':'#1A1A1A', sub = isDark?'#888':'#666';
  if(loading) return <SafeAreaView style={[s.safe,{backgroundColor:bg}]}><ActivityIndicator size="large" color="#6B21A8" style={{marginTop:80}}/></SafeAreaView>;

  return (
    <SafeAreaView style={[s.safe,{backgroundColor:bg}]}>
      <View style={[s.container,{backgroundColor:bg}]}>
        <Text style={[s.title,{color:txt}]}>{t('ذكرياتي 🧠','My Memories 🧠')}</Text>
        {error&&<Text style={{color:'#EF4444',textAlign:'center',marginBottom:12}}>{error}</Text>}
        <FlatList
          data={memories} keyExtractor={(item)=>item.id}
          contentContainerStyle={{paddingBottom:40}}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={()=>fetchMemories(true)} colors={['#6B21A8']}/>}
          ListEmptyComponent={<View style={{alignItems:'center',marginTop:60}}><BrainCircuit size={48} stroke={sub}/><Text style={{color:sub,fontSize:17,fontWeight:'600',marginTop:16}}>{t('لا توجد ذكريات','No memories')}</Text><Text style={{color:sub,fontSize:14,marginTop:6,textAlign:'center'}}>{t('تحدث مع توأمك لإنشاء ذكريات','Chat with your Twin to create memories')}</Text></View>}
          renderItem={({item})=>{
            const cat = item.category||'default'; const Icon = CATEGORY_ICONS[cat]||BrainCircuit; const color = CATEGORY_COLORS[cat]||'#6B21A8';
            return (
              <TouchableOpacity onLongPress={()=>handleDelete(item.id)} style={[s.card,{backgroundColor:card,borderColor:border}]}>
                <View style={s.cardRow}>
                  <View style={[s.iconWrap,{backgroundColor:color+'20'}]}><Icon size={16} color={color}/></View>
                  <View style={{flex:1}}>
                    <Text style={[s.cardText,{color:txt}]}>{item.content}</Text>
                    <Text style={[s.date,{color:sub}]}>{new Date(item.created_at).toLocaleDateString(isAr?'ar-EG':'en-US',{year:'numeric',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})}</Text>
                  </View>
                </View>
              </TouchableOpacity>
            );
          }}
        />
      </View>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe:{flex:1}, container:{flex:1,padding:20}, title:{fontSize:24,fontWeight:'800',marginBottom:20},
  card:{padding:14,borderRadius:14,borderWidth:1,marginBottom:10},
  cardRow:{flexDirection:'row',alignItems:'center',gap:10},
  iconWrap:{width:32,height:32,borderRadius:10,justifyContent:'center',alignItems:'center'},
  cardText:{fontSize:15,lineHeight:22,marginBottom:4},
  date:{fontSize:12},
});
