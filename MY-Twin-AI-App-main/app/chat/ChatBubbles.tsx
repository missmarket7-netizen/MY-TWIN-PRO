import React, { memo, useRef, useState, useEffect, useMemo } from 'react';
import {
  View, Text, Image, StyleSheet, TouchableOpacity, Share,
  Linking, TextInput, Animated, Dimensions,
} from 'react-native';
import { ChatMessage } from '../../store/useTwinStore';
import {
  Copy, Share2, RotateCcw, Edit3, Check, ThumbsUp,
  ThumbsDown, ExternalLink, Film, X, Brain, Sparkles,
  Zap, MessageCircle, User as UserIcon, Bot, Cpu, Shield,
} from 'lucide-react-native';
import Markdown from 'react-native-markdown-display';
import * as WebBrowser from 'expo-web-browser';
import * as Clipboard from 'expo-clipboard';

const { width: SCREEN_W } = Dimensions.get('window');
const APP_ICON = require('../../assets/icon.png');

export const COLORS = {
  light: {
    bg: '#FFFFFF', headerBg: '#FAFAFA', border: '#E8E8E8', text: '#1A1A1A',
    subtext: '#8E8E93', bubbleUser: '#7C3AED', userText: '#FFFFFF',
    twinText: '#1A1A1A',
    inputBg: '#F2F2F7', inputBorder: '#E5E5EA', sendActive: '#7C3AED',
    sendInactive: '#C7C7CC', retryColor: '#FF3B30', likeActive: '#34C759',
    dislikeActive: '#FF3B30', accent: '#7C3AED', codeBg: '#1C1C1E',
    tableBorder: '#E5E5EA', blockquoteBg: '#F2F2F7', link: '#5856D6',
  },
  dark: {
    bg: '#000000', headerBg: '#1C1C1E', border: '#38383A', text: '#FFFFFF',
    subtext: '#8E8E93', bubbleUser: '#7C3AED', userText: '#FFFFFF',
    twinText: '#FFFFFF',
    inputBg: '#2C2C2E', inputBorder: '#38383A', sendActive: '#A78BFA',
    sendInactive: '#48484A', retryColor: '#FF453A', likeActive: '#30D158',
    dislikeActive: '#FF453A', accent: '#A78BFA', codeBg: '#0A0A0A',
    tableBorder: '#38383A', blockquoteBg: '#2C2C2E', link: '#5E5CE6',
  },
};

const emotionEmoji: Record<string, string> = {
  joy: '😊', sadness: '😢', anger: '😠', fear: '😨', love: '❤️',
  surprise: '😮', neutral: '😌', excited: '🤩', calm: '😌',
  anxious: '😰', grateful: '🙏', curious: '🤔',
};

const providerLabels: Record<string, { ar: string; en: string; icon: any }> = {
  multi_ai: { ar: 'ذكاء متعدد', en: 'Multi AI', icon: Sparkles },
  tool: { ar: 'أداة', en: 'Tool', icon: Zap },
  error: { ar: 'خطأ', en: 'Error', icon: X },
  openai: { ar: 'GPT', en: 'GPT', icon: Bot },
  claude: { ar: 'Claude', en: 'Claude', icon: MessageCircle },
  gemini: { ar: 'Gemini', en: 'Gemini', icon: Sparkles },
  groq: { ar: 'Groq', en: 'Groq', icon: Cpu },
  council: { ar: 'مجلس', en: 'Council', icon: Sparkles },
  agent_loop: { ar: 'وكيل', en: 'Agent', icon: Zap },
  fallback: { ar: 'احتياطي', en: 'Fallback', icon: X },
  safety_engine: { ar: 'أمان', en: 'Safety', icon: Shield },
};

