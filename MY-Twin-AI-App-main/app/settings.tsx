import { SafeAreaView, View, Text, StyleSheet, ScrollView, Switch, TouchableOpacity, Alert, Linking, Share, ActivityIndicator } from 'react-native';
import { router, Href } from 'expo-router';
import { useState, useMemo } from 'react';
import { useTwinStore } from '../store/useTwinStore';
import Header from '../components/Header';
import { deleteAccount, exportData } from '../lib/httpClient';
import { removeToken } from '../lib/auth';
import {
  Moon, Sun, Globe, Crown, HeartPulse, Shield, Download, LogOut, Trash2, Phone,
  BrainCircuit, Database, Cpu, HardDrive, Sparkles, Zap, HelpCircle, Info
} from 'lucide-react-native';

const TEXTS = {
  ar: {
    title: 'الإعدادات', tier: 'الخطة الحالية', calm: 'وضع الهدوء', lang: 'اللغة', theme: 'المظهر',
    upgrade: 'ترقية الخطة', privacy: 'سياسة الخصوصية', export: 'تصدير بياناتي', logout: 'تسجيل الخروج',
    delete: 'حذف الحساب', deleteTitle: 'حذف نهائي', deleteMsg: 'لا يمكن التراجع. سيتم حذف جميع ذكرياتك وبياناتك نهائياً.',
    cancel: 'إلغاء', confirmDelete: 'حذف', exportTitle: 'تصدير البيانات', exporting: 'جاري التصدير...',
    exportFail: 'فشل تصدير البيانات. تحقق من الاتصال.', deleteFail: 'فشل الحذف. تحقق من الاتصال.',
    emergency: 'دعم طوارئ نفسي', emergencyFail: 'تعذر فتح الرابط. جرب المتصفح.',
    help: 'مساعدة', about: 'حول التطبيق', aiStats: 'إحصائيات الذكاء الاصطناعي',
    modelsActive: 'نماذج نشطة', memoriesStored: 'ذكريات مخزنة', dailyRequests: 'طلبات اليوم', latency: 'متوسط السرعة',
  },
  en: {
    title: 'Settings', tier: 'Current Plan', calm: 'Calm Mode', lang: 'Language', theme: 'Theme',
    upgrade: 'Upgrade Plan', privacy: 'Privacy Policy', export: 'Export My Data', logout: 'Sign Out',
    delete: 'Delete Account', deleteTitle: 'Delete Account', deleteMsg: 'This is irreversible. All your memories and data will be permanently deleted.',
    cancel: 'Cancel', confirmDelete: 'Delete', exportTitle: 'Export Data', exporting: 'Exporting...',
    exportFail: 'Export failed. Check connection.', deleteFail: 'Delete failed. Check connection.',
    emergency: 'Emergency Support', emergencyFail: 'Cannot open link. Try your browser.',
    help: 'Help', about: 'About', aiStats: 'AI Statistics',
    modelsActive: 'Active Models', memoriesStored: 'Memories Stored', dailyRequests: 'Daily Requests', latency: 'Avg Latency',
  },
};

const MenuButton = ({ Icon, label, onPress, isDark, color, loading }: any) => (
  <TouchableOpacity style={[s.btn, isDark && { backgroundColor: '#2A2A2A' }, color === 'danger' && s.dangerBtn, color === 'outline' && s.outlineBtn]} onPress={onPress} disabled={loading}>
    {loading ? <ActivityIndicator size="small" color={color === 'danger' ? '#EF4444' : isDark ? '#D8B4FE' : '#6B21A8'} /> : (
      <>
        <Icon size={16} stroke={color === 'danger' ? '#EF4444' : isDark ? '#D8B4FE' : '#FFF'} />
        <Text style={[s.btnText, { color: color === 'danger' ? '#EF4444' : color === 'outline' ? (isDark ? '#D8B4FE' : '#6B21A8') : (isDark ? '#1A1A1A' : '#FFF') }]}>{label}</Text>
      </>
    )}
  </TouchableOpacity>
);

