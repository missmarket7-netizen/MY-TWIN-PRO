import React, { memo, useState } from 'react';
import {
  View, Text, Image, StyleSheet, TouchableOpacity, Share,
  Linking, TextInput, Animated, Dimensions,
} from 'react-native';
import { ChatMessage } from '../../store/useTwinStore';
import {
  Copy, Share2, RotateCcw, Edit3, Check, ThumbsUp,
  ThumbsDown, ExternalLink, Film, X, Brain, Sparkles,
  Zap, MessageCircle, User as UserIcon, Bot,
} from 'lucide-react-native';
import Markdown from 'react-native-markdown-display';
import * as WebBrowser from 'expo-web-browser';
import * as Clipboard from 'expo-clipboard';

const { width: SCREEN_W } = Dimensions.get('window');
const APP_ICON = require('../../assets/icon.png');

// ==================== COLORS ====================

export const COLORS = {
  light: {
    bg: '#FFFFFF', headerBg: '#FAFAFA', border: '#E8E8E8', text: '#1A1A1A',
    subtext: '#8E8E93', bubbleUser: '#7C3AED', userText: '#FFFFFF',
    bubbleTwin: '#F5F5F7', twinText: '#1A1A1A',
    inputBg: '#F2F2F7', inputBorder: '#E5E5EA', sendActive: '#7C3AED',
    sendInactive: '#C7C7CC', retryColor: '#FF3B30', likeActive: '#34C759',
    dislikeActive: '#FF3B30', accent: '#7C3AED', codeBg: '#1C1C1E',
    tableBorder: '#E5E5EA', blockquoteBg: '#F2F2F7', link: '#5856D6',
  },
  dark: {
    bg: '#000000', headerBg: '#1C1C1E', border: '#38383A', text: '#FFFFFF',
    subtext: '#8E8E93', bubbleUser: '#7C3AED', userText: '#FFFFFF',
    bubbleTwin: '#1C1C1E', twinText: '#FFFFFF',
    inputBg: '#2C2C2E', inputBorder: '#38383A', sendActive: '#A78BFA',
    sendInactive: '#48484A', retryColor: '#FF453A', likeActive: '#30D158',
    dislikeActive: '#FF453A', accent: '#A78BFA', codeBg: '#0A0A0A',
    tableBorder: '#38383A', blockquoteBg: '#2C2C2E', link: '#5E5CE6',
  },
};

// ==================== HELPERS ====================

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
};

// ==================== MARKDOWN RENDERER ====================