export const MarkdownRenderer = memo(({ content, isDark }: { content: string; isDark: boolean }) => {
  const c = isDark ? COLORS.dark : COLORS.light;
  const markdownStyles: any = useMemo(() => ({
    body: { color: c.twinText, fontSize: 16, lineHeight: 26 },
    paragraph: { marginBottom: 12, marginTop: 4 },
    heading1: { fontSize: 24, fontWeight: '800', marginBottom: 16, marginTop: 8, color: c.accent },
    heading2: { fontSize: 20, fontWeight: '700', marginBottom: 12, marginTop: 8, color: c.accent },
    heading3: { fontSize: 18, fontWeight: '700', marginBottom: 10, marginTop: 6, color: c.text },
    bullet_list: { marginBottom: 12, marginLeft: 8 },
    ordered_list: { marginBottom: 12, marginLeft: 8 },
    list_item: { marginBottom: 8, flexDirection: 'row', alignItems: 'flex-start' },
    table: { marginVertical: 16, borderWidth: 1, borderColor: c.tableBorder, borderRadius: 12, overflow: 'hidden' },
    thead: { backgroundColor: c.codeBg },
    th: { padding: 12, fontWeight: '700', color: c.text, fontSize: 14 },
    td: { padding: 12, color: c.subtext, fontSize: 14, borderTopWidth: 1, borderColor: c.tableBorder },
    code_inline: { backgroundColor: c.codeBg, color: '#FF375F', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, fontSize: 14 },
    code_block: { backgroundColor: c.codeBg, padding: 16, borderRadius: 12, marginVertical: 12, borderWidth: 1, borderColor: c.border },
    blockquote: { borderLeftWidth: 4, borderLeftColor: c.accent, paddingLeft: 16, paddingVertical: 12, marginVertical: 12, backgroundColor: c.blockquoteBg, borderRadius: 8 },
    link: { color: c.link, fontWeight: '600' },
    strong: { fontWeight: '700', color: c.text },
    em: { fontStyle: 'italic', color: c.subtext },
  }), [isDark]);

  const handleLinkPress = (url: string): boolean => {
    WebBrowser.openBrowserAsync(url).catch(() => Linking.openURL(url));
    return true;
  };

  return <Markdown style={markdownStyles} onLinkPress={handleLinkPress}>{content}</Markdown>;
});

export const UserBubble = memo(({ item, isDark, isRTL }: any) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  useEffect(() => { Animated.timing(fadeAnim, { toValue: 1, duration: 200, useNativeDriver: true }).start(); }, []);
  const c = isDark ? COLORS.dark : COLORS.light;
  const time = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <Animated.View style={[styles.userRow, { opacity: fadeAnim }]}>
      <View style={styles.userBubbleWrapper}>
        <View style={[styles.userBubble, { backgroundColor: c.bubbleUser }]}>
          {item.image && <Image source={{ uri: item.image?.startsWith('data:') ? item.image : `data:image/jpeg;base64,${item.image}` }} style={styles.chatImage} />}
          <Text style={[styles.userText, { color: '#FFF' }]}>{item.content}</Text>
          <Text style={[styles.userTime, { color: 'rgba(255,255,255,0.6)' }]}>{time}</Text>
        </View>
      </View>
    </Animated.View>
  );
});