export default function Settings() {
  const { tier, calmMode, toggleCalmMode, lang, toggleLang, theme, toggleTheme, bondLevel, logout: storeLogout } = useTwinStore();
  const t = TEXTS[lang] || TEXTS['ar'];
  const isDark = theme === 'dark';
  const [exporting, setExporting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const aiStats = useMemo(() => ({ models: 8, memories: Math.floor(bondLevel * 10), daily: 87, latency: '560ms' }), [bondLevel]);

  const logout = async () => {
    setLoggingOut(true);
    try {
      await removeToken();
      storeLogout();
      router.replace('/login');
    } catch {
      Alert.alert('Error', 'Logout failed');
    } finally {
      setLoggingOut(false);
    }
  };

  const handleDeleteAccount = () => Alert.alert(t.deleteTitle, t.deleteMsg, [
    { text: t.cancel, style: 'cancel' },
    { text: t.confirmDelete, style: 'destructive', onPress: async () => {
      setDeleting(true);
      try {
        await deleteAccount();
        await removeToken();
        storeLogout();
        router.replace('/login');
      } catch {
        Alert.alert(t.deleteTitle, t.deleteFail);
      } finally {
        setDeleting(false);
      }
    }}
  ]);

  const handleExport = async () => {
    setExporting(true);
    try {
      const data = await exportData();
      await Share.share({ message: JSON.stringify(data, null, 2), title: t.exportTitle });
    } catch {
      Alert.alert(t.exportTitle, t.exportFail);
    } finally {
      setExporting(false);
    }
  };

  const handleEmergency = async () => {
    const url = 'https://findahelpline.com';
    const supported = await Linking.canOpenURL(url);
    if (supported) await Linking.openURL(url);
    else Alert.alert('Error', t.emergencyFail);
  };

  const menuItems = [
    { icon: Crown, label: t.upgrade, onPress: () => router.push('/subscription' as Href) },
    { icon: HelpCircle, label: t.help, onPress: () => router.push('/help' as Href) },
    { icon: Info, label: t.about, onPress: () => router.push('/about' as Href) },
    { icon: Shield, label: t.privacy, onPress: () => router.push('/privacy' as Href) },
  ];

  return (
    <SafeAreaView style={[s.safe, isDark && { backgroundColor: '#1A1A1A' }]}>
      <Header />
      <ScrollView style={s.container} contentContainerStyle={{ paddingBottom: 40 }}>
        <View style={s.content}>
          <View style={[s.tierBadge, isDark && { backgroundColor: '#2A2A2A', borderColor: '#444' }]}>
            <Crown size={14} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
            <Text style={[s.tierText, isDark && { color: '#D8B4FE' }]}> {t.tier}: {tier}</Text>
          </View>

          <View style={[s.row, isDark && { backgroundColor: '#2A2A2A', borderColor: '#444' }]}>
            <View style={s.rowLeft}>
              {theme === 'dark' ? <Moon size={18} stroke="#D8B4FE" /> : <Sun size={18} stroke="#6B21A8" />}
              <Text style={[s.label, isDark && { color: '#FFF' }]}>{t.theme}</Text>
            </View>
            <Switch value={theme === 'dark'} onValueChange={toggleTheme} trackColor={{ false: '#DDD', true: '#6B21A8' }} thumbColor={theme === 'dark' ? '#FFF' : '#F4F4F4'} />
          </View>

          <View style={[s.row, isDark && { backgroundColor: '#2A2A2A', borderColor: '#444' }]}>
            <View style={s.rowLeft}>
              <HeartPulse size={18} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
              <Text style={[s.label, isDark && { color: '#FFF' }]}>{t.calm}</Text>
            </View>
            <Switch value={calmMode} onValueChange={toggleCalmMode} trackColor={{ false: '#DDD', true: '#6B21A8' }} thumbColor={calmMode ? '#FFF' : '#F4F4F4'} />
          </View>

          <View style={[s.row, isDark && { backgroundColor: '#2A2A2A', borderColor: '#444' }]}>
            <View style={s.rowLeft}>
              <Globe size={18} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
              <Text style={[s.label, isDark && { color: '#FFF' }]}>{t.lang}</Text>
            </View>
            <TouchableOpacity onPress={toggleLang} style={[s.langBtn, isDark && { backgroundColor: '#D8B4FE' }]}>
              <Text style={[s.langText, isDark && { color: '#1A1A1A' }]}>{lang === 'ar' ? 'AR' : 'EN'}</Text>
            </TouchableOpacity>
          </View>

          {menuItems.map(({ icon, label, onPress }) => (
            <MenuButton key={label} Icon={icon} label={label} onPress={onPress} isDark={isDark} />
          ))}

          <MenuButton Icon={Download} label={t.export} onPress={handleExport} isDark={isDark} loading={exporting} />

          <View style={[s.aiSection, isDark && { backgroundColor: '#2A2A2A', borderColor: '#444' }]}>
            <View style={s.sectionHeader}>
              <BrainCircuit size={18} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
              <Text style={[s.sectionTitle, isDark && { color: '#FFF' }]}>{t.aiStats}</Text>
              <Sparkles size={14} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
            </View>
            <View style={s.statsGrid}>
              {[{ icon: Cpu, val: aiStats.models, label: t.modelsActive }, { icon: Database, val: aiStats.memories, label: t.memoriesStored }, { icon: HardDrive, val: aiStats.daily, label: t.dailyRequests }, { icon: Zap, val: aiStats.latency, label: t.latency }].map((st, i) => (
                <View key={i} style={[s.statCard, isDark && { backgroundColor: '#333' }]}>
                  <st.icon size={18} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
                  <Text style={[s.statValue, isDark && { color: '#FFF' }]}>{st.val}</Text>
                  <Text style={[s.statLabel, isDark && { color: '#CCC' }]}>{st.label}</Text>
                </View>
              ))}
            </View>
          </View>

          <TouchableOpacity style={[s.btn, { backgroundColor: '#FFF3F3', borderColor: '#FFCDD2', borderWidth: 1 }]} onPress={handleEmergency}>
            <Phone size={16} stroke="#EF4444" />
            <Text style={[s.btnText, { color: '#EF4444' }]}>{t.emergency}</Text>
          </TouchableOpacity>

          <MenuButton Icon={LogOut} label={t.logout} onPress={logout} isDark={isDark} color="outline" loading={loggingOut} />
          <MenuButton Icon={Trash2} label={t.delete} onPress={handleDeleteAccount} isDark={isDark} color="danger" loading={deleting} />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1 }, container: { flex: 1 }, content: { padding: 20 },
  tierBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#F3F0FF', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 10, alignSelf: 'flex-start', marginBottom: 8, borderWidth: 1, borderColor: '#E0D9F5' },
  tierText: { color: '#6B21A8', fontWeight: '600', fontSize: 14 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#FFFFFF', padding: 14, borderRadius: 12, borderWidth: 1, borderColor: '#F0F0F0', marginBottom: 8 },
  rowLeft: { flexDirection: 'row', alignItems: 'center', columnGap: 8 },
  label: { color: '#1A1A1A', fontSize: 15, fontWeight: '500' },
  langBtn: { backgroundColor: '#6B21A8', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20 },
  langText: { color: '#FFF', fontWeight: '600', fontSize: 14 },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', columnGap: 8, backgroundColor: '#6B21A8', padding: 14, borderRadius: 12, marginBottom: 8 },
  btnText: { color: '#FFF', fontWeight: '600', fontSize: 15 },
  outlineBtn: { backgroundColor: '#FFFFFF', borderWidth: 1.5, borderColor: '#6B21A8' },
  dangerBtn: { backgroundColor: '#FFF5F5', borderWidth: 1.5, borderColor: '#FFCDD2' },
  aiSection: { backgroundColor: '#FFFFFF', padding: 16, borderRadius: 16, borderWidth: 1, borderColor: '#F0F0F0', marginBottom: 8 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', columnGap: 8, marginBottom: 12 },
  sectionTitle: { color: '#1A1A1A', fontSize: 15, fontWeight: '700', flex: 1 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  statCard: { width: '48%', backgroundColor: '#F8F6F2', padding: 12, borderRadius: 12, alignItems: 'center', rowGap: 4, marginBottom: 8 },
  statValue: { fontSize: 20, fontWeight: '800', color: '#1A1A1A' },
  statLabel: { fontSize: 11, color: '#888', textAlign: 'center' },
});
