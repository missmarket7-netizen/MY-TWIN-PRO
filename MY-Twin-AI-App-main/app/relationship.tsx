import { SafeAreaView, ScrollView, Text, StyleSheet, View } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import CircleProgress from '../components/CircleProgress';
import BondTimeline from '../components/BondTimeline';
import { Shield, Heart, Handshake, Brain, Smile, Link } from 'lucide-react-native';

export default function Relationship() {
  const { lang, theme, relationshipDims } = useTwinStore();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';
  const bg = isDark ? '#1A1A1A' : '#F8F6F2';
  const txt = isDark ? '#FFF' : '#1A1A1A';

  const dimensions = [
    { key: 'trust', label_ar: 'ثقة', label_en: 'Trust', icon: Shield, color: '#3B82F6' },
    { key: 'affection', label_ar: 'مودة', label_en: 'Affection', icon: Heart, color: '#EC4899' },
    { key: 'support', label_ar: 'دعم', label_en: 'Support', icon: Handshake, color: '#10B981' },
    { key: 'empathy', label_ar: 'تفهم', label_en: 'Empathy', icon: Brain, color: '#8B5CF6' },
    { key: 'humor', label_ar: 'فكاهة', label_en: 'Humor', icon: Smile, color: '#F59E0B' },
    { key: 'dependency', label_ar: 'اعتمادية', label_en: 'Dependency', icon: Link, color: '#6366F1' },
  ];

  return (
    <SafeAreaView style={[s.safe, { backgroundColor: bg }]}>
      <ScrollView contentContainerStyle={s.container}>
        <Text style={[s.title, { color: txt }]}>
          {isAr ? 'علاقتي مع توأمي 💜' : 'My Relationship 💜'}
        </Text>

        {/* شريط التقدم الرئيسي + الأبعاد الأفقية */}
        <BondTimeline />

        {/* دوائر الأبعاد */}
        <Text style={[s.sectionTitle, { color: txt }]}>
          {isAr ? 'أبعاد العلاقة' : 'Relationship Dimensions'}
        </Text>
        <View style={s.grid}>
          {dimensions.map((d) => {
            const Icon = d.icon;
            const value = relationshipDims[d.key as keyof typeof relationshipDims] || 0;
            return (
              <View key={d.key} style={s.circleWrap}>
                <CircleProgress
                  percentage={value}
                  color={d.color}
                  size={80}
                  label={isAr ? d.label_ar : d.label_en}
                  icon={<Icon size={18} stroke={d.color} />}
                  trackColor={isDark ? '#444' : '#E8E8E3'}
                />
              </View>
            );
          })}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1 },
  container: { padding: 20, paddingBottom: 40 },
  title: { fontSize: 24, fontWeight: '800', marginBottom: 20, textAlign: 'center' },
  sectionTitle: { fontSize: 18, fontWeight: '700', marginTop: 20, marginBottom: 16 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', gap: 16 },
  circleWrap: { width: '30%', alignItems: 'center', marginBottom: 16 },
});