export const ToolChip = memo(({ label, icon: Icon, color, onClose }: any) => (
  <View style={[styles.toolChip, { backgroundColor: color + '12', borderColor: color + '25' }]}>
    <Icon size={14} stroke={color} />
    <Text style={[styles.toolChipText, { color }]}>{label}</Text>
    {onClose && <TouchableOpacity onPress={onClose}><X size={12} stroke={color} /></TouchableOpacity>}
  </View>
));
export const TwinBubble = memo(({ item, isDark, isRTL, isLast, onCopy, onRetry, onRegenerate, onLike, onDislike, liked, disliked, provider, lang }: any) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const glowAnim = useRef(new Animated.Value(0)).current;
  const [showToast, setShowToast] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout>(null);

  useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 300, useNativeDriver: true }).start();
  }, []);

  const isThinking = item.thinkingStage && item.thinkingStage !== 'complete';
  
  useEffect(() => {
    if (isThinking) {
      const loop = Animated.loop(
        Animated.sequence([
          Animated.timing(glowAnim, { toValue: 1, duration: 800, useNativeDriver: true }),
          Animated.timing(glowAnim, { toValue: 0, duration: 800, useNativeDriver: true }),
        ])
      );
      loop.start();
      return () => loop.stop();
    } else {
      glowAnim.setValue(0);
      Animated.timing(glowAnim, { toValue: 1, duration: 300, useNativeDriver: true }).start();
      setTimeout(() => glowAnim.setValue(0), 300);
    }
  }, [isThinking]);

  const c = isDark ? COLORS.dark : COLORS.light;
  const time = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const emotion = item.emotion || 'neutral';
  const emoji = emotionEmoji[emotion] || '😌';
  const prov = providerLabels[provider || 'multi_ai'] || providerLabels.multi_ai;
  const ProvIcon = prov.icon;
  const displayProv = lang === 'ar' ? prov.ar : prov.en;

  const handleCopy = async (text: string) => {
    await Clipboard.setStringAsync(text);
    setShowToast(true);
    timeoutRef.current = setTimeout(() => setShowToast(false), 2000);
  };

  const glowColor = isDark ? '#A78BFA' : '#7C3AED';

  return (
    <Animated.View style={[styles.twinRow, { opacity: fadeAnim }]}>
      <View style={[styles.twinHeader, { flexDirection: isRTL ? 'row-reverse' : 'row' }]}>
        <Animated.View style={[
          styles.twinAvatarGlow,
          { 
            shadowColor: glowColor,
            shadowOpacity: glowAnim.interpolate({ inputRange: [0, 1], outputRange: [0.1, 0.4] }),
            shadowRadius: glowAnim.interpolate({ inputRange: [0, 1], outputRange: [8, 20] }),
            transform: [{ scale: glowAnim.interpolate({ inputRange: [0, 1], outputRange: [1, 1.05] }) }]
          }
        ]}>
          <Image source={APP_ICON} style={styles.twinAvatar} />
        </Animated.View>
        <View style={{ flex: 1 }}>
          <View style={[styles.twinMeta, { flexDirection: isRTL ? 'row-reverse' : 'row' }]}>
            <Text style={[styles.twinName, { color: c.text }]}>MyTwin</Text>
            {item.emotion && <Text style={styles.emotionEmoji}>{emoji}</Text>}
            <Text style={[styles.timestamp, { color: c.subtext }]}>{time}</Text>
          </View>
          <View style={[styles.twinBadges, { flexDirection: isRTL ? 'row-reverse' : 'row' }]}>
            <View style={[styles.providerBadge, { backgroundColor: c.codeBg }]}>
              <ProvIcon size={10} stroke={c.accent} />
              <Text style={[styles.providerText, { color: c.subtext }]}>{displayProv}</Text>
            </View>
            {item.thinkingStage && item.thinkingStage !== 'complete' && (
              <View style={[styles.thinkingBadge, { backgroundColor: c.blockquoteBg }]}>
                <Zap size={10} stroke={c.accent} />
                <Text style={[styles.thinkingText, { color: c.accent }]}>
                  {item.thinkingStage === 'thinking' ? 'يفكر...' : item.thinkingStage}
                </Text>
              </View>
            )}
          </View>
        </View>
      </View>

      <View style={styles.twinContent}>
        {item.youtubeVideo && (
          <TouchableOpacity onPress={() => Linking.openURL(item.youtubeVideo)} style={[styles.youtubeCard, { backgroundColor: isDark ? '#1C1C1E' : '#FFF0F0' }]}>
            <Film size={20} stroke="#FF0000" />
            <Text style={{ color: '#FF0000', fontWeight: '700', flex: 1, marginHorizontal: 8 }}>▶️ شاهد الفيديو</Text>
            <ExternalLink size={14} stroke="#FF0000" />
          </TouchableOpacity>
        )}
        <MarkdownRenderer content={item.content} isDark={isDark} />
      </View>

      <View style={[styles.actionRow, { flexDirection: isRTL ? 'row-reverse' : 'row' }]}>
        <TouchableOpacity onPress={() => handleCopy(item.content)} style={styles.actionBtn}><Copy size={15} stroke={c.subtext} /></TouchableOpacity>
        <TouchableOpacity onPress={() => Share.share({ message: item.content })} style={styles.actionBtn}><Share2 size={15} stroke={c.subtext} /></TouchableOpacity>
        {isLast && <TouchableOpacity onPress={() => onRegenerate(item)} style={styles.actionBtn}><RotateCcw size={15} stroke={c.subtext} /></TouchableOpacity>}
        <TouchableOpacity onPress={() => onLike(item)} style={[styles.actionBtn, liked && styles.activeLike]}><ThumbsUp size={15} stroke={liked ? c.likeActive : c.subtext} fill={liked ? c.likeActive : 'transparent'} /></TouchableOpacity>
        <TouchableOpacity onPress={() => onDislike(item)} style={[styles.actionBtn, disliked && styles.activeDislike]}><ThumbsDown size={15} stroke={disliked ? c.dislikeActive : c.subtext} fill={disliked ? c.dislikeActive : 'transparent'} /></TouchableOpacity>
      </View>

      {item.failed && (
        <TouchableOpacity onPress={() => onRetry(item)} style={styles.retryBtn}><RotateCcw size={14} stroke={c.retryColor} /><Text style={[styles.retryText, { color: c.retryColor }]}>إعادة المحاولة</Text></TouchableOpacity>
      )}
    </Animated.View>
  );
});

