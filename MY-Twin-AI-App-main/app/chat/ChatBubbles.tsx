import React, { memo } from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity, Share, Linking, TextInput } from 'react-native';
import { ChatMessage } from '../../store/useTwinStore';
import { Copy, Share2, RotateCcw, Edit3, Check, ThumbsUp, ThumbsDown, ExternalLink, Film, X, Cpu } from 'lucide-react-native';
import Markdown from 'react-native-markdown-display';

const APP_ICON = require('../../assets/icon.png');

export const COLORS = {
  light: {
    bg: '#FFFFFF', headerBg: '#FFFFFF', border: '#E5E5E5', text: '#1A1A1A',
    subtext: '#999', bubbleUser: '#7C3AED', userText: '#FFFFFF',
    inputBg: '#F5F5F5', inputBorder: '#E5E5E5', sendActive: '#7C3AED',
    sendInactive: '#CCC', retryColor: '#EF4444', likeActive: '#10B981', dislikeActive: '#EF4444',
  },
  dark: {
    bg: '#1A1A1A', headerBg: '#1A1A1A', border: '#333', text: '#FFF',
    subtext: '#999', bubbleUser: '#7C3AED', userText: '#FFF',
    inputBg: '#2A2A2A', inputBorder: '#444', sendActive: '#7C3AED',
    sendInactive: '#555', retryColor: '#EF4444', likeActive: '#10B981', dislikeActive: '#EF4444',
  },
};

export const MarkdownRenderer = memo(({ content, isDark }: { content: string; isDark: boolean }) => {
  const markdownStyles: any = {
    body: { color: isDark ? '#FFF' : '#1A1A1A', fontSize: 16, lineHeight: 26 },
    heading1: { fontSize: 22, fontWeight: 'bold', marginBottom: 10, color: isDark ? '#FFF' : '#1A1A1A' },
    heading2: { fontSize: 20, fontWeight: 'bold', marginBottom: 8, color: isDark ? '#FFF' : '#1A1A1A' },
    heading3: { fontSize: 18, fontWeight: 'bold', marginBottom: 6, color: isDark ? '#FFF' : '#1A1A1A' },
    list_item: { marginBottom: 6, flexDirection: 'row' },
    bullet_list: { marginBottom: 10 },
    ordered_list: { marginBottom: 10 },
    table: { marginBottom: 10, borderWidth: 1, borderColor: isDark ? '#444' : '#E0E0E0', borderRadius: 8 },
    th: { padding: 8, backgroundColor: isDark ? '#333' : '#F5F5F5', fontWeight: 'bold' },
    td: { padding: 8, borderTopWidth: 1, borderColor: isDark ? '#444' : '#E0E0E0' },
    code_inline: { backgroundColor: isDark ? '#333' : '#F0F0F0', color: isDark ? '#FFF' : '#333', paddingHorizontal: 6, borderRadius: 4 },
    code_block: { backgroundColor: isDark ? '#222' : '#F0F0F0', padding: 12, borderRadius: 8, marginBottom: 8 },
    blockquote: { borderLeftWidth: 3, borderLeftColor: '#7C3AED', paddingLeft: 12, marginBottom: 8, backgroundColor: isDark ? '#2A2A2A' : '#F9F9F9' },
    strong: { fontWeight: 'bold' },
    em: { fontStyle: 'italic' },
    link: { color: '#7C3AED', textDecorationLine: 'underline' },
    thematicBreak: { borderBottomWidth: 1, borderBottomColor: isDark ? '#444' : '#E0E0E0', marginVertical: 16 },
  };
  return <Markdown style={markdownStyles} onLinkPress={(url: string) => { Linking.openURL(url).catch(() => {}); return false; }}>{content}</Markdown>;
});

export const UserBubble = memo(({ item, isDark, onStartEdit, onSaveEdit, isEditing, editContent, setEditContent, onEditInInput }: any) => (
  <View style={styles.userRow}>
    <View style={[styles.userBubble, { backgroundColor: isDark ? COLORS.dark.bubbleUser : COLORS.light.bubbleUser }]}>
      {item.image && <Image source={{ uri: item.image?.startsWith('data:') ? item.image : `data:image/jpeg;base64,${item.image}` }} style={styles.chatImage} />}
      {isEditing ? (
        <View style={{ gap: 8 }}>
          <TextInput style={[styles.editInput, { color: '#FFF' }]} value={editContent} onChangeText={setEditContent} multiline autoFocus />
          <TouchableOpacity onPress={() => onSaveEdit(item, editContent)} style={styles.editSaveBtn}><Check size={16} stroke="#FFF" /></TouchableOpacity>
        </View>
      ) : (
        <Text style={[styles.userText, { color: '#FFF' }]}>{item.content}</Text>
      )}
      {/* زر القلم: يحفظ النص في حقل الإدخال */}
      <TouchableOpacity onPress={() => onEditInInput ? onEditInInput(item) : onStartEdit(item)} style={styles.editBtn}>
        <Edit3 size={14} stroke="#FFF" />
      </TouchableOpacity>
    </View>
  </View>
));

const ProviderBadge = memo(({ provider, isDark }: { provider: string; isDark: boolean }) => {
  const labelMap: Record<string, string> = {
    groq: 'Groq', gemini: 'Gemini', openrouter: 'Llama 4',
    model_router: 'AI', agent_loop: 'Agent', multi_ai: 'Multi-AI',
    fallback: 'AI', tool: 'Tool',
  };
  const colorMap: Record<string, string> = {
    groq: '#F59E0B', gemini: '#10B981', openrouter: '#3B82F6',
    model_router: '#8B5CF6', agent_loop: '#EC4899', multi_ai: '#7C3AED',
    fallback: '#EF4444', tool: '#6366F1',
  };
  const label = labelMap[provider] || provider;
  const color = colorMap[provider] || '#666';
  return (
    <View style={[styles.providerBadge, { backgroundColor: color + '15', borderColor: color + '30' }]}>
      <Cpu size={10} stroke={color} />
      <Text style={[styles.providerText, { color }]}>{label}</Text>
    </View>
  );
});

