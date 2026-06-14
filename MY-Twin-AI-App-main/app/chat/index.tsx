import {
  View,
  FlatList,
  StyleSheet,
  StatusBar,
  KeyboardAvoidingView,
  Platform,
  Image,
  Animated,
  Text,
  Alert,
  TouchableOpacity,
} from 'react-native';
import { useState, useRef, useEffect, useCallback } from 'react';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Haptics from 'expo-haptics';
import * as Clipboard from 'expo-clipboard';
import { supabase } from '../../lib/supabase';
import { useTwinStore, ChatMessage } from '../../store/useTwinStore';
import {
  sendChatFromStore,
  updateStoreFromResponse,
  fetchWeather,
  fetchYouTube,
  fetchSpotify,
  fetchNews,
  fetchCurrency,
} from '../../lib/api';
import SideMenu from '../../components/SideMenu';
import TypingIndicator from '../../components/TypingIndicator';
import { Menu, Volume2, VolumeX } from 'lucide-react-native';
import { speakResponse } from '../../utils/voice_engine';
import { COLORS, UserBubble, TwinBubble, EnergyCircle } from './ChatBubbles';
import { ChatInput } from './ChatInput';

const APP_ICON = require('../../assets/icon.png');

export default function Chat() {
  const insets = useSafeAreaInsets();
  const {
    userId,
    twinName,
    twinGender,
    tier,
    chatHistory,
    addMessage,
    triggerHaptic,
    lang,
    theme,
    setTwinName,
    setTwinGender,
    openMenu,
    closeMenu,
    voiceEnabled,
    setVoiceEnabled,
    bondLevel,
    setThinking,
    setThinkingStage,
  } = useTwinStore((s) => ({
    userId: s.userId,
    twinName: s.twinName,
    twinGender: s.twinGender,
    tier: s.tier,
    chatHistory: s.chatHistory,
    addMessage: s.addMessage,
    triggerHaptic: s.triggerHaptic,
    lang: s.lang,
    theme: s.theme,
    setTwinName: s.setTwinName,
    setTwinGender: s.setTwinGender,
    openMenu: s.openMenu,
    closeMenu: s.closeMenu,
    voiceEnabled: s.voiceEnabled,
    setVoiceEnabled: s.setVoiceEnabled,
    bondLevel: s.bondLevel,
    setThinking: s.setThinking,
    setThinkingStage: s.setThinkingStage,
  }));

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAttach, setShowAttach] = useState(false);
  const [featureModal, setFeatureModal] = useState<{ visible: boolean; type: string }>({ visible: false, type: '' });
  const [featureInput, setFeatureInput] = useState('');
  const [messageQueue, setMessageQueue] = useState<Array<{ msg?: string; image?: string }>>([]);
  const [twinEnergy, setTwinEnergy] = useState(100);
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState('');
  const [feedbackMap, setFeedbackMap] = useState<Record<string, 'like' | 'dislike' | null>>({});

  const flatRef = useRef<FlatList<ChatMessage>>(null);
  const attachAnim = useRef(new Animated.Value(0)).current;

  const colors = theme === 'dark' ? COLORS.dark : COLORS.light;
  const isRTL = lang === 'ar';
  const isDark = theme === 'dark';

  // التمرير التلقائي عند تغيير التاريخ أو وضع التحرير
  useEffect(() => {
    const t = setTimeout(() => flatRef.current?.scrollToEnd({ animated: true }), 100);
    return () => clearTimeout(t);
  }, [chatHistory, editingMessageId]);

  // تحريك قائمة المرفقات
  useEffect(() => {
    Animated.spring(attachAnim, {
      toValue: showAttach ? 1 : 0,
      useNativeDriver: true,
      tension: 65,
      friction: 11,
    }).start();
  }, [showAttach]);

  // معالجة الرسائل الموجودة في الطابور
  useEffect(() => {
    if (messageQueue.length > 0 && !loading) {
      const next = messageQueue[0];
      setMessageQueue((prev) => prev.slice(1));
      sendMessage(next.msg, next.image);
    }
  }, [messageQueue, loading]);

  // حساب طاقة التوأم بناءً على إحصائيات الاستخدام
  useEffect(() => {
    (async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.access_token) {
          const res = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/stats`, {
            headers: { Authorization: `Bearer ${session.access_token}` },
          });
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

  // حفظ التقييم (إعجاب/عدم إعجاب) في Supabase
  const saveFeedback = async (messageId: string, rating: 'like' | 'dislike') => {
    if (!userId) return;
    try {
      await supabase.from('message_feedback').upsert(
        { user_id: userId, message_id: messageId, rating, created_at: new Date().toISOString() },
        { onConflict: 'user_id,message_id' }
      );
    } catch (e) {
      console.warn('Feedback save failed:', e);
    }
  };

  // معالج الإعجاب
  const handleLike = useCallback(
    (msg: ChatMessage) => {
      const current = feedbackMap[msg.id];
      if (current === 'like') {
        setFeedbackMap((prev) => ({ ...prev, [msg.id]: null }));
      } else {
        setFeedbackMap((prev) => ({ ...prev, [msg.id]: 'like' }));
        saveFeedback(msg.id, 'like');
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }
    },
    [feedbackMap, userId]
  );

  // معالج عدم الإعجاب
  const handleDislike = useCallback(
    (msg: ChatMessage) => {
      const current = feedbackMap[msg.id];
      if (current === 'dislike') {
        setFeedbackMap((prev) => ({ ...prev, [msg.id]: null }));
      } else {
        setFeedbackMap((prev) => ({ ...prev, [msg.id]: 'dislike' }));
        saveFeedback(msg.id, 'dislike');
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      }
    },
    [feedbackMap, userId]
  );

  // الإرسال الفعلي للرسالة إلى الخادم
  const sendMessage = useCallback(
    async (msg?: string, imageBase64?: string) => {
      const message = (msg || input).trim();
      if (!message && !imageBase64) return;

      const msgId = Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
      addMessage({
        id: msgId,
        role: 'user',
        content: message || '📷 صورة',
        image: imageBase64,
        timestamp: Date.now(),
      });
      setInput('');
      setLoading(true);
      setThinking(true);
      setThinkingStage('thinking');

      try {
        const response = await sendChatFromStore(message, imageBase64);

        // استخراج روابط يوتيوب إن وجدت
        const youtubeRegex = /https?:\/\/(?:www\.)?youtube\.com\/watch\?v=[\w-]+|https?:\/\/youtu\.be\/[\w-]+/g;
        const youtubeLinks = response.reply.match(youtubeRegex);

        addMessage({
          id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
          role: 'twin',
          content: response.reply,
          timestamp: Date.now(),
          emotion: response.emotion?.primary,
          memoryRecall: response.memory_used,
          youtubeVideo: youtubeLinks ? youtubeLinks[0] : undefined,
          provider: response.provider || 'multi_ai',
        });

        updateStoreFromResponse(response);

        // تحديث الطاقة بعد الرد
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.access_token) {
          const res = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/stats`, {
            headers: { Authorization: `Bearer ${session.access_token}` },
          });
          if (res.ok) {
            const stats = await res.json();
            const remaining = stats.limits?.messages?.remaining || 0;
            const limit = stats.limits?.messages?.limit || 15;
            setTwinEnergy(Math.round((remaining / limit) * 100));
          }
        }

        // تشغيل الصوت إذا مفعل
        if (voiceEnabled) {
          try {
            await speakResponse(response.reply);
          } catch {}
        }
      } catch (error: any) {
        if (error.name === 'AbortError') return;
        addMessage({
          id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
          role: 'twin',
          timestamp: Date.now(),
          failed: true,
          content: lang === 'ar' ? 'تعذر الاتصال 😔' : 'Connection failed 😔',
          provider: 'error',
        });
      } finally {
        setLoading(false);
        setThinking(false);
      }
    },
    [input, loading, voiceEnabled, lang, addMessage, setThinking, setThinkingStage]
  );

  // المدخل العام للإرسال مع آلية الطابور
  const send = useCallback(
    async (msg?: string, imageBase64?: string) => {
      if (loading) {
        setMessageQueue((prev) => [...prev, { msg, image: imageBase64 }]);
        return;
      }
      triggerHaptic();
      await sendMessage(msg, imageBase64);
    },
    [loading, sendMessage, triggerHaptic]
  );

  // نسخ النص إلى الحافظة
  const handleCopy = useCallback((content: string) => {
    Clipboard.setStringAsync(content);
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  }, []);

  // إعادة محاولة إرسال رسالة فاشلة
  const handleRetry = useCallback(
    (failedMsg: ChatMessage) => {
      sendMessage(failedMsg.content, failedMsg.image);
    },
    [sendMessage]
  );

  // إعادة توليد الرد (لآخر رسالة)
  const handleRegenerate = useCallback(
    (lastMsg: ChatMessage) => {
      sendMessage(lastMsg.content);
    },
    [sendMessage]
  );

  // تبديل حالة الصوت
  const toggleSound = () => setVoiceEnabled(!voiceEnabled);

  // بدء تحرير رسالة المستخدم
  const handleStartEdit = useCallback((msg: ChatMessage) => {
    setEditingMessageId(msg.id);
    setEditingContent(msg.content);
  }, []);

  // حفظ التعديل وإعادة الإرسال
  const handleSaveEdit = useCallback(
    (msg: ChatMessage, newContent: string) => {
      if (newContent.trim() && newContent !== msg.content) {
        setEditingMessageId(null);
        sendMessage(newContent.trim(), msg.image);
      } else {
        setEditingMessageId(null);
      }
    },
    [sendMessage]
  );

  // الأدوات السريعة (طقس، يوتيوب...)
  const handleQuickTool = async (tool: string) => {
    let result = '';
    setLoading(true);
    try {
      switch (tool) {
        case 'weather':
          result = (await fetchWeather('Cairo')).result || 'الطقس غير متاح';
          break;
        case 'youtube':
          result = (await fetchYouTube(input || 'music')).result || 'لم أجد فيديوهات';
          break;
        case 'spotify':
          result = (await fetchSpotify(input || 'music')).result || 'لم أجد أغاني';
          break;
        case 'news':
          result = (await fetchNews()).result || 'الأخبار غير متاحة';
          break;
        case 'currency':
          result = (await fetchCurrency('USD')).result || 'أسعار العملات غير متاحة';
          break;
      }
      if (result) {
        addMessage({
          id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
          role: 'twin',
          content: result,
          timestamp: Date.now(),
          provider: 'tool',
        });
        if (voiceEnabled) await speakResponse(result);
      }
    } catch {
      Alert.alert('خطأ', 'تعذر تنفيذ الأداة');
    } finally {
      setLoading(false);
    }
  };

  // عرض كل رسالة
  const renderMsg = useCallback(
    ({ item, index }: { item: ChatMessage; index: number }) => {
      if (item.role === 'user') {
        return (
          <UserBubble
            item={item}
            isDark={isDark}
            onStartEdit={handleStartEdit}
            onSaveEdit={handleSaveEdit}
            isEditing={editingMessageId === item.id}
            editContent={editingContent}
            setEditContent={setEditingContent}
          />
        );
      }
      return (
        <TwinBubble
          item={item}
          isDark={isDark}
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
    },
    [
      isDark,
      handleCopy,
      handleRetry,
      handleRegenerate,
      handleLike,
      handleDislike,
      feedbackMap,
      editingMessageId,
      editingContent,
    ]
  );

  // مؤشر الطباعة في نهاية القائمة
  const ListFooter = useCallback(() => {
    if (!loading) return null;
    return (
      <View style={styles.typingRow}>
        <Image source={APP_ICON} style={{ width: 28, height: 28, borderRadius: 14 }} />
        <TypingIndicator />
      </View>
    );
  }, [loading]);

  return (
    <View style={[styles.root, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
      <StatusBar
        barStyle={isDark ? 'light-content' : 'dark-content'}
        backgroundColor={colors.bg}
      />
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {/* الهيدر */}
        <View
          style={[
            styles.header,
            { backgroundColor: colors.headerBg, borderBottomColor: colors.border },
          ]}
        >
          <TouchableOpacity onPress={openMenu} style={styles.menuBtn}>
            <Menu size={22} stroke={colors.text} />
          </TouchableOpacity>

          <View style={styles.headerCenter}>
            <Text
              style={[styles.headerName, { color: colors.text }]}
              numberOfLines={1}
            >
              {twinName || (lang === 'ar' ? 'توأمك' : 'Your Twin')}
            </Text>
            <View style={styles.miniIndicators}>
              <View
                style={[
                  styles.miniDot,
                  {
                    backgroundColor:
                      twinEnergy > 60 ? '#10B981' : twinEnergy > 25 ? '#F59E0B' : '#EF4444',
                  },
                ]}
              />
              <Text style={[styles.miniText, { color: colors.subtext }]}>
                {Math.round(bondLevel)}%
              </Text>
            </View>
          </View>

          <TouchableOpacity onPress={toggleSound} style={styles.soundBtn}>
            {voiceEnabled ? (
              <Volume2 size={22} stroke={colors.text} />
            ) : (
              <VolumeX size={22} stroke={colors.subtext} />
            )}
          </TouchableOpacity>
        </View>

        {/* قائمة الرسائل */}
        <FlatList
          ref={flatRef}
          data={chatHistory}
          keyExtractor={(item) => item.id}
          renderItem={renderMsg}
          ListFooterComponent={ListFooter}
          contentContainerStyle={styles.listContent}
          onContentSizeChange={() => flatRef.current?.scrollToEnd({ animated: false })}
          removeClippedSubviews
          initialNumToRender={10}
          maxToRenderPerBatch={10}
          windowSize={5}
          keyboardDismissMode="interactive"
        />

        {/* شريط الإدخال */}
        <ChatInput
          input={input}
          setInput={setInput}
          loading={loading}
          isRTL={isRTL}
          isDark={isDark}
          colors={colors}
          lang={lang}
          onSend={send}
          onToolAction={handleQuickTool}
          onCamera={() => {}}
          onGallery={() => {}}
          onFile={() => {}}
          activeTools={[]}
          onRemoveTool={() => {}}
          showAttach={showAttach}
          setShowAttach={setShowAttach}
          attachAnim={attachAnim}
        />
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderBottomWidth: 0.5,
  },
  menuBtn: { padding: 4 },
  headerCenter: { flex: 1, alignItems: 'center' },
  headerName: { fontSize: 16, fontWeight: '600', textAlign: 'center' },
  miniIndicators: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 2 },
  miniDot: { width: 6, height: 6, borderRadius: 3 },
  miniText: { fontSize: 10, fontWeight: '500' },
  soundBtn: { padding: 4 },
  listContent: { paddingHorizontal: 16, paddingVertical: 12, flexGrow: 1 },
  typingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingLeft: 16,
    paddingVertical: 12,
    gap: 10,
  },
});
