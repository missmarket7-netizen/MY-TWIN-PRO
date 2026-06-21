import React, { memo } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Modal } from 'react-native';
import { Brain, Search, Cloud, Sparkles, BatteryCharging, Play } from 'lucide-react-native';

export const COLORS = {
  dark: {
    bg: '#0F0A1A', headerBg: '#130D20', border: '#2D1B4D',
    text: '#FFFFFF', subtext: '#8B7BA3', accent: '#A855F7',
    inputBg: '#161122', userBubble: '#1A1226', twinBubble: '#1A1226',
  },
  light: {
    bg: '#FAFAF8', headerBg: '#F0F0EB', border: '#E8E8E3',
    text: '#2D2D2D', subtext: '#6B6B6B', accent: '#6B21A8',
    inputBg: '#FDFDF9', userBubble: '#FFFFFF', twinBubble: '#F5F5F0',
  },
};

export const ThinkingBar = memo(({ stage, isDark }: { stage: string; isDark: boolean }) => {
  const stages: Record<string, { icon: any; text_ar: string; text_en: string; color: string }> = {
    thinking: { icon: Brain, text_ar: 'يفكر...', text_en: 'Thinking...', color: '#8B5CF6' },
    searching_memory: { icon: Search, text_ar: 'يبحث في الذكريات...', text_en: 'Searching memories...', color: '#3B82F6' },
    using_tool: { icon: Cloud, text_ar: 'يستخدم الأدوات...', text_en: 'Using tools...', color: '#10B981' },
    generating: { icon: Sparkles, text_ar: 'يصيغ الرد...', text_en: 'Crafting response...', color: '#F59E0B' },
    completed: { icon: Sparkles, text_ar: 'تم!', text_en: 'Done!', color: '#10B981' },
    idle: { icon: Brain, text_ar: '', text_en: '', color: '#8B5CF6' },
  };
  const info = stages[stage] || stages.thinking;
  const Icon = info.icon;
  return (
    <View style={[thinkStyles.container, { backgroundColor: info.color + '15' }]}>
      <Icon size={16} stroke={info.color} />
      <Text style={[thinkStyles.text, { color: info.color }]}>🧠 {info.text_ar || info.text_en}</Text>
    </View>
  );
});

const thinkStyles = StyleSheet.create({
  container: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, alignSelf: 'center', marginVertical: 8 },
  text: { fontSize: 13, fontWeight: '600' },
});

export const WelcomeState = memo(({ isDark, lang, twinName, onSuggestion }: any) => {
  const c = isDark ? COLORS.dark : COLORS.light;
  const suggestions = lang === 'ar' ? [
    'صباح الخير! كيف حالك اليوم؟', 'حابب نتكلم عن إيه؟', 'عندك أي أخبار حلوة؟',
  ] : [
    'Good morning! How are you today?', 'What would you like to talk about?', 'Any good news to share?',
  ];
  return (
    <View style={styles.welcomeContainer}>
      <View style={[styles.welcomeIconWrap, { backgroundColor: c.accent + '15' }]}>
        <Sparkles size={40} stroke={c.accent} />
      </View>
      <Text style={[styles.welcomeTitle, { color: c.text }]}>
        {lang === 'ar' ? `أهلاً بيك، ${twinName || 'توأمك'} جاهز!` : `Welcome! ${twinName || 'Your Twin'} is ready!`}
      </Text>
      <Text style={[styles.welcomeSub, { color: c.subtext }]}>
        {lang === 'ar' ? 'ابدأ محادثة أو اختر من الاقتراحات' : 'Start a conversation or pick a suggestion'}
      </Text>
      <View style={styles.suggestionsWrap}>
        {suggestions.map((s, i) => (
          <TouchableOpacity key={i} style={[styles.suggestionChip, { backgroundColor: c.inputBg, borderColor: c.border }]} onPress={() => onSuggestion(s)} activeOpacity={0.7}>
            <Text style={[styles.suggestionText, { color: c.text }]}>{s}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
});

export const EnergyModal = memo(({ visible, onClose, onWatchAd, adStatus, lang }: any) => {
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const ENERGY_PER_AD = 20;
  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.modalOverlay}>
        <View style={styles.energyCard}>
          <BatteryCharging size={56} stroke="#7C3AED" style={{ alignSelf: 'center', marginBottom: 16 }} />
          <Text style={styles.energyTitle}>{t('الطاقة منتهية', 'Out of Energy')}</Text>
          <Text style={styles.energyBody}>
            {t(
              `شاهد إعلاناً واحصل على ${ENERGY_PER_AD}% طاقة إضافية`,
              `Watch an ad and get ${ENERGY_PER_AD}% extra energy`
            )}
          </Text>
          {adStatus?.remaining_today > 0 ? (
            <TouchableOpacity style={styles.watchAdBtn} onPress={onWatchAd}>
              <Play size={20} stroke="#FFF" />
              <Text style={styles.watchAdText}>{t('مشاهدة إعلان', 'Watch Ad')}</Text>
            </TouchableOpacity>
          ) : (
            <Text style={styles.energyNote}>
              {t('استنفدت الإعلانات اليومية', 'Daily ads exhausted')}
            </Text>
          )}
          <TouchableOpacity onPress={onClose} style={styles.energyClose}>
            <Text style={styles.energyCloseText}>{t('إغلاق', 'Close')}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
});

const styles = StyleSheet.create({
  welcomeContainer: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: 60, paddingHorizontal: 24 },
  welcomeIconWrap: { width: 80, height: 80, borderRadius: 24, justifyContent: 'center', alignItems: 'center', marginBottom: 20 },
  welcomeTitle: { fontSize: 22, fontWeight: '800', textAlign: 'center', marginBottom: 8 },
  welcomeSub: { fontSize: 15, textAlign: 'center', marginBottom: 24 },
  suggestionsWrap: { gap: 10, width: '100%' },
  suggestionChip: { paddingHorizontal: 20, paddingVertical: 14, borderRadius: 16, borderWidth: 1, alignItems: 'center' },
  suggestionText: { fontSize: 15, fontWeight: '500' },
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)', padding: 30 },
  energyCard: { backgroundColor: '#FFFFFF', borderRadius: 24, padding: 30, alignItems: 'center', width: '100%', maxWidth: 350 },
  energyTitle: { fontSize: 22, fontWeight: '800', color: '#1A1226', marginBottom: 12 },
  energyBody: { fontSize: 15, color: '#7C6B99', textAlign: 'center', lineHeight: 22, marginBottom: 24 },
  watchAdBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: '#7C3AED', paddingHorizontal: 28, paddingVertical: 14, borderRadius: 14 },
  watchAdText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  energyNote: { fontSize: 13, color: '#EF4444', textAlign: 'center', marginBottom: 16 },
  energyClose: { marginTop: 16, padding: 10 },
  energyCloseText: { fontSize: 14, color: '#6B7280' },
});
