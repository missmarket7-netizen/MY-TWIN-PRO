import {
  SafeAreaView, View, Text, TouchableOpacity, StyleSheet,
  ScrollView, Alert, TextInput, ActivityIndicator, Modal,
  RefreshControl, Platform, KeyboardAvoidingView
} from 'react-native';
import { useState, useEffect, useCallback, useRef } from 'react';
import { supabase } from '../lib/supabase';
import { useTwinStore } from '../store/useTwinStore';
import Header from '../components/Header';
import { Stack } from 'expo-router';
import { router } from 'expo-router';
import {
  User, Mail, Phone, Crown, Zap, MessageSquare, Edit, LogOut, Trash2,
  Heart, Brain, TrendingUp, Plus, X, Smile, Sparkles,
  Lightbulb, Target, Star
} from 'lucide-react-native';

const MOOD_OPTIONS = [
  { emoji:'😊', label_ar:'سعيد', label_en:'Happy', value:'joy', color:'#F59E0B' },
  { emoji:'😌', label_ar:'هادئ', label_en:'Calm', value:'neutral', color:'#3B82F6' },
  { emoji:'😢', label_ar:'حزين', label_en:'Sad', value:'sadness', color:'#60A5FA' },
  { emoji:'😤', label_ar:'غاضب', label_en:'Angry', value:'anger', color:'#EF4444' },
  { emoji:'😨', label_ar:'قلق', label_en:'Anxious', value:'fear', color:'#A78BFA' },
  { emoji:'💕', label_ar:'محب', label_en:'Loving', value:'love', color:'#EC4899' },
  { emoji:'😴', label_ar:'متعب', label_en:'Tired', value:'tired', color:'#8B5CF6' },
];

const TEXTS: Record<string, Record<string,string>> = {
  ar: {
    title:'الملف الشخصي', name:'الاسم', email:'البريد الإلكتروني', phone:'رقم الهاتف',
    tier:'الباقة الحالية', messagesLeft:'الرسائل المتبقية', totalMessages:'إجمالي المحادثات',
    editProfile:'تعديل', upgrade:'ترقية', logout:'تسجيل الخروج', deleteAccount:'حذف الحساب',
    save:'حفظ', cancel:'إلغاء', contactInfo:'معلومات الاتصال', usageInfo:'الاستخدام',
    bond:'مستوى الرابطة', phase:'مرحلة الرحلة', attachment:'نمط التعلق', energy:'طاقة التوأم',
    recentMood:'آخر المشاعر', addMood:'تسجيل مشاعر', noMoodData:'لا توجد بيانات بعد',
    howFeel:'كيف تشعر؟', saveMood:'تسجيل', moodRecorded:'تم تسجيل المشاعر',
    discoveredTraits:'الصفات المكتشفة', personalityTraits:'سمات الشخصية',
    preferences:'تفضيلات', beliefs:'معتقدات', interests:'اهتمامات', communicationStyle:'أسلوب التواصل',
  },
  en: {
    title:'Profile', name:'Name', email:'Email', phone:'Phone',
    tier:'Current Plan', messagesLeft:'Messages left', totalMessages:'Total conversations',
    editProfile:'Edit', upgrade:'Upgrade', logout:'Logout', deleteAccount:'Delete Account',
    save:'Save', cancel:'Cancel', contactInfo:'Contact Info', usageInfo:'Usage',
    bond:'Bond Level', phase:'Journey Phase', attachment:'Attachment Style', energy:'Twin Energy',
    recentMood:'Recent Moods', addMood:'Log Mood', noMoodData:'No data yet',
    howFeel:'How do you feel?', saveMood:'Log', moodRecorded:'Mood recorded',
    discoveredTraits:'Discovered Traits', personalityTraits:'Personality Traits',
    preferences:'Preferences', beliefs:'Beliefs', interests:'Interests', communicationStyle:'Communication Style',
  }
};

