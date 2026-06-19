import { SafeAreaView, ScrollView, Text, StyleSheet, View, TextInput, Alert, ActivityIndicator, RefreshControl, Platform, TouchableOpacity, Modal, KeyboardAvoidingView } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { getProfile, updateProfile, getMoods, addMood } from '../lib/httpClient';
import { useState, useEffect, useCallback } from 'react';
import Header from '../components/Header';
import { Stack } from 'expo-router';
import { router } from 'expo-router';
import { User, Mail, Phone, Crown, Zap, Edit, LogOut, Trash2, Heart, TrendingUp, Brain, Plus, X, Sparkles, Lightbulb, Target, Star } from 'lucide-react-native';
import { removeToken } from '../lib/auth';

export default function Profile() {
  const { userId, tier, lang, theme, logout: storeLogout, bondLevel, journeyPhase, attachmentStyle, twinEnergy, totalMessages } = useTwinStore();
  const isAr = lang === 'ar'; const isDark = theme === 'dark';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const bg = isDark ? '#1A1A1A' : '#F8F6F2'; const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#888' : '#666'; const card = isDark ? '#2A2A2A' : '#FFF';
  const border = isDark ? '#444' : '#F0F0F0'; const primary = isDark ? '#D8B4FE' : '#6B21A8';

  const [profile, setProfile] = useState<any>({});
  const [email, setEmail] = useState('');
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [loadingProfile, setLoadingProfile] = useState(true);

  const [recentMoods, setRecentMoods] = useState<any[]>([]);
  const [showAddMoodModal, setShowAddMoodModal] = useState(false);
  const [selectedMood, setSelectedMood] = useState('joy');
  const [savingMood, setSavingMood] = useState(false);

  const MOOD_OPTIONS = [
    { emoji:'😊', label_ar:'سعيد', label_en:'Happy', value:'joy', color:'#F59E0B' },
    { emoji:'😌', label_ar:'هادئ', label_en:'Calm', value:'neutral', color:'#3B82F6' },
    { emoji:'😢', label_ar:'حزين', label_en:'Sad', value:'sadness', color:'#60A5FA' },
    { emoji:'😤', label_ar:'غاضب', label_en:'Angry', value:'anger', color:'#EF4444' },
    { emoji:'😨', label_ar:'قلق', label_en:'Anxious', value:'fear', color:'#A78BFA' },
    { emoji:'💕', label_ar:'محب', label_en:'Loving', value:'love', color:'#EC4899' },
    { emoji:'😴', label_ar:'متعب', label_en:'Tired', value:'tired', color:'#8B5CF6' },
  ];

  const fetchProfile = useCallback(async () => {
    if (!userId) { setLoadingProfile(false); return; }
    try {
      const data = await getProfile();
      setProfile(data);
      setName(data?.full_name || '');
      setPhone(data?.phone || '');
      setEmail(data?.email || '');
    } catch (e) { console.error(e); }
    finally { setLoadingProfile(false); }
  }, [userId]);

  const fetchMoods = useCallback(async () => {
    try { const data = await getMoods(); setRecentMoods(data || []); } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { fetchProfile(); fetchMoods(); }, [fetchProfile, fetchMoods]);

  const handleSave = async () => {
    try {
      await updateProfile({ full_name: name.trim(), phone: phone.trim() });
      setProfile((p: any) => ({ ...p, full_name: name.trim(), phone: phone.trim() }));
      setEditing(false);
      Alert.alert('✅', t('تم الحفظ', 'Saved'));
    } catch { Alert.alert('❌', t('فشل الحفظ', 'Save failed')); }
  };

  const handleLogout = async () => {
    await removeToken();
    storeLogout();
    router.replace('/login');
  };

  const handleAddMood = async () => {
    setSavingMood(true);
    try { await addMood(selectedMood); setShowAddMoodModal(false); fetchMoods(); }
    catch (e: any) { Alert.alert(t('خطأ', 'Error'), e.message); }
    finally { setSavingMood(false); }
  };

  const phaseLabels: Record<string, string> = { introduction: 'تعارف', trust_building: 'بناء ثقة', deepening: 'تعمق', growth: 'نمو', mature: 'نضج' };
  const attachmentLabels: Record<string, string> = { secure: 'آمن', anxious: 'قلق', avoidant: 'متجنب', disorganized: 'غير منظم', unknown: 'غير معروف' };

  if (loadingProfile) return <SafeAreaView style={[styles.safe, { backgroundColor: bg, justifyContent: 'center', alignItems: 'center' }]}><ActivityIndicator size="large" color={primary} /></SafeAreaView>;

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header title={t('الملف الشخصي', 'Profile')} />
      <ScrollView contentContainerStyle={styles.content} refreshControl={<RefreshControl refreshing={false} onRefresh={fetchProfile} colors={[primary]} />}>
        <TouchableOpacity style={[styles.editFab, { backgroundColor: primary }]} onPress={() => setEditing(!editing)}><Edit size={22} stroke="#FFF" /></TouchableOpacity>
        <View style={[styles.userCard, { backgroundColor: card, borderColor: border }]}>
          <View style={styles.avatar}><User size={44} stroke="#FFF" /></View>
          <Text style={[styles.userName, { color: txt }]}>{profile.full_name || '—'}</Text>
          <Text style={[styles.userEmail, { color: sub }]}>{email || '—'}</Text>
        </View>
        <View style={[styles.statsGrid, { marginBottom: 14 }]}>
          {[
            { icon: Heart, val: `${Math.round(bondLevel)}%`, label: t('الرابطة', 'Bond'), color: '#EC4899' },
            { icon: TrendingUp, val: phaseLabels[journeyPhase] || journeyPhase, label: t('المرحلة', 'Phase'), color: '#10B981' },
            { icon: Brain, val: attachmentLabels[attachmentStyle] || attachmentStyle, label: t('التعلق', 'Attachment'), color: '#8B5CF6' },
            { icon: Zap, val: `${Math.round(twinEnergy)}%`, label: t('الطاقة', 'Energy'), color: '#F59E0B' },
          ].map((s, i) => (
            <View key={i} style={[styles.statCard, { backgroundColor: card, borderColor: border }]}>
              <s.icon size={18} stroke={s.color} />
              <Text style={[styles.statValue, { color: txt }]}>{s.val}</Text>
              <Text style={[styles.statLabel, { color: sub }]}>{s.label}</Text>
            </View>
          ))}
        </View>
        <View style={[styles.section, { backgroundColor: card, borderColor: border }]}>
          <Text style={[styles.sectionTitle, { color: txt }]}>{t('معلومات الاتصال', 'Contact Info')}</Text>
          {editing ? (
            <>
              <TextInput style={[styles.input, { backgroundColor: isDark ? '#333' : '#F8F6F2', color: txt }]} placeholder={t('الاسم', 'Name')} value={name} onChangeText={setName} />
              <TextInput style={[styles.input, { backgroundColor: isDark ? '#333' : '#F8F6F2', color: txt }]} placeholder={t('الهاتف', 'Phone')} value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
              <View style={styles.btnRow}>
                <TouchableOpacity style={[styles.smallBtn, { backgroundColor: primary }]} onPress={handleSave}><Text style={styles.smallBtnText}>{t('حفظ', 'Save')}</Text></TouchableOpacity>
                <TouchableOpacity style={[styles.smallBtn, { backgroundColor: '#F0F0F0' }]} onPress={() => setEditing(false)}><Text style={[styles.smallBtnText, { color: '#666' }]}>{t('إلغاء', 'Cancel')}</Text></TouchableOpacity>
              </View>
            </>
          ) : (
            <>
              <View style={styles.row}><User size={16} stroke={primary} /><Text style={[styles.value, { color: txt }]}>{profile.full_name || '—'}</Text></View>
              <View style={styles.row}><Mail size={16} stroke={primary} /><Text style={[styles.value, { color: txt }]}>{email || '—'}</Text></View>
              <View style={styles.row}><Phone size={16} stroke={primary} /><Text style={[styles.value, { color: txt }]}>{profile.phone || '—'}</Text></View>
            </>
          )}
        </View>
        <View style={[styles.section, { backgroundColor: card, borderColor: border }]}>
          <Text style={[styles.sectionTitle, { color: txt }]}>{t('الباقة', 'Plan')}</Text>
          <View style={styles.row}><Crown size={16} stroke={primary} /><Text style={styles.label}>{t('الباقة الحالية', 'Current Plan')}:</Text><Text style={[styles.value, { color: txt }]}>{tier}</Text></View>
          <View style={styles.row}><Zap size={16} stroke={primary} /><Text style={styles.label}>{t('إجمالي المحادثات', 'Total Messages')}:</Text><Text style={[styles.value, { color: txt }]}>{totalMessages}</Text></View>
        </View>
        <TouchableOpacity style={[styles.btn, { backgroundColor: primary }]} onPress={() => router.push('/subscription')}><Crown size={16} stroke="#FFF" /><Text style={styles.btnText}>{t('ترقية', 'Upgrade')}</Text></TouchableOpacity>
        <TouchableOpacity style={[styles.btn, { backgroundColor: 'transparent', borderWidth: 1, borderColor: '#EF4444' }]} onPress={handleLogout}><LogOut size={16} stroke="#EF4444" /><Text style={[styles.btnText, { color: '#EF4444' }]}>{t('تسجيل الخروج', 'Sign Out')}</Text></TouchableOpacity>
        <TouchableOpacity style={[styles.btn, { backgroundColor: '#EF4444' }]} onPress={async () => { await removeToken(); storeLogout(); router.replace('/login'); }}><Trash2 size={16} stroke="#FFF" /><Text style={styles.btnText}>{t('حذف الحساب', 'Delete Account')}</Text></TouchableOpacity>
      </ScrollView>
      <Modal visible={showAddMoodModal} transparent animationType="fade" onRequestClose={() => setShowAddMoodModal(false)}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.modalOverlay}>
          <View style={[styles.modalContent, isDark && { backgroundColor: '#2A2A2A' }]}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <Text style={[styles.modalTitle, { color: txt }]}>{t('كيف تشعر؟', 'How do you feel?')}</Text>
              <TouchableOpacity onPress={() => setShowAddMoodModal(false)}><X size={22} stroke={sub} /></TouchableOpacity>
            </View>
            <View style={styles.moodGrid}>
              {MOOD_OPTIONS.map((mood) => (
                <TouchableOpacity key={mood.value} style={[styles.moodOption, { borderColor: selectedMood === mood.value ? mood.color : border, backgroundColor: selectedMood === mood.value ? mood.color + '20' : 'transparent' }]} onPress={() => setSelectedMood(mood.value)}>
                  <Text style={styles.moodOptionEmoji}>{mood.emoji}</Text>
                  <Text style={[styles.moodOptionLabel, { color: selectedMood === mood.value ? mood.color : sub }]}>{isAr ? mood.label_ar : mood.label_en}</Text>
                </TouchableOpacity>
              ))}
            </View>
            <TouchableOpacity style={[styles.saveBtn, { opacity: savingMood ? 0.6 : 1 }]} onPress={handleAddMood} disabled={savingMood}>
              {savingMood ? <ActivityIndicator color="#FFF" /> : <Text style={styles.saveBtnText}>{t('تسجيل', 'Log')}</Text>}
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 }, content: { padding: 20, paddingBottom: 40 },
  editFab: { position: 'absolute', top: 10, right: 20, zIndex: 10, padding: 10, borderRadius: 20 },
  userCard: { padding: 20, borderRadius: 20, borderWidth: 1, alignItems: 'center', marginBottom: 16 },
  avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: '#6B21A8', justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  userName: { fontSize: 22, fontWeight: '800' }, userEmail: { fontSize: 14, marginTop: 4 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  statCard: { width: '48%', padding: 14, borderRadius: 14, borderWidth: 1, alignItems: 'center', marginBottom: 10 },
  statValue: { fontSize: 20, fontWeight: '800', marginTop: 6 }, statLabel: { fontSize: 11, marginTop: 2 },
  section: { padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 16 },
  sectionTitle: { fontSize: 17, fontWeight: '700', marginBottom: 12 },
  input: { padding: 14, borderRadius: 12, borderWidth: 1, borderColor: '#E0D9F5', marginBottom: 8, fontSize: 15 },
  btnRow: { flexDirection: 'row', gap: 10 },
  smallBtn: { flex: 1, padding: 12, borderRadius: 10, alignItems: 'center' },
  smallBtnText: { fontWeight: '600', fontSize: 14 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 },
  label: { color: '#666', fontSize: 14 },
  value: { fontSize: 14, fontWeight: '600' },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 14, borderRadius: 12, marginBottom: 10 },
  btnText: { color: '#FFF', fontWeight: '600', fontSize: 15 },
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' },
  modalContent: { width: '90%', backgroundColor: '#FFF', borderRadius: 20, padding: 20 },
  modalTitle: { fontSize: 18, fontWeight: '700' },
  moodGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 16 },
  moodOption: { alignItems: 'center', padding: 12, borderRadius: 14, borderWidth: 1.5, width: '30%' },
  moodOptionEmoji: { fontSize: 28, marginBottom: 4 },
  moodOptionLabel: { fontSize: 12, fontWeight: '500' },
  saveBtn: { backgroundColor: '#6B21A8', padding: 14, borderRadius: 12, alignItems: 'center' },
  saveBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
});
