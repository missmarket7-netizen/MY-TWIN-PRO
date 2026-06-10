import {
  SafeAreaView, View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, TextInput, ActivityIndicator
} from 'react-native';
import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { useTwinStore } from '../store/useTwinStore';
import { router, Href } from 'expo-router';
import {
  User, Mail, Phone, Crown, Zap, MessageSquare, Edit, LogOut, Trash2, Sparkles, BrainCircuit
} from 'lucide-react-native';

const TEXTS = {
  ar: {
    title: 'الملف الشخصي', name: 'الاسم', email: 'البريد الإلكتروني', phone: 'رقم الهاتف',
    tier: 'الباقة الحالية', messagesLeft: 'الرسائل المتبقية اليوم', totalMessages: 'إجمالي المحادثات',
    editProfile: 'تعديل', upgrade: 'ترقية', logout: 'تسجيل الخروج', deleteAccount: 'حذف الحساب',
    save: 'حفظ', cancel: 'إلغاء', contactInfo: 'معلومات الاتصال', usageInfo: 'الاستخدام',
    knowledge: 'ماذا يعرف عنك توأمك؟', noKnowledge: 'تحدث مع توأمك أكثر ليكتشف أسرارك 💜',
  },
  en: {
    title: 'Profile', name: 'Name', email: 'Email', phone: 'Phone',
    tier: 'Current Plan', messagesLeft: 'Messages left today', totalMessages: 'Total conversations',
    editProfile: 'Edit', upgrade: 'Upgrade', logout: 'Logout', deleteAccount: 'Delete Account',
    save: 'Save', cancel: 'Cancel', contactInfo: 'Contact Info', usageInfo: 'Usage',
    knowledge: 'What your Twin knows about you', noKnowledge: 'Chat more with your Twin to unlock secrets 💜',
  },
};

