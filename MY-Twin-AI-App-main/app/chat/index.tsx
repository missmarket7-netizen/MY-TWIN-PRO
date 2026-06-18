import {
  View, FlatList, StyleSheet, StatusBar, KeyboardAvoidingView,
  Platform, Image, Animated, Text, Alert, TouchableOpacity,
  RefreshControl, Dimensions, Linking,
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
  Brain, Cpu, Search, Cloud, Music, Film, DollarSign, TrendingUp,
  ThumbsUp, ThumbsDown, RotateCcw, Copy, Share2, ExternalLink,
} from 'lucide-react-native';
import { speakResponse, stopSpeaking } from '../../utils/voice_engine';
import { COLORS, UserBubble, TwinBubble } from './ChatBubbles';
import { ChatInput } from './ChatInput';

const { width: SCREEN_W } = Dimensions.get('window');
const APP_ICON = require('../../assets/icon.png');

// ==================== مكونات بصرية محسنة ====================

const ThinkingBar = memo(({ stage, isDark }: { stage: string; isDark: boolean }) => {
  const stages: Record<string, { icon: any; text_ar: string; text_en: string; color: string }> = {
    thinking: { icon: Brain, text_ar: 'يفكر...', text_en: 'Thinking...', color: '#8B5CF6' },
    searching_memory: { icon: Search, text_ar: 'يبحث في الذكريات...', text_en: 'Searching memories...', color: '#3B82F6' },
    using_tool: { icon: Cloud, text_ar: 'يستخدم الأدوات...', text_en: 'Using tools...', color: '#10B981' },
    generating: { icon: Sparkles, text_ar: 'يصيغ الرد...', text_en: 'Crafting response...', color: '#F59E0B' },
    completed: { icon: Sparkles, text_ar: 'تم!', text_en: 'Done!', color: '#10B981' },
  };
  const info = stages[stage] || stages.thinking;
  const Icon = info.icon;
  return (
    <View style={[thinkStyles.container, { backgroundColor: info.color + '15' }]}>
      <Icon size={16} stroke={info.color} />
      <Text style={[thinkStyles.text, { color: info.color }]}>🧠 {info.text_ar}</Text>
    </View>
  );
});
const thinkStyles = StyleSheet.create({
  container: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, alignSelf: 'center', marginVertical: 8 },
  text: { fontSize: 13, fontWeight: '600' },
});

const MemoryChip = memo(({ text, isDark }: { text?: string; isDark: boolean }) => {
  const displayText = text || 'اعتمدت على ذاكرة سابقة';
  return (
    <View style={[memStyles.chip, { backgroundColor: '#8B5CF620', borderColor: '#8B5CF640' }]}>
      <Brain size={12} stroke="#8B5CF6" />
      <Text style={memStyles.text}>🧠 {displayText}</Text>
    </View>
  );
});
const memStyles = StyleSheet.create({
  chip: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 10, borderWidth: 1, alignSelf: 'flex-start', marginTop: 6 },
  text: { fontSize: 11, color: '#8B5CF6', fontWeight: '600' },
});

const ProviderBadge = memo(({ provider, isDark }: { provider: string; isDark: boolean }) => {
  const normalizedProvider = provider.includes('council') ? 'council' : provider.split('/')[0];
  const config: Record<string, { label: string; color: string; icon: any }> = {
    groq: { label: '⚡ Groq', color: '#F59E0B', icon: Cpu },
    gemini: { label: '🧠 Gemini', color: '#10B981', icon: Brain },
    openrouter: { label: '🦙 Llama', color: '#3B82F6', icon: Cpu },
    council: { label: '👑 Council', color: '#EC4899', icon: Sparkles },
    tool: { label: '🔧 Tool', color: '#6366F1', icon: Cloud },
    agent_loop: { label: '🤖 Agent', color: '#EC4899', icon: Search },
    fallback: { label: '🔄 Fallback', color: '#EF4444', icon: RotateCcw },
  };
  const info = config[normalizedProvider] || { label: provider, color: '#666', icon: Cpu };
  const Icon = info.icon;
  return (
    <View style={[provStyles.badge, { backgroundColor: info.color + '15', borderColor: info.color + '30' }]}>
      <Icon size={10} stroke={info.color} />
      <Text style={[provStyles.text, { color: info.color }]}>{info.label}</Text>
    </View>
  );
});
const provStyles = StyleSheet.create({
  badge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8, borderWidth: 1, alignSelf: 'flex-start', marginTop: 6 },
  text: { fontSize: 10, fontWeight: '600' },
});

