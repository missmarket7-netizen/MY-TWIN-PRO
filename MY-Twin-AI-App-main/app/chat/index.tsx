import {
  View, FlatList, StyleSheet, StatusBar, KeyboardAvoidingView,
  Platform, Image, Animated, Text, Alert, TouchableOpacity,
  RefreshControl, Dimensions,
} from 'react-native';
import { useState, useRef, useEffect, useCallback, memo } from 'react';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Haptics from 'expo-haptics';
import * as Clipboard from 'expo-clipboard';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import { supabase } from '../../lib/supabase';
import * as Location from 'expo-location';
import { useTwinStore, ChatMessage } from '../../store/useTwinStore';
import {
  sendChatFromStore, updateStoreFromResponse,
  fetchWeather, fetchYouTube, fetchSpotify, fetchNews, fetchCurrency,
} from '../../lib/api';
import SideMenu from '../../components/SideMenu';
import TypingIndicator from '../../components/TypingIndicator';
import {
  Menu, Volume2, VolumeX, Mic, MicOff, Sparkles,
} from 'lucide-react-native';
import { speakResponse, stopSpeaking } from '../../utils/voice_engine';
import { COLORS, UserBubble, TwinBubble } from './ChatBubbles';
import { ChatInput } from './ChatInput';

const { width: SCREEN_W } = Dimensions.get('window');
const APP_ICON = require('../../assets/icon.png');

// ==================== WELCOME COMPONENT ====================