export default function Profile() {
  const {
    userId, tier, lang, theme, logout: storeLogout,
    bondLevel, journeyPhase, attachmentStyle, energy, totalMessages
  } = useTwinStore();
  const [profile, setProfile] = useState<Record<string,any>>({});
  const [email, setEmail] = useState('');
  const [usage, setUsage] = useState({ messages: 0 });
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [loadingProfile, setLoadingProfile] = useState(true);

  const [recentMoods, setRecentMoods] = useState<any[]>([]);
  const [showAddMoodModal, setShowAddMoodModal] = useState(false);
  const [selectedMood, setSelectedMood] = useState('joy');
  const [savingMood, setSavingMood] = useState(false);
  const [moodsRefreshing, setMoodsRefreshing] = useState(false);
  const cancelledRef = useRef(false);

  const [discoveredProfile, setDiscoveredProfile] = useState<any>(null);

  const texts = TEXTS[lang] || TEXTS.ar;
  const t = (key: string) => texts[key] || key;
  const isAr = lang === 'ar'; const isDark = theme === 'dark';
  const bg = isDark ? '#1A1A1A' : '#F8F6F2'; const card = isDark ? '#2A2A2A' : '#FFF';
  const border = isDark ? '#444' : '#F0F0F0'; const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#CCC' : '#666'; const primary = isDark ? '#D8B4FE' : '#6B21A8';

  useEffect(() => {
    if (!userId) return;
    let cancelled = false;
    const load = async () => {
      try {
        const { data: profileData } = await supabase.from('profiles').select('*').eq('id', userId).maybeSingle();
        if (!cancelled && profileData) { setProfile(profileData); setName(profileData.full_name || ''); setPhone(profileData.phone || ''); }
        const { data: userData } = await supabase.auth.getUser();
        if (!cancelled && userData?.user?.email) setEmail(userData.user.email);
        const today = new Date().toISOString().split('T')[0];
        const { data: usageData } = await supabase.from('daily_usage').select('*').eq('user_id', userId).eq('date', today).maybeSingle();
        if (!cancelled && usageData) setUsage(usageData);
      } catch (e) { console.error('Profile load error:', e); }
      finally { if (!cancelled) setLoadingProfile(false); }
    };
    load();
    return () => { cancelled = true; };
  }, [userId]);

  useEffect(() => {
    if (!userId) return;
    (async () => {
      const { data } = await supabase.from('personality_profiles')
        .select('analyzed_traits').eq('user_id', userId)
        .order('created_at', { ascending: false }).limit(1).maybeSingle();
      if (data?.analyzed_traits) setDiscoveredProfile(data.analyzed_traits);
    })();
  }, [userId]);

  const fetchMoods = useCallback(async (showRefresh = false) => {
    if (!userId) return;
    if (showRefresh) setMoodsRefreshing(true);
    try {
      const { data } = await supabase.from('emotional_timeline').select('*').eq('user_id', userId).order('created_at', { ascending: false }).limit(7);
      if (!cancelledRef.current) setRecentMoods(data || []);
    } catch (e) { console.error('Mood fetch error:', e); }
    finally { if (!cancelledRef.current) setMoodsRefreshing(false); }
  }, [userId]);

  useEffect(() => { cancelledRef.current = false; fetchMoods(); return () => { cancelledRef.current = true; }; }, [fetchMoods]);

  const handleAddMood = async () => {
    if (!userId) return;
    setSavingMood(true);
    try {
      const { error } = await supabase.from('emotional_timeline').insert({
        user_id: userId, primary_emotion: selectedMood, intensity: 0.7,
        valence: selectedMood === 'joy' || selectedMood === 'love' ? 0.8 : selectedMood === 'sadness' || selectedMood === 'anger' ? -0.5 : 0.2,
      });
      if (error) throw error;
      setShowAddMoodModal(false);
      fetchMoods(true);
    } catch (e: any) { Alert.alert(t('خطأ'), e.message || t('فشل تسجيل المشاعر')); }
    finally { setSavingMood(false); }
  };

  const handleSave = async () => {
    if (!userId) return;
    try {
      await supabase.from('profiles').update({ full_name: name.trim(), phone: phone.trim() }).eq('id', userId);
      setProfile((p: any) => ({ ...p, full_name: name.trim(), phone: phone.trim() }));
      setEditing(false); Alert.alert('✅', t('save'));
    } catch { Alert.alert('❌', isAr ? 'فشل الحفظ' : 'Save failed'); }
  };

  const handleLogout = async () => { await supabase.auth.signOut(); storeLogout(); router.replace('/login'); };
  const handleDelete = () => {
    Alert.alert(t('deleteAccount'), isAr ? 'لا يمكن التراجع.' : 'This cannot be undone.', [
      { text: t('cancel'), style: 'cancel' },
      { text: t('deleteAccount'), style: 'destructive', onPress: async () => {
        try { await supabase.rpc('delete_user', { user_id: userId }); storeLogout(); router.replace('/login'); }
        catch { Alert.alert('❌', isAr ? 'فشل الحذف' : 'Delete failed'); }
      }}
    ]);
  };

  const phaseLabels: Record<string, string> = { introduction: 'تعارف', trust_building: 'بناء ثقة', deepening: 'تعمق', growth: 'نمو', mature: 'نضج' };
  const attachmentLabels: Record<string, string> = { secure: 'آمن', anxious: 'قلق', avoidant: 'متجنب', disorganized: 'غير منظم', unknown: 'غير معروف' };

  if (loadingProfile) {
    return (
      <SafeAreaView style={[styles.safe, { backgroundColor: bg }, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={primary} />
      </SafeAreaView>
    );
  }
  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header title={t('title')} />

      <ScrollView contentContainerStyle={styles.content} refreshControl={<RefreshControl refreshing={moodsRefreshing} onRefresh={() => fetchMoods(true)} colors={[primary]} />}>
        
        <TouchableOpacity style={[styles.editFab, { backgroundColor: primary }]} onPress={() => setEditing(!editing)}>
          <Edit size={22} stroke="#FFF" />
        </TouchableOpacity>

        <View style={[styles.userCard, { backgroundColor: card, borderColor: border }]}>
          <View style={styles.avatar}><User size={44} stroke="#FFF" /></View>
          <Text style={[styles.userName, { color: txt }]}>{profile.full_name || '—'}</Text>
          <Text style={[styles.userEmail, { color: sub }]}>{email || '—'}</Text>
        </View>

        <View style={[styles.statsGrid, { marginBottom: 14 }]}>
          <View style={[styles.statCard, { backgroundColor: card, borderColor: border }]}><Heart size={18} stroke="#EC4899" /><Text style={[styles.statValue, { color: txt }]}>{Math.round(bondLevel)}%</Text><Text style={[styles.statLabel, { color: sub }]}>{t('bond')}</Text></View>
          <View style={[styles.statCard, { backgroundColor: card, borderColor: border }]}><TrendingUp size={18} stroke="#10B981" /><Text style={[styles.statValue, { color: txt }]}>{phaseLabels[journeyPhase] || journeyPhase}</Text><Text style={[styles.statLabel, { color: sub }]}>{t('phase')}</Text></View>
          <View style={[styles.statCard, { backgroundColor: card, borderColor: border }]}><Brain size={18} stroke="#8B5CF6" /><Text style={[styles.statValue, { color: txt }]}>{attachmentLabels[attachmentStyle] || attachmentStyle}</Text><Text style={[styles.statLabel, { color: sub }]}>{t('attachment')}</Text></View>
          <View style={[styles.statCard, { backgroundColor: card, borderColor: border }]}><Zap size={18} stroke="#F59E0B" /><Text style={[styles.statValue, { color: txt }]}>{Math.round(energy)}%</Text><Text style={[styles.statLabel, { color: sub }]}>{t('energy')}</Text></View>
        </View>

        {discoveredProfile && (
          <View style={[styles.section, { backgroundColor: card, borderColor: border }]}>
            <View style={styles.sectionHeader}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                <Sparkles size={20} stroke={primary} />
                <Text style={[styles.sectionTitle, { color: txt, marginBottom: 0 }]}>{t('discoveredTraits')}</Text>
              </View>
            </View>
            {discoveredProfile.personality_traits && discoveredProfile.personality_traits.length > 0 && (
              <View style={{ marginBottom: 10 }}>
                <Text style={[styles.subLabel, { color: sub }]}>{t('personalityTraits')}</Text>
                <View style={styles.tagsRow}>
                  {discoveredProfile.personality_traits.map((trait: string, i: number) => (
                    <View key={i} style={[styles.tag, { backgroundColor: primary + '20', borderColor: primary + '40' }]}>
                      <Text style={[styles.tagText, { color: primary }]}>{trait}</Text>
                    </View>
                  ))}
                </View>
              </View>
            )}
            {discoveredProfile.preferences && discoveredProfile.preferences.length > 0 && (
              <View style={{ marginBottom: 10 }}>
                <Text style={[styles.subLabel, { color: sub }]}>{t('preferences')}</Text>
                <View style={styles.tagsRow}>
                  {discoveredProfile.preferences.map((pref: string, i: number) => (
                    <View key={i} style={[styles.tag, { backgroundColor: '#10B98120', borderColor: '#10B98140' }]}>
                      <Star size={12} stroke="#10B981" /><Text style={[styles.tagText, { color: '#10B981' }]}>{pref}</Text>
                    </View>
                  ))}
                </View>
              </View>
            )}
            {discoveredProfile.interests && discoveredProfile.interests.length > 0 && (
              <View style={{ marginBottom: 10 }}>
                <Text style={[styles.subLabel, { color: sub }]}>{t('interests')}</Text>
                <View style={styles.tagsRow}>
                  {discoveredProfile.interests.map((interest: string, i: number) => (
                    <View key={i} style={[styles.tag, { backgroundColor: '#F59E0B20', borderColor: '#F59E0B40' }]}>
                      <Lightbulb size={12} stroke="#F59E0B" /><Text style={[styles.tagText, { color: '#F59E0B' }]}>{interest}</Text>
                    </View>
                  ))}
                </View>
              </View>
            )}
            {discoveredProfile.beliefs && discoveredProfile.beliefs.length > 0 && (
              <View style={{ marginBottom: 10 }}>
                <Text style={[styles.subLabel, { color: sub }]}>{t('beliefs')}</Text>
                <View style={styles.tagsRow}>
                  {discoveredProfile.beliefs.map((belief: string, i: number) => (
                    <View key={i} style={[styles.tag, { backgroundColor: '#8B5CF620', borderColor: '#8B5CF640' }]}>
                      <Target size={12} stroke="#8B5CF6" /><Text style={[styles.tagText, { color: '#8B5CF6' }]}>{belief}</Text>
                    </View>
                  ))}
                </View>
              </View>
            )}
            {discoveredProfile.communication_style && (
              <View>
                <Text style={[styles.subLabel, { color: sub }]}>{t('communicationStyle')}</Text>
                <View style={[styles.tag, { backgroundColor: '#EC489920', borderColor: '#EC489940', alignSelf: 'flex-start' }]}>
                  <Text style={[styles.tagText, { color: '#EC4899' }]}>{discoveredProfile.communication_style}</Text>
                </View>
              </View>
            )}
          </View>
        )}

        <View style={[styles.section, { backgroundColor: card, borderColor: border }]}>
          <Text style={[styles.sectionTitle, { color: txt }]}>{t('contactInfo')}</Text>
          {editing ? (
            <>
              <TextInput style={[styles.input, { backgroundColor: isDark ? '#333' : '#F8F6F2', color: txt }]} placeholder={t('name')} value={name} onChangeText={setName} />
              <TextInput style={[styles.input, { backgroundColor: isDark ? '#333' : '#F8F6F2', color: txt }]} placeholder={t('phone')} value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
              <View style={styles.btnRow}><TouchableOpacity style={[styles.smallBtn, { backgroundColor: primary }]} onPress={handleSave}><Text style={styles.smallBtnText}>{t('save')}</Text></TouchableOpacity><TouchableOpacity style={[styles.smallBtn, { backgroundColor: '#F0F0F0' }]} onPress={() => setEditing(false)}><Text style={[styles.smallBtnText, { color: '#666' }]}>{t('cancel')}</Text></TouchableOpacity></View>
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
          <Text style={[styles.sectionTitle, { color: txt }]}>{t('usageInfo')}</Text>
          <View style={styles.row}><Crown size={16} stroke={primary} /><Text style={styles.label}>{t('tier')}</Text><Text style={[styles.value, { color: txt }]}>{tier}</Text></View>
          <View style={styles.row}><Zap size={16} stroke={primary} /><Text style={styles.label}>{t('messagesLeft')}</Text><Text style={[styles.value, { color: txt }]}>{usage.messages || 0}</Text></View>
          <View style={styles.row}><MessageSquare size={16} stroke={primary} /><Text style={styles.label}>{t('totalMessages')}</Text><Text style={[styles.value, { color: txt }]}>{totalMessages || 0}</Text></View>
        </View>

        <View style={[styles.section, { backgroundColor: card, borderColor: border }]}>
          <View style={[styles.sectionHeader, isAr && { flexDirection: 'row-reverse' }]}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}><Smile size={20} stroke={primary} /><Text style={[styles.sectionTitle, { color: txt, marginBottom: 0 }]}>{t('recentMood')}</Text></View>
            <TouchableOpacity style={[styles.addMoodBtn, { backgroundColor: primary }]} onPress={() => setShowAddMoodModal(true)}><Plus size={18} stroke="#FFF" /></TouchableOpacity>
          </View>
          {recentMoods.length === 0 ? <Text style={[styles.emptyMood, { color: sub }]}>{t('noMoodData')}</Text> : recentMoods.map((entry, i) => {
            const moodInfo = MOOD_OPTIONS.find(m => m.value === entry.primary_emotion) || MOOD_OPTIONS[1];
            return (
              <View key={i} style={[styles.moodRow, { borderColor: border }]}>
                <Text style={{ fontSize: 24 }}>{moodInfo.emoji}</Text>
                <View style={{ flex: 1 }}><Text style={[styles.moodLabel, { color: txt }]}>{isAr ? moodInfo.label_ar : moodInfo.label_en}</Text><Text style={[styles.moodTime, { color: sub }]}>{new Date(entry.created_at).toLocaleDateString(isAr ? 'ar-EG' : 'en-US', { weekday: 'long', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</Text></View>
                <View style={[styles.intensityDot, { backgroundColor: moodInfo.color, width: 12 + entry.intensity * 12, height: 12 + entry.intensity * 12, borderRadius: 6 + entry.intensity * 6 }]} />
              </View>
            );
          })}
        </View>

        <TouchableOpacity style={[styles.btn, { backgroundColor: primary }]} onPress={() => router.push('/subscription')}><Crown size={16} stroke="#FFF" /><Text style={styles.btnText}>{t('upgrade')}</Text></TouchableOpacity>
        <TouchableOpacity style={[styles.btn, styles.outlineBtn, { borderColor: primary }]} onPress={handleLogout}><LogOut size={16} stroke={primary} /><Text style={[styles.btnText, { color: primary }]}>{t('logout')}</Text></TouchableOpacity>
        <TouchableOpacity style={[styles.btn, styles.dangerBtn]} onPress={handleDelete}><Trash2 size={16} stroke="#EF4444" /><Text style={[styles.btnText, { color: '#EF4444' }]}>{t('deleteAccount')}</Text></TouchableOpacity>
      </ScrollView>

      <Modal visible={showAddMoodModal} transparent animationType="fade" onRequestClose={() => setShowAddMoodModal(false)}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.modalOverlay}>
          <View style={[styles.modalContent, isDark && { backgroundColor: '#2A2A2A' }]}>
            <View style={[styles.modalHeader, isAr && { flexDirection: 'row-reverse' }]}><Text style={[styles.modalTitle, { color: txt }]}>{t('howFeel')}</Text><TouchableOpacity onPress={() => setShowAddMoodModal(false)}><X size={22} stroke={sub} /></TouchableOpacity></View>
            <View style={styles.moodGrid}>
              {MOOD_OPTIONS.map((mood) => (
                <TouchableOpacity key={mood.value} style={[styles.moodOption, { borderColor: selectedMood === mood.value ? mood.color : border, backgroundColor: selectedMood === mood.value ? mood.color + '20' : 'transparent' }]} onPress={() => setSelectedMood(mood.value)}>
                  <Text style={styles.moodOptionEmoji}>{mood.emoji}</Text>
                  <Text style={[styles.moodOptionLabel, { color: selectedMood === mood.value ? mood.color : sub }]}>{isAr ? mood.label_ar : mood.label_en}</Text>
                </TouchableOpacity>
              ))}
            </View>
            <TouchableOpacity style={[styles.saveMoodBtn, { backgroundColor: primary, opacity: savingMood ? 0.6 : 1 }]} onPress={handleAddMood} disabled={savingMood}>
              {savingMood ? <ActivityIndicator color="#FFF" /> : <Text style={styles.saveMoodBtnText}>{t('saveMood')}</Text>}
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  content: { padding: 20, paddingBottom: 40 },
  editFab: { position: 'absolute', right: 20, top: 10, zIndex: 10, width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center', elevation: 5 },
  userCard: { alignItems: 'center', padding: 24, borderRadius: 20, borderWidth: 1, marginBottom: 16, marginTop: 50 },
  avatar: { width: 76, height: 76, borderRadius: 38, backgroundColor: '#6B21A8', justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  userName: { fontSize: 20, fontWeight: '800', marginBottom: 4 },
  userEmail: { fontSize: 14 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  statCard: { width: '48%', alignItems: 'center', padding: 14, borderRadius: 14, borderWidth: 1, marginBottom: 8 },
  statValue: { fontSize: 18, fontWeight: '700', marginTop: 4 },
  statLabel: { fontSize: 11, marginTop: 2 },
  section: { padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 14 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  sectionTitle: { fontSize: 16, fontWeight: '700' },
  subLabel: { fontSize: 13, fontWeight: '600', marginBottom: 6 },
  tagsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginBottom: 8 },
  tag: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 10, paddingVertical: 6, borderRadius: 12, borderWidth: 1 },
  tagText: { fontSize: 12, fontWeight: '600' },
  row: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 8 },
  label: { fontSize: 13, flex: 1 },
  value: { fontSize: 14, fontWeight: '500', flex: 2 },
  input: { padding: 10, borderRadius: 8, fontSize: 14, marginBottom: 8 },
  btnRow: { flexDirection: 'row', gap: 10, marginTop: 10 },
  smallBtn: { flex: 1, padding: 10, borderRadius: 8, alignItems: 'center' },
  smallBtnText: { color: '#FFF', fontWeight: '700', fontSize: 14 },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 14, borderRadius: 12, marginTop: 10 },
  btnText: { color: '#FFF', fontWeight: '700', fontSize: 15 },
  outlineBtn: { backgroundColor: 'transparent', borderWidth: 1.5 },
  dangerBtn: { backgroundColor: '#FFF5F5', borderWidth: 1.5, borderColor: '#FFCDD2' },
  addMoodBtn: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  emptyMood: { textAlign: 'center', fontSize: 14, marginTop: 10 },
  moodRow: { flexDirection: 'row', alignItems: 'center', padding: 12, borderRadius: 12, borderWidth: 1, marginBottom: 8, gap: 10 },
  moodLabel: { fontSize: 15, fontWeight: '600' },
  moodTime: { fontSize: 12, marginTop: 2 },
  intensityDot: {},
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' },
  modalContent: { width: '90%', backgroundColor: '#FFF', borderRadius: 20, padding: 20 },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  modalTitle: { fontSize: 18, fontWeight: '700' },
  moodGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 16 },
  moodOption: { alignItems: 'center', padding: 12, borderRadius: 14, borderWidth: 1.5, width: '30%' },
  moodOptionEmoji: { fontSize: 28, marginBottom: 4 },
  moodOptionLabel: { fontSize: 12, fontWeight: '500' },
  saveMoodBtn: { padding: 14, borderRadius: 12, alignItems: 'center' },
  saveMoodBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
});
