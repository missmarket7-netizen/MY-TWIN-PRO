import React, { memo, useRef, useState, useEffect, useMemo } from 'react';
import {
  View, Text, Image, StyleSheet, TouchableOpacity, Share,
  Linking, Animated,
} from 'react-native';
import {
  Copy, Share2, RotateCcw, ThumbsUp, ThumbsDown,
  Film, X, Sparkles, Zap, Bot, Cpu, Shield, Brain,
} from 'lucide-react-native';
import Markdown from 'react-native-markdown-display';
import * as WebBrowser from 'expo-web-browser';
import * as Clipboard from 'expo-clipboard';

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

// إيموجي المشاعر
const emotionEmoji: Record<string, string> = {
  joy: '😊', sadness: '😢', anger: '😠', fear: '😨', love: '❤️',
  surprise: '😮', neutral: '😌',
};

// ملصقات المزود (محدثة)
const providerLabels: Record<string, { ar: string; en: string; icon: any }> = {
  multi_ai: { ar: 'ذكاء متعدد', en: 'Multi AI', icon: Sparkles },
  orchestrator: { ar: 'المنسق', en: 'Orchestrator', icon: Brain },
  internal_mytwin: { ar: 'نموذج خاص', en: 'MyTwin', icon: Shield },
  gemini: { ar: 'Gemini', en: 'Gemini', icon: Sparkles },
  groq: { ar: 'Groq', en: 'Groq', icon: Cpu },
  openrouter: { ar: 'OpenRouter', en: 'OpenRouter', icon: Zap },
  tool: { ar: 'أداة', en: 'Tool', icon: Zap },
  error: { ar: 'خطأ', en: 'Error', icon: X },
  fallback: { ar: 'احتياطي', en: 'Fallback', icon: X },
};

// عارض Markdown
export const MarkdownRenderer = memo(({ content, isDark }: { content: string; isDark: boolean }) => {
  const c = isDark ? COLORS.dark : COLORS.light;
  const styles = useMemo(() => ({
    body: { color: c.twinText, fontSize: 16, lineHeight: 26 },
    code_inline: { backgroundColor: c.codeBg, color: '#FF375F', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
    code_block: { backgroundColor: c.codeBg, padding: 16, borderRadius: 12, marginVertical: 12 },
    link: { color: c.link, fontWeight: '600' },
  }), [isDark]);

  const handleLinkPress = (url: string): boolean => {
    WebBrowser.openBrowserAsync(url).catch(() => Linking.openURL(url));
    return true;
  };

  return <Markdown style={styles} onLinkPress={handleLinkPress}>{content}</Markdown>;
});

// فقاعة المستخدم
export const UserBubble = memo(({ item, isDark }: any) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  useEffect(() => { Animated.timing(fadeAnim, { toValue: 1, duration: 200, useNativeDriver: true }).start(); }, []);
  const c = isDark ? COLORS.dark : COLORS.light;
  const time = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <Animated.View style={[styles.userRow, { opacity: fadeAnim }]}>
      <View style={[styles.userBubble, { backgroundColor: c.bubbleUser }]}>
        <Text style={[styles.userText, { color: '#FFF' }]}>{item.content}</Text>
        <Text style={[styles.userTime, { color: 'rgba(255,255,255,0.6)' }]}>{time}</Text>
      </View>
    </Animated.View>
  );
});

