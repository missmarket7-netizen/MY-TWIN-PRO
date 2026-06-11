import { SafeAreaView, View, Text, StyleSheet, FlatList, ActivityIndicator, RefreshControl } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { supabase } from '../lib/supabase';
import { useState, useEffect, useCallback, useRef } from 'react';
import { BrainCircuit, Heart, Star, Lightbulb, Target, MessageCircle, Sparkles, Trophy, Smile, Moon } from 'lucide-react-native';

const EVENT_CONFIG: Record<string,{icon:any;color:string;label_ar:string;label_en:string}> = {
  memory:{icon:BrainCircuit,color:'#3B82F6',label_ar:'ذكرى',label_en:'Memory'},
  dream:{icon:Moon,color:'#8B5CF6',label_ar:'حلم',label_en:'Dream'},
  goal:{icon:Target,color:'#F59E0B',label_ar:'هدف',label_en:'Goal'},
  relationship:{icon:Heart,color:'#EC4899',label_ar:'علاقة',label_en:'Relationship'},
  achievement:{icon:Trophy,color:'#10B981',label_ar:'إنجاز',label_en:'Achievement'},
  emotion:{icon:Smile,color:'#F59E0B',label_ar:'مشاعر',label_en:'Emotion'},
  chat:{icon:MessageCircle,color:'#6B21A8',label_ar:'محادثة',label_en:'Chat'},
};

