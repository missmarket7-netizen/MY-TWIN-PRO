import React, { useState, useCallback } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  Switch, ActivityIndicator, Alert, Modal, TextInput,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore, useTwinStoreFull } from '../../store/useTwinStore';
import { useTheme } from '../../utils/theme';
import { router } from 'expo-router';
import {
  ArrowLeft, Lightbulb, Music, Power, Home, Timer,
  Thermometer, Cloud, Check, X,
} from 'lucide-react-native';

export default function SmartHome() {
  const insets = useSafeAreaInsets();
  const theme = useTheme();
  const { lang } = useTwinStore();
  const { smartHomeCommand } = useTwinStoreFull();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';

  const [isLightOn, setIsLightOn] = useState(false);
  const [lightColor, setLightColor] = useState('أبيض');
  const [timer, setTimer] = useState(0);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const [voiceCommand, setVoiceCommand] = useState('');

  const colors = {
    bg: isDark ? '#0F0A1A' : '#FAFAF8',
    card: isDark ? '#1A1226' : '#FFFFFF',
    text: isDark ? '#FFFFFF' : '#2D2D2D',
    subtext: isDark ? '#8B7BA3' : '#6B6B6B',
    accent: '#06B6D4',
    accentLight: '#06B6D420',
    border: isDark ? '#2D1B4D' : '#E8E8E3',
    success: '#10B981',
    warning: '#F59E0B',
  };

  const colorOptions = [
    { name: 'أحمر', hex: '#EF4444' },
    { name: 'أزرق', hex: '#3B82F6' },
    { name: 'أخضر', hex: '#10B981' },
    { name: 'بنفسجي', hex: '#8B5CF6' },
    { name: 'أصفر', hex: '#F59E0B' },
    { name: 'أبيض', hex: '#F9FAFB' },
  ];

  const handleToggleLight = useCallback(async () => {
    setLoading(true);
    const command = isLightOn ? 'اطفئ النور' : 'شغل النور';
    try {
      const data = await smartHomeCommand(command);
      setIsLightOn(!isLightOn);
      setStatusMessage(data?.response || (isLightOn ? 'تم إطفاء النور' : 'تم تشغيل النور'));
    } catch (e: any) {
      Alert.alert(isAr ? 'خطأ' : 'Error', e.message);
    } finally { setLoading(false); }
  }, [isLightOn, smartHomeCommand]);

  const handleSetColor = useCallback(async (colorName: string) => {
    setLoading(true);
    try {
      const data = await smartHomeCommand(`غير لون النور إلى ${colorName}`);
      setLightColor(colorName);
      setStatusMessage(data?.response || `تم تغيير اللون إلى ${colorName}`);
    } catch (e: any) {
      Alert.alert(isAr ? 'خطأ' : 'Error', e.message);
    } finally { setLoading(false); }
  }, [smartHomeCommand]);

  const handleVoiceCommand = useCallback(async () => {
    if (!voiceCommand.trim()) return;
    setShowVoiceModal(false);
    setLoading(true);
    try {
      const data = await smartHomeCommand(voiceCommand.trim());
      setStatusMessage(data?.response || isAr ? 'تم تنفيذ الأمر' : 'Command executed');
      setVoiceCommand('');
    } catch (e: any) {
      Alert.alert(isAr ? 'خطأ' : 'Error', e.message);
    } finally { setLoading(false); }
  }, [voiceCommand, smartHomeCommand]);

  const handleSetTimer = (minutes: number) => {
    setTimer(minutes);
    setStatusMessage(isAr ? `تم ضبط المؤقت على ${minutes} دقيقة` : `Timer set to ${minutes} minutes`);
  };

  return (
    <View style={[st.root, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
      {/* الهيدر */}
      <View style={[st.header, { borderBottomColor: colors.border }]}>
        <TouchableOpacity onPress={() => router.back()}>
          <ArrowLeft size={24} stroke={colors.text} />
        </TouchableOpacity>
        <View style={st.headerCenter}>
          <Home size={24} stroke={colors.accent} />
          <Text style={[st.headerTitle, { color: colors.text }]}>
            {isAr ? 'المنزل الذكي' : 'Smart Home'}
          </Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={st.content}>
        {/* بطاقة الترحيب */}
        <View style={[st.heroCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <Home size={48} stroke={colors.accent} style={{ alignSelf: 'center', marginBottom: 16 }} />
          <Text style={[st.heroTitle, { color: colors.text }]}>
            {isAr ? 'مركز التحكم' : 'Control Center'}
          </Text>
          <Text style={[st.heroSub, { color: colors.subtext }]}>
            {isAr ? 'تحكم بمنزلك الذكي بلمسة واحدة' : 'Control your smart home with a tap'}
          </Text>
        </View>

        {/* بطاقة الإضاءة الرئيسية */}
        <View style={[st.controlCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
              <Lightbulb size={28} stroke={isLightOn ? colors.warning : colors.subtext} fill={isLightOn ? colors.warning : 'transparent'} />
              <View>
                <Text style={[st.controlLabel, { color: colors.text }]}>
                  {isAr ? 'الإضاءة الرئيسية' : 'Main Light'}
                </Text>
                <Text style={[st.controlStatus, { color: isLightOn ? colors.warning : colors.subtext }]}>
                  {isLightOn ? (isAr ? 'مضاءة' : 'On') : (isAr ? 'مطفأة' : 'Off')}
                </Text>
              </View>
            </View>
            <Switch
              value={isLightOn}
              onValueChange={handleToggleLight}
              trackColor={{ false: '#D1D5DB', true: colors.accent + '40' }}
              thumbColor={isLightOn ? colors.accent : '#F9FAFB'}
            />
          </View>
        </View>

        {/* اختيار اللون */}
        <Text style={[st.sectionTitle, { color: colors.text }]}>
          {isAr ? 'اختر لون الإضاءة' : 'Choose Color'}
        </Text>
        <View style={st.colorRow}>
          {colorOptions.map(c => (
            <TouchableOpacity
              key={c.name}
              style={[
                st.colorBtn,
                { backgroundColor: c.hex },
                lightColor === c.name && { borderColor: colors.text, borderWidth: 3 },
              ]}
              onPress={() => handleSetColor(c.name)}
            />
          ))}
        </View>

        {/* المؤقت */}
        <Text style={[st.sectionTitle, { color: colors.text }]}>
          {isAr ? 'مؤقت الإطفاء' : 'Sleep Timer'}
        </Text>
        <View style={st.timerRow}>
          {[5, 15, 30, 60].map(min => (
            <TouchableOpacity
              key={min}
              style={[
                st.timerBtn,
                { borderColor: colors.border },
                timer === min && { backgroundColor: colors.accent, borderColor: colors.accent },
              ]}
              onPress={() => handleSetTimer(min)}
            >
              <Timer size={16} stroke={timer === min ? '#FFF' : colors.text} />
              <Text style={[st.timerText, { color: timer === min ? '#FFF' : colors.text }]}>
                {min} {isAr ? 'د' : 'm'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* أمر صوتي */}
        <TouchableOpacity
          style={[st.voiceBtn, { backgroundColor: colors.card, borderColor: colors.border }]}
          onPress={() => setShowVoiceModal(true)}
        >
          <Cloud size={22} stroke={colors.accent} />
          <Text style={[st.voiceBtnText, { color: colors.text }]}>
            {isAr ? 'أمر صوتي' : 'Voice Command'}
          </Text>
        </TouchableOpacity>

        {/* رسالة الحالة */}
        {statusMessage && (
          <View style={[st.statusCard, { backgroundColor: colors.success + '15', borderColor: colors.success }]}>
            <Check size={20} stroke={colors.success} />
            <Text style={[st.statusText, { color: colors.success }]}>{statusMessage}</Text>
          </View>
        )}
      </ScrollView>

      {/* مودال الأمر الصوتي */}
      <Modal visible={showVoiceModal} transparent animationType="fade" onRequestClose={() => setShowVoiceModal(false)}>
        <TouchableOpacity style={st.modalOverlay} activeOpacity={1} onPress={() => setShowVoiceModal(false)}>
          <View style={[st.modalContent, { backgroundColor: colors.card }]}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <Text style={[st.modalTitle, { color: colors.text }]}>
                {isAr ? 'أمر صوتي' : 'Voice Command'}
              </Text>
              <TouchableOpacity onPress={() => setShowVoiceModal(false)}>
                <X size={22} stroke={colors.subtext} />
              </TouchableOpacity>
            </View>
            <TextInput
              style={[st.voiceInput, { backgroundColor: colors.bg, color: colors.text, borderColor: colors.border }]}
              placeholder={isAr ? 'مثلاً: شغل النور' : 'e.g., Turn on the light'}
              placeholderTextColor={colors.subtext}
              value={voiceCommand}
              onChangeText={setVoiceCommand}
              autoFocus
            />
            <TouchableOpacity
              style={[st.voiceSubmitBtn, { backgroundColor: colors.accent, opacity: voiceCommand.trim() ? 1 : 0.6 }]}
              onPress={handleVoiceCommand}
              disabled={!voiceCommand.trim() || loading}
            >
              {loading ? (
                <ActivityIndicator color="#FFF" />
              ) : (
                <Text style={st.voiceSubmitBtnText}>
                  {isAr ? 'تنفيذ' : 'Execute'}
                </Text>
              )}
            </TouchableOpacity>
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
  heroCard: { borderRadius: 24, padding: 28, marginBottom: 20, borderWidth: 1, alignItems: 'center' },
  heroTitle: { fontSize: 20, fontWeight: '800', marginBottom: 8 },
  heroSub: { fontSize: 14, textAlign: 'center' },
  controlCard: { borderRadius: 20, padding: 20, marginBottom: 24, borderWidth: 1 },
  controlLabel: { fontSize: 16, fontWeight: '600' },
  controlStatus: { fontSize: 13, marginTop: 2 },
  sectionTitle: { fontSize: 15, fontWeight: '600', marginBottom: 12, marginTop: 8 },
  colorRow: { flexDirection: 'row', gap: 14, marginBottom: 24 },
  colorBtn: { width: 44, height: 44, borderRadius: 22, borderWidth: 2, borderColor: 'transparent' },
  timerRow: { flexDirection: 'row', gap: 10, marginBottom: 24 },
  timerBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 20, paddingVertical: 12, borderRadius: 16, borderWidth: 1.5 },
  timerText: { fontSize: 14, fontWeight: '600' },
  voiceBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10, padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 24 },
  voiceBtnText: { fontSize: 15, fontWeight: '600' },
  statusCard: { flexDirection: 'row', alignItems: 'center', gap: 10, padding: 16, borderRadius: 16, borderWidth: 1 },
  statusText: { fontSize: 14, fontWeight: '600', flex: 1 },
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' },
  modalContent: { width: '85%', borderRadius: 20, padding: 20 },
  modalTitle: { fontSize: 18, fontWeight: '700' },
  voiceInput: { borderRadius: 14, padding: 16, fontSize: 16, borderWidth: 1, marginBottom: 16 },
  voiceSubmitBtn: { padding: 14, borderRadius: 14, alignItems: 'center' },
  voiceSubmitBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
});
