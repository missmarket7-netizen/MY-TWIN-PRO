import React, { useState, useRef, useEffect, useCallback, memo, useMemo } from 'react';
import {
  View, FlatList, StyleSheet, StatusBar, KeyboardAvoidingView,
  Platform, Image, Animated, Text, Alert, TouchableOpacity,
  RefreshControl, Dimensions, Linking, Modal, ActivityIndicator,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Haptics from 'expo-haptics';
import * as Clipboard from 'expo-clipboard';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import * as Location from 'expo-location';
import { useTwinStore } from '../../store/useTwinStore';
import { apiPost, apiGet } from '../../lib/httpClient';
import { speakResponse, stopSpeaking } from '../../utils/voice_engine';
import TypingIndicator from '../../components/TypingIndicator';
import {
  Menu, Volume2, VolumeX, Mic, MicOff, Sparkles, Brain, Cpu, Search, Cloud, Music,
  Film, DollarSign, TrendingUp, Zap, BatteryCharging, Play, ExternalLink,
} from 'lucide-react-native';
import { COLORS, UserBubble, TwinBubble, ToolChip } from './ChatBubbles';
import { ChatInput } from './ChatInput';

const { width: SCREEN_W } = Dimensions.get('window');
const APP_ICON = require('../../assets/icon.png');

const MAX_FREE_ADS_PER_DAY = 2;
const ENERGY_PER_AD = 20;

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
          <TouchableOpacity key={i} style={[styles.suggestionChip, { backgroundColor: c.inputBg, borderColor: c.border }]} onPress={() => onSuggestion(s)} activeOpacity={0.7}>
            <Text style={[styles.suggestionText, { color: c.text }]}>{s}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
});