export default function Timeline() {
  const { lang, theme, userId } = useTwinStore();
  const isAr = lang==='ar'; const isDark = theme==='dark';
  const t = (ar:string,en:string)=>isAr?ar:en;
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string|null>(null);
  const cancelledRef = useRef(false);

  const fetchEvents = useCallback(async (showRefresh=false)=>{
    if(!userId){ setLoading(false); return; }
    if(showRefresh) setRefreshing(true); else setLoading(true);
    setError(null);
    try {
      const [memoriesRes, dreamsRes, goalsRes, emotionsRes, twinRes] = await Promise.all([
        supabase.from('memories').select('*').eq('user_id',userId).limit(30),
        supabase.from('dreams').select('*').eq('user_id',userId).limit(10),
        supabase.from('goals').select('*').eq('user_id',userId).limit(10),
        supabase.from('emotional_timeline').select('*').eq('user_id',userId).limit(15),
        supabase.from('twin_states').select('bond_level,updated_at').eq('user_id',userId).single(),
      ]);
      if(cancelledRef.current) return;
      const all:any[] = [];
      memoriesRes.data?.forEach((m:any)=> all.push({id:`mem-${m.id}`,type:'memory',title:m.content?.slice(0,60),timestamp:m.created_at}));
      dreamsRes.data?.forEach((d:any)=> all.push({id:`dream-${d.id}`,type:'dream',title:d.content?.slice(0,60),timestamp:d.created_at}));
      goalsRes.data?.forEach((g:any)=> all.push({id:`goal-${g.id}`,type:'goal',title:g.title,timestamp:g.created_at}));
      emotionsRes.data?.forEach((e:any)=> { if(e.intensity>0.6) all.push({id:`emo-${e.id}`,type:'emotion',title:`${e.primary_emotion}`,timestamp:e.created_at}); });
      const twinData = twinRes.data;
      if(twinData?.bond_level){
        const b = twinData.bond_level;
        if(b>=20) all.push({id:'rel-familiar',type:'relationship',title:t('أصبحتما مألوفين','Became familiar'),timestamp:twinData.updated_at});
        if(b>=50) all.push({id:'rel-friend',type:'relationship',title:t('أصبحتما صديقين','Became friends'),timestamp:twinData.updated_at});
        if(b>=80) all.push({id:'rel-soulmate',type:'relationship',title:t('توأم روح','Soulmate'),timestamp:twinData.updated_at});
      }
      all.sort((a,b)=>new Date(b.timestamp).getTime()-new Date(a.timestamp).getTime());
      setEvents(all);
    } catch(e){ if(!cancelledRef.current) setError(t('فشل تحميل الخط الزمني','Failed to load timeline')); }
    finally { if(!cancelledRef.current){ setLoading(false); setRefreshing(false); } }
  },[userId,isAr]);

  useEffect(()=>{ cancelledRef.current=false; fetchEvents(); return ()=>{cancelledRef.current=true;}; },[fetchEvents]);

  const bg = isDark?'#1A1A1A':'#F8F6F2', card = isDark?'#2A2A2A':'#FFF', border = isDark?'#444':'#F0F0F0', txt = isDark?'#FFF':'#1A1A1A', sub = isDark?'#888':'#666';
  if(loading) return <SafeAreaView style={[s.safe,{backgroundColor:bg}]}><ActivityIndicator size="large" color="#6B21A8" style={{marginTop:80}}/></SafeAreaView>;

  return (
    <SafeAreaView style={[s.safe,{backgroundColor:bg}]}>
      <View style={[s.container,{backgroundColor:bg}]}>
        <Text style={[s.title,{color:txt}]}>{t('رحلتكما معاً 💜','Your Journey Together 💜')}</Text>
        {error&&<Text style={{color:'#EF4444',textAlign:'center',marginBottom:12}}>{error}</Text>}
        <FlatList
          data={events} keyExtractor={(item)=>item.id}
          contentContainerStyle={{paddingBottom:40}}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={()=>fetchEvents(true)} colors={['#6B21A8']}/>}
          ListEmptyComponent={<View style={{alignItems:'center',marginTop:60}}><BrainCircuit size={48} stroke={sub}/><Text style={{color:sub,fontSize:17,fontWeight:'600',marginTop:16}}>{t('لا توجد أحداث','No events yet')}</Text><Text style={{color:sub,fontSize:14,marginTop:6,textAlign:'center'}}>{t('ابدأ المحادثة مع توأمك','Start chatting with your Twin')}</Text></View>}
          renderItem={({item,index})=>{
            const config = EVENT_CONFIG[item.type]||EVENT_CONFIG.chat; const Icon = config.icon; const color = config.color;
            const isLast = index===events.length-1;
            return (
              <View style={[s.eventRow,isAr&&{flexDirection:'row-reverse'}]}>
                <View style={s.lineCol}>
                  <View style={[s.dot,{backgroundColor:color}]}/>
                  {!isLast&&<View style={[s.connector,{backgroundColor:isDark?'#444':'#E0D9F5'}]}/>}
                </View>
                <View style={[s.card,{backgroundColor:card,borderColor:border}]}>
                  <View style={[s.cardHeader,isAr&&{flexDirection:'row-reverse'}]}>
                    <View style={[s.iconWrap,{backgroundColor:color+'20'}]}><Icon size={16} color={color}/></View>
                    <Text style={[s.cardTitle,{color:txt}]}>{item.title}</Text>
                    <Text style={[s.cardTime,{color:sub}]}>{new Date(item.timestamp).toLocaleDateString(isAr?'ar-EG':'en-US',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})}</Text>
                  </View>
                </View>
              </View>
            );
          }}
        />
      </View>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe:{flex:1}, container:{flex:1,padding:20}, title:{fontSize:24,fontWeight:'800',marginBottom:20},
  eventRow:{flexDirection:'row',marginBottom:0},
  lineCol:{alignItems:'center',width:32,marginRight:10},
  dot:{width:12,height:12,borderRadius:6,marginTop:4},
  connector:{width:2,flex:1,marginVertical:4},
  card:{flex:1,padding:12,borderRadius:14,borderWidth:1,marginBottom:12},
  cardHeader:{flexDirection:'row',alignItems:'center',gap:8},
  iconWrap:{width:32,height:32,borderRadius:10,justifyContent:'center',alignItems:'center'},
  cardTitle:{fontSize:14,fontWeight:'600',flex:1},
  cardTime:{fontSize:11},
});