const WelcomeState = memo(({ isDark, lang, twinName, onSuggestion }: any) => {
  const c = isDark ? COLORS.dark : COLORS.light;
  const suggestions = lang === 'ar' ? [
    'صباح الخير! كيف حالك اليوم؟',
    'حابب نتكلم عن إيه؟',
    'عندك أي أخبار حلوة؟',
  ] : [
    'Good morning! How are you today?',
    'What would you like to talk about?',
    'Any good news to share?',
  ];

  return (
    <View style={styles.welcomeContainer}>
      <View style={[styles.welcomeIconWrap, { backgroundColor: c.accent + '15' }]}>
        <Sparkles size={40} stroke={c.accent} />
      </View>
      <Text style={[styles.welcomeTitle, { color: c.text }]}>
        {lang === 'ar' ? `أهلاً بيك، ${twinName || 'توأمك'} جاهز!` : `Welcome! ${twinName || 'Your Twin'} is ready!`}
      </Text>
      <Text style={[styles.welcomeSub, { color: c.subtext }]}>
        {lang === 'ar' ? 'ابدأ محادثة أو اختر من الاقتراحات' : 'Start a conversation or pick a suggestion'}
      </Text>
      <View style={styles.suggestionsWrap}>
        {suggestions.map((s, i) => (
          <TouchableOpacity
            key={i}
            style={[styles.suggestionChip, { backgroundColor: c.inputBg, borderColor: c.border }]}
            onPress={() => onSuggestion(s)}
            activeOpacity={0.7}
          >
            <Text style={[styles.suggestionText, { color: c.text }]}>{s}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
});

// ==================== MAIN CHAT ====================

export default function Chat() {
  const insets = useSafeAreaInsets();
  const {
    userId, twinName, twinGender, tier, chatHistory, addMessage,
    triggerHaptic, lang, theme, setTwinName, setTwinGender,
    openMenu, closeMenu, voiceEnabled, setVoiceEnabled,
    bondLevel, setThinking, setThinkingStage,
    incrementDailyMessage, recordInteraction, getEnergyPercent,
    resetDailyIfNeeded,
  } = useTwinStore((s) => ({
    userId: s.userId, twinName: s.twinName, twinGender: s.twinGender, tier: s.tier,
    chatHistory: s.chatHistory, addMessage: s.addMessage,
    triggerHaptic: s.triggerHaptic, lang: s.lang, theme: s.theme,
    setTwinName: s.setTwinName, setTwinGender: s.setTwinGender,
    openMenu: s.openMenu, closeMenu: s.closeMenu,
    voiceEnabled: s.voiceEnabled, setVoiceEnabled: s.setVoiceEnabled,
    bondLevel: s.bondLevel, setThinking: s.setThinking, setThinkingStage: s.setThinkingStage,
    incrementDailyMessage: s.incrementDailyMessage,
    recordInteraction: s.recordInteraction,
    getEnergyPercent: s.getEnergyPercent,
    resetDailyIfNeeded: s.resetDailyIfNeeded,
  }));

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAttach, setShowAttach] = useState(false);
  const [messageQueue, setMessageQueue] = useState<Array<{ msg?: string; image?: string }>>([]);
  // ✅ إصلاح: استخدام getEnergyPercent() من Store بدلاً من state محلي
  const [twinEnergy, setTwinEnergy] = useState(() => getEnergyPercent());
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [activeToolsList, setActiveToolsList] = useState<any[]>([]);
  const [editingContent, setEditingContent] = useState('');
  const [feedbackMap, setFeedbackMap] = useState<Record<string, 'like' | 'dislike' | null>>({});
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const flatRef = useRef<FlatList<ChatMessage>>(null);
  const attachAnim = useRef(new Animated.Value(0)).current;

  const colors = theme === 'dark' ? COLORS.dark : COLORS.light;
  const isRTL = lang === 'ar';
  const isDark = theme === 'dark';

  // ✅ إصلاح: تحديث الطاقة من Store مباشرة
  useEffect(() => {
    const energy = getEnergyPercent();
    setTwinEnergy(energy);
  }, [chatHistory.length, getEnergyPercent]);

  // ✅ التحقق من التصفير اليومي كل دقيقة
  useEffect(() => {
    const interval = setInterval(() => {
      const wasReset = resetDailyIfNeeded();
      if (wasReset) {
        setTwinEnergy(100);
        Alert.alert(
          lang === 'ar' ? 'تم التجدد! ✨' : 'Refreshed! ✨',
          lang === 'ar' ? 'تم تجديد طاقة توأمك بعد 20 ساعة' : 'Your twin energy has been renewed after 20 hours'
        );
      }
    }, 60000);
    return () => clearInterval(interval);
  }, [resetDailyIfNeeded, lang]);

  // Scroll to end
  useEffect(() => {
    const t = setTimeout(() => flatRef.current?.scrollToEnd({ animated: true }), 100);
    return () => clearTimeout(t);
  }, [chatHistory, editingMessageId]);

  // Animate attach menu
  useEffect(() => {
    Animated.spring(attachAnim, {
      toValue: showAttach ? 1 : 0,
      useNativeDriver: true,
      tension: 65,
      friction: 11,
    }).start();
  }, [showAttach]);

  // Process message queue
  useEffect(() => {
    if (messageQueue.length > 0 && !loading) {
      const next = messageQueue[0];
      setMessageQueue(prev => prev.slice(1));
      sendMessage(next.msg, next.image);
    }
  }, [messageQueue, loading]);

  // Load twin profile
  useEffect(() => {
    (async () => {
      if (!userId) return;
      try {
        const { data: profile } = await supabase
          .from('profiles')
          .select('twin_name, twin_gender')
          .eq('id', userId)
          .single();
        if (profile) {
          if (profile.twin_name) setTwinName(profile.twin_name);
          if (profile.twin_gender) setTwinGender(profile.twin_gender);
        }
      } catch (e) {
        console.warn('Profile load failed:', e);
      }
    })();
  }, [userId, setTwinName, setTwinGender]);


  // ==================== SESSIONS ====================

  const createSessionIfNeeded = useCallback(async () => {
    if (currentSessionId || !userId) return;
    try {
      const { data, error } = await supabase
        .from('chat_sessions')
        .insert({ user_id: userId, messages: [] })
        .select('id')
        .single();
      if (data && !error) setCurrentSessionId(data.id);
    } catch (e) {
      console.warn('Session creation failed:', e);
    }
  }, [currentSessionId, userId]);

  const updateSession = useCallback(async (messages: ChatMessage[]) => {
    if (!currentSessionId || !userId) return;
    try {
      await supabase
        .from('chat_sessions')
        .update({ messages, updated_at: new Date().toISOString() })
        .eq('id', currentSessionId);
    } catch (e) {
      console.warn('Session update failed:', e);
    }
  }, [currentSessionId, userId]);

  // ==================== FEEDBACK ====================

  const saveFeedback = useCallback(async (messageId: string, rating: 'like' | 'dislike') => {
    if (!userId) return;
    try {
      await supabase.from('message_feedback').upsert({
        user_id: userId,
        message_id: messageId,
        rating,
        created_at: new Date().toISOString(),
      }, { onConflict: 'user_id,message_id' });
    } catch (e) {
      console.warn('Feedback save failed:', e);
    }
  }, [userId]);

  const handleLike = useCallback((msg: ChatMessage) => {
    const current = feedbackMap[msg.id];
    if (current === 'like') {
      setFeedbackMap(prev => ({ ...prev, [msg.id]: null }));
    } else {
      setFeedbackMap(prev => ({ ...prev, [msg.id]: 'like' }));
      saveFeedback(msg.id, 'like');
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }
  }, [feedbackMap, saveFeedback]);

  const handleDislike = useCallback((msg: ChatMessage) => {
    const current = feedbackMap[msg.id];
    if (current === 'dislike') {
      setFeedbackMap(prev => ({ ...prev, [msg.id]: null }));
    } else {
      setFeedbackMap(prev => ({ ...prev, [msg.id]: 'dislike' }));
      saveFeedback(msg.id, 'dislike');
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    }
  }, [feedbackMap, saveFeedback]);

  // ==================== SEND MESSAGE ====================

  const sendMessage = useCallback(async (msg?: string, imageBase64?: string) => {
    const message = (msg || input).trim();
    if (!message && !imageBase64 && activeToolsList.length === 0) return;

    // ✅ التحقق من الطاقة من Store
    const energy = getEnergyPercent();
    if (energy <= 0 && !activeToolsList.length) {
      Alert.alert(
        lang === 'ar' ? '⚡ الطاقة منتهية' : '⚡ Out of Energy',
        lang === 'ar' ? 'انتظر 20 ساعة للتجديد أو اترقّى' : 'Wait 20 hours for renewal or upgrade'
      );
      return;
    }

    await createSessionIfNeeded();

    const msgId = Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
    const userMsg: ChatMessage = {
      id: msgId,
      role: 'user',
      content: message || (imageBase64 ? '📷 صورة' : ''),
      image: imageBase64,
      timestamp: Date.now(),
    };
    addMessage(userMsg);

    setInput('');
    setLoading(true);
    setThinking(true);
    setThinkingStage('thinking');

    try {
      if (activeToolsList.length > 0) {
        const tool = activeToolsList[0];
        let result = '';
        let location = 'Cairo';

        if (tool.type === 'weather') {
          try {
            const { status } = await Location.requestForegroundPermissionsAsync();
            if (status === 'granted') {
              const loc = await Location.getCurrentPositionAsync({});
              location = `${loc.coords.latitude},${loc.coords.longitude}`;
            }
          } catch { /* fallback to Cairo */ }
        }

        switch (tool.type) {
          case 'weather': result = (await fetchWeather(location)).result || 'الطقس غير متاح'; break;
          case 'youtube': result = (await fetchYouTube(input || 'music')).result || 'لم أجد فيديوهات'; break;
          case 'spotify': result = (await fetchSpotify(input || 'music')).result || 'لم أجد أغاني'; break;
          case 'news': result = (await fetchNews()).result || 'الأخبار غير متاحة'; break;
          case 'currency': result = (await fetchCurrency('USD')).result || 'أسعار العملات غير متاحة'; break;
          default: result = 'الأداة غير مدعومة';
        }

        if (result) {
          const twinMsg: ChatMessage = {
            id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
            role: 'twin',
            content: result,
            timestamp: Date.now(),
            provider: 'tool',
          };
          addMessage(twinMsg);
          if (voiceEnabled) {
            await speakResponse(result, {
              onStart: () => console.log('🔊 TTS started'),
              onDone: () => console.log('🔊 TTS done'),
            });
          }
        }
        setActiveToolsList([]);
        setLoading(false);
        setThinking(false);
        return;
      }

      const response = await sendChatFromStore(message, imageBase64);
      const youtubeRegex = /https?:\/\/(?:www\.)?youtube\.com\/watch\?v=[\w-]+|https?:\/\/youtu\.be\/[\w-]+/g;
      const youtubeLinks = response.reply.match(youtubeRegex);

      const twinMsg: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
        role: 'twin',
        content: response.reply,
        timestamp: Date.now(),
        emotion: response.emotion?.primary,
        memoryRecall: response.memory_used,
        thinkingStage: response.thinking_stage,
        youtubeVideo: youtubeLinks ? youtubeLinks[0] : undefined,
        provider: response.provider || 'multi_ai',
      };
      addMessage(twinMsg);
      updateStoreFromResponse(response);

      // ✅ تحديث الطاقة والترابط
      const tokenEstimate = Math.ceil(message.length / 4) + Math.ceil(response.reply.length / 4);
      incrementDailyMessage(tokenEstimate);
      recordInteraction(1);

      // ✅ تحديث الطاقة المحلية من Store
      setTwinEnergy(getEnergyPercent());

      const updatedHistory = useTwinStore.getState().chatHistory;
      updateSession(updatedHistory);

      if (voiceEnabled) {
        try {
          await speakResponse(response.reply, {
            onStart: () => console.log('🔊 Speaking started'),
            onDone: () => console.log('🔊 Speaking finished'),
          });
        } catch (e) {
          console.warn('Voice failed:', e);
        }
      }

    } catch (error: any) {
      const isAr = lang === 'ar';
      let errMsg = '';
      if (error?.response) {
        const status = error.response.status;
        if (status === 401) errMsg = isAr ? 'انتهت الجلسة 🔒' : 'Session expired 🔒';
        else if (status === 429) errMsg = isAr ? 'تم تجاوز الحد اليومي ⏳' : 'Daily limit reached ⏳';
        else if (status >= 500) errMsg = isAr ? 'السيرفر غير متاح حالياً 🔧' : 'Server unavailable 🔧';
        else errMsg = isAr ? `خطأ ${status} 😬` : `Error ${status} 😬`;
      } else if (error?.message === 'Network Error') {
        errMsg = isAr ? 'لا يوجد اتصال بالإنترنت 📡' : 'No internet connection 📡';
      } else if (error?.code === 'ECONNABORTED' || error?.name === 'AbortError') {
        errMsg = isAr ? 'الطلب استغرق وقتاً طويلاً 🐌' : 'Request timed out 🐌';
      } else {
        errMsg = isAr ? 'حدث خطأ غير متوقع 🌪️' : 'Unexpected error 🌪️';
      }

      const errorMsg: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
        role: 'twin',
        content: errMsg,
        timestamp: Date.now(),
        failed: true,
        provider: 'error',
      };
      addMessage(errorMsg);
    } finally {
      setLoading(false);
      setThinking(false);
    }
  }, [
    input, loading, voiceEnabled, lang, addMessage, setThinking, setThinkingStage,
    activeToolsList, currentSessionId, userId, createSessionIfNeeded,
    updateSession, getEnergyPercent, incrementDailyMessage, recordInteraction,
  ]);

  const send = useCallback(async (msg?: string, imageBase64?: string) => {
    if (loading) {
      setMessageQueue(prev => [...prev, { msg, image: imageBase64 }]);
      return;
    }
    triggerHaptic();
    await sendMessage(msg, imageBase64);
  }, [loading, sendMessage, triggerHaptic]);

  // ==================== HANDLERS ====================

  const handleCopy = useCallback((content: string) => {
    Clipboard.setStringAsync(content);
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  }, []);

  const handleRetry = useCallback((failedMsg: ChatMessage) => {
    sendMessage(failedMsg.content, failedMsg.image);
  }, [sendMessage]);

  const handleRegenerate = useCallback((lastMsg: ChatMessage) => {
    sendMessage(lastMsg.content);
  }, [sendMessage]);

  const toggleSound = useCallback(() => {
    if (voiceEnabled) stopSpeaking();
    setVoiceEnabled(!voiceEnabled);
  }, [voiceEnabled, setVoiceEnabled]);

  const handleEditInInput = useCallback((msg: ChatMessage) => {
    setInput(msg.content);
  }, []);

  const handleStartEdit = useCallback((msg: ChatMessage) => {
    setEditingMessageId(msg.id);
    setEditingContent(msg.content);
  }, []);

  const handleSaveEdit = useCallback((msg: ChatMessage, newContent: string) => {
    if (newContent.trim() && newContent !== msg.content) {
      setEditingMessageId(null);
      sendMessage(newContent.trim(), msg.image);
    } else {
      setEditingMessageId(null);
    }
  }, [sendMessage]);

  // ==================== CAMERA / GALLERY / FILE ====================

  const handleCamera = useCallback(async () => {
    setShowAttach(false);
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) {
      Alert.alert('Permission', lang === 'ar' ? 'مطلوب إذن الكاميرا' : 'Camera permission needed');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({ base64: true, quality: 0.7 });
    if (!result.canceled && result.assets?.[0]?.base64) {
      send('', result.assets[0].base64);
    }
  }, [send, lang]);

  const handleGallery = useCallback(async () => {
    setShowAttach(false);
    const p = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!p.granted) {
      Alert.alert('Permission', lang === 'ar' ? 'مطلوب إذن الصور' : 'Permission needed');
      return;
    }
    const r = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      base64: true,
      quality: 0.7,
    });
    if (!r.canceled && r.assets?.[0]?.base64) {
      send('', r.assets[0].base64);
    }
  }, [send, lang]);

  const handleFile = useCallback(async () => {
    setShowAttach(false);
    try {
      const res = await DocumentPicker.getDocumentAsync({ type: '*/*' });
      if (!res.canceled && res.assets?.[0]) {
        send('📄 ' + (res.assets[0].name || 'ملف مرفق'));
      }
    } catch {
      Alert.alert('Error', lang === 'ar' ? 'فشل اختيار الملف' : 'File selection failed');
    }
  }, [send, lang]);

  // ==================== STT (VOICE INPUT) ====================

  const handleVoiceInput = useCallback(async () => {
    if (isRecording) {
      setIsRecording(false);
      return;
    }

    setIsRecording(true);
    try {
      Alert.alert(
        lang === 'ar' ? '🎤 تسجيل صوتي' : '🎤 Voice Recording',
        lang === 'ar' ? 'اضغط مع الاستمرار للتسجيل' : 'Press and hold to record'
      );
    } catch (e) {
      console.warn('Voice input failed:', e);
    } finally {
      setIsRecording(false);
    }
  }, [isRecording, lang]);

  // ==================== TOOLS ====================

  const handleAddTool = useCallback((toolDef: any) => {
    setActiveToolsList(prev => [...prev, { id: Date.now().toString(), ...toolDef }]);
  }, []);

  const handleRemoveTool = useCallback((toolId: string) => {
    setActiveToolsList(prev => prev.filter(t => t.id !== toolId));
  }, []);

  // ==================== REFRESH ====================

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      const energy = getEnergyPercent();
      setTwinEnergy(energy);
    } catch (e) {
      console.warn('Refresh failed:', e);
    }
    setRefreshing(false);
  }, [getEnergyPercent]);


  // ==================== RENDER ====================

  const renderMsg = useCallback(({ item, index }: { item: ChatMessage; index: number }) => {
    const isLast = index === chatHistory.length - 1;
    if (item.role === 'user') {
      return (
        <UserBubble
          item={item}
          isDark={isDark}
          isRTL={isRTL}
          onStartEdit={handleStartEdit}
          onSaveEdit={handleSaveEdit}
          isEditing={editingMessageId === item.id}
          editContent={editingContent}
          setEditContent={setEditingContent}
          onEditInInput={handleEditInInput}
        />
      );
    }
    return (
      <TwinBubble
        item={item}
        isDark={isDark}
        isRTL={isRTL}
        isLast={isLast}
        onCopy={handleCopy}
        onRetry={handleRetry}
        onRegenerate={handleRegenerate}
        onLike={handleLike}
        onDislike={handleDislike}
        liked={feedbackMap[item.id] === 'like'}
        disliked={feedbackMap[item.id] === 'dislike'}
        provider={item.provider}
      />
    );
  }, [
    isDark, isRTL, chatHistory.length, editingMessageId, editingContent,
    handleCopy, handleRetry, handleRegenerate, handleLike, handleDislike,
    handleStartEdit, handleSaveEdit, handleEditInInput, feedbackMap,
  ]);

  const ListFooter = useCallback(() => {
    if (!loading) return null;
    return (
      <View style={styles.typingRow}>
        <Image source={APP_ICON} style={{ width: 28, height: 28, borderRadius: 14 }} />
        <TypingIndicator />
      </View>
    );
  }, [loading]);

  const ListHeader = useCallback(() => {
    if (chatHistory.length > 0) return null;
    return (
      <WelcomeState
        isDark={isDark}
        lang={lang}
        twinName={twinName}
        onSuggestion={(s: string) => send(s)}
      />
    );
  }, [chatHistory.length, isDark, lang, twinName, send]);

  return (
    <View style={[styles.root, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} backgroundColor={colors.bg} />

      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        {/* Header */}
        <View style={[styles.header, { backgroundColor: colors.headerBg, borderBottomColor: colors.border }]}>
          <TouchableOpacity onPress={openMenu} style={styles.menuBtn}>
            <Menu size={22} stroke={colors.text} />
          </TouchableOpacity>

          <View style={styles.headerCenter}>
            <Text style={[styles.headerName, { color: colors.text }]} numberOfLines={1}>
              {twinName || (lang === 'ar' ? 'توأمك' : 'Your Twin')}
            </Text>
            <View style={styles.miniIndicators}>
              <View style={[
                styles.energyDot,
                {
                  backgroundColor: twinEnergy > 60 ? '#34C759' : twinEnergy > 25 ? '#FF9500' : '#FF3B30',
                  shadowColor: twinEnergy > 60 ? '#34C759' : twinEnergy > 25 ? '#FF9500' : '#FF3B30',
                }
              ]} />
              <Text style={[styles.miniText, { color: colors.subtext }]}>
                {Math.round(bondLevel)}%
              </Text>
              <Text style={[styles.miniText, { color: colors.subtext, fontSize: 10 }]}>
                | {twinEnergy}%
              </Text>
            </View>
          </View>

          <View style={{ flexDirection: 'row', gap: 8 }}>
            <TouchableOpacity
              onPress={handleVoiceInput}
              style={[styles.iconBtn, isRecording && styles.recordingBtn]}
            >
              {isRecording ? (
                <MicOff size={20} stroke="#FF3B30" />
              ) : (
                <Mic size={20} stroke={colors.text} />
              )}
            </TouchableOpacity>

            <TouchableOpacity onPress={toggleSound} style={styles.iconBtn}>
              {voiceEnabled ? (
                <Volume2 size={22} stroke={colors.text} />
              ) : (
                <VolumeX size={22} stroke={colors.subtext} />
              )}
            </TouchableOpacity>
          </View>
        </View>

        {/* Messages */}
        <FlatList
          ref={flatRef}
          data={chatHistory}
          keyExtractor={(item) => item.id}
          renderItem={renderMsg}
          ListHeaderComponent={ListHeader}
          ListFooterComponent={ListFooter}
          contentContainerStyle={styles.listContent}
          onContentSizeChange={() => flatRef.current?.scrollToEnd({ animated: false })}
          removeClippedSubviews
          initialNumToRender={10}
          maxToRenderPerBatch={10}
          windowSize={5}
          keyboardDismissMode="interactive"
          keyboardShouldPersistTaps="handled"
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={colors.accent}
              colors={[colors.accent]}
            />
          }
        />

        {/* Input */}
        <ChatInput
          input={input}
          setInput={setInput}
          loading={loading}
          isRTL={isRTL}
          isDark={isDark}
          colors={colors}
          lang={lang}
          onSend={send}
          onAddTool={handleAddTool}
          onRemoveTool={handleRemoveTool}
          activeTools={activeToolsList}
          onCamera={handleCamera}
          onGallery={handleGallery}
          onFile={handleFile}
          showAttach={showAttach}
          setShowAttach={setShowAttach}
          attachAnim={attachAnim}
        />
      </KeyboardAvoidingView>
    </View>
  );
}