const ToolCard = memo(({ type, content, isDark }: { type: string; content: string; isDark: boolean }) => {
  const bg = isDark ? '#2A2A2A' : '#F8F6F2';
  const border = isDark ? '#444' : '#E0E0E0';
  const configs: Record<string, { icon: any; color: string; label: string; onPress?: () => void }> = {
    weather: { icon: Cloud, color: '#06B6D4', label: 'الطقس' },
    youtube: { icon: Film, color: '#EF4444', label: 'يوتيوب', onPress: () => {
      const urlMatch = content.match(/https?:\/\/[^\s]+/);
      if (urlMatch) Linking.openURL(urlMatch[0]);
    }},
    spotify: { icon: Music, color: '#EC4899', label: 'موسيقى' },
    news: { icon: TrendingUp, color: '#8B5CF6', label: 'أخبار', onPress: () => {
      const urlMatch = content.match(/https?:\/\/[^\s]+/);
      if (urlMatch) Linking.openURL(urlMatch[0]);
    }},
    currency: { icon: DollarSign, color: '#10B981', label: 'عملات' },
  };
  const cfg = configs[type] || configs.weather;
  const Icon = cfg.icon;
  return (
    <TouchableOpacity 
      style={[toolCardStyles.card, { backgroundColor: bg, borderColor: border }]}
      onPress={cfg.onPress}
      disabled={!cfg.onPress}
      activeOpacity={0.7}
    >
      <View style={[toolCardStyles.iconWrap, { backgroundColor: cfg.color + '15' }]}>
        <Icon size={24} stroke={cfg.color} />
      </View>
      <View style={{ flex: 1 }}>
        <Text style={[toolCardStyles.label, { color: cfg.color }]}>{cfg.label}</Text>
        <Text style={[toolCardStyles.content, { color: isDark ? '#CCC' : '#444' }]} numberOfLines={3}>{content}</Text>
      </View>
      {cfg.onPress && <ExternalLink size={16} stroke={isDark ? '#999' : '#666'} />}
    </TouchableOpacity>
  );
});
const toolCardStyles = StyleSheet.create({
  card: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 12, borderRadius: 16, borderWidth: 1, marginVertical: 6 },
  iconWrap: { width: 44, height: 44, borderRadius: 14, justifyContent: 'center', alignItems: 'center' },
  label: { fontSize: 14, fontWeight: '700', marginBottom: 4 },
  content: { fontSize: 13, lineHeight: 20 },
});

const VoiceIndicator = memo(({ type, isDark }: { type: 'speaking' | 'listening'; isDark: boolean }) => {
  const color = type === 'speaking' ? '#10B981' : '#EF4444';
  const text = type === 'speaking' ? '🔊 التوأم يتحدث...' : '🎤 جاري الاستماع...';
  return (
    <View style={[voiceStyles.bar, { backgroundColor: color + '15' }]}>
      <Text style={[voiceStyles.text, { color }]}>{text}</Text>
    </View>
  );
});
const voiceStyles = StyleSheet.create({
  bar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 6, paddingHorizontal: 16, borderRadius: 12, alignSelf: 'center', marginVertical: 4 },
  text: { fontSize: 13, fontWeight: '600' },
});

