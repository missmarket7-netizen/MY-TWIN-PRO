import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Linking } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../store/useTwinStore';
import { Stack } from 'expo-router';
import Header from '../components/Header';
import { Mail, MessageCircle, ExternalLink } from 'lucide-react-native';

export default function HelpScreen() {
  const { theme, lang } = useTwinStore();
  const isDark = theme === 'dark';
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;

  const colors = {
    bg: isDark ? '#1A1A1A' : '#F8F6F2',
    card: isDark ? '#2A2A2A' : '#FFFFFF',
    text: isDark ? '#FFFFFF' : '#1A1A1A',
    subtext: isDark ? '#CCCCCC' : '#666666',
    primary: '#7C3AED',
    border: isDark ? '#333333' : '#E5E5E5',
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header title={t('مساعدة', 'Help')} />

      <ScrollView style={styles.content} contentContainerStyle={{ paddingBottom: 40 }}>
        {/* الأسئلة الشائعة */}
        <Text style={[styles.sectionTitle, { color: colors.text }]}>
          {t('الأسئلة الشائعة', 'Frequently Asked Questions')}
        </Text>

        {[
          {
            q: t('كيف أتحدث مع توأمي؟', 'How do I chat with my Twin?'),
            a: t('اذهب إلى المحادثة من القائمة الرئيسية وابدأ الكتابة.', 'Go to Chat from the main menu and start typing.'),
          },
          {
            q: t('ما الأدوات المتاحة؟', 'What tools are available?'),
            a: t('اضغط على زر + في المحادثة لتظهر الأدوات: الطقس، اليوتيوب، الأخبار، العملات، البحث، وتوليد الصور.', 'Tap the + button in chat to see tools: weather, YouTube, news, currency, search, and image generation.'),
          },
          {
            q: t('كيف تتكون الرابطة؟', 'How is the bond built?'),
            a: t('كلما تحدثت مع توأمك أكثر، كلما زادت الرابطة وفهم التوأم لك.', 'The more you talk to your Twin, the stronger the bond and understanding.'),
          },
          {
            q: t('هل بياناتي آمنة؟', 'Is my data safe?'),
            a: t('نعم، جميع بياناتك مشفرة ولا نشاركها مع أي طرف ثالث.', 'Yes, all your data is encrypted and we do not share it.'),
          },
        ].map((item, i) => (
          <View key={i} style={[styles.faqCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
            <Text style={[styles.faqQuestion, { color: colors.text }]}>{item.q}</Text>
            <Text style={[styles.faqAnswer, { color: colors.subtext }]}>{item.a}</Text>
          </View>
        ))}

        {/* التواصل */}
        <Text style={[styles.sectionTitle, { color: colors.text, marginTop: 24 }]}>
          {t('تواصل معنا', 'Contact Us')}
        </Text>

        <TouchableOpacity 
          style={[styles.contactBtn, { backgroundColor: colors.card, borderColor: colors.border }]}
          onPress={() => Linking.openURL('mailto:support@mytwin.app')}
        >
          <Mail size={20} stroke={colors.primary} />
          <Text style={[styles.contactText, { color: colors.text }]}>support@mytwin.app</Text>
          <ExternalLink size={16} stroke={colors.subtext} />
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.contactBtn, { backgroundColor: colors.card, borderColor: colors.border }]}
          onPress={() => Linking.openURL('https://t.me/MyTwinSupport')}
        >
          <MessageCircle size={20} stroke={colors.primary} />
          <Text style={[styles.contactText, { color: colors.text }]}>Telegram</Text>
          <ExternalLink size={16} stroke={colors.subtext} />
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { flex: 1, paddingHorizontal: 20, paddingTop: 20 },
  sectionTitle: { fontSize: 20, fontWeight: '700', marginBottom: 16 },
  faqCard: { padding: 16, borderRadius: 12, borderWidth: 1, marginBottom: 12 },
  faqQuestion: { fontSize: 15, fontWeight: '600', marginBottom: 8 },
  faqAnswer: { fontSize: 14, lineHeight: 22 },
  contactBtn: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16, borderRadius: 12, borderWidth: 1, marginBottom: 10 },
  contactText: { fontSize: 15, fontWeight: '500', flex: 1 },
});
