import {
  SafeAreaView, View, Text, TouchableOpacity, StyleSheet,
  ScrollView, TextInput, Alert
} from 'react-native';
import { useState, useEffect, useCallback } from 'react';
import { useTwinStore, TwinStyle, TwinGender, ReplyStyle } from '../store/useTwinStore';
import { router } from 'expo-router';
import { Palette, User, Save, Smile, Heart, Star, RotateCcw, Sparkles, ArrowLeft } from 'lucide-react-native';

const STYLES: Record<string, Record<string, string>> = {
  ar: { supportive: 'داعم', coach: 'مدرب', wise: 'حكيم', fun: 'مرح', calm: 'هادئ' },
  en: { supportive: 'Supportive', coach: 'Coach', wise: 'Wise', fun: 'Fun', calm: 'Calm' },
};

const REPLY_LABELS: Record<string, Record<string, string>> = {
  ar: { short: 'مختصر', medium: 'متوسط', long: 'مفصل' },
  en: { short: 'Short', medium: 'Medium', long: 'Detailed' },
};

const GENDER_LABELS: Record<string, Record<string, string>> = {
  ar: { female: '♀ أنثى', male: '♂ ذكر' },
  en: { female: '♀ Female', male: '♂ Male' },
};

const TRAITS_OPTIONS = [
  'حنون', 'متفائل', 'ذكي', 'مخلص', 'صبور',
  'قوي', 'حساس', 'مغامر', 'عملي', 'خجول',
];