const EmotionBadge = memo(({ emotion, isDark }: { emotion: string; isDark: boolean }) => {
  const config: Record<string, { emoji: string; color: string }> = {
    joy: { emoji: '😊', color: '#F59E0B' },
    sadness: { emoji: '😔', color: '#3B82F6' },
    anger: { emoji: '😤', color: '#EF4444' },
    fear: { emoji: '😰', color: '#A78BFA' },
    love: { emoji: '💕', color: '#EC4899' },
    surprise: { emoji: '🤩', color: '#10B981' },
    neutral: { emoji: '😌', color: '#6B7280' },
    anxiety: { emoji: '😰', color: '#A78BFA' },
    stress: { emoji: '😫', color: '#EF4444' },
    confusion: { emoji: '🤔', color: '#F59E0B' },
    excitement: { emoji: '🤩', color: '#10B981' },
  };
  const info = config[emotion] || config.neutral;
  return (
    <View style={[emoStyles.badge, { backgroundColor: info.color + '15', borderColor: info.color + '30' }]}>
      <Text style={{ fontSize: 14 }}>{info.emoji}</Text>
    </View>
  );
});
const emoStyles = StyleSheet.create({
  badge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8, borderWidth: 1, alignSelf: 'flex-start', marginTop: 6 },
});