export default function Profile() {
  const { userId, tier, lang, theme, logout: storeLogout } = useTwinStore();
  const [profile, setProfile] = useState<Record<string, any>>({});
  const [email, setEmail] = useState('');
  const [usage, setUsage] = useState({ messages: 0 });
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [knowledge, setKnowledge] = useState<string[]>([]);
  const [loadingKnowledge, setLoadingKnowledge] = useState(true);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const t = TEXTS[lang] || TEXTS['ar'];
  const isDark = theme === 'dark';

  useEffect(() => {
    if (!userId) return;
    let cancelled = false;

    const loadProfile = async () => {
      try {
        const { data: profileData, error: profileError } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', userId)
          .maybeSingle();

        if (!cancelled && !profileError && profileData) {
          setProfile(profileData);
          setName(profileData.full_name || '');
          setPhone(profileData.phone || '');
        }

        const { data: userData, error: userError } = await supabase.auth.getUser();
        if (!cancelled && !userError && userData?.user?.email) {
          setEmail(userData.user.email);
        }

        const today = new Date().toISOString().split('T')[0];
        const { data: usageData } = await supabase
          .from('daily_usage')
          .select('*')
          .eq('user_id', userId)
          .eq('date', today)
          .maybeSingle();
        if (!cancelled && usageData) setUsage(usageData);

        const { data: knowledgeData } = await supabase
          .from('knowledge_entities')
          .select('entity_name, entity_type')
          .eq('user_id', userId)
          .limit(5);
        if (!cancelled && knowledgeData) {
          const items = knowledgeData.map((k: any) => `${k.entity_type === 'person' ? '👤' : '❤️'} ${k.entity_name}`);
          setKnowledge(items);
        }
      } catch (e) {
        console.error('Profile load error:', e);
      } finally {
        if (!cancelled) setLoadingProfile(false);
      }
    };

    loadProfile();
    return () => { cancelled = true; };
  }, [userId]);

  const handleSave = async () => {
    if (!userId) return;
    try {
      const { error } = await supabase
        .from('profiles')
        .update({ full_name: name.trim(), phone: phone.trim() })
        .eq('id', userId);
      if (error) throw error;
      setProfile((p: any) => ({ ...p, full_name: name.trim(), phone: phone.trim() }));
      setEditing(false);
      Alert.alert('✅', t.save);
    } catch {
      Alert.alert('❌', lang === 'ar' ? 'فشل الحفظ' : 'Save failed');
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    storeLogout();
    router.replace('/login');
  };

  const handleDelete = () => {
    Alert.alert(t.deleteAccount, lang === 'ar' ? 'لا يمكن التراجع.' : 'This cannot be undone.', [
      { text: t.cancel, style: 'cancel' },
      { text: t.deleteAccount, style: 'destructive', onPress: async () => {
          try {
            await supabase.rpc('delete_user', { user_id: userId });
            storeLogout();
            router.replace('/login');
          } catch {
            Alert.alert('❌', lang === 'ar' ? 'فشل الحذف' : 'Delete failed');
          }
        }
      },
    ]);
  };

  if (loadingProfile) {
    return (
      <SafeAreaView style={[s.safe, isDark && { backgroundColor: '#1A1A1A' }, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color="#6B21A8" />
      </SafeAreaView>
    );
  }

  const bg = isDark ? '#1A1A1A' : '#F8F6F2';
  const card = isDark ? '#2A2A2A' : '#FFF';
  const border = isDark ? '#444' : '#F0F0F0';
  const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#888' : '#666';

  return (
    <SafeAreaView style={[s.safe, { backgroundColor: bg }]}>
      <ScrollView style={s.container} contentContainerStyle={{ paddingBottom: 40 }}>
        <Text style={[s.title, { color: txt }]}>{t.title}</Text>

        <View style={[s.card, { backgroundColor: card, borderColor: border }]}>
          <View style={s.avatar}><User size={44} stroke="#FFF" /></View>
          <Text style={[s.name, { color: txt }]}>{profile.full_name || '—'}</Text>
          <Text style={[s.email, { color: sub }]}>{email || '—'}</Text>
        </View>

        <View style={[s.section, { backgroundColor: card, borderColor: border }]}>
          <View style={s.sectionHeader}>
            <User size={18} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
            <Text style={[s.sectionTitle, { color: txt }]}>{t.contactInfo}</Text>
          </View>
          {editing ? (
            <>
              <View style={[s.row, isDark && { borderBottomColor: '#444' }]}>
                <User size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
                <TextInput style={[s.input, { backgroundColor: isDark ? '#333' : '#F8F6F2', color: txt }]} placeholder={t.name} value={name} onChangeText={setName} />
              </View>
              <View style={[s.row, isDark && { borderBottomColor: '#444' }]}>
                <Phone size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
                <TextInput style={[s.input, { backgroundColor: isDark ? '#333' : '#F8F6F2', color: txt }]} placeholder={t.phone} value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
              </View>
              <View style={s.btnRow}>
                <TouchableOpacity style={[s.smallBtn, { backgroundColor: '#6B21A8' }]} onPress={handleSave}>
                  <Text style={s.smallBtnText}>{t.save}</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[s.smallBtn, { backgroundColor: '#F0F0F0' }]} onPress={() => setEditing(false)}>
                  <Text style={[s.smallBtnText, { color: '#666' }]}>{t.cancel}</Text>
                </TouchableOpacity>
              </View>
            </>
          ) : (
            <>
              <View style={[s.row, isDark && { borderBottomColor: '#444' }]}>
                <User size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
                <Text style={[s.value, { color: txt }]}>{profile.full_name || '—'}</Text>
              </View>
              <View style={[s.row, isDark && { borderBottomColor: '#444' }]}>
                <Mail size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
                <Text style={[s.value, { color: txt }]}>{email || '—'}</Text>
              </View>
              <View style={[s.row, isDark && { borderBottomColor: '#444' }]}>
                <Phone size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
                <Text style={[s.value, { color: txt }]}>{profile.phone || '—'}</Text>
              </View>
            </>
          )}
        </View>

        <View style={[s.section, { backgroundColor: card, borderColor: border }]}>
          <View style={s.sectionHeader}>
            <Zap size={18} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
            <Text style={[s.sectionTitle, { color: txt }]}>{t.usageInfo}</Text>
          </View>
          <View style={[s.row, isDark && { borderBottomColor: '#444' }]}>
            <Crown size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
            <Text style={s.label}>{t.tier}</Text>
            <Text style={[s.value, { color: txt }]}>{tier}</Text>
          </View>
          <View style={[s.row, isDark && { borderBottomColor: '#444' }]}>
            <Zap size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
            <Text style={s.label}>{t.messagesLeft}</Text>
            <Text style={[s.value, { color: txt }]}>{usage.messages || 0}</Text>
          </View>
          <View style={[s.row, isDark && { borderBottomColor: '#444' }]}>
            <MessageSquare size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
            <Text style={s.label}>{t.totalMessages}</Text>
            <Text style={[s.value, { color: txt }]}>{profile.total_messages || 0}</Text>
          </View>
        </View>

        <TouchableOpacity style={s.btn} onPress={() => router.push('/subscription' as Href)}>
          <Crown size={16} stroke="#FFF" />
          <Text style={s.btnText}>{t.upgrade}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[s.btn, s.outlineBtn]} onPress={handleLogout}>
          <LogOut size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
          <Text style={[s.btnText, { color: isDark ? '#D8B4FE' : '#6B21A8' }]}>{t.logout}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[s.btn, s.dangerBtn]} onPress={handleDelete}>
          <Trash2 size={16} stroke="#EF4444" />
          <Text style={[s.btnText, { color: '#EF4444' }]}>{t.deleteAccount}</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1 },
  container: { flex: 1, padding: 20 },
  title: { fontSize: 24, fontWeight: '800', marginBottom: 20 },
  card: { alignItems: 'center', padding: 20, borderRadius: 20, marginBottom: 16, borderWidth: 1 },
  avatar: { width: 76, height: 76, borderRadius: 38, backgroundColor: '#6B21A8', justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  name: { fontSize: 20, fontWeight: '800', marginBottom: 4 },
  email: { fontSize: 14 },
  section: { padding: 16, borderRadius: 16, marginBottom: 14, borderWidth: 1 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 12 },
  sectionTitle: { fontSize: 15, fontWeight: '700' },
  row: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#F8F8F8' },
  label: { fontSize: 13, flex: 1 },
  value: { fontSize: 14, fontWeight: '500', flex: 2 },
  input: { flex: 1, padding: 10, borderRadius: 8, fontSize: 14 },
  btnRow: { flexDirection: 'row', gap: 10, marginTop: 10 },
  smallBtn: { flex: 1, padding: 10, borderRadius: 8, alignItems: 'center' },
  smallBtnText: { color: '#FFF', fontWeight: '700', fontSize: 14 },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, backgroundColor: '#6B21A8', padding: 14, borderRadius: 12, marginTop: 10 },
  btnText: { color: '#FFF', fontWeight: '700', fontSize: 15 },
  outlineBtn: { backgroundColor: 'transparent', borderWidth: 1.5, borderColor: '#6B21A8' },
  dangerBtn: { backgroundColor: '#FFF5F5', borderWidth: 1.5, borderColor: '#FFCDD2' },
});