// فقاعة التوأم (محدثة)
export const TwinBubble = memo(({ item, isDark, isRTL, isLast, onCopy, onRetry, onRegenerate, onLike, onDislike, provider, lang }: any) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 300, useNativeDriver: true }).start();
  }, []);

  const c = isDark ? COLORS.dark : COLORS.light;
  const time = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const emotion = item.emotion || 'neutral';
  const emoji = emotionEmoji[emotion] || '😌';

  // استخدام ألوان المشاعر من theme.ts
  let emotionColor = c.accent;
  try {
    const { getEmotionColor } = require('../../utils/theme');
    emotionColor = getEmotionColor(emotion, { emotionJoy: '#F59E0B', emotionSad: '#60A5FA', emotionFear: '#A78BFA', emotionLove: '#EC4899', emotionAnger: '#FF6B6B', emotionNeutral: c.subtext, emotionSurprise: '#F472B6' } as any);
  } catch {}

  const prov = providerLabels[provider || 'orchestrator'] || providerLabels.orchestrator;
  const ProvIcon = prov.icon;

  return (
    <Animated.View style={[styles.twinRow, { opacity: fadeAnim }]}>
      <View style={[styles.twinHeader, { flexDirection: isRTL ? 'row-reverse' : 'row' }]}>
        <Image source={APP_ICON} style={styles.twinAvatar} />
        <View style={{ flex: 1 }}>
          <View style={[styles.twinMeta, { flexDirection: isRTL ? 'row-reverse' : 'row' }]}>
            <Text style={[styles.twinName, { color: c.text }]}>MyTwin</Text>
            {item.emotion && <Text>{emoji}</Text>}
            <Text style={[styles.timestamp, { color: c.subtext }]}>{time}</Text>
          </View>
          <View style={[styles.twinBadges, { flexDirection: isRTL ? 'row-reverse' : 'row' }]}>
            <View style={[styles.providerBadge, { backgroundColor: c.codeBg, borderLeftColor: emotionColor, borderLeftWidth: 2 }]}>
              <ProvIcon size={10} stroke={emotionColor} />
              <Text style={[styles.providerText, { color: c.subtext }]}>{lang === 'ar' ? prov.ar : prov.en}</Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.twinContent}>
        <MarkdownRenderer content={item.content} isDark={isDark} />
      </View>

      {/* شريط الإجراءات */}
      <View style={[styles.actionRow, { flexDirection: isRTL ? 'row-reverse' : 'row' }]}>
        <TouchableOpacity onPress={() => Clipboard.setStringAsync(item.content)} style={styles.actionBtn}><Copy size={15} stroke={c.subtext} /></TouchableOpacity>
        <TouchableOpacity onPress={() => Share.share({ message: item.content })} style={styles.actionBtn}><Share2 size={15} stroke={c.subtext} /></TouchableOpacity>
        {isLast && <TouchableOpacity onPress={() => onRegenerate(item)} style={styles.actionBtn}><RotateCcw size={15} stroke={c.subtext} /></TouchableOpacity>}
        <TouchableOpacity onPress={() => onLike(item)} style={styles.actionBtn}><ThumbsUp size={15} stroke={c.subtext} /></TouchableOpacity>
        <TouchableOpacity onPress={() => onDislike(item)} style={styles.actionBtn}><ThumbsDown size={15} stroke={c.subtext} /></TouchableOpacity>
      </View>

      {item.failed && (
        <TouchableOpacity onPress={() => onRetry(item)} style={styles.retryBtn}>
          <RotateCcw size={14} stroke={c.retryColor} />
          <Text style={[styles.retryText, { color: c.retryColor }]}>إعادة المحاولة</Text>
        </TouchableOpacity>
      )}
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

const styles = StyleSheet.create({
  userRow: { flexDirection: 'row', justifyContent: 'flex-end', marginBottom: 20, paddingHorizontal: 12 },
  userBubble: { paddingHorizontal: 16, paddingVertical: 12, borderRadius: 20, borderBottomRightRadius: 4, maxWidth: '85%' },
  userText: { fontSize: 16, lineHeight: 24 },
  userTime: { fontSize: 10, marginTop: 4, textAlign: 'right' },
  twinRow: { marginBottom: 24, paddingHorizontal: 12 },
  twinHeader: { alignItems: 'center', marginBottom: 8, gap: 10 },
  twinAvatar: { width: 38, height: 38, borderRadius: 19 },
  twinName: { fontSize: 14, fontWeight: '700' },
  twinMeta: { alignItems: 'center', gap: 6 },
  timestamp: { fontSize: 11 },
  twinBadges: { marginTop: 2, gap: 6 },
  providerBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6 },
  providerText: { fontSize: 10, fontWeight: '600' },
  twinContent: { marginBottom: 8 },
  actionRow: { alignItems: 'center', gap: 4, marginBottom: 4 },
  actionBtn: { padding: 6, borderRadius: 8 },
  retryBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, padding: 10, borderRadius: 10, backgroundColor: 'rgba(255,59,48,0.08)', alignSelf: 'flex-start' },
  retryText: { fontSize: 13, fontWeight: '600' },
  toolChip: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20, borderWidth: 1 },
  toolChipText: { fontSize: 13, fontWeight: '600' },
});
