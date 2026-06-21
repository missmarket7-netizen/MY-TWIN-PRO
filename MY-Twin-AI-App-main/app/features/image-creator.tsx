import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  Image, ActivityIndicator, ScrollView, Animated,
  Dimensions, Alert, FlatList, Modal,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore, useTwinStoreFull } from '../../store/useTwinStore';
import { useTheme } from '../../utils/theme';
import { router } from 'expo-router';
import {
  Sparkles, ImageIcon, Download, ArrowLeft, RefreshCw,
  Wand2, Lightbulb, Layers, X, Check,
} from 'lucide-react-native';
import * as MediaLibrary from 'expo-media-library';
import * as FileSystem from 'expo-file-system';

const { width: SCREEN_W } = Dimensions.get('window');

const SUGGESTIONS = [
  { ar: 'قطة في الفضاء', en: 'A cat in space' },
  { ar: 'غروب على المريخ', en: 'Sunset on Mars' },
  { ar: 'مدينة مستقبلية', en: 'Futuristic city' },
  { ar: 'غابة سحرية', en: 'Enchanted forest' },
  { ar: 'قلعة على السحاب', en: 'Castle on the clouds' },
];

const STYLES = [
  { id: 'realistic', label_ar: 'واقعي', label_en: 'Realistic' },
  { id: 'anime', label_ar: 'أنمي', label_en: 'Anime' },
  { id: 'oil_painting', label_ar: 'لوحة زيتية', label_en: 'Oil Painting' },
  { id: 'pixel_art', label_ar: 'بكسل آرت', label_en: 'Pixel Art' },
];