const WelcomeState = memo(({ isDark, lang, twinName, onSuggestion, hasSession, onResume }: any) => {
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
      {hasSession && (
        <TouchableOpacity 
          style={[styles.resumeBtn, { backgroundColor: '#7C3AED20', borderColor: '#7C3AED' }]}
          onPress={onResume}
        >
          <Text style={{ color: '#7C3AED', fontWeight: '600' }}>
            {lang === 'ar' ? '📋 استكمال المحادثة السابقة' : '📋 Resume previous conversation'}
          </Text>
        </TouchableOpacity>
      )}
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

export default function Chat() {
  const insets = useSafeAreaInsets();
  const {
    userId, twinName, twinGender, tier, chatHistory, addMessage,
    triggerHaptic, lang, theme, setTwinName, setTwinGender,
    openMenu, closeMenu, voiceEnabled, setVoiceEnabled,
    bondLevel, setThinking, setThinkingStage, thinkingStage,
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
    thinkingStage: s.thinkingStage,
    incrementDailyMessage: s.incrementDailyMessage,
    recordInteraction: s.recordInteraction,
    getEnergyPercent: s.getEnergyPercent,
    resetDailyIfNeeded: s.resetDailyIfNeeded,
  }));

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAttach, setShowAttach] = useState(false);
  const messageQueue = useRef<Array<{ msg?: string; image?: string }>>([]);
  const [queueVersion, setQueueVersion] = useState(0);
  const [twinEnergy, setTwinEnergy] = useState(() => getEnergyPercent());
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [activeToolsList, setActiveToolsList] = useState<any[]>([]);
  const [editingContent, setEditingContent] = useState('');
  const [feedbackMap, setFeedbackMap] = useState<Record<string, 'like' | 'dislike' | null>>({});
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState<'speaking' | 'listening' | null>(null);
  const [hasPreviousSession, setHasPreviousSession] = useState(false);

  const flatRef = useRef<FlatList<ChatMessage>>(null);
  const attachAnim = useRef(new Animated.Value(0)).current;

  const colors = theme === 'dark' ? COLORS.dark : COLORS.light;
  const isRTL = lang === 'ar';
  const isDark = theme === 'dark';

  useEffect(() => { setTwinEnergy(getEnergyPercent()); }, [chatHistory.length, getEnergyPercent]);
  useEffect(() => {
    const interval = setInterval(() => {
      const wasReset = resetDailyIfNeeded();
      if (wasReset) setTwinEnergy(100);
    }, 60000);
    return () => clearInterval(interval);
  }, [resetDailyIfNeeded]);

  useEffect(() => {
    if (!userId) return;
    (async () => {
      const { data } = await supabase.from('chat_sessions').select('id').eq('user_id', userId).order('created_at', { ascending: false }).limit(1);
      setHasPreviousSession(!!data?.length);
    })();
  }, [userId]);

  useEffect(() => {
    const t = setTimeout(() => flatRef.current?.scrollToEnd({ animated: true }), 100);
    return () => clearTimeout(t);
  }, [chatHistory, editingMessageId]);

  useEffect(() => {
    Animated.spring(attachAnim, { toValue: showAttach ? 1 : 0, useNativeDriver: true, tension: 65, friction: 11 }).start();
  }, [showAttach]);

  useEffect(() => {
    if (messageQueue.current.length > 0 && !loading) {
      const next = messageQueue.current[0];
      messageQueue.current = messageQueue.current.slice(1);
      setQueueVersion(v => v + 1);
      sendMessage(next.msg, next.image);
    }
  }, [queueVersion, loading]);

  useEffect(() => {
    (async () => {
      if (!userId) return;
      try {
        const { data: profile } = await supabase.from('profiles').select('twin_name, twin_gender').eq('id', userId).single();
        if (profile) {
          if (profile.twin_name) setTwinName(profile.twin_name);
          if (profile.twin_gender) setTwinGender(profile.twin_gender);
        }
      } catch {}
    })();
  }, [userId]);

  const createSessionIfNeeded = useCallback(async () => {
    if (currentSessionId || !userId) return;
    try {
      const { data, error } = await supabase.from('chat_sessions').insert({ user_id: userId, messages: [] }).select('id').single();
      if (data && !error) setCurrentSessionId(data.id);
    } catch {}
  }, [currentSessionId, userId]);

  const updateSession = useCallback(async (messages: ChatMessage[]) => {
    if (!currentSessionId || !userId) return;
    try {
      await supabase.from('chat_sessions').update({ messages, updated_at: new Date().toISOString() }).eq('id', currentSessionId);
    } catch {}
  }, [currentSessionId, userId]);

  const resumeLastSession = useCallback(async () => {
    if (!userId) return;
    try {
      const { data } = await supabase.from('chat_sessions').select('messages').eq('user_id', userId).order('created_at', { ascending: false }).limit(1).single();
      if (data?.messages) {
        useTwinStore.getState().addMessage(data.messages);
      }
    } catch {}
  }, [userId]);

  const saveFeedback = useCallback(async (messageId: string, rating: 'like' | 'dislike') => {
    if (!userId) return;
    try {
      await supabase.from('message_feedback').upsert({ user_id: userId, message_id: messageId, rating, created_at: new Date().toISOString() }, { onConflict: 'user_id,message_id' });
    } catch {}
  }, [userId]);

  const handleLike = useCallback((msg: ChatMessage) => {
    const current = feedbackMap[msg.id];
    setFeedbackMap(prev => ({ ...prev, [msg.id]: current === 'like' ? null : 'like' }));
    if (current !== 'like') { saveFeedback(msg.id, 'like'); Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success); }
  }, [feedbackMap, saveFeedback]);

  const handleDislike = useCallback((msg: ChatMessage) => {
    const current = feedbackMap[msg.id];
    setFeedbackMap(prev => ({ ...prev, [msg.id]: current === 'dislike' ? null : 'dislike' }));
    if (current !== 'dislike') { saveFeedback(msg.id, 'dislike'); Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning); }
  }, [feedbackMap, saveFeedback]);

  const sendMessage = useCallback(async (msg?: string, imageBase64?: string) => {
    const message = (msg || input).trim();
    if (!message && !imageBase64 && activeToolsList.length === 0) return;

    const energy = getEnergyPercent();
    if (energy <= 0 && !activeToolsList.length) {
      Alert.alert(lang === 'ar' ? '⚡ الطاقة منتهية' : '⚡ Out of Energy', lang === 'ar' ? 'انتظر 20 ساعة للتجديد أو اترقّى' : 'Wait 20 hours for renewal or upgrade');
      return;
    }

    await createSessionIfNeeded();

    const msgId = Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
    addMessage({ id: msgId, role: 'user', content: message || (imageBase64 ? '📷 صورة' : ''), image: imageBase64, timestamp: Date.now() });

    setInput('');
    setLoading(true);
    setThinking(true);
    setThinkingStage('thinking');

    try {
      if (activeToolsList.length > 0) {
        setThinkingStage('using_tool');
        const toolPromises = activeToolsList.map(async (tool) => {
          let result = '';
          let location = 'Cairo';
          if (tool.type === 'weather') {
            try {
              const { status } = await Location.requestForegroundPermissionsAsync();
              if (status === 'granted') { const loc = await Location.getCurrentPositionAsync({}); location = `${loc.coords.latitude},${loc.coords.longitude}`; }
            } catch {}
          }
          switch (tool.type) {
            case 'weather': result = (await fetchWeather(location)).result || ''; break;
            case 'youtube': result = (await fetchYouTube(input || 'music')).result || ''; break;
            case 'spotify': result = (await fetchSpotify(input || 'music')).result || ''; break;
            case 'news': result = (await fetchNews()).result || ''; break;
            case 'currency': result = (await fetchCurrency('USD')).result || ''; break;
          }
          return { type: tool.type, result, success: !!result };
        });

        const settledResults = await Promise.allSettled(toolPromises);
        settledResults.forEach((res) => {
          if (res.status === 'fulfilled' && res.value.success) {
            addMessage({
              id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
              role: 'twin', content: res.value.result, timestamp: Date.now(), provider: 'tool',
              toolType: res.value.type,
            });
          }
        });
        setActiveToolsList([]);
        setThinkingStage('completed');
        setLoading(false); setThinking(false);
        return;
      }

      setThinkingStage('generating');
      const response = await sendChatFromStore(message, imageBase64);
      const youtubeRegex = /https?:\/\/(?:www\.)?youtube\.com\/watch\?v=[\w-]+|https?:\/\/youtu\.be\/[\w-]+/g;
      const youtubeLinks = response.reply?.match(youtubeRegex);

      addMessage({
        id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
        role: 'twin', content: response.reply, timestamp: Date.now(),
        emotion: response.emotion?.primary, memoryRecall: response.memory_used,
        thinkingStage: response.thinking_stage, youtubeVideo: youtubeLinks ? youtubeLinks[0] : undefined,
        provider: response.provider || 'multi_ai',
      });
      updateStoreFromResponse(response);
      incrementDailyMessage(Math.ceil(message.length / 4) + Math.ceil((response.reply?.length || 0) / 4));
      recordInteraction(1);
      setTwinEnergy(getEnergyPercent());
      
      setTimeout(() => {
        updateSession(useTwinStore.getState().chatHistory);
      }, 0);

      if (voiceEnabled) {
        setVoiceStatus('speaking');
        try { await speakResponse(response.reply); } catch {}
        setVoiceStatus(null);
      }
      setThinkingStage('completed');

    } catch (error: any) {
      const isAr = lang === 'ar';
      let errMsg = '';
      if (error?.response) {
        const status = error.response.status;
        if (status === 401) errMsg = isAr ? 'انتهت الجلسة يا وحش 😅 سجّل دخول تاني' : 'Session expired buddy 😅 Log in again';
        else if (status === 429) errMsg = isAr ? 'استهدى بالله! كده كتير 🤯 جرب بعد شوية' : 'Whoa slow down! 🤯 Try later';
        else if (status >= 500) errMsg = isAr ? 'السيرفر نام شوية ☕ هنصحيه ونكمل' : 'Server napping ☕ waking it up';
        else errMsg = isAr ? `حصل خطأ ${status} 😬 جرب تاني` : `Error ${status} 😬 Try again`;
      } else if (error?.message === 'Network Error') {
        errMsg = isAr ? 'الإنترنت طاير 😵‍💫 شوف الواي فاي' : 'No internet 😵‍💫 Check Wi-Fi';
      } else if (error?.code === 'ECONNABORTED' || error?.name === 'AbortError') {
        errMsg = isAr ? 'النت بطيء 🐌 اصبر شوية' : 'Too slow 🐌 Wait a bit';
      } else {
        errMsg = isAr ? 'حصل حاجة غريبة 🌪️ جرب تاني' : 'Something weird 🌪️ Try again';
      }
      addMessage({ id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36), role: 'twin', content: errMsg, timestamp: Date.now(), failed: true, provider: 'error' });
    } finally {
      setLoading(false); setThinking(false);
    }
  }, [input, loading, voiceEnabled, lang, addMessage, setThinking, setThinkingStage, activeToolsList, currentSessionId, userId, createSessionIfNeeded, updateSession, getEnergyPercent, incrementDailyMessage, recordInteraction]);

  const send = useCallback(async (msg?: string, imageBase64?: string) => {
    if (loading) {
      messageQueue.current = [...messageQueue.current, { msg, image: imageBase64 }];
      setQueueVersion(v => v + 1);
      return;
    }
    triggerHaptic();
    await sendMessage(msg, imageBase64);
  }, [loading, sendMessage, triggerHaptic]);

  const handleCopy = useCallback((content: string) => { Clipboard.setStringAsync(content); Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success); }, []);
  const handleRetry = useCallback((failedMsg: ChatMessage) => { sendMessage(failedMsg.content, failedMsg.image); }, [sendMessage]);
  const handleRegenerate = useCallback((lastMsg: ChatMessage) => { sendMessage(lastMsg.content); }, [sendMessage]);
  const toggleSound = useCallback(() => { if (voiceEnabled) stopSpeaking(); setVoiceEnabled(!voiceEnabled); }, [voiceEnabled, setVoiceEnabled]);
  const handleEditInInput = useCallback((msg: ChatMessage) => { setInput(msg.content); }, []);
  const handleStartEdit = useCallback((msg: ChatMessage) => { setEditingMessageId(msg.id); setEditingContent(msg.content); }, []);
  const handleSaveEdit = useCallback((msg: ChatMessage, newContent: string) => {
    if (newContent.trim() && newContent !== msg.content) { setEditingMessageId(null); sendMessage(newContent.trim(), msg.image); }
    else { setEditingMessageId(null); }
  }, [sendMessage]);

  const handleCamera = useCallback(async () => {
    setShowAttach(false);
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) { Alert.alert('Permission', lang === 'ar' ? 'مطلوب إذن الكاميرا' : 'Camera permission needed'); return; }
    const result = await ImagePicker.launchCameraAsync({ base64: true, quality: 0.7 });
    if (!result.canceled && result.assets?.[0]?.base64) send('', result.assets[0].base64);
  }, [send, lang]);

  const handleGallery = useCallback(async () => {
    setShowAttach(false);
    const p = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!p.granted) { Alert.alert('Permission', lang === 'ar' ? 'مطلوب إذن الصور' : 'Permission needed'); return; }
    const r = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, base64: true, quality: 0.7 });
    if (!r.canceled && r.assets?.[0]?.base64) send('', r.assets[0].base64);
  }, [send, lang]);

  const handleFile = useCallback(async () => {
    setShowAttach(false);
    try {
      const res = await DocumentPicker.getDocumentAsync({ type: '*/*' });
      if (!res.canceled && res.assets?.[0]) send('📄 ' + (res.assets[0].name || 'ملف مرفق'));
    } catch { Alert.alert('Error', lang === 'ar' ? 'فشل اختيار الملف' : 'File selection failed'); }
  }, [send, lang]);

  const handleVoiceInput = useCallback(async () => {
    if (isRecording) { setIsRecording(false); setVoiceStatus(null); return; }
    setIsRecording(true); setVoiceStatus('listening');
    try {
      setTimeout(() => { setIsRecording(false); setVoiceStatus(null); }, 3000);
    } catch { setIsRecording(false); setVoiceStatus(null); }
  }, [isRecording]);

  const handleAddTool = useCallback((toolDef: any) => { setActiveToolsList(prev => [...prev, { id: Date.now().toString(), ...toolDef }]); }, []);
  const handleRemoveTool = useCallback((toolId: string) => { setActiveToolsList(prev => prev.filter(t => t.id !== toolId)); }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    setTwinEnergy(getEnergyPercent());
    setRefreshing(false);
  }, [getEnergyPercent]);

  const renderMsg = useCallback(({ item, index }: { item: ChatMessage; index: number }) => {
    const isLast = index === chatHistory.length - 1;
    if (item.role === 'user') {
      return (
        <UserBubble
          item={item} isDark={isDark} isRTL={isRTL}
          onStartEdit={handleStartEdit} onSaveEdit={handleSaveEdit}
          isEditing={editingMessageId === item.id} editContent={editingContent}
          setEditContent={setEditingContent} onEditInInput={handleEditInInput}
        />
      );
    }
    return (
      <View>
        {(item as any).toolType && (item as any).provider === 'tool' ? (
          <ToolCard type={(item as any).toolType} content={item.content} isDark={isDark} />
        ) : (
          <TwinBubble
            item={item} isDark={isDark} isRTL={isRTL} isLast={isLast}
            onCopy={handleCopy} onRetry={handleRetry} onRegenerate={handleRegenerate}
            onLike={handleLike} onDislike={handleDislike}
            liked={feedbackMap[item.id] === 'like'} disliked={feedbackMap[item.id] === 'dislike'}
            provider={item.provider}
          />
        )}
        {item.memoryRecall && <MemoryChip text={(item as any).memoryRecallText} isDark={isDark} />}
        {item.provider && item.provider !== 'tool' && !item.failed && (
          <ProviderBadge provider={item.provider} isDark={isDark} />
        )}
        {item.emotion && <EmotionBadge emotion={item.emotion} isDark={isDark} />}
      </View>
    );
  }, [isDark, isRTL, chatHistory.length, editingMessageId, editingContent, handleCopy, handleRetry, handleRegenerate, handleLike, handleDislike, handleStartEdit, handleSaveEdit, handleEditInInput, feedbackMap]);

  const ListFooter = useCallback(() => {
    if (!loading) return null;
    return (
      <View>
        <ThinkingBar stage={thinkingStage} isDark={isDark} />
        <View style={styles.typingRow}>
          <Image source={APP_ICON} style={{ width: 28, height: 28, borderRadius: 14 }} />
          <TypingIndicator />
        </View>
      </View>
    );
  }, [loading, thinkingStage, isDark]);

  const ListHeader = useCallback(() => {
    if (chatHistory.length > 0) return null;
    return (
      <WelcomeState
        isDark={isDark} lang={lang} twinName={twinName}
        onSuggestion={(s: string) => send(s)}
        hasSession={hasPreviousSession}
        onResume={resumeLastSession}
      />
    );
  }, [chatHistory.length, isDark, lang, twinName, send, hasPreviousSession, resumeLastSession]);

  return (
    <View style={[styles.root, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} backgroundColor={colors.bg} />

      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined} keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}>
        <View style={[styles.header, { backgroundColor: colors.headerBg, borderBottomColor: colors.border }]}>
          <TouchableOpacity onPress={openMenu} style={styles.menuBtn}><Menu size={22} stroke={colors.text} /></TouchableOpacity>
          <View style={styles.headerCenter}>
            <Text style={[styles.headerName, { color: colors.text }]} numberOfLines={1}>{twinName || (lang === 'ar' ? 'توأمك' : 'Your Twin')}</Text>
            <View style={styles.miniIndicators}>
              <View style={[styles.energyDot, { backgroundColor: twinEnergy > 60 ? '#34C759' : twinEnergy > 25 ? '#FF9500' : '#FF3B30' }]} />
              <Text style={[styles.miniText, { color: colors.subtext }]}>❤️ {Math.round(bondLevel)}%</Text>
              <Text style={[styles.miniText, { color: colors.subtext, fontSize: 10 }]}>⚡ {twinEnergy}%</Text>
            </View>
          </View>
          <View style={{ flexDirection: 'row', gap: 8 }}>
            <TouchableOpacity onPress={handleVoiceInput} style={[styles.iconBtn, isRecording && styles.recordingBtn]}>
              {isRecording ? <MicOff size={20} stroke="#FF3B30" /> : <Mic size={20} stroke={colors.text} />}
            </TouchableOpacity>
            <TouchableOpacity onPress={toggleSound} style={styles.iconBtn}>
              {voiceEnabled ? <Volume2 size={22} stroke={colors.text} /> : <VolumeX size={22} stroke={colors.subtext} />}
            </TouchableOpacity>
          </View>
        </View>

        {voiceStatus && <VoiceIndicator type={voiceStatus} isDark={isDark} />}

        <FlatList
          ref={flatRef} data={chatHistory} keyExtractor={(item) => item.id}
          renderItem={renderMsg} ListHeaderComponent={ListHeader} ListFooterComponent={ListFooter}
          contentContainerStyle={styles.listContent}
          onContentSizeChange={() => flatRef.current?.scrollToEnd({ animated: false })}
          removeClippedSubviews initialNumToRender={10} maxToRenderPerBatch={10} windowSize={5}
          keyboardDismissMode="interactive" keyboardShouldPersistTaps="handled"
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} colors={[colors.accent]} />}
        />

        <ChatInput
          input={input} setInput={setInput} loading={loading} isRTL={isRTL} isDark={isDark} colors={colors} lang={lang}
          onSend={send} onAddTool={handleAddTool} onRemoveTool={handleRemoveTool} activeTools={activeToolsList}
          onCamera={handleCamera} onGallery={handleGallery} onFile={handleFile}
          showAttach={showAttach} setShowAttach={setShowAttach} attachAnim={attachAnim}
        />
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: StyleSheet.hairlineWidth },
  menuBtn: { padding: 6, borderRadius: 10 },
  headerCenter: { flex: 1, alignItems: 'center' },
  headerName: { fontSize: 17, fontWeight: '700', letterSpacing: -0.3 },
  miniIndicators: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 4 },
  energyDot: { width: 8, height: 8, borderRadius: 4, shadowOffset: { width: 0, height: 0 }, shadowOpacity: 0.5, shadowRadius: 4, elevation: 2 },
  miniText: { fontSize: 12, fontWeight: '600' },
  iconBtn: { padding: 6, borderRadius: 10 },
  recordingBtn: { backgroundColor: '#FF3B3015' },
  listContent: { paddingHorizontal: 0, paddingVertical: 12, flexGrow: 1 },
  typingRow: { flexDirection: 'row', alignItems: 'center', paddingLeft: 16, paddingVertical: 12, gap: 10 },
  welcomeContainer: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: 60, paddingHorizontal: 24 },
  welcomeIconWrap: { width: 80, height: 80, borderRadius: 24, justifyContent: 'center', alignItems: 'center', marginBottom: 20 },
  welcomeTitle: { fontSize: 22, fontWeight: '800', textAlign: 'center', marginBottom: 8, letterSpacing: -0.5 },
  welcomeSub: { fontSize: 15, textAlign: 'center', marginBottom: 24, lineHeight: 22 },
  suggestionsWrap: { gap: 10, width: '100%' },
  suggestionChip: { paddingHorizontal: 20, paddingVertical: 14, borderRadius: 16, borderWidth: 1, alignItems: 'center' },
  suggestionText: { fontSize: 15, fontWeight: '500' },
  resumeBtn: { paddingHorizontal: 20, paddingVertical: 10, borderRadius: 12, borderWidth: 1, marginBottom: 16 },
});