// ==================== STYLES ====================

const styles = StyleSheet.create({
  root: { flex: 1 },

  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  menuBtn: { padding: 6, borderRadius: 10 },
  headerCenter: { flex: 1, alignItems: 'center' },
  headerName: { fontSize: 17, fontWeight: '700', letterSpacing: -0.3 },
  miniIndicators: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 4 },
  energyDot: {
    width: 8, height: 8, borderRadius: 4,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5, shadowRadius: 4, elevation: 2,
  },
  miniText: { fontSize: 12, fontWeight: '600' },
  iconBtn: { padding: 6, borderRadius: 10 },
  recordingBtn: { backgroundColor: '#FF3B3015' },

  listContent: { paddingHorizontal: 0, paddingVertical: 12, flexGrow: 1 },
  typingRow: { flexDirection: 'row', alignItems: 'center', paddingLeft: 16, paddingVertical: 12, gap: 10 },

  welcomeContainer: {
    flex: 1, alignItems: 'center', justifyContent: 'center',
    paddingVertical: 60, paddingHorizontal: 24,
  },
  welcomeIconWrap: {
    width: 80, height: 80, borderRadius: 24,
    justifyContent: 'center', alignItems: 'center', marginBottom: 20,
  },
  welcomeTitle: { fontSize: 22, fontWeight: '800', textAlign: 'center', marginBottom: 8, letterSpacing: -0.5 },
  welcomeSub: { fontSize: 15, textAlign: 'center', marginBottom: 24, lineHeight: 22 },
  suggestionsWrap: { gap: 10, width: '100%' },
  suggestionChip: {
    paddingHorizontal: 20, paddingVertical: 14, borderRadius: 16,
    borderWidth: 1, alignItems: 'center',
  },
  suggestionText: { fontSize: 15, fontWeight: '500' },
});
