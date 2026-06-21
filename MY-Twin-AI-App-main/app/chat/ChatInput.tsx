import React, { memo, useRef, useMemo } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  Modal, Animated, ActivityIndicator, ScrollView,
} from 'react-native';
import {
  Send, X, Camera, Image as ImageIcon, FileText,
  Search, Cloud, Music, Film, DollarSign, TrendingUp,
  Wand2, Mic, MicOff, GraduationCap, Code2, Heart,
  Moon, PenLine, BarChart3, Home,
} from 'lucide-react-native';
import { ToolChip } from './ChatBubbles';

interface ToolItem {
  id: string;
  icon: any;
  label_ar: string;
  label_en: string;
  color: string;
  category: 'attach' | 'tool' | 'feature';
  onPress?: () => void;
}

export const ChatInput = memo(({
  input, setInput, loading, isRTL, isDark, colors, lang,
  onSend, onAddTool, activeTools, onRemoveTool,
  onCamera, onGallery, onFile,
  showAttach, setShowAttach, attachAnim,
  isRecording = false, onMicPress,
  onFeatureSelect,
}: any) => {
  const inputRef = useRef<TextInput>(null);

  // القائمة الموحدة الموسعة (مضافة Smart Home)
  const unifiedMenu: ToolItem[] = useMemo(() => [
    // === قسم الإرفاق ===
    { id: 'camera', icon: Camera, label_ar: 'كاميرا', label_en: 'Camera', color: '#8B5CF6', category: 'attach', onPress: onCamera },
    { id: 'gallery', icon: ImageIcon, label_ar: 'معرض', label_en: 'Gallery', color: '#EC4899', category: 'attach', onPress: onGallery },
    { id: 'file', icon: FileText, label_ar: 'ملف', label_en: 'File', color: '#F59E0B', category: 'attach', onPress: onFile },
    { id: 'image_ai', icon: Wand2, label_ar: 'صورة AI', label_en: 'AI Image', color: '#A855F7', category: 'tool' },
    // === قسم الأدوات ===
    { id: 'youtube', icon: Film, label_ar: 'يوتيوب', label_en: 'YouTube', color: '#EF4444', category: 'tool' },
    { id: 'music', icon: Music, label_ar: 'موسيقى', label_en: 'Music', color: '#EC4899', category: 'tool' },
    { id: 'weather', icon: Cloud, label_ar: 'طقس', label_en: 'Weather', color: '#06B6D4', category: 'tool' },
    { id: 'currency', icon: DollarSign, label_ar: 'عملات', label_en: 'Currency', color: '#10B981', category: 'tool' },
    { id: 'news', icon: TrendingUp, label_ar: 'أخبار', label_en: 'News', color: '#8B5CF6', category: 'tool' },
    { id: 'search', icon: Search, label_ar: 'بحث', label_en: 'Search', color: '#6366F1', category: 'tool' },
    // === قدرات التوأم ===
    { id: 'study', icon: GraduationCap, label_ar: 'مذاكرة', label_en: 'Study', color: '#3B82F6', category: 'feature' },
    { id: 'code', icon: Code2, label_ar: 'برمجة', label_en: 'Code', color: '#10B981', category: 'feature' },
    { id: 'business', icon: BarChart3, label_ar: 'تحليل أعمال', label_en: 'Business', color: '#F59E0B', category: 'feature' },
    { id: 'coach', icon: Heart, label_ar: 'مدرب حياة', label_en: 'Life Coach', color: '#EC4899', category: 'feature' },
    { id: 'dream', icon: Moon, label_ar: 'تفسير حلم', label_en: 'Dream', color: '#6366F1', category: 'feature' },
    { id: 'content', icon: PenLine, label_ar: 'كتابة محتوى', label_en: 'Content', color: '#D946EF', category: 'feature' },
    { id: 'smart_home', icon: Home, label_ar: 'منزل ذكي', label_en: 'Smart Home', color: '#06B6D4', category: 'feature' },
  ], [onCamera, onGallery, onFile]);

  const handleToolSelect = (item: ToolItem) => {
    setShowAttach(false);
    if (item.category === 'attach' && item.onPress) {
      item.onPress();
    } else if (item.category === 'tool' && onAddTool) {
      onAddTool({
        type: item.id,
        label: lang === 'ar' ? item.label_ar : item.label_en,
        icon: item.icon,
        color: item.color,
      });
    } else if (item.category === 'feature' && onFeatureSelect) {
      onFeatureSelect(item.id);
    }
  };

  const hasContent = input.trim().length > 0 || (activeTools && activeTools.length > 0);
  return (
    <>
      {/* الأدوات النشطة */}
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

      {/* شريط الإدخال المحسن */}
      <View style={[styles.inputBar, { backgroundColor: colors.headerBg, borderTopColor: colors.border }]}>
        <TouchableOpacity
          onPress={() => setShowAttach((prev: boolean) => !prev)}
          style={[styles.attachBtn, { backgroundColor: colors.inputBg }]}
          activeOpacity={0.7}
        >
          <Text style={{ fontSize: 20, color: colors.subtext, fontWeight: '300' }}>+</Text>
        </TouchableOpacity>

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
            blurOnSubmit={false}
            returnKeyType="default"
            autoCorrect={false}
            autoCapitalize="sentences"
          />
          
          {/* زر الميكروفون (STT) */}
          <TouchableOpacity
            onPress={onMicPress || (() => {})}
            style={[styles.micBtn, isRecording && styles.micActive]}
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
            { backgroundColor: hasContent && !loading ? colors.sendActive : colors.sendInactive }
          ]}
        >
          {loading ? <ActivityIndicator size="small" color="#FFF" /> : <Send size={20} stroke="#FFF" />}
        </TouchableOpacity>
      </View>

      {/* نافذة المرفقات والأدوات المحسنة */}
      <Modal visible={showAttach} transparent animationType="none" onRequestClose={() => setShowAttach(false)}>
        <View style={styles.attachOverlay}>
          <TouchableOpacity style={StyleSheet.absoluteFill} activeOpacity={1} onPress={() => setShowAttach(false)} />
          <Animated.View style={[styles.attachContainer, { backgroundColor: isDark ? '#1C1C1E' : '#FFF', transform: [{ translateY: attachAnim.interpolate({ inputRange: [0, 1], outputRange: [400, 0] }) }] }]}>
            <View style={styles.attachHeader}>
              <Text style={[styles.attachTitle, { color: colors.text }]}>{lang === 'ar' ? 'إرفاق وأدوات' : 'Attach & Tools'}</Text>
              <TouchableOpacity onPress={() => setShowAttach(false)} style={styles.closeBtn}><X size={22} stroke={colors.subtext} /></TouchableOpacity>
            </View>

            {/* فئة الإرفاق */}
            <Text style={[styles.categoryLabel, { color: colors.subtext }]}>{lang === 'ar' ? '📎 إرفاق' : '📎 Attach'}</Text>
            <View style={styles.attachGrid}>
              {unifiedMenu.filter(i => i.category === 'attach').map((item, idx) => (
                <TouchableOpacity key={idx} style={[styles.attachItem, { backgroundColor: isDark ? '#2C2C2E' : '#F2F2F7' }]} onPress={() => handleToolSelect(item)}>
                  <View style={[styles.attachIconWrap, { backgroundColor: item.color + '15' }]}><item.icon size={24} stroke={item.color} /></View>
                  <Text style={[styles.attachLabel, { color: colors.text }]}>{lang === 'ar' ? item.label_ar : item.label_en}</Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* فئة الأدوات */}
            <Text style={[styles.categoryLabel, { color: colors.subtext }]}>{lang === 'ar' ? '🔧 أدوات' : '🔧 Tools'}</Text>
            <View style={styles.attachGrid}>
              {unifiedMenu.filter(i => i.category === 'tool').map((item, idx) => (
                <TouchableOpacity key={idx} style={[styles.attachItem, { backgroundColor: isDark ? '#2C2C2E' : '#F2F2F7' }]} onPress={() => handleToolSelect(item)}>
                  <View style={[styles.attachIconWrap, { backgroundColor: item.color + '15' }]}><item.icon size={24} stroke={item.color} /></View>
                  <Text style={[styles.attachLabel, { color: colors.text }]}>{lang === 'ar' ? item.label_ar : item.label_en}</Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* فئة قدرات التوأم */}
            <Text style={[styles.categoryLabel, { color: colors.subtext }]}>{lang === 'ar' ? '🚀 قدرات التوأم' : '🚀 Twin Powers'}</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 12 }}>
              <View style={{ flexDirection: 'row', gap: 10, paddingHorizontal: 4 }}>
                {unifiedMenu.filter(i => i.category === 'feature').map((item, idx) => (
                  <TouchableOpacity key={idx} style={[styles.featureItem, { backgroundColor: isDark ? '#2C2C2E' : '#F2F2F7' }]} onPress={() => handleToolSelect(item)}>
                    <View style={[styles.featureIconWrap, { backgroundColor: item.color + '15' }]}><item.icon size={28} stroke={item.color} /></View>
                    <Text style={[styles.featureLabel, { color: colors.text }]}>{lang === 'ar' ? item.label_ar : item.label_en}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>

            <Text style={[styles.attachHint, { color: colors.subtext }]}>{lang === 'ar' ? 'اختر أداة أو قدرة لاستخدامها' : 'Select a tool or power to use'}</Text>
          </Animated.View>
        </View>
      </Modal>
    </>
  );
});

// ==================== STYLES ====================

const styles = StyleSheet.create({
  chipsRow: { paddingVertical: 8, borderTopWidth: StyleSheet.hairlineWidth },
  inputBar: { flexDirection: 'row', alignItems: 'flex-end', paddingHorizontal: 12, paddingTop: 10, paddingBottom: 16, borderTopWidth: StyleSheet.hairlineWidth, gap: 8 },
  attachBtn: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center' },
  inputWrap: { flex: 1, flexDirection: 'row', alignItems: 'center', borderRadius: 24, borderWidth: 1, paddingHorizontal: 4, paddingVertical: 4 },
  textInput: { flex: 1, paddingHorizontal: 12, paddingVertical: 8, fontSize: 16, maxHeight: 120, minHeight: 40, lineHeight: 22 },
  micBtn: { width: 32, height: 32, borderRadius: 16, justifyContent: 'center', alignItems: 'center', marginRight: 4 },
  micActive: { backgroundColor: '#FF3B3015' },
  sendBtn: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.3, shadowRadius: 8, elevation: 4 },
  attachOverlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.4)' },
  attachContainer: { borderTopLeftRadius: 28, borderTopRightRadius: 28, paddingHorizontal: 20, paddingTop: 24, paddingBottom: 40, shadowColor: '#000', shadowOffset: { width: 0, height: -4 }, shadowOpacity: 0.15, shadowRadius: 12, elevation: 8, maxHeight: '80%' },
  attachHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  attachTitle: { fontSize: 20, fontWeight: '800', letterSpacing: -0.5 },
  closeBtn: { padding: 4, borderRadius: 8 },
  categoryLabel: { fontSize: 13, fontWeight: '700', marginBottom: 8, marginTop: 12, letterSpacing: 0.3 },
  attachGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 8 },
  attachItem: { flexBasis: '30%', alignItems: 'center', paddingVertical: 14, borderRadius: 16, gap: 8 },
  attachIconWrap: { width: 50, height: 50, borderRadius: 16, justifyContent: 'center', alignItems: 'center' },
  attachLabel: { fontSize: 12, fontWeight: '600', textAlign: 'center' },
  featureItem: { alignItems: 'center', paddingVertical: 14, paddingHorizontal: 16, borderRadius: 16, gap: 8, width: 90 },
  featureIconWrap: { width: 50, height: 50, borderRadius: 16, justifyContent: 'center', alignItems: 'center' },
  featureLabel: { fontSize: 11, fontWeight: '600', textAlign: 'center' },
  attachHint: { textAlign: 'center', fontSize: 12, marginTop: 8, fontWeight: '500' },
});
