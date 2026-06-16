import { SafeAreaView, View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking, Image } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { router, Href, Stack } from 'expo-router';
import Constants from 'expo-constants';
import Header from '../components/Header';
import { Info, Heart, Zap, Globe, Mic, Brain, Target, Mail, Shield, FileText, Star, ExternalLink, Building2 } from 'lucide-react-native';

const APP_ICON = require('../assets/icon.png');

export default function About() {
  const { lang, theme } = useTwinStore();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';
  const version = Constants.expoConfig?.version || '1.0.0';
  const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#CCC' : '#444';
  const bg = isDark ? '#1A1A1A' : '#F8F6F2';
  const card = isDark ? '#2A2A2A' : '#FFF';
  const border = isDark ? '#444' : '#F0F0F0';
  const primary = isDark ? '#D8B4FE' : '#6B21A8';
  const companyURL = 'https://sirmarket7-cloud.github.io/Soul-Sync/index.html#product';

  const features = [
    { icon: Brain, label_ar: 'ذاكرة طويلة المدى', label_en: 'Long-Term Memory' },
    { icon: Globe, label_ar: '19 لهجة', label_en: '19 Dialects' },
    { icon: Mic, label_ar: 'صوت طبيعي', label_en: 'Natural Voice' },
    { icon: Heart, label_ar: 'ذكاء عاطفي', label_en: 'Emotional Intelligence' },
    { icon: Target, label_ar: 'نمو شخصي', label_en: 'Personal Growth' },
  ];

  const poweredBy = ['Gemini', 'Groq', 'OpenRouter', 'Supabase', 'Railway'];

  return (
    <SafeAreaView style={[s.safe, { backgroundColor: bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header />
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 40 }}>
        <Image source={APP_ICON} style={s.logo} />
        <Text style={[s.title, { color: txt }]}>MyTwin</Text>
        <Text style={[s.version, { color: sub }]}>v{version}</Text>

        <Text style={[s.description, { color: sub }]}>
          {isAr ? 'رفيق ذكي مصمم لبناء علاقة طويلة المدى مع المستخدم...' : 'AI Companion designed to build long-term...'}
        </Text>

        <Text style={[s.sectionTitle, { color: txt }]}>{isAr ? 'الميزات' : 'Features'}</Text>
        <View style={s.featuresGrid}>
          {features.map((f, i) => {
            const Icon = f.icon;
            return (
              <View key={i} style={[s.featureCard, { backgroundColor: card, borderColor: border }]}>
                <Icon size={28} stroke={primary} />
                <Text style={[s.featureLabel, { color: txt }]}>{isAr ? f.label_ar : f.label_en}</Text>
              </View>
            );
          })}
        </View>

        <Text style={[s.sectionTitle, { color: txt }]}>{isAr ? 'مدعوم من' : 'Powered By'}</Text>
        <View style={s.poweredRow}>
          {poweredBy.map((tech) => (
            <View key={tech} style={[s.techBadge, { backgroundColor: primary + '20' }]}>
              <Text style={[s.techText, { color: primary }]}>{tech}</Text>
            </View>
          ))}
        </View>

        <View style={[s.card, { backgroundColor: card, borderColor: border }]}>
          <Text style={[s.cardTitle, { color: txt }]}>{isAr ? 'من نحن' : 'Who We Are'}</Text>
          <Text style={[s.cardBody, { color: sub }]}>
            {isAr ? 'Soul Sync Ltd. هي شركة ناشئة...' : 'Soul Sync Ltd. is an AI startup...'}
          </Text>
          <TouchableOpacity style={[s.companyBtn, { backgroundColor: primary + '15', borderColor: primary }]} onPress={() => Linking.openURL(companyURL)}>
            <Building2 size={20} stroke={primary} />
            <Text style={[s.companyBtnText, { color: primary }]}>{isAr ? 'زيارة موقع الشركة' : 'Visit Company Site'}</Text>
            <ExternalLink size={16} stroke={primary} />
          </TouchableOpacity>
        </View>

        <Text style={[s.sectionTitle, { color: txt }]}>{isAr ? 'تواصل معنا' : 'Contact Us'}</Text>
        <View style={[s.card, { backgroundColor: card, borderColor: border }]}>
          <TouchableOpacity style={s.linkRow} onPress={() => Linking.openURL('mailto:support@mytwin.app')}>
            <Mail size={18} stroke={primary} />
            <Text style={[s.linkText, { color: txt }]}>support@mytwin.app</Text>
          </TouchableOpacity>
        </View>

        <Text style={[s.sectionTitle, { color: txt }]}>{isAr ? 'قانوني' : 'Legal'}</Text>
        <View style={[s.card, { backgroundColor: card, borderColor: border }]}>
          <TouchableOpacity style={s.linkRow} onPress={() => router.push('/privacy' as Href)}>
            <Shield size={18} stroke={primary} />
            <Text style={[s.linkText, { color: txt }]}>{isAr ? 'سياسة الخصوصية' : 'Privacy Policy'}</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={[s.rateBtn, { backgroundColor: primary }]} onPress={() => Linking.openURL('https://mytwin.app/rate')}>
          <Star size={18} stroke="#FFF" />
          <Text style={s.rateBtnText}>{isAr ? 'قيّم MyTwin' : 'Rate MyTwin'}</Text>
        </TouchableOpacity>

        <View style={[s.footer, isDark && { borderTopColor: '#444' }]}>
          <Heart size={14} stroke={primary} />
          <Text style={[s.footerText, { color: primary }]}>Soul Sync Ltd. © 2026</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1 },
  logo: { width: 90, height: 90, borderRadius: 22, alignSelf: 'center', marginBottom: 10 },
  title: { fontSize: 30, fontWeight: '800', textAlign: 'center', marginBottom: 2 },
  version: { fontSize: 14, textAlign: 'center', marginBottom: 16 },
  description: { fontSize: 15, lineHeight: 24, textAlign: 'center', marginBottom: 28, paddingHorizontal: 10 },
  sectionTitle: { fontSize: 18, fontWeight: '700', marginBottom: 12, marginTop: 8 },
  featuresGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', marginBottom: 20 },
  featureCard: { width: '30%', alignItems: 'center', padding: 14, borderRadius: 14, borderWidth: 1, marginBottom: 10 },
  featureLabel: { fontSize: 12, fontWeight: '600', textAlign: 'center', marginTop: 8 },
  poweredRow: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', gap: 8, marginBottom: 24 },
  techBadge: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20 },
  techText: { fontSize: 13, fontWeight: '600' },
  card: { padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 14 },
  cardTitle: { fontSize: 16, fontWeight: '700', marginBottom: 8 },
  cardBody: { fontSize: 14, lineHeight: 22, marginBottom: 12 },
  companyBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 12, borderRadius: 12, borderWidth: 1, marginTop: 8 },
  companyBtnText: { fontSize: 14, fontWeight: '600' },
  linkRow: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 8 },
  linkText: { fontSize: 14 },
  rateBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 14, borderRadius: 14, marginTop: 16 },
  rateBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  footer: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 6, marginTop: 24, paddingTop: 16, borderTopWidth: 1, borderTopColor: '#E0D9F5' },
  footerText: { fontSize: 13, fontWeight: '600' },
});
