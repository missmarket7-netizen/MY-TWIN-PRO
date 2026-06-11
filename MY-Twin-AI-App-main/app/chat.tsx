import { View, Text, FlatList, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, Modal, Animated, Alert, StatusBar, Image, ActivityIndicator, Pressable } from 'react-native';
import { useState, useRef, useEffect, useCallback } from 'react';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Haptics from 'expo-haptics';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import * as Localization from 'expo-localization';
import { supabase } from '../lib/supabase';
import { useTwinStore } from '../store/useTwinStore';
import { API } from '../lib/api';
import SideMenu from '../components/SideMenu';
import TypingIndicator from '../components/TypingIndicator';
import { Menu, Send, X, Volume2, VolumeX, RotateCcw } from 'lucide-react-native';
import { speakResponse } from '../utils/voice_engine';

const APP_ICON = require('../assets/icon.png');

export default function Chat() {
  const insets = useSafeAreaInsets();
  const { userId, twinName, twinGender, tier, chatHistory, addMessage, updateBond, updateRelationshipDims, calmMode, triggerHaptic, lang, theme, setTwinName, setTwinGender, openMenu, closeMenu, voiceEnabled, setVoiceEnabled, setEnergy } = useTwinStore();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAttach, setShowAttach] = useState(false);
  const [featureModal, setFeatureModal] = useState<{visible:boolean;type:string}>({visible:false,type:''});
  const [featureInput, setFeatureInput] = useState('');
  const [messageQueue, setMessageQueue] = useState<Array<{msg?:string;image?:string}>>([]);
  const flatRef = useRef<FlatList<any>>(null);
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const attachAnim = useRef(new Animated.Value(0)).current;
  const abortRef = useRef<AbortController|null>(null);
  const isRTL = lang === 'ar';
  const isDark = theme === 'dark';
  const isFree = tier === 'free';
  const APP_ICON = require('../assets/icon.png');

  useEffect(()=>{ if(chatHistory.length>0 && chatHistory[chatHistory.length-1]?.role==='twin'){ Animated.sequence([ Animated.timing(pulseAnim,{toValue:1.4,duration:200,useNativeDriver:true}), Animated.timing(pulseAnim,{toValue:1,duration:200,useNativeDriver:true}) ]).start(); } },[chatHistory]);

  useEffect(()=>{ (async()=>{ const {data:profile}=await supabase.from('profiles').select('twin_name,twin_gender').eq('id',userId).single(); if(profile){ if(profile.twin_name) setTwinName(profile.twin_name); if(profile.twin_gender) setTwinGender(profile.twin_gender); } })(); },[userId]);

  useEffect(()=>{ const t=setTimeout(()=>flatRef.current?.scrollToEnd({animated:true}),100); return ()=>clearTimeout(t); },[chatHistory]);
  useEffect(()=>{ Animated.spring(attachAnim,{toValue:showAttach?1:0,useNativeDriver:true,tension:65,friction:11}).start(); },[showAttach]);
  useEffect(()=>{ if(messageQueue.length>0&&!loading){ const next=messageQueue[0]; setMessageQueue(prev=>prev.slice(1)); sendMessage(next.msg,next.image); } },[messageQueue,loading]);

  const countryCode = (Localization.region||'SA').toUpperCase();
  const sendMessage = useCallback(async (msg?:string, imageBase64?:string)=>{
    const message = (msg||input).trim();
    if(!message&&!imageBase64) return;
    if(abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();
    addMessage('user', message||'📷 صورة', imageBase64);
    setInput(''); setLoading(true);
    try {
      const res = await API.post('/api/chat', { message:message||'صورة مرفقة', twin_name:twinName, bond_level:0, relationship_dims:{}, calm_mode:calmMode, lang, image:imageBase64||undefined }, { headers:{ 'X-Calm-Mode':String(calmMode), 'X-Country-Code':countryCode, 'X-Twin-Gender':twinGender }, signal:abortRef.current.signal });
      addMessage('twin', res.data.reply);
      updateBond(res.data.new_bond??0);
      if(res.data.relationship_dims) updateRelationshipDims(res.data.relationship_dims);
      if(res.data.energy!==undefined) setEnergy(res.data.energy);
      if(voiceEnabled){ try{ await speakResponse(res.data.reply,{pitch:1.0,rate:1.0}); }catch{} }
    } catch(error:any){ if(error.name==='AbortError') return; const status=error?.response?.status; addMessage('twin', status===401? (lang==='ar'?'انتهت جلستك 🔒':'Session expired 🔒') : (lang==='ar'?'تعذر الاتصال 😔':'Connection failed 😔')); }
    finally { setLoading(false); }
  },[input,loading,twinName,calmMode,lang,addMessage,updateBond,updateRelationshipDims,voiceEnabled,twinGender,countryCode]);

  const send = useCallback(async (msg?:string, imageBase64?:string)=>{
    if(loading){ setMessageQueue(prev=>[...prev,{msg,image:imageBase64}]); return; }
    triggerHaptic(); await sendMessage(msg,imageBase64);
  },[loading,sendMessage,triggerHaptic]);

  const handleRetry = useCallback((failedMsg:any)=>{ addMessage('user',failedMsg.content,failedMsg.image); sendMessage(failedMsg.content,failedMsg.image); },[addMessage,sendMessage]);
  const handleRegenerate = useCallback((lastMsg:any)=>{ sendMessage(lastMsg.content); },[sendMessage]);
  const handleCopy = useCallback((content:string)=>{ Alert.alert('✅',lang==='ar'?'تم النسخ':'Copied'); },[lang]);
  const toggleSound = ()=>setVoiceEnabled(!voiceEnabled);
  const attachItems = [
    { icon:'📷', label: lang==='ar'?'كاميرا':'Camera', action:'camera' },
    { icon:'🖼️', label: lang==='ar'?'معرض':'Gallery', action:'image' },
    { icon:'📄', label: lang==='ar'?'ملف':'File', action:'file' },
    { icon:'🔍', label: lang==='ar'?'بحث':'Search', action:'search' },
    { icon:'💪', label: lang==='ar'?'تدريب':'Coaching', action:'coach' },
    { icon:'🌙', label: lang==='ar'?'تفسير أحلام':'Dreams', action:'dream' },
  ];

  const renderMsg = useCallback(({item,index}:{item:any;index:number})=>{
    const isUser = item.role === 'user';
    const isLast = index === chatHistory.length-1;
    return (
      <View style={[s.msgRow, isUser ? s.userRow : s.twinRow]}>
        {!isUser && isLast && (
          <Animated.View style={{ transform:[{scale:pulseAnim}] }}>
            <Image source={APP_ICON} style={s.avatar} />
          </Animated.View>
        )}
        {!isUser && !isLast && <Image source={APP_ICON} style={s.avatar} />}
        {isUser ? (
          <View style={[s.bubble, s.userBubble]}>
            {item.image && <Image source={{uri: item.image.startsWith('data:')?item.image:`data:image/jpeg;base64,${item.image}`}} style={s.chatImage} />}
            <Text style={s.userText}>{item.content}</Text>
            <Text style={s.timestamp}>{new Date(item.timestamp).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}</Text>
          </View>
        ) : (
          <View style={s.twinBubbleWrap}>
            <Text style={[s.twinText, isDark&&{color:'#FFF'}]}>{item.content}</Text>
            <Text style={[s.timestamp, isDark&&{color:'#999'}]}>{new Date(item.timestamp).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}</Text>
          </View>
        )}
      </View>
    );
  },[chatHistory.length,isDark]);

  return (
    <View style={[s.root,{paddingTop:insets.top,backgroundColor:isDark?'#1A1A1A':'#FFFFFF'}]}>
      <StatusBar barStyle={isDark?'light-content':'dark-content'} backgroundColor={isDark?'#1A1A1A':'#FFFFFF'} />
      <KeyboardAvoidingView style={{flex:1}} behavior={Platform.OS==='ios'?'padding':undefined}>
        <View style={[s.header,isDark&&{backgroundColor:'#1A1A1A',borderBottomColor:'#333'}]}>
          <TouchableOpacity onPress={openMenu} style={s.menuBtn}><Menu size={22} stroke={isDark?'#FFF':'#1A1A1A'}/></TouchableOpacity>
          <View style={s.headerCenter}><Text style={[s.headerName,isDark&&{color:'#FFF'}]}>{twinName||(lang==='ar'?'توأمك':'Your Twin')}</Text></View>
          <TouchableOpacity onPress={toggleSound} style={s.soundBtn}>{voiceEnabled?<Volume2 size={22} stroke={isDark?'#FFF':'#1A1A1A'}/>:<VolumeX size={22} stroke={isDark?'#999':'#999'}/>}</TouchableOpacity>
        </View>
        <FlatList
          ref={flatRef} data={chatHistory} keyExtractor={(item,idx)=>item.id||idx.toString()}
          renderItem={renderMsg}
          ListFooterComponent={loading?<View style={s.typingRow}><Image source={APP_ICON} style={{width:28,height:28,borderRadius:14}}/><TypingIndicator/></View>:null}
          contentContainerStyle={s.listContent}
          onContentSizeChange={()=>flatRef.current?.scrollToEnd({animated:false})}
          removeClippedSubviews initialNumToRender={15} maxToRenderPerBatch={10} windowSize={5}
        />
        <View style={[s.inputBar,isDark&&{backgroundColor:'#1A1A1A',borderTopColor:'#333'}]}>
          <TouchableOpacity onPress={()=>setShowAttach(true)} style={s.addBtn}><Text style={s.addBtnText}>+</Text></TouchableOpacity>
          <TextInput
            style={[s.textInput,isRTL&&{textAlign:'right'},isDark&&{backgroundColor:'#333',color:'#FFF',borderColor:'#555'}]}
            value={input} onChangeText={setInput}
            placeholder={lang==='ar'?'اكتب رسالتك... 💜':'Type your message... 💜'}
            placeholderTextColor="#C4B5D4" multiline maxLength={2000} editable={!loading}
            onSubmitEditing={()=>send()}
          />
          <TouchableOpacity onPress={()=>send()} disabled={loading||input.trim().length===0} style={[s.sendBtn,{backgroundColor:(input.trim().length>0&&!loading)?'#6B21A8':'#E0D9F5'}]}>
            {loading?<ActivityIndicator size="small" color="#C4B5D4"/>:<Send size={18} stroke={input.trim().length>0?'#FFF':'#C4B5D4'}/>}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

const s = StyleSheet.create({
  root:{flex:1}, header:{flexDirection:'row',alignItems:'center',justifyContent:'space-between',paddingHorizontal:12,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'#F0F0F0'},
  menuBtn:{padding:4}, headerCenter:{flex:1,alignItems:'center'}, headerName:{fontSize:15,fontWeight:'700'}, soundBtn:{padding:4},
  listContent:{paddingHorizontal:12,paddingVertical:12,flexGrow:1},
  typingRow:{flexDirection:'row',alignItems:'center',paddingLeft:10,paddingVertical:8,gap:8},
  msgRow:{flexDirection:'row',marginBottom:10},
  userRow:{justifyContent:'flex-end'}, twinRow:{justifyContent:'flex-start',gap:6},
  avatar:{width:32,height:32,borderRadius:16},
  bubble:{maxWidth:'80%',paddingHorizontal:14,paddingVertical:8,borderRadius:16},
  userBubble:{backgroundColor:'#6B21A8',borderBottomRightRadius:4},
  userText:{color:'#FFF',fontSize:15,lineHeight:22},
  twinBubbleWrap:{flex:1},
  twinText:{color:'#1A1A1A',fontSize:15,lineHeight:22},
  chatImage:{width:200,height:200,borderRadius:12,marginBottom:6},
  timestamp:{fontSize:10,color:'#999',marginTop:4},
  inputBar:{flexDirection:'row',alignItems:'center',paddingHorizontal:10,paddingTop:8,borderTopWidth:1,borderTopColor:'#F0F0F0',gap:8},
  addBtn:{width:36,height:36,borderRadius:18,backgroundColor:'#F3F0FF',justifyContent:'center',alignItems:'center',borderWidth:1,borderColor:'#E0D9F5'},
  addBtnText:{fontSize:18,color:'#6B21A8',fontWeight:'700'},
  textInput:{flex:1,backgroundColor:'#F8F8F8',color:'#1A1A1A',paddingHorizontal:14,paddingVertical:10,borderRadius:22,fontSize:15,maxHeight:100,minHeight:44,borderWidth:1,borderColor:'#EFEFEF'},
  sendBtn:{width:42,height:42,borderRadius:21,justifyContent:'center',alignItems:'center'},
});
