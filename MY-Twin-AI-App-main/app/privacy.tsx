import { SafeAreaView, ScrollView, Text, StyleSheet, View } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import Header from '../components/Header';
import { Stack } from 'expo-router';
import {
  Shield, Lock, Brain, UserCheck, Trash2, AlertTriangle,
  Download, Mail, FileText, Cloud, Smartphone, Eye
} from 'lucide-react-native';

export default function Privacy() {
  const { lang, theme } = useTwinStore();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';

  const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#CCC' : '#444';
  const bg = isDark ? '#1A1A1A' : '#F8F6F2';
  const card = isDark ? '#2A2A2A' : '#FFF';
  const border = isDark ? '#444' : '#F0F0F0';
  const primary = isDark ? '#D8B4FE' : '#6B21A8';

  const sections = isAr ? [
    { icon: UserCheck, title: 'بياناتك ملكك 🔒', body: 'نجمع فقط البيانات الضرورية لتشغيل التطبيق: البريد الإلكتروني، الاسم (اختياري)، تفضيلات التوأم، وسجل المحادثات. لا نبيع بياناتك لأي طرف ثالث ولا نستخدمها لأغراض إعلانية بدون موافقتك الصريحة.' },
    { icon: Lock, title: 'أين تُخزّن بياناتك؟ ☁️', body: 'تُخزَّن بياناتك على خوادم Supabase الآمنة في السحابة. نستخدم إجراءات أمان معيارية (TLS, AES-256) لحماية بياناتك، لكننا لا نطبّق تشفيرًا من طرف إلى طرف (E2EE). الوصول إلى البيانات مقيد للأنظمة والخدمات المصرح لها والضرورية لتشغيل المنصة فقط.' },
    { icon: Brain, title: 'كيف تعمل معالجة الذكاء الاصطناعي؟ 🧠', body: 'يستخدم MyTwin نماذج ذكاء اصطناعي متعددة (Gemini، Groq، OpenRouter). قد تُعالج بعض الرسائل على خوادم هذه النماذج وفقًا لسياسات الخصوصية الخاصة بها. لا نتحكم في كيفية معالجة هذه النماذج للبيانات، ونوصي بمراجعة سياساتها.' },
    { icon: Trash2, title: 'الاحتفاظ بالبيانات والحذف 🗑️', body: 'نحتفظ بالبيانات طوال مدة استخدامك للتطبيق. يمكنك طلب حذف حسابك وجميع بياناتك في أي وقت من خلال الإعدادات > حذف الحساب. قد تُحذف البيانات تلقائيًا بعد فترة من عدم النشاط (حسب الباقة).' },
    { icon: Download, title: 'تصدير بياناتك 📤', body: 'لك الحق في تصدير جميع بياناتك بصيغة JSON. يمكنك فعل ذلك من الإعدادات > تصدير بياناتي. سنرسل لك الملف خلال 48 ساعة.' },
    { icon: AlertTriangle, title: 'إخلاء مسؤولية طبي ونفسي 🏥', body: 'MyTwin هو تطبيق رفيق ذكي للأغراض الترفيهية والداعمة فقط. هو ليس طبيباً، ولا معالجاً نفسياً، ولا مستشاراً مالياً، ولا مستشاراً قانونياً. لا يقدم التطبيق تشخيصات أو نصائح طبية أو نفسية أو مالية أو قانونية. إذا كنت تعاني من أزمة، استخدم ميزة "دعم طوارئ نفسي" في الإعدادات أو اتصل بالخدمات المهنية.' },
    { icon: AlertTriangle, title: 'إخلاء مسؤولية الذكاء الاصطناعي 🤖', body: 'الردود التي يولدها الذكاء الاصطناعي قد تكون غير دقيقة أو غير مناسبة أو تحتوي على أخطاء (هلوسة). استخدم التطبيق بوعي ولا تعتمد على ردود التوأم كمصدر وحيد للمعلومات أو الدعم أو القرارات. تحقق دائمًا من المعلومات المهمة من مصادر مستقلة.' },
    { icon: Shield, title: 'خصوصية القاصرين 👶', body: 'التطبيق غير مخصص للأطفال دون سن 16 عامًا. لا نجمع بيانات عن قاصرين عن قصد. إذا كنت ولي أمر وتعتقد أن طفلك استخدم التطبيق، يرجى التواصل معنا لحذف بياناته فورًا.' },
    { icon: Eye, title: 'المحتوى الذي ينشئه المستخدم 📁', body: 'أنت مسؤول عن جميع المحتويات التي ترفعها أو تنشئها داخل التطبيق، بما في ذلك الصور والملفات والنصوص. لا نتحمل مسؤولية أي محتوى ينشئه المستخدمون.' },
    { icon: Smartphone, title: 'خدمات الطرف الثالث 🔗', body: 'يستخدم MyTwin خدمات خارجية تشمل: Supabase (قاعدة بيانات)، Railway (استضافة)، OpenRouter / Groq / Gemini (نماذج ذكاء اصطناعي)، OneSignal (إشعارات)، Edge TTS / ElevenLabs (تحويل نص إلى كلام)، PostHog (تحليلات). لهذه الخدمات سياسات خصوصية خاصة بها نوصي بمراجعتها.' },
    { icon: Mail, title: 'تواصل معنا ✉️', body: 'لأي أسئلة حول الخصوصية أو طلبات البيانات، راسلنا على: support@mytwin.app. سنرد خلال 48 ساعة.' },
  ] : [
    { icon: UserCheck, title: 'Your Data is Yours 🔒', body: 'We collect only data necessary to operate the app: email, name (optional), twin preferences, and chat history. We do not sell your data to third parties or use it for advertising without your explicit consent.' },
    { icon: Lock, title: 'Where is Your Data Stored? ☁️', body: 'Your data is stored on secure Supabase cloud servers. We use standard security measures (TLS, AES-256) to protect your data, but we do not implement end-to-end encryption (E2EE). Access is restricted to authorized systems and services required to operate the platform only.' },
    { icon: Brain, title: 'How AI Processing Works 🧠', body: 'MyTwin uses multiple AI models (Gemini, Groq, OpenRouter). Some messages may be processed on these models servers according to their privacy policies. We do not control how these models handle data; we recommend reviewing their policies.' },
    { icon: Trash2, title: 'Data Retention & Deletion 🗑️', body: 'We retain data as long as you use the app. You can request deletion of your account and all data at any time via Settings > Delete Account. Data may be deleted automatically after a period of inactivity (depending on your plan).' },
    { icon: Download, title: 'Export Your Data 📤', body: 'You have the right to export all your data in JSON format. You can do this from Settings > Export My Data. We will send you the file within 48 hours.' },
    { icon: AlertTriangle, title: 'Medical & Professional Disclaimer 🏥', body: 'MyTwin is an AI companion app for entertainment and supportive purposes only. It is NOT a doctor, therapist, financial advisor, or legal advisor. The app does not provide medical, psychological, financial, or legal diagnoses or advice. If you are in crisis, use the "Emergency Support" feature in Settings or contact professional services.' },
    { icon: AlertTriangle, title: 'AI Disclaimer 🤖', body: 'AI-generated responses may be inaccurate, inappropriate, or contain errors (hallucinations). Use the app mindfully and do not rely solely on twin responses as a source of information, support, or decisions. Always verify important information from independent sources.' },
    { icon: Shield, title: 'Children Privacy 👶', body: 'The app is not intended for children under 16. We do not knowingly collect data from minors. If you are a guardian and believe your child used the app, please contact us immediately to delete their data.' },
    { icon: Eye, title: 'User Generated Content 📁', body: 'You are responsible for all content you upload or create within the app, including images, files, and text. We are not liable for any user-generated content.' },
    { icon: Smartphone, title: 'Third Party Services 🔗', body: 'MyTwin uses external services including: Supabase (database), Railway (hosting), OpenRouter/Groq/Gemini (AI models), OneSignal (notifications), Edge TTS/ElevenLabs (text-to-speech), PostHog (analytics). These services have their own privacy policies which we recommend reviewing.' },
    { icon: Mail, title: 'Contact Us ✉️', body: 'For privacy questions or data requests, email us at: support@mytwin.app. We will respond within 48 hours.' },
  ];

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header />

      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 40 }}>
        <Shield size={48} stroke={primary} style={{ alignSelf: 'center', marginBottom: 16 }} />
        <Text style={[styles.title, { color: txt }]}>{isAr ? 'سياسة الخصوصية' : 'Privacy Policy'}</Text>
        <Text style={[styles.updated, { color: sub }]}>{isAr ? 'آخر تحديث: يونيو 2026' : 'Last updated: June 2026'}</Text>

        {sections.map((section, i) => {
          const Icon = section.icon;
          return (
            <View key={i} style={[styles.card, { backgroundColor: card, borderColor: border }]}>
              <View style={[styles.cardHeader, isAr && { flexDirection: 'row-reverse' }]}>
                <Icon size={22} stroke={primary} />
                <Text style={[styles.cardTitle, { color: txt }]}>{section.title}</Text>
              </View>
              <Text style={[styles.cardBody, { color: sub }]}>{section.body}</Text>
            </View>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  title: { fontSize: 26, fontWeight: '800', textAlign: 'center', marginBottom: 4 },
  updated: { fontSize: 13, textAlign: 'center', marginBottom: 24 },
  card: { padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 14 },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 10 },
  cardTitle: { fontSize: 16, fontWeight: '700', flex: 1 },
  cardBody: { fontSize: 14, lineHeight: 22 },
});
