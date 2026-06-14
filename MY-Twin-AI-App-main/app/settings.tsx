import { SafeAreaView, View, Text, TouchableOpacity, StyleSheet, ScrollView, Switch, Alert, Linking, Share, ActivityIndicator } from 'react-native';
import { router, Href } from 'expo-router';
import { useState } from 'react';
import { useTwinStore } from '../store/useTwinStore';
import { supabase } from '../lib/supabase';
import { API } from '../lib/api';
import {
  Moon, Sun, Globe, Crown, Target, HeartPulse, History,
  Shield, Download, LogOut, Trash2, Phone, Sparkles, Zap, Info, ExternalLink, Building2,
  HelpCircle, MessageCircle
} from 'lucide-react-native';

const TEXTS = {
  ar: {
    title: 'الإعدادات', tier: 'الخطة الحالية', calm: 'وضع الهدوء', lang: 'اللغة', theme: 'المظهر',
    upgrade: 'ترقية الخطة', goals: 'أهدافي', emergency: 'دعم طوارئ نفسي', mood: 'لوحة المشاعر',
    timeline: 'خط الذكريات', privacy: 'سياسة الخصوصية', export: 'تصدير بياناتي', logout: 'تسجيل الخروج',
    delete: 'حذف الحساب', deleteTitle: 'حذف نهائي', deleteMsg: 'لا يمكن التراجع. سيتم حذف جميع ذكرياتك وبياناتك نهائياً.',
    cancel: 'إلغاء', confirmDelete: 'حذف', exportTitle: 'تصدير البيانات', exporting: 'جاري التصدير...',
    exportFail: 'فشل تصدير البيانات.', deleteFail: 'فشل الحذف.',
    about: 'حول التطبيق', aboutDesc: 'MyTwin — رفيق ذكي مصمم لبناء علاقة طويلة المدى.',
    visitSite: 'زيارة موقع الشركة', company: 'Soul Sync Ltd.',
    help: 'المساعدة', faq: 'الأسئلة الشائعة', contact: 'اتصل بنا',
  },
  en: {
    title: 'Settings', tier: 'Current Plan', calm: 'Calm Mode', lang: 'Language', theme: 'Theme',
    upgrade: 'Upgrade Plan', goals: 'My Goals', emergency: 'Emergency Support', mood: 'Mood Board',
    timeline: 'Memory Timeline', privacy: 'Privacy Policy', export: 'Export My Data', logout: 'Sign Out',
    delete: 'Delete Account', deleteTitle: 'Delete Account', deleteMsg: 'This is irreversible.',
    cancel: 'Cancel', confirmDelete: 'Delete', exportTitle: 'Export Data', exporting: 'Exporting...',
    exportFail: 'Export failed.', deleteFail: 'Delete failed.',
    about: 'About', aboutDesc: 'MyTwin — Your Intelligent Digital Companion.',
    visitSite: 'Visit Company Site', company: 'Soul Sync Ltd.',
    help: 'Help', faq: 'FAQ', contact: 'Contact Us',
  },
};

const FAQS = [
  { q_ar: 'كيف أغير اسم التوأم؟', a_ar: 'من الإعدادات > تخصيص التوأم', q_en: 'How to change twin name?', a_en: 'Settings > Customize Twin' },
  { q_ar: 'كيف أشارك كود الإحالة؟', a_ar: 'من القائمة > الإحالة', q_en: 'How to share referral?', a_en: 'Menu > Referral' },
  { q_ar: 'هل محادثاتي خاصة؟', a_ar: 'نعم، جميع المحادثات مشفرة.', q_en: 'Are my chats private?', a_en: 'Yes, all chats are encrypted.' },
  { q_ar: 'كيف أستمع لرد التوأم؟', a_ar: 'اضغط على أيقونة الصوت في الأعلى.', q_en: 'How to hear twin reply?', a_en: 'Press the volume icon on top.' },
  { q_ar: 'كيف أرفع صورة؟', a_ar: 'اضغط على + ثم اختر الكاميرا أو المعرض.', q_en: 'How to upload an image?', a_en: 'Press + then choose camera or gallery.' },
  { q_ar: 'ما الباقات المتاحة؟', a_ar: 'Free, Plus, Premium, Pro, Yearly', q_en: 'What plans are available?', a_en: 'Free, Plus, Premium, Pro, Yearly' },
];

