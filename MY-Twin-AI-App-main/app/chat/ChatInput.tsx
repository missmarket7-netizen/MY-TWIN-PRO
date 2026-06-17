import React, { memo, useState, useRef } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  Modal, Animated, ActivityIndicator, ScrollView,
} from 'react-native';
import {
  Send, X, Camera, Image as ImageIcon, FileText,
  Search, Cloud, Music, Film, DollarSign, TrendingUp,
  Wand2, Mic, MicOff, Brain, Sparkles, Zap,
} from 'lucide-react-native';
import { ToolChip } from './ChatBubbles';

const SCREEN_WIDTH = require('react-native').Dimensions.get('window').width;

export const ChatInput = memo(({
  input, setInput, loading, isRTL, isDark, colors, lang,
  onSend, onAddTool, activeTools, onRemoveTool,
  onCamera, onGallery, onFile,
  showAttach, setShowAttach, attachAnim,
}: any) => {
  const [isRecording, setIsRecording] = useState(false);
  const [showQuickReplies, setShowQuickReplies] = useState(false);
  const inputRef = useRef<TextInput>(null);

  // ✅ قائمة الأدوات والإرفاق الموحدة
  const unifiedMenu = [
    { icon: Camera, label_ar: 'كاميرا', label_en: 'Camera', color: '#8B5CF6', onPress: onCamera },
    { icon: ImageIcon, label_ar: 'معرض', label_en: 'Gallery', color: '#EC4899', onPress: onGallery },
    { icon: FileText, label_ar: 'ملف', label_en: 'File', color: '#F59E0B', onPress: onFile },
    { icon: Wand2, label_ar: 'صورة AI', label_en: 'AI Image', color: '#A855F7', tool: 'image' },
    { icon: Film, label_ar: 'يوتيوب', label_en: 'YouTube', color: '#EF4444', tool: 'youtube' },
    { icon: Music, label_ar: 'موسيقى', label_en: 'Music', color: '#EC4899', tool: 'spotify' },
    { icon: Cloud, label_ar: 'طقس', label_en: 'Weather', color: '#06B6D4', tool: 'weather' },
    { icon: DollarSign, label_ar: 'عملات', label_en: 'Currency', color: '#10B981', tool: 'currency' },
    { icon: TrendingUp, label_ar: 'أخبار', label_en: 'News', color: '#8B5CF6', tool: 'news' },
    { icon: Search, label_ar: 'بحث', label_en: 'Search', color: '#6366F1', tool: 'search' },
  ];

  // ✅ ردود سريعة ذكية
  const quickReplies = lang === 'ar' ? [
    'كيف حالك؟', 'شكراً', 'ممتاز', 'أحتاج مساعدة',
  ] : [
    'How are you?', 'Thanks', 'Great', 'I need help',
  ];

  const handleToolSelect = (item: any) => {
    setShowAttach(false);
    if (item.onPress) {
      item.onPress();
    } else if (item.tool && onAddTool) {
      onAddTool({
        type: item.tool,
        label: lang === 'ar' ? item.label_ar : item.label_en,
        icon: item.icon,
        color: item.color,
      });
    }
  };

  const handleQuickReply = (text: string) => {
    setInput(text);
    setShowQuickReplies(false);
    inputRef.current?.focus();
  };

  const handleVoicePress = () => {
    setIsRecording(!isRecording);
    // TODO: تكامل مع expo-av للتسجيل الصوتي
  };

  const hasContent = input.trim().length > 0 || (activeTools && activeTools.length > 0);

  return (
    <>
      {/* ✅ الأدوات النشطة */}
      {activeTools && activeTools.length > 0 && (
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={[styles.chipsRow, { backgroundColor: colors.headerBg }]}
          contentContainerStyle={{ paddingHorizontal: 16, gap: 8 }}
        >
          {activeTools.map((tool: any) => (
            <ToolChip
              key={tool.id}
              label={tool.label}
              icon={tool.icon}
              color={tool.color}
              onClose={() => onRemoveTool && onRemoveTool(tool.id)}
            />
          ))}
        </ScrollView>
      )}

      {/* ✅ ردود سريعة (تظهر عندما يكون الإدخال فارغاً) */}
      {!hasContent && !loading && (
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={[styles.quickRepliesRow, { backgroundColor: colors.headerBg }]}
          contentContainerStyle={{ paddingHorizontal: 16, gap: 8 }}
        >
          {quickReplies.map((reply, i) => (
            <TouchableOpacity
              key={i}
              style={[styles.quickReplyChip, { backgroundColor: colors.inputBg, borderColor: colors.border }]}
              onPress={() => handleQuickReply(reply)}
              activeOpacity={0.7}
            >
              <Text style={[styles.quickReplyText, { color: colors.text }]}>{reply}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      )}


      {/* ✅ شريط الإدخال المحسّن */}
      <View style={[styles.inputBar, { backgroundColor: colors.headerBg, borderTopColor: colors.border }]}>
        {/* زر الإرفاق */}
        <TouchableOpacity
          onPress={() => setShowAttach(true)}
          style={[styles.attachBtn, { backgroundColor: colors.inputBg }]}
          activeOpacity={0.7}
        >
          <Text style={{ fontSize: 20, color: colors.subtext, fontWeight: '300' }}>+</Text>
        </TouchableOpacity>

        {/* حقل الإدخال */}
        <View style={[styles.inputWrap, { backgroundColor: colors.inputBg, borderColor: colors.inputBorder }]}>
          <TextInput
            ref={inputRef}
            style={[styles.textInput, isRTL && { textAlign: 'right' }, { color: colors.text }]}
            value={input}
            onChangeText={setInput}
            placeholder={lang === 'ar' ? 'اكتب رسالتك... 💬' : 'Type a message... 💬'}
            placeholderTextColor={colors.subtext}
            multiline
            maxLength={2000}
            editable={!loading}
            onSubmitEditing={() => onSend && onSend()}
            returnKeyType="send"
          />
          
          {/* ✅ زر الميكروفون (STT) - يعمل في كل الباقات */}
          <TouchableOpacity
            onPress={handleVoicePress}
            style={[styles.micBtn, isRecording && styles.micActive]}
            activeOpacity={0.7}
          >
            {isRecording ? (
              <MicOff size={18} stroke="#FF3B30" />
            ) : (
              <Mic size={18} stroke={colors.subtext} />
            )}
          </TouchableOpacity>
        </View>

        {/* زر الإرسال */}
        <TouchableOpacity
          onPress={() => onSend && onSend()}
          disabled={loading || !hasContent}
          style={[
            styles.sendBtn,
            {
              backgroundColor: hasContent && !loading ? colors.sendActive : colors.sendInactive,
              shadowColor: hasContent && !loading ? colors.sendActive : 'transparent',
            }
          ]}
          activeOpacity={0.8}
        >
          {loading ? (
            <ActivityIndicator size="small" color="#FFF" />
          ) : (
            <Send size={20} stroke="#FFF" />
          )}
        </TouchableOpacity>
      </View>

      {/* ✅ نافذة الإرفاق والأدوات المحسّنة */}
      <Modal
        visible={showAttach}
        transparent
        animationType="none"
        onRequestClose={() => setShowAttach(false)}
      >
        <TouchableOpacity
          style={styles.attachOverlay}
          activeOpacity={1}
          onPress={() => setShowAttach(false)}
        >
          <Animated.View style={[
            styles.attachContainer,
            {
              backgroundColor: isDark ? '#1C1C1E' : '#FFF',
              transform: [{ translateY: attachAnim.interpolate({ inputRange: [0, 1], outputRange: [400, 0] }) }]
            }
          ]}>
            {/* Header */}
            <View style={styles.attachHeader}>
              <Text style={[styles.attachTitle, { color: colors.text }]}>
                {lang === 'ar' ? 'إرفاق وأدوات' : 'Attach & Tools'}
              </Text>
              <TouchableOpacity onPress={() => setShowAttach(false)} style={styles.closeBtn}>
                <X size={22} stroke={colors.subtext} />
              </TouchableOpacity>
            </View>

            {/* Grid */}
            <View style={styles.attachGrid}>
              {unifiedMenu.map((item, idx) => (
                <TouchableOpacity
                  key={idx}
                  style={[styles.attachItem, { backgroundColor: isDark ? '#2C2C2E' : '#F2F2F7' }]}
                  onPress={() => handleToolSelect(item)}
                  activeOpacity={0.7}
                >
                  <View style={[styles.attachIconWrap, { backgroundColor: item.color + '15' }]}>
                    <item.icon size={24} stroke={item.color} />
                  </View>
                  <Text style={[styles.attachLabel, { color: colors.text }]}>
                    {lang === 'ar' ? item.label_ar : item.label_en}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* Footer hint */}
            <Text style={[styles.attachHint, { color: colors.subtext }]}>
              {lang === 'ar' ? 'اختر أداة أو أرفق ملف' : 'Select a tool or attach a file'}
            </Text>
          </Animated.View>
        </TouchableOpacity>
      </Modal>
    </>
  );
});

// ==================== STYLES ====================

const styles = StyleSheet.create({
  // Chips
  chipsRow: { paddingVertical: 8, borderTopWidth: StyleSheet.hairlineWidth },

  // Quick Replies
  quickRepliesRow: { paddingVertical: 8, borderTopWidth: StyleSheet.hairlineWidth },
  quickReplyChip: {
    paddingHorizontal: 16, paddingVertical: 10,
    borderRadius: 20, borderWidth: 1,
  },
  quickReplyText: { fontSize: 14, fontWeight: '500' },

  // Input Bar
  inputBar: {
    flexDirection: 'row', alignItems: 'flex-end',
    paddingHorizontal: 12, paddingTop: 10, paddingBottom: 16,
    borderTopWidth: StyleSheet.hairlineWidth, gap: 8,
  },
  attachBtn: {
    width: 40, height: 40, borderRadius: 20,
    justifyContent: 'center', alignItems: 'center',
  },
  inputWrap: {
    flex: 1, flexDirection: 'row', alignItems: 'center',
    borderRadius: 24, borderWidth: 1, paddingHorizontal: 4, paddingVertical: 4,
  },
  textInput: {
    flex: 1, paddingHorizontal: 12, paddingVertical: 8,
    fontSize: 16, maxHeight: 120, minHeight: 40,
    lineHeight: 22,
  },
  micBtn: {
    width: 32, height: 32, borderRadius: 16,
    justifyContent: 'center', alignItems: 'center',
    marginRight: 4,
  },
  micActive: { backgroundColor: '#FF3B3015' },
  sendBtn: {
    width: 44, height: 44, borderRadius: 22,
    justifyContent: 'center', alignItems: 'center',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3, shadowRadius: 8, elevation: 4,
  },

  // Attach Modal
  attachOverlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.4)' },
  attachContainer: {
    borderTopLeftRadius: 28, borderTopRightRadius: 28,
    paddingHorizontal: 20, paddingTop: 24, paddingBottom: 40,
    shadowColor: '#000', shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.15, shadowRadius: 12, elevation: 8,
  },
  attachHeader: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    marginBottom: 24,
  },
  attachTitle: { fontSize: 20, fontWeight: '800', letterSpacing: -0.5 },
  closeBtn: { padding: 4, borderRadius: 8 },
  attachGrid: {
    flexDirection: 'row', flexWrap: 'wrap', gap: 12,
    justifyContent: 'space-between',
  },
  attachItem: {
    width: (SCREEN_WIDTH - 72) / 3,
    alignItems: 'center', paddingVertical: 18, borderRadius: 18,
    gap: 8,
  },
  attachIconWrap: {
    width: 56, height: 56, borderRadius: 18,
    justifyContent: 'center', alignItems: 'center',
  },
  attachLabel: { fontSize: 13, fontWeight: '600', textAlign: 'center' },
  attachHint: {
    textAlign: 'center', fontSize: 12, marginTop: 20,
    fontWeight: '500',
  },
});