export const MarkdownRenderer = memo(({ content, isDark }: { content: string; isDark: boolean }) => {
  const c = isDark ? COLORS.dark : COLORS.light;

  const markdownStyles: any = {
    body: { color: c.twinText, fontSize: 16, lineHeight: 26, fontFamily: 'System' },
    paragraph: { marginBottom: 12, marginTop: 4 },
    heading1: { fontSize: 24, fontWeight: '800', marginBottom: 16, marginTop: 8, color: c.accent, letterSpacing: -0.5 },
    heading2: { fontSize: 20, fontWeight: '700', marginBottom: 12, marginTop: 8, color: c.accent, letterSpacing: -0.3 },
    heading3: { fontSize: 18, fontWeight: '700', marginBottom: 10, marginTop: 6, color: c.text },
    heading4: { fontSize: 16, fontWeight: '700', marginBottom: 8, color: c.text },
    heading5: { fontSize: 15, fontWeight: '600', marginBottom: 6, color: c.subtext },
    heading6: { fontSize: 14, fontWeight: '600', marginBottom: 6, color: c.subtext },

    bullet_list: { marginBottom: 12, marginLeft: 8 },
    ordered_list: { marginBottom: 12, marginLeft: 8 },
    list_item: { marginBottom: 8, flexDirection: 'row', alignItems: 'flex-start' },
    bullet_list_icon: { marginRight: 10, marginTop: 8, width: 6, height: 6, borderRadius: 3, backgroundColor: c.accent },
    ordered_list_icon: { marginRight: 10, marginTop: 2, color: c.accent, fontWeight: '700', fontSize: 14 },

    table: { marginVertical: 16, borderWidth: 1, borderColor: c.tableBorder, borderRadius: 12, overflow: 'hidden' },
    thead: { backgroundColor: c.codeBg },
    th: { padding: 12, fontWeight: '700', color: c.text, fontSize: 14, borderRightWidth: 1, borderColor: c.tableBorder },
    td: { padding: 12, color: c.subtext, fontSize: 14, borderRightWidth: 1, borderTopWidth: 1, borderColor: c.tableBorder },
    tr: { borderBottomWidth: 1, borderColor: c.tableBorder },

    code_inline: {
      backgroundColor: c.codeBg, color: '#FF375F', paddingHorizontal: 8, paddingVertical: 3,
      borderRadius: 6, fontSize: 14, fontFamily: 'Courier', fontWeight: '600',
    },
    code_block: {
      backgroundColor: c.codeBg, padding: 16, borderRadius: 12, marginVertical: 12,
      borderWidth: 1, borderColor: c.border,
    },
    fence: {
      backgroundColor: c.codeBg, padding: 16, borderRadius: 12, marginVertical: 12,
      borderWidth: 1, borderColor: c.border,
    },
    code_block_content: { color: '#34C759', fontFamily: 'Courier', fontSize: 14, lineHeight: 22 },

    blockquote: {
      borderLeftWidth: 4, borderLeftColor: c.accent, paddingLeft: 16, paddingVertical: 12,
      marginVertical: 12, backgroundColor: c.blockquoteBg, borderRadius: 8,
    },

    link: { color: c.link, textDecorationLine: 'none', fontWeight: '600' },
    autolink: { color: c.link, textDecorationLine: 'none' },

    hr: { borderBottomWidth: 1, borderBottomColor: c.border, marginVertical: 20 },

    strong: { fontWeight: '700', color: c.text },
    em: { fontStyle: 'italic', color: c.subtext },
    s: { textDecorationLine: 'line-through', color: c.subtext },
    del: { textDecorationLine: 'line-through', color: c.subtext },

    image: { borderRadius: 12, marginVertical: 12, width: SCREEN_W - 80, height: 200 },

    tasklist: { marginLeft: 8 },
    tasklist_checkbox: { marginRight: 8, marginTop: 4 },
  };

  // ✅ إصلاح الخطأ 2: onLinkPress يجب أن يرجع boolean وليس Promise
  const handleLinkPress = (url: string): boolean => {
    WebBrowser.openBrowserAsync(url, {
      toolbarColor: isDark ? '#1C1C1E' : '#FFFFFF',
      controlsColor: c.accent,
    }).catch(() => {
      Linking.openURL(url);
    });
    return true; // ✅ نرجع boolean فوراً
  };

  return (
    <Markdown style={markdownStyles} onLinkPress={handleLinkPress}>
      {content}
    </Markdown>
  );
});

// ==================== COPY TOAST ====================

const CopyToast = memo(({ visible, isDark }: { visible: boolean; isDark: boolean }) => {
  if (!visible) return null;
  return (
    <View style={[styles.toastContainer, { backgroundColor: isDark ? '#2C2C2E' : '#1C1C1E' }]}>
      <Check size={16} stroke="#34C759" />
      <Text style={styles.toastText}>تم النسخ</Text>
    </View>
  );
});

// ==================== USER BUBBLE ====================

