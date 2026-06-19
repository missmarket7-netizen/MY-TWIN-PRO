import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Switch, ActivityIndicator, Alert, Animated } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiPost } from '../../lib/httpClient';
import { ArrowLeft, Lightbulb, Thermometer, Music, Power, Home, Timer } from 'lucide-react-native';

// ألوان متناسقة
const primary = '#6B21A8';
const accent = '#A855F7';

export default function SmartHome() {
  const insets = useSafeAreaInsets();
  const { lang } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;

  const [isLightOn, setIsLightOn] = useState(false);
  const [lightColor, setLightColor] = useState('#FEF3C7');
  const [timer, setTimer] = useState(0);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const handleToggleLight = async () => {
    setLoading(true);
    const command = isLightOn ? 'اطفئ النور' : 'شغل النور';
    try {
      const data = await apiPost('/api/features/smart-home', { command });
      setIsLightOn(!isLightOn);
      setStatusMessage(data.result);
    } catch (e: any) { Alert.alert(t('خطأ', 'Error'), e.message); }
    finally { setLoading(false); }
  };

  const handleSetColor = async (colorName: string, colorHex: string) => {
    setLoading(true);
    try {
      const data = await apiPost('/api/features/smart-home', { command: `غير لون النور إلى ${colorName}` });
      setLightColor(colorHex);
      setStatusMessage(data.result);
    } catch (e: any) { Alert.alert(t('خطأ', 'Error'), e.message); }
    finally { setLoading(false); }
  };

  const handleSetTimer = async (minutes: number) => {
    setTimer(minutes);
    setStatusMessage(t(`تم ضبط المؤقت على ${minutes} دقيقة`, `Timer set to ${minutes} minutes`));
    // في الإنتاج: نرسل أمرًا للخادم لجدولة الإطفاء
  };

  return (
    <View style={[st.container, { paddingTop: insets.top }]}>
      <View style={st.header}>
        <TouchableOpacity onPress={() => router.back()} style={st.backBtn}><ArrowLeft size={24} stroke={primary} /></TouchableOpacity>
        <Text style={st.headerTitle}>{t('المنزل الذكي', 'Smart Home')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={st.content}>
        {/* بطاقة الترحيب */}
        <View style={st.heroCard}>
          <Home size={48} stroke={primary} style={{ alignSelf: 'center', marginBottom: 16 }} />
          <Text style={st.heroTitle}>{t('مركز التحكم', 'Control Center')}</Text>
          <Text style={st.heroSub}>{t('تحكم بمنزلك الذكي بلمسة واحدة', 'Control your smart home with a tap')}</Text>
        </View>

        {/* بطاقة الإضاءة الرئيسية */}
        <View style={[st.controlCard, { backgroundColor: isLightOn ? '#FEF3C7' : '#F3F4F6' }]}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
              <Lightbulb size={28} stroke={isLightOn ? '#F59E0B' : '#6B7280'} fill={isLightOn ? '#F59E0B' : 'transparent'} />
              <View>
                <Text style={st.controlLabel}>{t('الإضاءة الرئيسية', 'Main Light')}</Text>
                <Text style={st.controlStatus}>{isLightOn ? t('مضاءة', 'On') : t('مطفأة', 'Off')}</Text>
              </View>
            </View>
            <Switch
              value={isLightOn}
              onValueChange={handleToggleLight}
              trackColor={{ false: '#D1D5DB', true: '#F59E0B' }}
              thumbColor={isLightOn ? '#FFF' : '#F9FAFB'}
            />
          </View>
        </View>

        {/* اختيار اللون */}
        <Text style={st.sectionTitle}>{t('اختر لون الإضاءة', 'Choose Light Color')}</Text>
        <View style={st.colorRow}>
          {[
            { name: 'أحمر', hex: '#EF4444', arName: 'أحمر' },
            { name: 'أزرق', hex: '#3B82F6', arName: 'أزرق' },
            { name: 'أخضر', hex: '#10B981', arName: 'أخضر' },
            { name: 'بنفسجي', hex: '#8B5CF6', arName: 'بنفسجي' },
            { name: 'أصفر', hex: '#F59E0B', arName: 'أصفر' },
            { name: 'أبيض', hex: '#F9FAFB', arName: 'أبيض' },
          ].map(c => (
            <TouchableOpacity
              key={c.name}
              style={[st.colorBtn, { backgroundColor: c.hex, borderColor: lightColor === c.hex ? '#1F2937' : 'transparent' }]}
              onPress={() => handleSetColor(c.arName, c.hex)}
            />
          ))}
        </View>

        {/* المؤقت */}
        <Text style={st.sectionTitle}>{t('مؤقت الإطفاء', 'Sleep Timer')}</Text>
        <View style={st.timerRow}>
          {[5, 15, 30, 60].map(min => (
            <TouchableOpacity key={min} style={[st.timerBtn, timer === min && st.activeTimerBtn]} onPress={() => handleSetTimer(min)}>
              <Timer size={16} stroke={timer === min ? '#FFF' : primary} />
              <Text style={[st.timerText, timer === min && { color: '#FFF' }]}>{min} د</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* رسالة الحالة */}
        {statusMessage ? (
          <View style={st.statusCard}>
            <Power size={20} stroke={primary} />
            <Text style={st.statusText}>{statusMessage}</Text>
          </View>
        ) : null}
      </ScrollView>
    </View>
  );
}

const st = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5, borderBottomColor: '#EDE9F6' },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'flex-start' },
  headerTitle: { fontSize: 18, fontWeight: '700', color: primary },
  content: { padding: 20, paddingBottom: 40 },
  heroCard: { backgroundColor: '#FAFAFE', borderRadius: 24, padding: 28, marginBottom: 20, borderWidth: 1, borderColor: '#EDE9F6' },
  heroTitle: { fontSize: 20, fontWeight: '800', color: '#1A1226', textAlign: 'center', marginBottom: 8 },
  heroSub: { fontSize: 14, color: '#7C6B99', textAlign: 'center' },
  controlCard: { borderRadius: 20, padding: 20, marginBottom: 24 },
  controlLabel: { fontSize: 16, fontWeight: '600', color: '#1A1226' },
  controlStatus: { fontSize: 13, color: '#6B7280', marginTop: 2 },
  sectionTitle: { fontSize: 15, fontWeight: '600', color: '#1A1226', marginBottom: 12, marginTop: 8 },
  colorRow: { flexDirection: 'row', gap: 14, marginBottom: 24 },
  colorBtn: { width: 44, height: 44, borderRadius: 22, borderWidth: 3 },
  timerRow: { flexDirection: 'row', gap: 10, marginBottom: 24 },
  timerBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 20, paddingVertical: 12, borderRadius: 16, borderWidth: 1.5, borderColor: '#EDE9F6' },
  activeTimerBtn: { backgroundColor: primary, borderColor: primary },
  timerText: { fontSize: 14, fontWeight: '600', color: primary },
  statusCard: { flexDirection: 'row', alignItems: 'center', gap: 10, backgroundColor: '#F5F3FF', padding: 16, borderRadius: 16 },
  statusText: { fontSize: 14, color: primary, fontWeight: '600', flex: 1 },
});