export default function Customize() {
  const {
    twinName, twinGender, twinStyle, replyStyle,
    twinTraits, setTwinName, setTwinGender, setTwinStyle,
    setReplyStyle, setTwinTraits, lang, theme,
  } = useTwinStore();

  const isAr = lang === 'ar';
  const isDark = theme === 'dark';
  const t = (ar: string, en: string) => isAr ? ar : en;

  const [name, setName] = useState(twinName || '');
  const [gender, setGender] = useState<TwinGender>(twinGender || 'female');
  const [style, setStyle] = useState<TwinStyle>(twinStyle || 'supportive');
  const [reply, setReply] = useState<ReplyStyle>(replyStyle || 'medium');
  const [selectedTraits, setSelectedTraits] = useState<string[]>(twinTraits || []);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setName(twinName || '');
    setGender(twinGender || 'female');
    setStyle(twinStyle || 'supportive');
    setReply(replyStyle || 'medium');
    setSelectedTraits(twinTraits || []);
  }, [twinName, twinGender, twinStyle, replyStyle, twinTraits]);

  const handleSave = useCallback(() => {
    if (!name.trim()) {
      Alert.alert(t('خطأ', 'Error'), t('الرجاء إدخال اسم', 'Please enter a name'));
      return;
    }
    setTwinName(name.trim());
    setTwinGender(gender);
    setTwinStyle(style);
    setReplyStyle(reply);
    setTwinTraits(selectedTraits);
    setSaved(true);
    Alert.alert('✅', t('تم حفظ التغييرات', 'Changes saved'));
  }, [name, gender, style, reply, selectedTraits, setTwinName, setTwinGender, setTwinStyle, setReplyStyle, setTwinTraits, t]);

  const handleReset = () => {
    Alert.alert(
      t('إعادة التعيين', 'Reset'),
      t('هل تريد استعادة الإعدادات الافتراضية؟', 'Reset to default settings?'),
      [
        { text: t('إلغاء', 'Cancel'), style: 'cancel' },
        {
          text: t('تعيين', 'Reset'),
          onPress: () => {
            setTwinName('توأمك');
            setTwinGender('female');
            setTwinStyle('supportive');
            setReplyStyle('medium');
            setTwinTraits([]);
            setName('توأمك');
            setGender('female');
            setStyle('supportive');
            setReply('medium');
            setSelectedTraits([]);
          },
        },
      ]
    );
  };

  const toggleTrait = (trait: string) => {
    setSelectedTraits(prev => {
      if (prev.includes(trait)) return prev.filter(x => x !== trait);
      if (prev.length >= 5) {
        Alert.alert(t('تنبيه', 'Notice'), t('5 صفات كحد أقصى', 'Max 5 traits'));
        return prev;
      }
      return [...prev, trait];
    });
  };

  const bg = isDark ? '#1A1A1A' : '#F8F6F2';
  const card = isDark ? '#2A2A2A' : '#FFF';
  const border = isDark ? '#444' : '#F0F0F0';
  const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#CCC' : '#666';
  const primary = isDark ? '#D8B4FE' : '#6B21A8';

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      {/* Header احترافي */}
      <View style={[styles.header, { borderBottomColor: border }]}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <ArrowLeft size={24} stroke={txt} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: txt }]}>
          {t('تخصيص التوأم', 'Customize Twin')}
        </Text>
        <View style={styles.backBtn} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <Sparkles size={40} stroke={primary} style={{ alignSelf: 'center', marginBottom: 20 }} />

        {/* الاسم */}
        <Text style={[styles.label, { color: sub }]}>{t('الاسم', 'Name')}</Text>
        <View style={[styles.inputRow, { backgroundColor: card, borderColor: border }]}>
          <User size={18} stroke={primary} />
          <TextInput
            style={[styles.input, { color: txt }]}
            value={name}
            onChangeText={setName}
            placeholder={t('أدخل الاسم', 'Enter name')}
            placeholderTextColor="#999"
            maxLength={20}
          />
        </View>

        {/* النوع */}
        <Text style={[styles.label, { color: sub }]}>{t('النوع', 'Gender')}</Text>
        <View style={[styles.optionsRow, isAr && { flexDirection: 'row-reverse' }]}>
          {(['female', 'male'] as TwinGender[]).map(g => (
            <TouchableOpacity
              key={g}
              style={[styles.option, { borderColor: border, backgroundColor: card }, gender === g && { borderColor: primary, backgroundColor: primary + '20' }]}
              onPress={() => setGender(g)}
            >
              <Text style={[styles.optionText, { color: sub }, gender === g && { color: primary, fontWeight: '700' }]}>
                {GENDER_LABELS[lang]?.[g] || g}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* أسلوب الرد */}
        <Text style={[styles.label, { color: sub }]}>{t('طريقة الكلام', 'Reply Style')}</Text>
        <View style={[styles.optionsRow, isAr && { flexDirection: 'row-reverse' }]}>
          {(['short', 'medium', 'long'] as ReplyStyle[]).map(r => (
            <TouchableOpacity
              key={r}
              style={[styles.option, { borderColor: border, backgroundColor: card }, reply === r && { borderColor: primary, backgroundColor: primary + '20' }]}
              onPress={() => setReply(r)}
            >
              <Text style={[styles.optionText, { color: sub }, reply === r && { color: primary, fontWeight: '700' }]}>
                {REPLY_LABELS[lang]?.[r] || r}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* نمط الشخصية */}
        <Text style={[styles.label, { color: sub }]}>{t('نمط الشخصية', 'Personality Style')}</Text>
        <View style={[styles.optionsRow, isAr && { flexDirection: 'row-reverse' }]}>
          {(Object.keys(STYLES[lang] || STYLES.en) as TwinStyle[]).map(sk => (
            <TouchableOpacity
              key={sk}
              style={[styles.option, { borderColor: border, backgroundColor: card }, style === sk && { borderColor: primary, backgroundColor: primary + '20' }]}
              onPress={() => setStyle(sk)}
            >
              <Text style={[styles.optionText, { color: sub }, style === sk && { color: primary, fontWeight: '700' }]}>
                {STYLES[lang]?.[sk] || sk}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* صفات التوأم */}
        <Text style={[styles.label, { color: sub }]}>{t('صفات التوأم', 'Twin Traits')}</Text>
        <View style={[styles.optionsRow, isAr && { flexDirection: 'row-reverse' }]}>
          {TRAITS_OPTIONS.map(trait => (
            <TouchableOpacity
              key={trait}
              style={[styles.option, { borderColor: border, backgroundColor: card }, selectedTraits.includes(trait) && { borderColor: primary, backgroundColor: primary + '20' }]}
              onPress={() => toggleTrait(trait)}
            >
              <Text style={[styles.optionText, { color: sub }, selectedTraits.includes(trait) && { color: primary, fontWeight: '700' }]}>
                {trait}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* أزرار الحفظ وإعادة التعيين */}
        <View style={[styles.btnRow, isAr && { flexDirection: 'row-reverse' }]}>
          <TouchableOpacity style={[styles.saveBtn, saved && { backgroundColor: '#10B981' }]} onPress={handleSave}>
            {saved ? <Sparkles size={18} stroke="#FFF" /> : <Save size={18} stroke="#FFF" />}
            <Text style={styles.saveText}>{t('حفظ التغييرات', 'Save Changes')}</Text>
          </TouchableOpacity>

          <TouchableOpacity style={[styles.resetBtn, { borderColor: primary }]} onPress={handleReset}>
            <RotateCcw size={18} stroke={primary} />
            <Text style={[styles.resetText, { color: primary }]}>{t('استعادة الافتراضي', 'Reset')}</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1 },
  backBtn: { width: 36, height: 36, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { fontSize: 20, fontWeight: '700', textAlign: 'center', flex: 1 },
  content: { padding: 20, paddingBottom: 40 },
  label: { fontSize: 14, fontWeight: '600', marginBottom: 8, marginTop: 16 },
  inputRow: { flexDirection: 'row', alignItems: 'center', padding: 14, borderRadius: 12, borderWidth: 1, marginBottom: 4, gap: 10 },
  input: { flex: 1, fontSize: 15 },
  optionsRow: { flexDirection: 'row', flexWrap: 'wrap', marginHorizontal: -4 },
  option: { paddingHorizontal: 16, paddingVertical: 10, borderRadius: 20, borderWidth: 1.5, marginHorizontal: 4, marginBottom: 8 },
  optionText: { fontSize: 13, fontWeight: '500' },
  btnRow: { flexDirection: 'row', gap: 12, marginTop: 32 },
  saveBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#6B21A8', padding: 16, borderRadius: 12, gap: 8 },
  saveText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  resetBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: 'transparent', padding: 16, borderRadius: 12, borderWidth: 1.5, gap: 8 },
  resetText: { fontWeight: '700', fontSize: 16 },
});
