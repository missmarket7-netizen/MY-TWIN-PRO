import {
  View, FlatList, StyleSheet, StatusBar, KeyboardAvoidingView,
  Platform, Image, Animated, Text, Alert, TouchableOpacity,
} from 'react-native';
import { useState, useRef, useEffect, useCallback } from 'react';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Haptics from 'expo-haptics';
import * as Clipboard from 'expo-clipboard';
import { supabase } from '../../lib/supabase';
import * as Location from 'expo-location';
import { useTwinStore, ChatMessage } from '../../store/useTwinStore';
import {
  sendChatFromStore, updateStoreFromResponse,
  fetchWeather, fetchYouTube, fetchSpotify, fetchNews, fetchCurrency,
} from '../../lib/api';
import SideMenu from '../../components/SideMenu';
import TypingIndicator from '../../components/TypingIndicator';
import { Menu, Volume2, VolumeX } from 'lucide-react-native';
import { speakResponse } from '../../utils/voice_engine';
import { COLORS, UserBubble, TwinBubble } from './ChatBubbles';
import { ChatInput } from './ChatInput';

const APP_ICON = require('../../assets/icon.png');

export default function Chat() {
  const insets = useSafeAreaInsets();
  const {
    userId, twinName, twinGender, tier, chatHistory, addMessage,
    triggerHaptic, lang, theme, setTwinName, setTwinGender,
    openMenu, closeMenu, voiceEnabled, setVoiceEnabled,
    bondLevel, setThinking, setThinkingStage,
  } = useTwinStore((s) => ({
    userId: s.userId, twinName: s.twinName, twinGender: s.twinGender, tier: s.tier,
    chatHistory: s.chatHistory, addMessage: s.addMessage,
    triggerHaptic: s.triggerHaptic, lang: s.lang, theme: s.theme,
    setTwinName: s.setTwinName, setTwinGender: s.setTwinGender,
    openMenu: s.openMenu, closeMenu: s.closeMenu,
    voiceEnabled: s.voiceEnabled, setVoiceEnabled: s.setVoiceEnabled,
    bondLevel: s.bondLevel, setThinking: s.setThinking, setThinkingStage: s.setThinkingStage,
  }));

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAttach, setShowAttach] = useState(false);
  const [messageQueue, setMessageQueue] = useState<Array<{ msg?: string; image?: string }>>([]);
  const [twinEnergy, setTwinEnergy] = useState(100);
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [activeToolsList, setActiveToolsList] = useState<any[]>([]);
  const [editingContent, setEditingContent] = useState('');
  const [feedbackMap, setFeedbackMap] = useState<Record<string, 'like' | 'dislike' | null>>({});
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  const flatRef = useRef<FlatList<ChatMessage>>(null);
  const attachAnim = useRef(new Animated.Value(0)).current;

  const colors = theme === 'dark' ? COLORS.dark : COLORS.light;
  const isRTL = lang === 'ar';
  const isDark = theme === 'dark';

  useEffect(() => { const t = setTimeout(() => flatRef.current?.scrollToEnd({ animated: true }), 100); return () => clearTimeout(t); }, [chatHistory, editingMessageId]);
  useEffect(() => { Animated.spring(attachAnim, { toValue: showAttach ? 1 : 0, useNativeDriver: true, tension: 65, friction: 11 }).start(); }, [showAttach]);
  useEffect(() => { if (messageQueue.length > 0 && !loading) { const next = messageQueue[0]; setMessageQueue(prev => prev.slice(1)); sendMessage(next.msg, next.image); } }, [messageQueue, loading]);

  useEffect(() => {
    (async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.access_token) {
          const res = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/stats`, { headers: { Authorization: `Bearer ${session.access_token}` } });
          if (res.ok) {
            const stats = await res.json();
            const remaining = stats.limits?.messages?.remaining || 0;
            const limit = stats.limits?.messages?.limit || 15;
            setTwinEnergy(Math.round((remaining / limit) * 100));
          }
        }
      } catch {}
    })();
  }, [chatHistory]);

  // إنشاء جلسة جديدة عند أول رسالة
  const createSessionIfNeeded = async () => {
    if (currentSessionId || !userId) return;
    try {
      const { data, error } = await supabase
        .from('chat_sessions')
        .insert({ user_id: userId, messages: [] })
        .select('id')
        .single();
      if (data && !error) {
        setCurrentSessionId(data.id);
      }
    } catch (e) {
      console.warn('Session creation failed:', e);
    }
  };

  // تحديث الجلسة بالرسائل الجديدة
  const updateSession = async (messages: ChatMessage[]) => {
    if (!currentSessionId || !userId) return;
    try {
      await supabase
        .from('chat_sessions')
        .update({ messages, updated_at: new Date().toISOString() })
        .eq('id', currentSessionId);
    } catch (e) {
      console.warn('Session update failed:', e);
    }
  };

  const saveFeedback = async (messageId: string, rating: 'like' | 'dislike') => {
    if (!userId) return;
    try { await supabase.from('message_feedback').upsert({ user_id: userId, message_id: messageId, rating, created_at: new Date().toISOString() }, { onConflict: 'user_id,message_id' }); } catch (e) { console.warn('Feedback save failed:', e); }
  };

  const handleLike = useCallback((msg: ChatMessage) => {
    const current = feedbackMap[msg.id];
    if (current === 'like') { setFeedbackMap(prev => ({ ...prev, [msg.id]: null })); } else { setFeedbackMap(prev => ({ ...prev, [msg.id]: 'like' })); saveFeedback(msg.id, 'like'); Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success); }
  }, [feedbackMap, userId]);

  const handleDislike = useCallback((msg: ChatMessage) => {
    const current = feedbackMap[msg.id];
    if (current === 'dislike') { setFeedbackMap(prev => ({ ...prev, [msg.id]: null })); } else { setFeedbackMap(prev => ({ ...prev, [msg.id]: 'dislike' })); saveFeedback(msg.id, 'dislike'); Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning); }
  }, [feedbackMap, userId]);

  const sendMessage = useCallback(async (msg?: string, imageBase64?: string) => {
    const message = (msg || input).trim();
    if (!message && !imageBase64 && activeToolsList.length === 0) return;

    await createSessionIfNeeded();

    const msgId = Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
    const userMsg: ChatMessage = { id: msgId, role: 'user', content: message || '📷 صورة', image: imageBase64, timestamp: Date.now() };
    addMessage(userMsg);
    setInput(''); setLoading(true); setThinking(true); setThinkingStage('thinking');

    try {
      if (activeToolsList.length > 0) {
        const tool = activeToolsList[0].type;
        let result = '';
        switch (tool) {
          case 'weather':
          const loc = activeToolsList[0]?.location || 'Cairo';
          result = (await fetchWeather(loc)).result || 'الطقس غير متاح';
          break;
          case 'youtube': result = (await fetchYouTube(input || 'music')).result || 'لم أجد فيديوهات'; break;
          case 'spotify': result = (await fetchSpotify(input || 'music')).result || 'لم أجد أغاني'; break;
          case 'news': result = (await fetchNews()).result || 'الأخبار غير متاحة'; break;
          case 'currency': result = (await fetchCurrency('USD')).result || 'أسعار العملات غير متاحة'; break;
        }
        if (result) {
          const twinMsg: ChatMessage = { id: Math.random().toString(36).substr(2,9)+Date.now().toString(36), role: 'twin', content: result, timestamp: Date.now(), provider: 'tool' };
          addMessage(twinMsg);
          if (voiceEnabled) await speakResponse(result);
        }
        setActiveToolsList([]);
        return;
      }

      const response = await sendChatFromStore(message, imageBase64);
      const youtubeRegex = /https?:\/\/(?:www\.)?youtube\.com\/watch\?v=[\w-]+|https?:\/\/youtu\.be\/[\w-]+/g;
      const youtubeLinks = response.reply.match(youtubeRegex);
      const twinMsg: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
        role: 'twin', content: response.reply, timestamp: Date.now(),
        emotion: response.emotion?.primary, memoryRecall: response.memory_used,
        youtubeVideo: youtubeLinks ? youtubeLinks[0] : undefined,
        provider: response.provider || 'multi_ai',
      };
      addMessage(twinMsg);
      updateStoreFromResponse(response);
      
      // حفظ الجلسة بعد كل رسالة جديدة
      const updatedHistory = useTwinStore.getState().chatHistory;
      updateSession(updatedHistory);
      
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) {
        const res = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/stats`, { headers: { Authorization: `Bearer ${session.access_token}` } });
        if (res.ok) { const stats = await res.json(); const remaining = stats.limits?.messages?.remaining || 0; const limit = stats.limits?.messages?.limit || 15; setTwinEnergy(Math.round((remaining / limit) * 100)); }
      }
      if (voiceEnabled) { try { await speakResponse(response.reply); } catch {} }
    } catch (error: any) {
      const isAr = lang === 'ar';
      let errMsg = '';
      if (error?.response) {
        const status = error.response.status;
        if (status === 401) errMsg = isAr ? 'انتهت الجلسة، سجّل الدخول تاني يا وحش 😅' : 'Session expired, log in again buddy 😅';
        else if (status === 429) errMsg = isAr ? 'استهدى بالله، كده كتير! جرب بعد شوية 🤯' : 'Whoa, slow down! Try again later 🤯';
        else if (status >= 500) errMsg = isAr ? 'السيرفر نام شوية، هنصحيه ونكمل ☕' : 'Server is napping, let me wake it up ☕';
        else errMsg = isAr ? `حصل خطأ ${status}: جرب مرة تانية 😬` : `Error ${status}: Something went wrong 😬`;
      } else if (error?.message === 'Network Error') {
        errMsg = isAr ? 'الإنترنت طاير، شوف الواي فاي 😵‍💫' : 'No internet, check your Wi-Fi 😵‍💫';
      } else if (error?.code === 'ECONNABORTED' || error?.name === 'AbortError') {
        errMsg = isAr ? 'النت بطيء، اصبر شوية 🐌' : 'Too slow! Let me try again 🐌';
      } else {
        errMsg = isAr ? 'حصل حاجة غريبة، جرب تاني 🌪️' : 'Something weird happened, try again 🌪️';
      }
      const errorMsg: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
        role: 'twin', timestamp: Date.now(), failed: true,
        content: errMsg, provider: 'error',
      };
      addMessage(errorMsg);
    } finally { setLoading(false); setThinking(false); }
  }, [input, loading, voiceEnabled, lang, addMessage, setThinking, setThinkingStage, activeToolsList, currentSessionId, userId]);

  const send = useCallback(async (msg?: string, imageBase64?: string) => {
    if (loading) { setMessageQueue(prev => [...prev, { msg, image: imageBase64 }]); return; }
    triggerHaptic(); await sendMessage(msg, imageBase64);
  }, [loading, sendMessage, triggerHaptic]);

  const handleCopy = useCallback((content: string) => { Clipboard.setStringAsync(content); Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success); }, []);
  const handleRetry = useCallback((failedMsg: ChatMessage) => { sendMessage(failedMsg.content, failedMsg.image); }, [sendMessage]);
  const handleRegenerate = useCallback((lastMsg: ChatMessage) => { sendMessage(lastMsg.content); }, [sendMessage]);
  const toggleSound = () => setVoiceEnabled(!voiceEnabled);
  const handleEditInInput = useCallback((msg: ChatMessage) => { setInput(msg.content); }, []);
  const handleStartEdit = useCallback((msg: ChatMessage) => { setEditingMessageId(msg.id); setEditingContent(msg.content); }, []);
  const handleSaveEdit = useCallback((msg: ChatMessage, newContent: string) => {
    if (newContent.trim() && newContent !== msg.content) { setEditingMessageId(null); sendMessage(newContent.trim(), msg.image); } else { setEditingMessageId(null); }
  }, [sendMessage]);

  
  const getCurrentLocation = async (): Promise<string> => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        const loc = await Location.getCurrentPositionAsync({});
        return `${loc.coords.latitude},${loc.coords.longitude}`;
      }
    } catch (e) {
      console.warn('Location error:', e);
    }
    return 'Cairo';
  };

  const handleAddTool = (toolDef: any) => { setActiveToolsList(prev => [...prev, { id: Date.now().toString(), ...toolDef }]); };
  const handleRemoveTool = (toolId: string) => { setActiveToolsList(prev => prev.filter(t => t.id !== toolId)); };

  const renderMsg = useCallback(({ item }: { item: ChatMessage }) => {
    if (item.role === 'user') return (
      <UserBubble item={item} isDark={isDark} onStartEdit={handleStartEdit} onSaveEdit={handleSaveEdit}
        isEditing={editingMessageId === item.id} editContent={editingContent} setEditContent={setEditingContent}
        onEditInInput={handleEditInInput} />
    );
    return (
      <TwinBubble item={item} isDark={isDark} onCopy={handleCopy} onRetry={handleRetry}
        onRegenerate={handleRegenerate} onLike={handleLike} onDislike={handleDislike}
        liked={feedbackMap[item.id] === 'like'} disliked={feedbackMap[item.id] === 'dislike'}
        provider={item.provider} />
    );
  }, [isDark, handleCopy, handleRetry, handleRegenerate, handleLike, handleDislike, feedbackMap, editingMessageId, editingContent, handleStartEdit, handleSaveEdit, handleEditInInput]);

  const ListFooter = useCallback(() => {
    if (!loading) return null;
    return (<View style={styles.typingRow}><Image source={APP_ICON} style={{ width: 28, height: 28, borderRadius: 14 }} /><TypingIndicator /></View>);
  }, [loading]);

  return (
    <View style={[styles.root, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} backgroundColor={colors.bg} />
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <View style={[styles.header, { backgroundColor: colors.headerBg, borderBottomColor: colors.border }]}>
          <TouchableOpacity onPress={openMenu} style={styles.menuBtn}><Menu size={22} stroke={colors.text} /></TouchableOpacity>
          <View style={styles.headerCenter}>
            <Text style={[styles.headerName, { color: colors.text }]} numberOfLines={1}>{twinName || (lang === 'ar' ? 'توأمك' : 'Your Twin')}</Text>
            <View style={styles.miniIndicators}>
              <View style={[styles.miniDot, { backgroundColor: twinEnergy > 60 ? '#10B981' : twinEnergy > 25 ? '#F59E0B' : '#EF4444' }]} />
              <Text style={[styles.miniText, { color: colors.subtext }]}>{Math.round(bondLevel)}%</Text>
            </View>
          </View>
          <TouchableOpacity onPress={toggleSound} style={styles.soundBtn}>{voiceEnabled ? <Volume2 size={22} stroke={colors.text} /> : <VolumeX size={22} stroke={colors.subtext} />}</TouchableOpacity>
        </View>
        <FlatList ref={flatRef} data={chatHistory} keyExtractor={(item) => item.id} renderItem={renderMsg}
          ListFooterComponent={ListFooter} contentContainerStyle={styles.listContent}
          onContentSizeChange={() => flatRef.current?.scrollToEnd({ animated: false })}
          removeClippedSubviews initialNumToRender={10} maxToRenderPerBatch={10} windowSize={5}
          keyboardDismissMode="interactive" />
        <ChatInput input={input} setInput={setInput} loading={loading} isRTL={isRTL} isDark={isDark}
          colors={colors} lang={lang} onSend={send} onAddTool={handleAddTool}
          onRemoveTool={handleRemoveTool} activeTools={activeToolsList}
          onCamera={() => {}} onGallery={() => {}} onFile={() => {}}
          showAttach={showAttach} setShowAttach={setShowAttach} attachAnim={attachAnim} />
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 10, borderBottomWidth: 0.5 },
  menuBtn: { padding: 4 },
  headerCenter: { flex: 1, alignItems: 'center' },
  headerName: { fontSize: 16, fontWeight: '600', textAlign: 'center' },
  miniIndicators: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 2 },
  miniDot: { width: 6, height: 6, borderRadius: 3 },
  miniText: { fontSize: 10, fontWeight: '500' },
  soundBtn: { padding: 4 },
  listContent: { paddingHorizontal: 16, paddingVertical: 12, flexGrow: 1 },
  typingRow: { flexDirection: 'row', alignItems: 'center', paddingLeft: 16, paddingVertical: 12, gap: 10 },
});
