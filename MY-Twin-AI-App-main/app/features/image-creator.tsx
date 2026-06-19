import { useState, useRef, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Image, ActivityIndicator, ScrollView, Animated, Dimensions, Alert, FlatList } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiPost, apiGet } from '../../lib/httpClient';
import { Sparkles, Image as ImageIcon, Download, ArrowLeft, RefreshCw } from 'lucide-react-native';
import * as MediaLibrary from 'expo-media-library';
import * as FileSystem from 'expo-file-system';

const { width: SCREEN_W } = Dimensions.get('window');

const SUGGESTIONS = [
  { ar: 'قطة في الفضاء', en: 'A cat in space' },
  { ar: 'غروب على المريخ', en: 'Sunset on Mars' },
  { ar: 'مدينة مستقبلية', en: 'Futuristic city' },
  { ar: 'غابة سحرية', en: 'Enchanted forest' },
];

export default function ImageCreator() {
  const insets = useSafeAreaInsets();
  const { lang } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const primary = '#6B21A8';

  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentImage, setCurrentImage] = useState<string | null>(null);
  const [gallery, setGallery] = useState<any[]>([]);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    apiGet('/api/features/images').then(data => setGallery(data || [])).catch(() => {});
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setCurrentImage(null);
    try {
      const data = await apiPost('/api/features/image', { prompt: prompt.trim() });
      if (data.image_base64) {
        setCurrentImage(data.image_base64);
        Animated.timing(fadeAnim, { toValue: 1, duration: 500, useNativeDriver: true }).start();
        setGallery(prev => [{ prompt: prompt.trim(), image_base64: data.image_base64 }, ...prev].slice(0, 20));
      }
    } catch (e: any) { Alert.alert(t('خطأ', 'Error'), e.message); }
    finally { setLoading(false); }
  };

  const handleDownload = async () => {
    if (!currentImage) return;
    try {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status === 'granted') {
        const uri = FileSystem.cacheDirectory + `mytwin-${Date.now()}.png`;
        await FileSystem.writeAsStringAsync(uri, currentImage, { encoding: FileSystem.EncodingType.Base64 });
        await MediaLibrary.saveToLibraryAsync(uri);
        Alert.alert('✅', t('تم الحفظ', 'Saved!'));
      }
    } catch { Alert.alert(t('خطأ', 'Error'), t('فشل الحفظ', 'Save failed')); }
  };

  return (
    <View style={[st.container, { paddingTop: insets.top }]}>
      <View style={st.header}>
        <TouchableOpacity onPress={() => router.back()} style={st.backBtn}><ArrowLeft size={24} stroke={primary} /></TouchableOpacity>
        <Text style={st.headerTitle}>{t('إنشاء صورة', 'Image Creator')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={st.content} keyboardShouldPersistTaps="handled">
        <View style={st.inputCard}>
          <Sparkles size={32} stroke={primary} style={{ alignSelf: 'center', marginBottom: 16 }} />
          <TextInput
            style={[st.input, isAr && { textAlign: 'right' }]}
            placeholder={t('وصف الصورة...', 'Describe the image...')}
            placeholderTextColor="#7C6B99"
            value={prompt}
            onChangeText={setPrompt}
            multiline numberOfLines={3}
          />
          <TouchableOpacity style={[st.btn, { opacity: prompt.trim() ? 1 : 0.6 }]} onPress={handleGenerate} disabled={loading || !prompt.trim()}>
            {loading ? <ActivityIndicator color="#FFF" /> : <><Sparkles size={18} stroke="#FFF" /><Text style={st.btnText}>{t('توليد', 'Generate')}</Text></>}
          </TouchableOpacity>
          <View style={st.suggestions}>
            {SUGGESTIONS.map((sug, i) => (
              <TouchableOpacity key={i} style={st.chip} onPress={() => setPrompt(isAr ? sug.ar : sug.en)}>
                <Text style={st.chipText}>{isAr ? sug.ar : sug.en}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {currentImage && (
          <Animated.View style={[st.resultCard, { opacity: fadeAnim }]}>
            <Image source={{ uri: `data:image/png;base64,${currentImage}` }} style={st.resultImage} resizeMode="contain" />
            <View style={st.actions}>
              <TouchableOpacity style={st.actionBtn} onPress={handleDownload}><Download size={20} stroke={primary} /><Text style={st.actionText}>{t('حفظ', 'Save')}</Text></TouchableOpacity>
              <TouchableOpacity style={st.regenerateBtn} onPress={handleGenerate}><RefreshCw size={20} stroke={primary} /></TouchableOpacity>
            </View>
          </Animated.View>
        )}

        {gallery.length > 0 && (
          <View style={st.gallerySection}>
            <Text style={st.galleryTitle}>{t('المعرض', 'Gallery')}</Text>
            <FlatList horizontal data={gallery} keyExtractor={(_, i) => i.toString()} renderItem={({ item }) => (
              <TouchableOpacity style={st.galleryItem} onPress={() => { setCurrentImage(item.image_base64); }}>
                <Image source={{ uri: `data:image/png;base64,${item.image_base64}` }} style={st.galleryImage} />
              </TouchableOpacity>
            )} showsHorizontalScrollIndicator={false} />
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const st = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5, borderBottomColor: '#EDE9F6' },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'flex-start' },
  headerTitle: { fontSize: 18, fontWeight: '700', color: '#6B21A8' },
  content: { padding: 20, paddingBottom: 40 },
  inputCard: { backgroundColor: '#FAFAFE', borderRadius: 24, padding: 24, borderWidth: 1, borderColor: '#EDE9F6' },
  input: { backgroundColor: '#FFF', borderRadius: 16, padding: 16, fontSize: 15, color: '#1A1226', borderWidth: 1, borderColor: '#EDE9F6', minHeight: 80, textAlignVertical: 'top' },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#6B21A8', padding: 16, borderRadius: 16, marginTop: 16, gap: 8 },
  btnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  suggestions: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 16 },
  chip: { paddingHorizontal: 16, paddingVertical: 10, borderRadius: 20, backgroundColor: '#F5F3FF', borderWidth: 1, borderColor: '#EDE9F6' },
  chipText: { fontSize: 13, color: '#6B21A8', fontWeight: '500' },
  resultCard: { marginTop: 24, backgroundColor: '#FAFAFE', borderRadius: 24, padding: 16, borderWidth: 1, borderColor: '#EDE9F6' },
  resultImage: { width: '100%', height: SCREEN_W * 0.8, borderRadius: 16, marginBottom: 16 },
  actions: { flexDirection: 'row', gap: 12, justifyContent: 'center' },
  actionBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingVertical: 12, paddingHorizontal: 20, borderRadius: 14, backgroundColor: '#F5F3FF' },
  actionText: { fontSize: 14, fontWeight: '600', color: '#6B21A8' },
  regenerateBtn: { padding: 12, borderRadius: 14, backgroundColor: '#F5F3FF' },
  gallerySection: { marginTop: 24 },
  galleryTitle: { fontSize: 16, fontWeight: '700', color: '#1A1226', marginBottom: 12 },
  galleryItem: { marginRight: 12 },
  galleryImage: { width: 80, height: 80, borderRadius: 12 },
});
