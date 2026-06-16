import { SafeAreaView, ScrollView, Text, StyleSheet, View } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import Header from '../components/Header';
import { Stack } from 'expo-router';
import {
  FileText, AlertTriangle, Shield, UserCheck, Ban, CreditCard,
  RotateCcw, MessageSquare, Image, RefreshCw, XCircle, Mail
} from 'lucide-react-native';

export default function Terms() {
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
    { icon: FileText, title: 'قبول الشروط 📜', body: 'باستخدامك تطبيق MyTwin، فإنك توافق على الالتزام بهذه الشروط والأحكام. إذا كنت لا توافق على أي بند، يرجى عدم استخدام التطبيق.' },
    { icon: UserCheck, title: 'استخدام التطبيق ✅', body: 'أنت مسؤول عن استخدامك للتطبيق وعن جميع الأنشطة التي تتم تحت حسابك. يجب ألا تستخدم التطبيق لأي غرض غير قانوني أو محظور بموجب هذه الشروط.' },
    { icon: Shield, title: 'الملكية الفكرية ©️', body: 'جميع المحتويات والبرمجيات والتصاميم والأيقونات في التطبيق هي ملك لشركة Soul Sync Ltd. ومحمية بموجب قوانين الملكية الفكرية الدولية.' },
    { icon: Ban, title: 'القيود 🚫', body: 'لا يجوز لك: نسخ، تعديل، توزيع، بيع، أو تأجير أي جزء من التطبيق؛ استخدام التطبيق لأي غرض غير قانوني أو ضار؛ محاولة الوصول غير المصرح به إلى أنظمتنا أو اختراقها.' },
    { icon: AlertTriangle, title: 'تحديد المسؤولية ⚠️', body: 'يتم توفير التطبيق "كما هو" دون أي ضمانات صريحة أو ضمنية. لا تتحمل Soul Sync Ltd. أي مسؤولية عن أي أضرار مباشرة أو غير مباشرة ناتجة عن استخدام التطبيق أو عدم القدرة على استخدامه. أنت وحدك المسؤول عن تفاعلاتك مع التوأم الرقمي.' },
    { icon: AlertTriangle, title: 'إخلاء مسؤولية طبي وقانوني 🏥', body: 'MyTwin ليس طبيباً أو معالجاً نفسياً أو مستشاراً مالياً أو قانونياً. لا تقدم المنصة أي تشخيصات أو نصائح طبية أو نفسية أو مالية أو قانونية. استشر المختصين المؤهلين دائمًا.' },
    { icon: AlertTriangle, title: 'تنبيه الذكاء الاصطناعي 🤖', body: 'الردود التي يولدها الذكاء الاصطناعي قد تحتوي على أخطاء أو معلومات غير دقيقة أو مضللة (هلوسة). يجب التحقق من المعلومات المهمة بشكل مستقل. لا نضمن دقة أو اكتمال أي رد.' },
    { icon: CreditCard, title: 'الاشتراكات والمدفوعات 💳', body: 'نقدم باقات اشتراك متنوعة (مجانية، Plus، Premium، Pro، Yearly). يتم تجديد الاشتراكات تلقائيًا ما لم يتم الإلغاء قبل 24 ساعة من موعد التجديد. يمكنك إلغاء الاشتراك في أي وقت من إعدادات متجر التطبيقات. لا نقدم استردادًا للمدة المتبقية من الاشتراك الملغي.' },
    { icon: RotateCcw, title: 'سياسة الاسترداد ↩️', body: 'لا نقدم استردادًا للمدفوعات إلا في الحالات التي يقتضيها القانون المحلي. يمكنك طلب مراجعة حالة خاصة عبر البريد الإلكتروني.' },
    { icon: MessageSquare, title: 'المحتوى الذي ينشئه المستخدم 📁', body: 'أنت تحتفظ بجميع حقوق المحتوى الذي تنشئه أو ترفعه داخل التطبيق (نصوص، صور، ملفات). أنت تمنح Soul Sync Ltd. ترخيصًا غير حصري لمعالجة هذا المحتوى لتقديم الخدمة فقط. أنت مسؤول عن قانونية المحتوى الذي ترفعه.' },
    { icon: Image, title: 'الصور والملفات 🖼️', body: 'عند رفع صور أو ملفات، أنت تقر بأنك تملك الحقوق اللازمة لذلك. لا نتحمل مسؤولية أي انتهاك لحقوق الملكية الفكرية من قبل المستخدمين.' },
    { icon: RefreshCw, title: 'تعديل الشروط 📝', body: 'قد نُعدل هذه الشروط من وقت لآخر. سيتم إخطارك بالتغييرات المهمة عبر البريد الإلكتروني أو إشعار داخل التطبيق. استمرار استخدامك للتطبيق بعد التعديلات يعني قبولك لها.' },
    { icon: XCircle, title: 'إنهاء الخدمة 🛑', body: 'نحتفظ بالحق في تعليق أو إنهاء حسابك في حال مخالفة هذه الشروط أو إساءة استخدام الخدمة أو الانخراط في سلوك ضار. سيتم إخطارك بسبب الإنهاء عند الإمكان.' },
    { icon: Mail, title: 'تواصل معنا ✉️', body: 'لأي استفسارات حول الشروط والأحكام: support@mytwin.app' },
  ] : [
    { icon: FileText, title: 'Acceptance of Terms 📜', body: 'By using MyTwin, you agree to be bound by these terms and conditions. If you disagree with any part, please do not use the app.' },
    { icon: UserCheck, title: 'Use of the App ✅', body: 'You are responsible for your use of the app and all activities under your account. You must not use the app for any illegal or prohibited purpose.' },
    { icon: Shield, title: 'Intellectual Property ©️', body: 'All content, software, designs, and icons in the app are owned by Soul Sync Ltd. and protected by international intellectual property laws.' },
    { icon: Ban, title: 'Restrictions 🚫', body: 'You may not: copy, modify, distribute, sell, or lease any part of the app; use the app for any illegal or harmful purpose; attempt unauthorized access to or hack our systems.' },
    { icon: AlertTriangle, title: 'Limitation of Liability ⚠️', body: 'The app is provided "as is" without any express or implied warranties. Soul Sync Ltd. is not liable for any direct or indirect damages arising from the use or inability to use the app. You are solely responsible for your interactions with the digital twin.' },
    { icon: AlertTriangle, title: 'Medical & Professional Disclaimer 🏥', body: 'MyTwin is NOT a doctor, therapist, financial advisor, or legal advisor. The platform does not provide medical, psychological, financial, or legal diagnoses or advice. Always consult qualified professionals.' },
    { icon: AlertTriangle, title: 'AI Disclaimer 🤖', body: 'AI-generated responses may contain errors, inaccuracies, or misleading information (hallucinations). Important information should be independently verified. We do not guarantee the accuracy or completeness of any response.' },
    { icon: CreditCard, title: 'Subscriptions & Payments 💳', body: 'We offer various subscription plans (Free, Plus, Premium, Pro, Yearly). Subscriptions auto-renew unless cancelled at least 24 hours before the renewal date. You can cancel anytime from your app store settings. We do not provide refunds for unused portions of cancelled subscriptions.' },
    { icon: RotateCcw, title: 'Refund Policy ↩️', body: 'We do not offer refunds except where required by local law. You may request a special case review via email.' },
    { icon: MessageSquare, title: 'User Generated Content 📁', body: 'You retain all rights to content you create or upload within the app (text, images, files). You grant Soul Sync Ltd. a non-exclusive license to process this content solely to provide the service. You are responsible for the legality of the content you upload.' },
    { icon: Image, title: 'Images & Files 🖼️', body: 'By uploading images or files, you confirm you have the necessary rights. We are not liable for any intellectual property infringement by users.' },
    { icon: RefreshCw, title: 'Changes to Terms 📝', body: 'We may modify these terms from time to time. You will be notified of significant changes via email or in-app notification. Continued use after modifications constitutes acceptance.' },
    { icon: XCircle, title: 'Termination 🛑', body: 'We reserve the right to suspend or terminate your account for violating these terms, misusing the service, or engaging in harmful behavior. You will be notified of the reason when possible.' },
    { icon: Mail, title: 'Contact Us ✉️', body: 'For inquiries about the terms and conditions: support@mytwin.app' },
  ];

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header />

      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 40 }}>
        <FileText size={48} stroke={primary} style={{ alignSelf: 'center', marginBottom: 16 }} />
        <Text style={[styles.title, { color: txt }]}>{isAr ? 'الشروط والأحكام' : 'Terms & Conditions'}</Text>
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

        <Text style={[styles.footer, { color: sub }]}>
          © 2026 Soul Sync Ltd. All rights reserved.
        </Text>
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
  footer: { textAlign: 'center', marginTop: 24, fontSize: 12 },
});