const styles = StyleSheet.create({
  userRow: { flexDirection: 'row', justifyContent: 'flex-end', marginBottom: 20, paddingHorizontal: 12 },
  userBubbleWrapper: { maxWidth: '85%' },
  userBubble: { paddingHorizontal: 16, paddingVertical: 12, borderRadius: 20, borderBottomRightRadius: 4 },
  userText: { fontSize: 16, lineHeight: 24 },
  userTime: { fontSize: 10, marginTop: 4, textAlign: 'right' },
  chatImage: { width: 220, height: 220, borderRadius: 14, marginBottom: 8 },
  twinRow: { marginBottom: 24, paddingHorizontal: 12 },
  twinHeader: { alignItems: 'center', marginBottom: 8, gap: 10 },
  twinAvatarGlow: { borderRadius: 22, padding: 3 },
  twinAvatar: { width: 38, height: 38, borderRadius: 19 },
  twinName: { fontSize: 14, fontWeight: '700' },
  twinMeta: { alignItems: 'center', gap: 6 },
  emotionEmoji: { fontSize: 14 },
  timestamp: { fontSize: 11 },
  twinBadges: { marginTop: 2, gap: 6 },
  providerBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6 },
  providerText: { fontSize: 10, fontWeight: '600' },
  thinkingBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6 },
  thinkingText: { fontSize: 10, fontWeight: '600' },
  twinContent: { marginBottom: 8 },
  youtubeCard: { flexDirection: 'row', alignItems: 'center', padding: 10, borderRadius: 12, borderWidth: 1, borderColor: '#FF000020', marginBottom: 8 },
  actionRow: { alignItems: 'center', gap: 4, marginBottom: 4 },
  actionBtn: { padding: 6, borderRadius: 8 },
  activeLike: { backgroundColor: '#34C75915' },
  activeDislike: { backgroundColor: '#FF3B3015' },
  retryBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, padding: 10, borderRadius: 10, backgroundColor: 'rgba(255,59,48,0.08)', alignSelf: 'flex-start' },
  retryText: { fontSize: 13, fontWeight: '600' },
  toolChip: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20, borderWidth: 1 },
  toolChipText: { fontSize: 13, fontWeight: '600' },
});