const EnergyModal = memo(({ visible, onClose, onWatchAd, adStatus, lang }: any) => {
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.modalOverlay}>
        <View style={styles.energyCard}>
          <BatteryCharging size={56} stroke="#7C3AED" style={{ alignSelf: 'center', marginBottom: 16 }} />
          <Text style={styles.energyTitle}>{t('الطاقة منتهية', 'Out of Energy')}</Text>
          <Text style={styles.energyBody}>
            {t(
              `شاهد إعلاناً واحصل على ${ENERGY_PER_AD}% طاقة إضافية (يمكنك المشاهدة حتى ${MAX_FREE_ADS_PER_DAY} مرات يومياً)`,
              `Watch an ad and get ${ENERGY_PER_AD}% extra energy (you can watch up to ${MAX_FREE_ADS_PER_DAY} times a day)`
            )}
          </Text>
          {adStatus?.remaining_today > 0 ? (
            <TouchableOpacity style={styles.watchAdBtn} onPress={onWatchAd}>
              <Play size={20} stroke="#FFF" />
              <Text style={styles.watchAdText}>{t('مشاهدة إعلان', 'Watch Ad')}</Text>
            </TouchableOpacity>
          ) : (
            <Text style={styles.energyNote}>
              {t('استنفدت الإعلانات اليومية. انتظر 20 ساعة للتجديد.', 'Daily ads exhausted. Wait 20 hours for renewal.')}
            </Text>
          )}
          <TouchableOpacity onPress={onClose} style={styles.energyClose}>
            <Text style={styles.energyCloseText}>{t('إغلاق', 'Close')}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
});
export default function Chat() {
  const insets = useSafeAreaInsets();
  const {
    userId, twinName, twinGender, tier, chatHistory, addMessage,
    lang, theme, setTwinName, setTwinGender,
    openMenu, closeMenu, voiceEnabled, setVoiceEnabled,
    bondLevel, sendMessage: storeSendMessage,
    isThinking: storeIsThinking, setThinking: storeSetThinking,
    thinkingStage: storeThinkingStage, setThinkingStage: storeSetThinkingStage,
    twinEnergy, setTwinEnergy,
  } = useTwinStore();

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAttach, setShowAttach] = useState(false);
  const [activeToolsList, setActiveToolsList] = useState<any[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState<'speaking' | 'listening' | null>(null);
  const [showEnergyModal, setShowEnergyModal] = useState(false);
  const [adStatus, setAdStatus] = useState<any>(null);

  const flatRef = useRef<FlatList>(null);
  const attachAnim = useRef(new Animated.Value(0)).current;

  const colors = theme === 'dark' ? COLORS.dark : COLORS.light;
  const isRTL = lang === 'ar';
  const isDark = theme === 'dark';

  useEffect(() => {
    apiGet('/api/ads/status').then(setAdStatus).catch(() => {});
  }, []);

  useEffect(() => {
    Animated.spring(attachAnim, { toValue: showAttach ? 1 : 0, useNativeDriver: true, tension: 65, friction: 11 }).start();
  }, [showAttach]);

  const sendMessage = useCallback(async (msg?: string, imageBase64?: string) => {
    const message = (msg || input).trim();
    if (!message && !imageBase64 && activeToolsList.length === 0) return;

    if (twinEnergy <= 0 && !activeToolsList.length) {
      const freshAdStatus = await apiGet('/api/ads/status');
      setAdStatus(freshAdStatus);
      setShowEnergyModal(true);
      return;
    }

    const msgId = Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
    addMessage({ id: msgId, role: 'user', content: message || (imageBase64 ? '📷 صورة' : ''), image: imageBase64, timestamp: Date.now() });

    setInput('');
    setLoading(true);
    storeSetThinking(true);
    storeSetThinkingStage('thinking');

    try {
      if (activeToolsList.length > 0) {
        storeSetThinkingStage('using_tool');
        const toolPromises = activeToolsList.map(async (tool) => {
          const data = await apiPost(`/api/features/${tool.type}`, { query: message || 'music', lang });
          return { type: tool.type, result: data.reply || data.result, success: true };
        });
        const settledResults = await Promise.allSettled(toolPromises);
        settledResults.forEach((res) => {
          if (res.status === 'fulfilled' && res.value.success) {
            addMessage({ id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36), role: 'twin', content: res.value.result, timestamp: Date.now(), provider: 'tool' });
          }
        });
        setActiveToolsList([]);
        storeSetThinkingStage('completed');
        setLoading(false); storeSetThinking(false);
        return;
      }

      storeSetThinkingStage('generating');
      const response = await apiPost('/api/chat', { message, history: chatHistory.slice(-10).map(m => ({ role: m.role, content: m.content })), lang });
      
      addMessage({ id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36), role: 'twin', content: response.reply, timestamp: Date.now(), emotion: response.emotion?.primary, provider: response.provider || 'gemini' });

      if (voiceEnabled) {
        setVoiceStatus('speaking');
        try { await speakResponse(response.reply); } catch {}
        setVoiceStatus(null);
      }
      storeSetThinkingStage('completed');
    } catch (error: any) {
      const isAr = lang === 'ar';
      let errMsg = isAr ? 'حدث خطأ ما. حاول مجدداً 💜' : 'Something went wrong. Try again 💜';
      addMessage({ id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36), role: 'twin', content: errMsg, timestamp: Date.now(), failed: true, provider: 'error' });
    } finally {
      setLoading(false); storeSetThinking(false);
    }
  }, [input, loading, voiceEnabled, lang, addMessage, storeSetThinking, storeSetThinkingStage, activeToolsList, twinEnergy, chatHistory]);

  const handleWatchAd = async () => {
    setShowEnergyModal(false);
    try {
      const data = await apiPost('/api/ads/reward', { ad_type: 'rewarded' });
      if (data.success) {
        setTwinEnergy(Math.min(100, twinEnergy + ENERGY_PER_AD));
        const freshStatus = await apiGet('/api/ads/status');
        setAdStatus(freshStatus);
      }
    } catch (e) { Alert.alert('خطأ', 'فشل تحميل الإعلان'); }
  };

  const send = useCallback(async (msg?: string, imageBase64?: string) => {
    if (loading) return;
    await sendMessage(msg, imageBase64);
  }, [loading, sendMessage]);

  const toggleSound = useCallback(() => {
    if (voiceEnabled) stopSpeaking();
    setVoiceEnabled(!voiceEnabled);
  }, [voiceEnabled, setVoiceEnabled]);

  const handleVoiceInput = useCallback(async () => {
    if (isRecording) { setIsRecording(false); setVoiceStatus(null); return; }
    setIsRecording(true); setVoiceStatus('listening');
    try {
      setTimeout(() => { setIsRecording(false); setVoiceStatus(null); }, 3000);
    } catch { setIsRecording(false); setVoiceStatus(null); }
  }, [isRecording]);

  const handleAddTool = useCallback((toolDef: any) => { setActiveToolsList(prev => [...prev, { id: Date.now().toString(), ...toolDef }]); }, []);
  const handleRemoveTool = useCallback((toolId: string) => { setActiveToolsList(prev => prev.filter(t => t.id !== toolId)); }, []);

  const renderMsg = useCallback(({ item }: any) => {
    if (item.role === 'user') return <UserBubble item={item} isDark={isDark} isRTL={isRTL} />;
    return (
      <TwinBubble
        item={item} isDark={isDark} isRTL={isRTL} isLast={false}
        onCopy={() => {}} onRetry={() => {}} onRegenerate={() => {}} onLike={() => {}} onDislike={() => {}}
        provider={item.provider} lang={lang}
      />
    );
  }, [isDark, isRTL, lang]);

  const ListHeader = useCallback(() => {
    if (chatHistory.length > 0) return null;
    return <WelcomeState isDark={isDark} lang={lang} twinName={twinName} onSuggestion={(s: string) => send(s)} />;
  }, [chatHistory.length, isDark, lang, twinName, send]);

  const ListFooter = useCallback(() => {
    if (!loading) return null;
    return (
      <View>
        <ThinkingBar stage={storeThinkingStage} isDark={isDark} />
        <View style={styles.typingRow}>
          <Image source={APP_ICON} style={{ width: 28, height: 28, borderRadius: 14 }} />
          <TypingIndicator />
        </View>
      </View>
    );
  }, [loading, storeThinkingStage, isDark]);

  return (
    <View style={[styles.root, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} backgroundColor={colors.bg} />
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <View style={[styles.header, { backgroundColor: colors.headerBg, borderBottomColor: colors.border }]}>
          <TouchableOpacity onPress={openMenu} style={styles.menuBtn}><Menu size={22} stroke={colors.text} /></TouchableOpacity>
          <View style={styles.headerCenter}>
            <Text style={[styles.headerName, { color: colors.text }]}>{twinName}</Text>
            <View style={styles.miniIndicators}>
              <View style={[styles.energyDot, { backgroundColor: twinEnergy > 60 ? '#34C759' : twinEnergy > 25 ? '#FF9500' : '#FF3B30' }]} />
              <Text style={[styles.miniText, { color: colors.subtext }]}>⚡ {twinEnergy}%</Text>
            </View>
          </View>
          <View style={{ flexDirection: 'row', gap: 4 }}>
            <TouchableOpacity onPress={handleVoiceInput} style={[styles.iconBtn, isRecording && styles.recordingBtn]}>
              <Mic size={22} stroke={isRecording ? "#FF3B30" : colors.text} fill={isRecording ? "#FF3B3020" : "transparent"} />
            </TouchableOpacity>
            <TouchableOpacity onPress={toggleSound} style={styles.iconBtn}>
              {voiceEnabled ? <Volume2 size={22} stroke={colors.accent} fill={colors.accent + '30'} /> : <VolumeX size={22} stroke={colors.subtext} />}
            </TouchableOpacity>
          </View>
        </View>

        <FlatList
          ref={flatRef} data={chatHistory} keyExtractor={(item) => item.id}
          renderItem={renderMsg} ListHeaderComponent={ListHeader} ListFooterComponent={ListFooter}
          contentContainerStyle={styles.listContent}
          onContentSizeChange={() => flatRef.current?.scrollToEnd({ animated: false })}
          keyboardShouldPersistTaps="handled"
        />

        {activeToolsList.length > 0 && (
          <View style={[styles.toolsRow, { backgroundColor: colors.headerBg }]}>
            {activeToolsList.map((tool: any) => (
              <ToolChip key={tool.id} label={tool.label} icon={tool.icon} color={tool.color} onClose={() => handleRemoveTool(tool.id)} />
            ))}
          </View>
        )}

        <ChatInput
          input={input} setInput={setInput} loading={loading} isRTL={isRTL} isDark={isDark} colors={colors} lang={lang}
          onSend={send} onAddTool={handleAddTool} onRemoveTool={handleRemoveTool} activeTools={activeToolsList}
          showAttach={showAttach} setShowAttach={setShowAttach} attachAnim={attachAnim}
        />
      </KeyboardAvoidingView>

      <EnergyModal visible={showEnergyModal} onClose={() => setShowEnergyModal(false)} onWatchAd={handleWatchAd} adStatus={adStatus} lang={lang} />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 10, borderBottomWidth: 0.5 },
  menuBtn: { padding: 6, borderRadius: 10 },
  headerCenter: { flex: 1, alignItems: 'center', marginHorizontal: 10 },
  headerName: { fontSize: 18, fontWeight: '700' },
  miniIndicators: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 4 },
  energyDot: { width: 6, height: 6, borderRadius: 3 },
  miniText: { fontSize: 11, fontWeight: '600' },
  iconBtn: { padding: 6, borderRadius: 10 },
  recordingBtn: { backgroundColor: '#FF3B3015' },
  listContent: { paddingHorizontal: 0, paddingVertical: 12, flexGrow: 1 },
  typingRow: { flexDirection: 'row', alignItems: 'center', paddingLeft: 16, paddingVertical: 12, gap: 10 },
  toolsRow: { flexDirection: 'row', padding: 10, borderTopWidth: 1, borderTopColor: '#E5E5EA', gap: 8 },
  welcomeContainer: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: 60, paddingHorizontal: 24 },
  welcomeIconWrap: { width: 80, height: 80, borderRadius: 24, justifyContent: 'center', alignItems: 'center', marginBottom: 20 },
  welcomeTitle: { fontSize: 22, fontWeight: '800', textAlign: 'center', marginBottom: 8 },
  welcomeSub: { fontSize: 15, textAlign: 'center', marginBottom: 24 },
  suggestionsWrap: { gap: 10, width: '100%' },
  suggestionChip: { paddingHorizontal: 20, paddingVertical: 14, borderRadius: 16, borderWidth: 1, alignItems: 'center' },
  suggestionText: { fontSize: 15, fontWeight: '500' },
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)', padding: 30 },
  energyCard: { backgroundColor: '#FFFFFF', borderRadius: 24, padding: 30, alignItems: 'center', width: '100%', maxWidth: 350 },
  energyTitle: { fontSize: 22, fontWeight: '800', color: '#1A1226', marginBottom: 12 },
  energyBody: { fontSize: 15, color: '#7C6B99', textAlign: 'center', lineHeight: 22, marginBottom: 24 },
  watchAdBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: '#7C3AED', paddingHorizontal: 28, paddingVertical: 14, borderRadius: 14 },
  watchAdText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  energyNote: { fontSize: 13, color: '#EF4444', textAlign: 'center', marginBottom: 16 },
  energyClose: { marginTop: 16, padding: 10 },
  energyCloseText: { fontSize: 14, color: '#6B7280' },
});