export default function Settings() {
  const { tier, calmMode, toggleCalmMode, lang, toggleLang, theme, toggleTheme, logout: storeLogout } = useTwinStore();
  const t = TEXTS[lang] || TEXTS['ar'];
  const isDark = theme === 'dark';
  const [exporting, setExporting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const logout = async () => { setLoggingOut(true); try { await supabase.auth.signOut(); storeLogout(); router.replace('/login'); } catch { Alert.alert('Error', 'Logout failed'); } finally { setLoggingOut(false); } };
  const deleteAccount = () => { Alert.alert(t.deleteTitle, t.deleteMsg, [{ text: t.cancel, style: 'cancel' }, { text: t.confirmDelete, style: 'destructive', onPress: async () => { setDeleting(true); try { await API.delete('/api/account'); await supabase.auth.signOut(); storeLogout(); router.replace('/login'); } catch { Alert.alert(t.deleteTitle, t.deleteFail); } finally { setDeleting(false); } } }]); };
  const handleExport = async () => { setExporting(true); try { const { data } = await API.get('/api/me/export'); await Share.share({ message: JSON.stringify(data, null, 2), title: t.exportTitle }); } catch { Alert.alert(t.exportTitle, t.exportFail); } finally { setExporting(false); } };

  return (
    <SafeAreaView style={[styles.safe, isDark && { backgroundColor: '#1A1A1A' }]}>
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={[styles.title, isDark && { color: '#FFF' }]}>{t.title}</Text>

          <View style={[styles.row, isDark && { backgroundColor: '#2A2A2A', borderColor: '#444' }]}>
            <View style={styles.rowLeft}><Crown size={18} stroke={isDark ? '#D8B4FE' : '#6B21A8'} /><Text style={[styles.label, isDark && { color: '#FFF' }]}> {t.tier}: {tier}</Text></View>
          </View>
          <View style={[styles.row, isDark && { backgroundColor: '#2A2A2A', borderColor: '#444' }]}>
            <View style={styles.rowLeft}>{theme === 'dark' ? <Moon size={18} stroke="#D8B4FE" /> : <Sun size={18} stroke="#6B21A8" />}<Text style={[styles.label, isDark && { color: '#FFF' }]}>{t.theme}</Text></View>
            <Switch value={theme === 'dark'} onValueChange={toggleTheme} trackColor={{ false: '#DDD', true: '#6B21A8' }} />
          </View>
          <View style={[styles.row, isDark && { backgroundColor: '#2A2A2A', borderColor: '#444' }]}>
            <View style={styles.rowLeft}><Globe size={18} stroke={isDark ? '#D8B4FE' : '#6B21A8'} /><Text style={[styles.label, isDark && { color: '#FFF' }]}>{t.lang}</Text></View>
            <TouchableOpacity onPress={toggleLang} style={[styles.langBtn, isDark && { backgroundColor: '#D8B4FE' }]}><Text style={[styles.langText, isDark && { color: '#1A1A1A' }]}>{lang === 'ar' ? 'AR' : 'EN'}</Text></TouchableOpacity>
          </View>

          {[{ icon: Crown, label: t.upgrade, action: () => router.push('/subscription' as Href) }, { icon: Target, label: t.goals, action: () => router.push('/relationship' as Href) }, { icon: History, label: t.timeline, action: () => router.push('/memories' as Href) }].map(({ icon: Icon, label, action }) => (
            <TouchableOpacity key={label} style={[styles.btn, isDark && { backgroundColor: '#2A2A2A' }]} onPress={action}><Icon size={16} stroke={isDark ? '#D8B4FE' : '#FFF'} /><Text style={[styles.btnText, { color: isDark ? '#D8B4FE' : '#FFF' }]}>{label}</Text></TouchableOpacity>
          ))}

          <View style={[styles.aboutSection, isDark && { backgroundColor: '#2A2A2A', borderColor: '#444' }]}>
            <View style={styles.sectionHeader}><Info size={18} stroke={isDark ? '#D8B4FE' : '#6B21A8'} /><Text style={[styles.sectionTitle, isDark && { color: '#FFF' }]}>{t.about}</Text></View>
            <Text style={[styles.aboutDesc, { color: isDark ? '#CCC' : '#666' }]}>{t.aboutDesc}</Text>
            <View style={styles.poweredRow}>
              {['Gemini', 'Groq', 'OpenRouter', 'Supabase', 'Railway'].map(tech => (
                <View key={tech} style={[styles.techBadge, { backgroundColor: (isDark ? '#D8B4FE' : '#6B21A8') + '20' }]}><Text style={[styles.techText, { color: isDark ? '#D8B4FE' : '#6B21A8' }]}>{tech}</Text></View>
              ))}
            </View>
            <TouchableOpacity style={[styles.companyBtn, { borderColor: isDark ? '#D8B4FE' : '#6B21A8' }]} onPress={() => Linking.openURL('https://sirmarket7-cloud.github.io/Soul-Sync/index.html#product')}>
              <Building2 size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
              <Text style={[styles.companyBtnText, { color: isDark ? '#D8B4FE' : '#6B21A8' }]}>{t.visitSite}</Text>
              <ExternalLink size={14} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
            </TouchableOpacity>
          </View>

          <View style={[styles.aboutSection, isDark && { backgroundColor: '#2A2A2A', borderColor: '#444' }]}>
            <View style={styles.sectionHeader}><HelpCircle size={18} stroke={isDark ? '#D8B4FE' : '#6B21A8'} /><Text style={[styles.sectionTitle, isDark && { color: '#FFF' }]}>{t.help}</Text></View>
            <Text style={[styles.sectionTitle, isDark && { color: '#FFF' }]}>{t.faq}</Text>
            {FAQS.map((faq, i) => (
              <View key={i} style={[styles.faqCard, isDark && { backgroundColor: '#333', borderColor: '#444' }]}>
                <MessageCircle size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
                <View style={{ flex: 1 }}>
                  <Text style={[styles.faqQ, isDark && { color: '#FFF' }]}>{lang === 'ar' ? faq.q_ar : faq.q_en}</Text>
                  <Text style={[styles.faqA, isDark && { color: '#CCC' }]}>{lang === 'ar' ? faq.a_ar : faq.a_en}</Text>
                </View>
              </View>
            ))}
            <Text style={[styles.sectionTitle, isDark && { color: '#FFF' }]}>{t.contact}</Text>
            <View style={[styles.contactCard, isDark && { backgroundColor: '#333', borderColor: '#444' }]}>
              <Phone size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} />
              <Text style={[styles.contactText, isDark && { color: '#CCC' }]}>support@mytwin.app</Text>
            </View>
          </View>

          <TouchableOpacity style={[styles.btn, isDark && { backgroundColor: '#2A2A2A' }]} onPress={handleExport}><Download size={16} stroke={isDark ? '#D8B4FE' : '#FFF'} /><Text style={[styles.btnText, { color: isDark ? '#D8B4FE' : '#FFF' }]}>{t.export} {exporting && '...'}</Text></TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.outlineBtn]} onPress={logout}><LogOut size={16} stroke={isDark ? '#D8B4FE' : '#6B21A8'} /><Text style={[styles.btnText, { color: isDark ? '#D8B4FE' : '#6B21A8' }]}>{t.logout}</Text></TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.dangerBtn]} onPress={deleteAccount}><Trash2 size={16} stroke="#EF4444" /><Text style={[styles.btnText, { color: '#EF4444' }]}>{t.delete}</Text></TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 }, container: { flex: 1, backgroundColor: '#F8F6F2' }, content: { padding: 20, marginBottom: 10 },
  title: { fontSize: 24, fontWeight: '800', color: '#1A1A1A', marginBottom: 12 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#FFFFFF', padding: 14, borderRadius: 12, borderWidth: 1, borderColor: '#F0F0F0', marginBottom: 8 },
  rowLeft: { flexDirection: 'row', alignItems: 'center', columnGap: 8 },
  label: { color: '#1A1A1A', fontSize: 15, fontWeight: '500' },
  langBtn: { backgroundColor: '#6B21A8', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20 },
  langText: { color: '#FFF', fontWeight: '600', fontSize: 14 },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', columnGap: 8, backgroundColor: '#6B21A8', padding: 14, borderRadius: 12, marginBottom: 8 },
  btnText: { color: '#FFF', fontWeight: '600', fontSize: 15 },
  outlineBtn: { backgroundColor: '#FFFFFF', borderWidth: 1.5, borderColor: '#6B21A8' },
  dangerBtn: { backgroundColor: '#FFF5F5', borderWidth: 1.5, borderColor: '#FFCDD2' },
  aboutSection: { backgroundColor: '#FFFFFF', padding: 16, borderRadius: 16, borderWidth: 1, borderColor: '#F0F0F0', marginBottom: 8 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', columnGap: 8, marginBottom: 8 },
  sectionTitle: { color: '#1A1A1A', fontSize: 15, fontWeight: '700', flex: 1 },
  aboutDesc: { fontSize: 13, lineHeight: 20, marginBottom: 10 },
  poweredRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginBottom: 10 },
  techBadge: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 20 },
  techText: { fontSize: 11, fontWeight: '600' },
  companyBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, padding: 10, borderRadius: 10, borderWidth: 1 },
  companyBtnText: { fontSize: 13, fontWeight: '600' },
  faqCard: { flexDirection: 'row', alignItems: 'flex-start', gap: 12, padding: 14, backgroundColor: '#FFF', borderRadius: 12, marginBottom: 8, borderWidth: 1, borderColor: '#F0F0F0' },
  faqQ: { fontSize: 15, fontWeight: '600', color: '#1A1A1A', marginBottom: 4 },
  faqA: { fontSize: 14, color: '#666' },
  contactCard: { flexDirection: 'row', alignItems: 'center', gap: 10, padding: 14, backgroundColor: '#FFF', borderRadius: 12, borderWidth: 1, borderColor: '#F0F0F0' },
  contactText: { fontSize: 15, color: '#1A1A1A' },
});