export default function ImageCreator() {
  const insets = useSafeAreaInsets();
  const theme = useTheme();
  const { lang } = useTwinStore();
  const { generateImage } = useTwinStoreFull();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';

  const [prompt, setPrompt] = useState('');
  const [selectedStyle, setSelectedStyle] = useState('realistic');
  const [loading, setLoading] = useState(false);
  const [enhancing, setEnhancing] = useState(false);
  const [currentImage, setCurrentImage] = useState<string | null>(null);
  const [gallery, setGallery] = useState<any[]>([]);
  const [showStylePicker, setShowStylePicker] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const colors = {
    bg: isDark ? '#0F0A1A' : '#FAFAF8',
    card: isDark ? '#1A1226' : '#FFFFFF',
    text: isDark ? '#FFFFFF' : '#2D2D2D',
    subtext: isDark ? '#8B7BA3' : '#6B6B6B',
    accent: '#8B5CF6',
    accentLight: '#8B5CF620',
    border: isDark ? '#2D1B4D' : '#E8E8E3',
    inputBg: isDark ? '#161122' : '#FDFDF9',
    success: '#10B981',
    warning: '#F59E0B',
  };

  // تحسين الوصف
  const handleEnhancePrompt = useCallback(async () => {
    if (!prompt.trim()) return;
    setEnhancing(true);
    try {
      const response = await fetch(
        `https://my-twin-pro-production-b744.up.railway.app/api/image-lab/enhance-prompt?user_id=${useTwinStore.getState().userId}&prompt=${encodeURIComponent(prompt.trim())}`,
        { method: 'POST' }
      );
      const data = await response.json();
      if (data.enhanced) {
        setPrompt(data.enhanced);
      }
    } catch (e) {
      Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'فشل تحسين الوصف' : 'Enhancement failed');
    } finally {
      setEnhancing(false);
    }
  }, [prompt]);

  // توليد الصورة
  const handleGenerate = useCallback(async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setCurrentImage(null);
    try {
      const imageUrl = await generateImage(prompt.trim(), selectedStyle);
      if (imageUrl) {
        setCurrentImage(imageUrl);
        Animated.timing(fadeAnim, { toValue: 1, duration: 500, useNativeDriver: true }).start();
        setGallery(prev => [{ prompt: prompt.trim(), image_url: imageUrl, style: selectedStyle }, ...prev].slice(0, 20));
      }
    } catch (e: any) {
      Alert.alert(isAr ? 'خطأ' : 'Error', e.message);
    } finally {
      setLoading(false);
    }
  }, [prompt, selectedStyle, generateImage]);

  // حفظ الصورة
  const handleDownload = async () => {
    if (!currentImage) return;
    try {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status === 'granted') {
        const localUri = FileSystem.cacheDirectory + `mytwin-${Date.now()}.png`;
        await FileSystem.downloadAsync(currentImage, localUri);
        await MediaLibrary.saveToLibraryAsync(localUri);
        Alert.alert('✅', isAr ? 'تم الحفظ في المعرض' : 'Saved to gallery!');
      }
    } catch {
      Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'فشل الحفظ' : 'Save failed');
    }
  };

  return (
    <View style={[st.root, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
      {/* الهيدر */}
      <View style={[st.header, { borderBottomColor: colors.border }]}>
        <TouchableOpacity onPress={() => router.back()}>
          <ArrowLeft size={24} stroke={colors.text} />
        </TouchableOpacity>
        <View style={st.headerCenter}>
          <ImageIcon size={24} stroke={colors.accent} />
          <Text style={[st.headerTitle, { color: colors.text }]}>
            {isAr ? 'إنشاء صورة' : 'Image Creator'}
          </Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={st.content} keyboardShouldPersistTaps="handled">
        {/* بطاقة الإدخال */}
        <View style={[st.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={[st.iconWrap, { backgroundColor: colors.accentLight }]}>
            <Sparkles size={32} stroke={colors.accent} />
          </View>

          {/* اختيار النمط */}
          <TouchableOpacity
            style={[st.stylePicker, { borderColor: colors.border }]}
            onPress={() => setShowStylePicker(true)}
          >
            <Layers size={16} stroke={colors.subtext} />
            <Text style={[st.stylePickerText, { color: colors.text }]}>
              {STYLES.find(s => s.id === selectedStyle)?.label_ar || 'واقعي'}
            </Text>
          </TouchableOpacity>

          {/* حقل الوصف */}
          <TextInput
            style={[st.input, { backgroundColor: colors.inputBg, color: colors.text, borderColor: colors.border }, isAr && { textAlign: 'right' }]}
            placeholder={isAr ? 'وصف الصورة...' : 'Describe the image...'}
            placeholderTextColor={colors.subtext}
            value={prompt}
            onChangeText={setPrompt}
            multiline
            numberOfLines={4}
            textAlignVertical="top"
          />

          {/* زر تحسين الوصف */}
          <TouchableOpacity
            style={[st.enhanceBtn, { borderColor: colors.border }]}
            onPress={handleEnhancePrompt}
            disabled={enhancing || !prompt.trim()}
          >
            {enhancing ? (
              <ActivityIndicator size="small" color={colors.accent} />
            ) : (
              <Wand2 size={16} stroke={colors.accent} />
            )}
            <Text style={[st.enhanceBtnText, { color: colors.accent }]}>
              {isAr ? 'تحسين الوصف' : 'Enhance Prompt'}
            </Text>
          </TouchableOpacity>

          {/* زر التوليد */}
          <TouchableOpacity
            style={[st.generateBtn, { backgroundColor: colors.accent, opacity: prompt.trim() ? 1 : 0.6 }]}
            onPress={handleGenerate}
            disabled={loading || !prompt.trim()}
          >
            {loading ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <>
                <Sparkles size={18} stroke="#FFF" />
                <Text style={st.generateBtnText}>
                  {isAr ? 'توليد الصورة' : 'Generate Image'}
                </Text>
              </>
            )}
          </TouchableOpacity>

          {/* اقتراحات */}
          <View style={st.suggestions}>
            {SUGGESTIONS.map((sug, i) => (
              <TouchableOpacity
                key={i}
                style={[st.chip, { backgroundColor: colors.accentLight, borderColor: colors.accent + '30' }]}
                onPress={() => setPrompt(isAr ? sug.ar : sug.en)}
              >
                <Lightbulb size={12} stroke={colors.accent} />
                <Text style={[st.chipText, { color: colors.accent }]}>
                  {isAr ? sug.ar : sug.en}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* الصورة الناتجة */}
        {currentImage && (
          <Animated.View style={[st.resultCard, { backgroundColor: colors.card, borderColor: colors.border, opacity: fadeAnim }]}>
            <Image
              source={{ uri: currentImage }}
              style={st.resultImage}
              resizeMode="contain"
            />
            <View style={st.actions}>
              <TouchableOpacity style={[st.actionBtn, { backgroundColor: colors.accentLight }]} onPress={handleDownload}>
                <Download size={20} stroke={colors.accent} />
                <Text style={[st.actionText, { color: colors.accent }]}>
                  {isAr ? 'حفظ' : 'Save'}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity style={[st.regenerateBtn, { backgroundColor: colors.accentLight }]} onPress={handleGenerate}>
                <RefreshCw size={20} stroke={colors.accent} />
              </TouchableOpacity>
            </View>
          </Animated.View>
        )}

        {/* المعرض */}
        {gallery.length > 0 && (
          <View style={st.gallerySection}>
            <Text style={[st.galleryTitle, { color: colors.text }]}>
              {isAr ? '🎨 المعرض' : '🎨 Gallery'}
            </Text>
            <FlatList
              horizontal
              data={gallery}
              keyExtractor={(_, i) => i.toString()}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[st.galleryItem, { borderColor: colors.border }]}
                  onPress={() => setCurrentImage(item.image_url)}
                >
                  <Image source={{ uri: item.image_url }} style={st.galleryImage} />
                </TouchableOpacity>
              )}
              showsHorizontalScrollIndicator={false}
            />
          </View>
        )}
      </ScrollView>

      {/* مودال اختيار النمط */}
      <Modal visible={showStylePicker} transparent animationType="fade" onRequestClose={() => setShowStylePicker(false)}>
        <TouchableOpacity style={st.modalOverlay} activeOpacity={1} onPress={() => setShowStylePicker(false)}>
          <View style={[st.modalContent, { backgroundColor: colors.card }]}>
            <Text style={[st.modalTitle, { color: colors.text }]}>
              {isAr ? 'اختر النمط' : 'Select Style'}
            </Text>
            {STYLES.map(style => (
              <TouchableOpacity
                key={style.id}
                style={[
                  st.styleOption,
                  { borderColor: selectedStyle === style.id ? colors.accent : 'transparent' },
                  selectedStyle === style.id && { backgroundColor: colors.accentLight },
                ]}
                onPress={() => { setSelectedStyle(style.id); setShowStylePicker(false); }}
              >
                <Text style={[st.styleOptionText, { color: colors.text }]}>
                  {isAr ? style.label_ar : style.label_en}
                </Text>
                {selectedStyle === style.id && <Check size={18} stroke={colors.accent} />}
              </TouchableOpacity>
            ))}
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
}

const st = StyleSheet.create({
  root: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5 },
  headerCenter: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  headerTitle: { fontSize: 18, fontWeight: '700' },
  content: { padding: 20, paddingBottom: 40 },
  card: { borderRadius: 24, padding: 24, borderWidth: 1, alignItems: 'center', marginBottom: 24 },
  iconWrap: { width: 64, height: 64, borderRadius: 20, justifyContent: 'center', alignItems: 'center', marginBottom: 16 },
  stylePicker: { flexDirection: 'row', alignItems: 'center', gap: 8, borderWidth: 1, borderRadius: 14, padding: 10, paddingHorizontal: 16, marginBottom: 16 },
  stylePickerText: { fontSize: 14, fontWeight: '500' },
  input: { width: '100%', borderRadius: 16, padding: 16, fontSize: 15, borderWidth: 1, minHeight: 100, textAlignVertical: 'top', marginBottom: 12 },
  enhanceBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingVertical: 10, paddingHorizontal: 16, borderRadius: 12, borderWidth: 1, marginBottom: 12 },
  enhanceBtnText: { fontSize: 13, fontWeight: '600' },
  generateBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 14, borderRadius: 14, width: '100%', gap: 8 },
  generateBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  suggestions: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 16 },
  chip: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, borderWidth: 1 },
  chipText: { fontSize: 12, fontWeight: '500' },
  resultCard: { borderRadius: 24, padding: 16, borderWidth: 1, marginBottom: 24 },
  resultImage: { width: '100%', height: SCREEN_W * 0.8, borderRadius: 16, marginBottom: 16 },
  actions: { flexDirection: 'row', gap: 12, justifyContent: 'center' },
  actionBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingVertical: 12, paddingHorizontal: 20, borderRadius: 14 },
  actionText: { fontSize: 14, fontWeight: '600' },
  regenerateBtn: { padding: 12, borderRadius: 14 },
  gallerySection: { marginTop: 8 },
  galleryTitle: { fontSize: 16, fontWeight: '700', marginBottom: 12 },
  galleryItem: { marginRight: 12, borderRadius: 14, borderWidth: 1, overflow: 'hidden' },
  galleryImage: { width: 80, height: 80, borderRadius: 12 },
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' },
  modalContent: { width: '80%', borderRadius: 20, padding: 20 },
  modalTitle: { fontSize: 18, fontWeight: '700', marginBottom: 16 },
  styleOption: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 14, borderRadius: 14, borderWidth: 1.5, marginBottom: 8 },
  styleOptionText: { fontSize: 15, fontWeight: '600' },
});