export const UserBubble = memo(({
  item, isDark, isRTL, onStartEdit, onSaveEdit,
  isEditing, editContent, setEditContent, onEditInInput,
}: any) => {
  const [fadeAnim] = useState(new Animated.Value(0));

  React.useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 200, useNativeDriver: true }).start();
  }, []);

  const c = isDark ? COLORS.dark : COLORS.light;
  const time = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <Animated.View style={[styles.userRow, { opacity: fadeAnim }]}>
      <View style={styles.userRowInner}>
        <View style={[styles.userBubble, { backgroundColor: c.bubbleUser }]}>
          {item.image && (
            <Image
              source={{ uri: item.image?.startsWith('data:') ? item.image : `data:image/jpeg;base64,${item.image}` }}
              style={styles.chatImage}
              resizeMode="cover"
            />
          )}
          {isEditing ? (
            <View style={{ gap: 10 }}>
              <TextInput
                style={[styles.editInput, { color: '#FFF', borderColor: 'rgba(255,255,255,0.3)' }]}
                value={editContent}
                onChangeText={setEditContent}
                multiline
                autoFocus
                placeholder="تعديل الرسالة..."
                placeholderTextColor="rgba(255,255,255,0.5)"
              />
              <View style={{ flexDirection: 'row', gap: 8, justifyContent: 'flex-end' }}>
                <TouchableOpacity onPress={() => onStartEdit?.(null)} style={styles.editCancelBtn}>
                  <Text style={{ color: '#FFF', fontSize: 13 }}>إلغاء</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => onSaveEdit(item, editContent)} style={styles.editSaveBtn}>
                  <Check size={16} stroke="#FFF" />
                  <Text style={{ color: '#FFF', fontSize: 13, fontWeight: '600' }}>حفظ</Text>
                </TouchableOpacity>
              </View>
            </View>
          ) : (
            <Text style={[styles.userText, { color: '#FFF' }]}>{item.content}</Text>
          )}

          <View style={[styles.metaRow, { justifyContent: 'flex-start' }]}>
            <Text style={[styles.timestamp, { color: 'rgba(255,255,255,0.6)' }]}>{time}</Text>
            {!isEditing && (
              <TouchableOpacity onPress={() => onEditInInput ? onEditInInput(item) : onStartEdit(item)} style={styles.editBtn}>
                <Edit3 size={12} stroke="rgba(255,255,255,0.6)" />
              </TouchableOpacity>
            )}
          </View>
        </View>
        <View style={[styles.avatarSmall, { backgroundColor: c.bubbleUser }]}>
          <UserIcon size={14} stroke="#FFF" />
        </View>
      </View>
    </Animated.View>
  );
});


// ==================== TWIN BUBBLE ====================