export const TwinBubble = memo(({ item, isDark, onCopy, onRetry, onRegenerate, onLike, onDislike, liked, disliked, provider }: any) => (
  <View style={styles.twinRow}>
    {/* أيقونة التوأم أعلى الرد */}
    <Image source={APP_ICON} style={styles.twinAvatarTop} />
    <View style={styles.twinContentFull}>
      {item.youtubeVideo && (
        <TouchableOpacity onPress={() => Linking.openURL(item.youtubeVideo!)} style={styles.youtubeCard}>
          <Film size={24} stroke="#EF4444" />
          <View style={{ flex: 1, marginLeft: 8 }}><Text style={{ color: '#EF4444', fontWeight: '600' }}>▶️ شاهد الفيديو</Text><Text style={{ color: '#999', fontSize: 11 }}>{item.youtubeVideo}</Text></View>
          <ExternalLink size={16} stroke="#EF4444" />
        </TouchableOpacity>
      )}
      <MarkdownRenderer content={item.content} isDark={isDark} />
      <View style={styles.actionRow}>
        <TouchableOpacity onPress={() => onCopy(item.content)} style={styles.actionBtn}><Copy size={16} stroke={isDark ? '#999' : '#666'} /></TouchableOpacity>
        <TouchableOpacity onPress={() => Share.share({ message: item.content })} style={styles.actionBtn}><Share2 size={16} stroke={isDark ? '#999' : '#666'} /></TouchableOpacity>
        <TouchableOpacity onPress={() => onRegenerate(item)} style={styles.actionBtn}><RotateCcw size={16} stroke={isDark ? '#999' : '#666'} /></TouchableOpacity>
        <TouchableOpacity onPress={() => onLike(item)} style={[styles.actionBtn, liked && { backgroundColor: '#10B98120', borderRadius: 8 }]}><ThumbsUp size={16} stroke={liked ? '#10B981' : isDark ? '#999' : '#666'} fill={liked ? '#10B981' : 'transparent'} /></TouchableOpacity>
        <TouchableOpacity onPress={() => onDislike(item)} style={[styles.actionBtn, disliked && { backgroundColor: '#EF444420', borderRadius: 8 }]}><ThumbsDown size={16} stroke={disliked ? '#EF4444' : isDark ? '#999' : '#666'} fill={disliked ? '#EF4444' : 'transparent'} /></TouchableOpacity>
      </View>
      {provider && <ProviderBadge provider={provider} isDark={isDark} />}
      {item.failed && (
        <TouchableOpacity onPress={() => onRetry(item)} style={styles.retryBtn}><RotateCcw size={14} stroke="#EF4444" /><Text style={styles.retryText}>إعادة المحاولة</Text></TouchableOpacity>
      )}
    </View>
  </View>
));

export const ToolChip = memo(({ label, icon: Icon, color, onClose }: any) => (
  <View style={[styles.toolChip, { backgroundColor: color + '15', borderColor: color + '30' }]}>
    <Icon size={16} stroke={color} /><Text style={[styles.toolChipText, { color }]}>{label}</Text>
    <TouchableOpacity onPress={onClose} style={styles.toolChipClose}><X size={14} stroke={color} /></TouchableOpacity>
  </View>
));

const styles = StyleSheet.create({
  userRow: { flexDirection: 'row', justifyContent: 'flex-end', marginBottom: 20 },
  userBubble: { maxWidth: '80%', paddingHorizontal: 16, paddingVertical: 12, borderRadius: 20, borderBottomRightRadius: 4 },
  userText: { fontSize: 16, lineHeight: 24 },
  chatImage: { width: 220, height: 220, borderRadius: 14, marginBottom: 8 },
  editBtn: { position: 'absolute', bottom: -12, right: 8, backgroundColor: 'rgba(255,255,255,0.3)', borderRadius: 10, padding: 4 },
  editInput: { fontSize: 16, padding: 8, borderRadius: 8, borderWidth: 1, borderColor: '#FFF' },
  editSaveBtn: { backgroundColor: '#10B981', borderRadius: 14, padding: 6 },
  twinRow: { alignItems: 'flex-start', marginBottom: 24, paddingHorizontal: 16 },
  twinAvatarTop: { width: 30, height: 30, borderRadius: 15, marginBottom: 8 },
  twinContentFull: { width: '100%' },
  youtubeCard: { flexDirection: 'row', alignItems: 'center', padding: 10, borderRadius: 12, borderWidth: 1, borderColor: '#EF444420', backgroundColor: '#EF444410', marginBottom: 8 },
  actionRow: { flexDirection: 'row', alignItems: 'center', gap: 12, marginTop: 10 },
  actionBtn: { padding: 4 },
  retryBtn: { flexDirection: 'row', alignItems: 'center', marginTop: 8, gap: 4 },
  retryText: { color: '#EF4444', fontSize: 13 },
  toolChip: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20, borderWidth: 1 },
  toolChipText: { fontSize: 13, fontWeight: '500' },
  toolChipClose: { marginLeft: 4, padding: 2 },
  providerBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8, borderWidth: 1, alignSelf: 'flex-start', marginTop: 8 },
  providerText: { fontSize: 10, fontWeight: '600' },
});
