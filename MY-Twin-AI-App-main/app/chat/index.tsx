import React, { useState, useRef, useEffect, useCallback, memo, useMemo } from 'react';
import {
  View, FlatList, StyleSheet, StatusBar, KeyboardAvoidingView,
  Platform, Image, Animated, Text, Alert, TouchableOpacity,
  RefreshControl, Dimensions, Linking, Modal, ActivityIndicator,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Haptics from 'expo-haptics';
import { useTwinStore } from '../../store/useTwinStore';
import { apiPost, apiGet } from '../../lib/httpClient';
import { speakResponse, stopSpeaking } from '../../utils/voice_engine';
import TypingIndicator from '../../components/TypingIndicator';
import {
  Menu, Volume2, VolumeX, Mic, Sparkles,
} from 'lucide-react-native';
import { COLORS, ThinkingBar, WelcomeState, EnergyModal } from './ChatComponents';
import { UserBubble, TwinBubble, ToolChip } from './ChatBubbles';
import { ChatInput } from './ChatInput';

const APP_ICON = require('../../assets/icon.png');

export default function Chat() {
  const insets = useSafeAreaInsets();
  const {
    userId, twinName, twinGender, tier, chatHistory, addMessage,
    lang, theme, twinEnergy, setTwinEnergy,
    openMenu, closeMenu, voiceEnabled, setVoiceEnabled,
    bondLevel,
  } = useTwinStore();

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAttach, setShowAttach] = useState(false);
  const [activeToolsList, setActiveToolsList] = useState<any[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState<'speaking' | 'listening' | null>(null);
  const [showEnergyModal, setShowEnergyModal] = useState(false);
  const [adStatus, setAdStatus] = useState<any>(null);
  const [thinkingStage, setThinkingStage] = useState('idle');
  const [isThinking, setIsThinking] = useState(false);

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
    setIsThinking(true);
    setThinkingStage('thinking');

    try {
      setThinkingStage('generating');
      const response = await apiPost('/api/chat', {
        message,
        history: chatHistory.slice(-10).map(m => ({ role: m.role, content: m.content })),
        lang,
      });

      addMessage({
        id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
        role: 'twin', content: response.reply, timestamp: Date.now(),
        emotion: response.emotion?.primary, provider: response.provider || 'orchestrator',
      });

      if (voiceEnabled) {
        setVoiceStatus('speaking');
        try { await speakResponse(response.reply); } catch {}
        setVoiceStatus(null);
      }
      setThinkingStage('completed');
    } catch (error: any) {
      const isAr = lang === 'ar';
      let errMsg = isAr ? 'حدث خطأ ما. حاول مجدداً 💜' : 'Something went wrong. Try again 💜';
      addMessage({
        id: Math.random().toString(36).substr(2, 9) + Date.now().toString(36),
        role: 'twin', content: errMsg, timestamp: Date.now(), failed: true, provider: 'error',
      });
    } finally {
      setLoading(false); setIsThinking(false);
      setTimeout(() => setThinkingStage('idle'), 2000);
    }
  }, [input, loading, voiceEnabled, lang, addMessage, activeToolsList, twinEnergy, chatHistory]);

  const handleWatchAd = async () => {
    setShowEnergyModal(false);
    try {
      const data = await apiPost('/api/ads/reward', { ad_type: 'rewarded' });
      if (data.success) {
        setTwinEnergy(Math.min(100, twinEnergy + 20));
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
        <ThinkingBar stage={thinkingStage} isDark={isDark} />
        <View style={styles.typingRow}>
          <Image source={APP_ICON} style={{ width: 28, height: 28, borderRadius: 14 }} />
          <TypingIndicator />
        </View>
      </View>
    );
  }, [loading, thinkingStage, isDark]);

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
});