export const TwinBubble = memo(({
  item, isDark, isRTL, isLast, onCopy, onRetry,
  onRegenerate, onLike, onDislike, liked, disliked, provider,
}: any) => {
  const [fadeAnim] = useState(new Animated.Value(0));
  const [showToast, setShowToast] = useState(false);

  React.useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 300, useNativeDriver: true }).start();
  }, []);

  const c = isDark ? COLORS.dark : COLORS.light;
  const time = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  // ✅ إصلاح الخطأ 3: استخدام Clipboard.setStringAsync من expo-clipboard
  const handleCopy = async (text: string) => {
    try {
      await Clipboard.setStringAsync(text);
      setShowToast(true);
      setTimeout(() => setShowToast(false), 2000);
      onCopy?.(text);
    } catch (e) {
      console.warn('Copy failed:', e);
    }
  };

  const emotion = item.emotion || 'neutral';
  const emoji = emotionEmoji[emotion] || '😌';
  const prov = providerLabels[provider || 'multi_ai'] || providerLabels.multi_ai;
  const ProvIcon = prov.icon;

  return (
    <Animated.View style={[styles.twinRow, { opacity: fadeAnim }]}>
      <View style={styles.twinRowInner}>
        {/* Avatar */}
        <View style={styles.twinAvatarWrap}>
          <Image source={APP_ICON} style={styles.twinAvatar} />
          {item.memoryRecall && (
            <View style={[styles.memoryDot, { backgroundColor: c.likeActive }]}>
              <Brain size={10} stroke="#FFF" />
            </View>
          )}
        </View>

        {/* Content */}
        <View style={[styles.twinContent, { backgroundColor: c.bubbleTwin }]}>
          {/* Header */}
          <View style={[styles.twinHeader, { flexDirection: isRTL ? 'row-reverse' : 'row' }]}>
            <View style={[styles.providerBadge, { backgroundColor: c.codeBg }]}>
              <ProvIcon size={12} stroke={c.accent} />
              <Text style={[styles.providerText, { color: c.subtext }]}>{prov.ar}</Text>
            </View>

            {item.emotion && (
              <View style={[styles.emotionBadge, { backgroundColor: c.blockquoteBg }]}>
                <Text style={styles.emotionEmoji}>{emoji}</Text>
                <Text style={[styles.emotionText, { color: c.subtext }]}>{emotion}</Text>
              </View>
            )}

            <Text style={[styles.timestamp, { color: c.subtext }]}>{time}</Text>
          </View>

          {/* Thinking Stage */}
          {item.thinkingStage && item.thinkingStage !== 'complete' && (
            <View style={[styles.thinkingBadge, { backgroundColor: c.blockquoteBg }]}>
              <Zap size={12} stroke={c.accent} />
              <Text style={[styles.thinkingText, { color: c.accent }]}>
                {item.thinkingStage === 'thinking' ? 'يفكر...' :
                 item.thinkingStage === 'searching' ? 'يبحث...' :
                 item.thinkingStage === 'reflecting' ? 'يتأمل...' : item.thinkingStage}
              </Text>
            </View>
          )}

          {/* YouTube Card */}
          {item.youtubeVideo && (
            <TouchableOpacity
              onPress={() => Linking.openURL(item.youtubeVideo)}
              style={[styles.youtubeCard, { backgroundColor: isDark ? '#1C1C1E' : '#FFF0F0' }]}
              activeOpacity={0.8}
            >
              <View style={[styles.youtubeIconWrap, { backgroundColor: '#FF000020' }]}>
                <Film size={20} stroke="#FF0000" />
              </View>
              <View style={{ flex: 1, marginHorizontal: 10 }}>
                <Text style={{ color: '#FF0000', fontWeight: '700', fontSize: 14 }}>▶️ شاهد الفيديو</Text>
                <Text style={{ color: c.subtext, fontSize: 11, marginTop: 2 }} numberOfLines={1}>{item.youtubeVideo}</Text>
              </View>
              <ExternalLink size={16} stroke="#FF0000" />
            </TouchableOpacity>
          )}

          {/* Content */}
          <View style={styles.contentWrap}>
            <MarkdownRenderer content={item.content} isDark={isDark} />
          </View>

          {/* Actions */}
          <View style={[styles.actionRow, { flexDirection: isRTL ? 'row-reverse' : 'row' }]}>
            <TouchableOpacity onPress={() => handleCopy(item.content)} style={styles.actionBtn} activeOpacity={0.6}>
              <Copy size={16} stroke={c.subtext} />
            </TouchableOpacity>

            <TouchableOpacity onPress={() => Share.share({ message: item.content })} style={styles.actionBtn} activeOpacity={0.6}>
              <Share2 size={16} stroke={c.subtext} />
            </TouchableOpacity>

            {isLast && (
              <TouchableOpacity onPress={() => onRegenerate(item)} style={styles.actionBtn} activeOpacity={0.6}>
                <RotateCcw size={16} stroke={c.subtext} />
              </TouchableOpacity>
            )}

            <View style={styles.divider} />

            <TouchableOpacity onPress={() => onLike(item)} style={[styles.actionBtn, liked && styles.activeLike]} activeOpacity={0.6}>
              <ThumbsUp size={16} stroke={liked ? c.likeActive : c.subtext} fill={liked ? c.likeActive : 'transparent'} />
            </TouchableOpacity>

            <TouchableOpacity onPress={() => onDislike(item)} style={[styles.actionBtn, disliked && styles.activeDislike]} activeOpacity={0.6}>
              <ThumbsDown size={16} stroke={disliked ? c.dislikeActive : c.subtext} fill={disliked ? c.dislikeActive : 'transparent'} />
            </TouchableOpacity>
          </View>

          {/* Retry */}
          {item.failed && (
            <TouchableOpacity onPress={() => onRetry(item)} style={styles.retryBtn} activeOpacity={0.8}>
              <RotateCcw size={14} stroke={c.retryColor} />
              <Text style={[styles.retryText, { color: c.retryColor }]}>إعادة المحاولة</Text>
            </TouchableOpacity>
          )}

          <CopyToast visible={showToast} isDark={isDark} />
        </View>
      </View>
    </Animated.View>
  );
});

// ==================== TOOL CHIP ====================

export const ToolChip = memo(({ label, icon: Icon, color, onClose }: any) => (
  <View style={[styles.toolChip, { backgroundColor: color + '12', borderColor: color + '25' }]}>
    <Icon size={14} stroke={color} />
    <Text style={[styles.toolChipText, { color }]}>{label}</Text>
    <TouchableOpacity onPress={onClose} style={styles.toolChipClose} activeOpacity={0.6}>
      <X size={12} stroke={color} />
    </TouchableOpacity>
  </View>
));

// ==================== STYLES ====================

