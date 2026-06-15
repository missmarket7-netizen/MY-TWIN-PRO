import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { Stack } from 'expo-router';
import { ChevronLeft } from 'lucide-react-native';
import { router } from 'expo-router';

export default function History() {
  const { theme, lang } = useTwinStore();
  const isDark = theme === 'dark';
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;

  const colors = {
    bg: isDark ? '#1A1A1A' : '#F8F6F2',
    text: isDark ? '#FFF' : '#1A1A1A',
    subtext: isDark ? '#CCC' : '#666',
    primary: '#7C3AED',
    border: isDark ? '#333' : '#E5E5E5',
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      
      {/* شريط علوي بسيط مع زر الرجوع */}
      <View style={[styles.header, { borderBottomColor: colors.border }]}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <ChevronLeft size={24} stroke={colors.primary} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: colors.text }]}>
          {t('سجل المحادثات', 'Chat History')}
        </Text>
        <View style={{ width: 40 }} />
      </View>

      {/* المحتوى (يمكن إضافة سجل المحادثات لاحقاً) */}
      <View style={styles.content}>
        <Text style={[styles.placeholder, { color: colors.subtext }]}>
          {t('سجل المحادثات سيظهر هنا قريباً', 'Chat history will appear here soon')}
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5 },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { fontSize: 18, fontWeight: '700' },
  content: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  placeholder: { fontSize: 16, textAlign: 'center' },
});