const styles = StyleSheet.create({
  toastContainer: {
    position: 'absolute', top: -40, right: 10,
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 12, paddingVertical: 6,
    borderRadius: 20, zIndex: 100,
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15, shadowRadius: 8, elevation: 4,
  },
  toastText: { color: '#FFF', fontSize: 13, fontWeight: '600' },

  userRow: { flexDirection: 'row', justifyContent: 'flex-end', marginBottom: 20, paddingHorizontal: 12 },
  userRowInner: { flexDirection: 'row', alignItems: 'flex-end', gap: 8, maxWidth: '85%' },
  userBubble: {
    paddingHorizontal: 16, paddingVertical: 12, borderRadius: 20,
    borderBottomRightRadius: 4, gap: 6,
    shadowColor: '#7C3AED', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15, shadowRadius: 8, elevation: 3,
  },
  userText: { fontSize: 16, lineHeight: 24, fontWeight: '400' },
  chatImage: { width: 220, height: 220, borderRadius: 14, marginBottom: 8 },
  metaRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 4 },
  timestamp: { fontSize: 11, fontWeight: '500' },
  editBtn: { padding: 4, borderRadius: 6, backgroundColor: 'rgba(255,255,255,0.15)' },
  editInput: {
    fontSize: 16, padding: 10, borderRadius: 10,
    borderWidth: 1, backgroundColor: 'rgba(255,255,255,0.1)',
    minHeight: 60, textAlignVertical: 'top',
  },
  editCancelBtn: {
    paddingHorizontal: 14, paddingVertical: 8,
    borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.15)',
  },
  editSaveBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 14, paddingVertical: 8,
    borderRadius: 8, backgroundColor: '#34C759',
  },
  avatarSmall: {
    width: 28, height: 28, borderRadius: 14,
    justifyContent: 'center', alignItems: 'center',
  },

  twinRow: { marginBottom: 24, paddingHorizontal: 12 },
  twinRowInner: { flexDirection: 'row', alignItems: 'flex-start', gap: 10 },
  twinAvatarWrap: { position: 'relative' },
  twinAvatar: { width: 32, height: 32, borderRadius: 16 },
  memoryDot: {
    position: 'absolute', bottom: -2, right: -2,
    width: 16, height: 16, borderRadius: 8,
    justifyContent: 'center', alignItems: 'center',
    borderWidth: 2, borderColor: '#000',
  },
  twinContent: {
    flex: 1, borderRadius: 16, padding: 14, gap: 10,
    borderWidth: 1, borderColor: 'transparent',
    shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05, shadowRadius: 4, elevation: 1,
  },
  twinHeader: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    flexWrap: 'wrap', marginBottom: 4,
  },
  providerBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8,
  },
  providerText: { fontSize: 11, fontWeight: '600' },
  emotionBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8,
  },
  emotionEmoji: { fontSize: 14 },
  emotionText: { fontSize: 11, fontWeight: '500' },
  thinkingBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8,
    alignSelf: 'flex-start',
  },
  thinkingText: { fontSize: 12, fontWeight: '600' },
  contentWrap: { marginTop: 4 },
  youtubeCard: {
    flexDirection: 'row', alignItems: 'center',
    padding: 12, borderRadius: 12, marginBottom: 8,
    borderWidth: 1, borderColor: '#FF000020',
  },
  youtubeIconWrap: {
    width: 40, height: 40, borderRadius: 10,
    justifyContent: 'center', alignItems: 'center',
  },

  actionRow: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    marginTop: 8, paddingTop: 8,
    borderTopWidth: 1, borderTopColor: 'rgba(128,128,128,0.1)',
  },
  actionBtn: { padding: 8, borderRadius: 8 },
  activeLike: { backgroundColor: '#34C75915' },
  activeDislike: { backgroundColor: '#FF3B3015' },
  divider: { width: 1, height: 20, backgroundColor: 'rgba(128,128,128,0.2)', marginHorizontal: 4 },

  retryBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    marginTop: 8, padding: 10, borderRadius: 10,
    backgroundColor: 'rgba(255,59,48,0.08)', alignSelf: 'flex-start',
  },
  retryText: { fontSize: 13, fontWeight: '600' },

  toolChip: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 12, paddingVertical: 8,
    borderRadius: 20, borderWidth: 1,
  },
  toolChipText: { fontSize: 13, fontWeight: '600' },
  toolChipClose: { marginLeft: 4, padding: 2 },
});
