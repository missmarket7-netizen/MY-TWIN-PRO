import { View, Text, TouchableOpacity, StyleSheet, Alert, ScrollView } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../store/useTwinStore';
import { router, usePathname } from 'expo-router';
import { supabase } from '../lib/supabase';
import { useMemo } from 'react';
import { 
  Home, Heart, History, User, Palette, Diamond, Settings, LogOut, X, 
  PlusCircle, Gift, Sparkles, BatteryFull, BatteryMedium, BatteryLow, 
  ArrowRight, Clock 
} from 'lucide-react-native';

const TIER_LABELS: Record<string, { ar: string; en: string }> = {
  free: { ar: 'مجاني', en: 'Free' },
  free_trial_14d: { ar: 'تجربة مجانية', en: 'Free Trial' },
  premium_trial: { ar: 'تجربة مميزة', en: 'Premium Trial' },
  plus: { ar: 'Plus', en: 'Plus' },
  premium: { ar: 'Premium', en: 'Premium' },
  pro: { ar: 'Pro', en: 'Pro' },
  yearly: { ar: 'سنوي', en: 'Yearly' },
};

export default function SideMenu({ onClose }: { onClose: () => void }) {
  const insets = useSafeAreaInsets();
  const pathname = usePathname();
  
  const { 
    lang, theme, twinName, bondLevel, twinEnergy, tier, clearHistory 
  } = useTwinStore((s) => ({ 
    lang: s.lang, 
    theme: s.theme, 
    twinName: s.twinName, 
    bondLevel: s.bondLevel, 
    twinEnergy: s.twinEnergy, 
    tier: s.tier, 
    clearHistory: s.clearHistory 
  }));
  
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';
  const t = (ar: string, en: string) => (isAr ? ar : en);
  
  const navigate = (route: string) => {
    router.push(route);
    onClose();
  };
  
  const startNewChat = () => {
    clearHistory();
    onClose();
    router.push('/chat');
  };

  // ✅ مؤشر الطاقة مرتبط بـ twinEnergy
  const energy = Math.max(0, Math.min(100, twinEnergy || 100));
  
  const getEnergyColor = (val: number) => {
    if (val >= 70) return '#10B981';
    if (val >= 30) return '#F59E0B';
    return '#EF4444';
  };

  const energyIcon = useMemo(() => {
    const color = getEnergyColor(energy);
    if (energy >= 70) return <BatteryFull size={18} stroke={color} />;
    if (energy >= 30) return <BatteryMedium size={18} stroke={color} />;
    return <BatteryLow size={18} stroke={color} />;
  }, [energy]);

  const colors = {
    bg: isDark ? '#1A1A1A' : '#FFFFFF',
    border: isDark ? '#333' : '#E8E8E3',
    text: isDark ? '#FFF' : '#1A1A1A',
    subtext: isDark ? '#CCC' : '#666',
    primary: isDark ? '#D8B4FE' : '#6B21A8',
    accent: '#A855F7',
    danger: '#EF4444',
    bond: isDark ? '#F472B6' : '#EC4899',
    energyFill: getEnergyColor(energy),
  };

  const menuItems = [
    { icon: Home, label: t('الرئيسية', 'Home'), route: '/chat' },
    { icon: PlusCircle, label: t('دردشة جديدة', 'New Chat'), onPress: startNewChat },
    { icon: Heart, label: t('علاقتي', 'My Relationship'), route: '/relationship' },
    { icon: Clock, label: t('سجل المحادثات', 'Chat History'), route: '/history' },
    { icon: History, label: t('ذكرياتنا', 'Memories'), route: '/memories' },
    { icon: User, label: t('الملف الشخصي', 'Profile'), route: '/profile' },
    { icon: Palette, label: t('تخصيص', 'Customize'), route: '/customize' },
    { icon: Diamond, label: t('الاشتراكات', 'Subscription'), route: '/subscription' },
    { icon: Gift, label: t('الإحالة', 'Referral'), route: '/referral' },
    { icon: Settings, label: t('الإعدادات', 'Settings'), route: '/settings' },
  ];

  // دعم RTL/LTR كامل
  const itemDirection = isAr ? 'row-reverse' : 'row';
  const textAlign = isAr ? 'right' : 'left';
  const closeBtnAlign = isAr ? 'flex-start' : 'flex-end';
  const activeBorderSide = isAr ? 'borderRightWidth' : 'borderLeftWidth';
  const activeBorderColor = isAr ? 'borderRightColor' : 'borderLeftColor';

  return (
    <ScrollView 
      style={[styles.container, { paddingTop: insets.top + 20, backgroundColor: colors.bg }]} 
      contentContainerStyle={{ paddingBottom: 40 }} 
      keyboardShouldPersistTaps="handled"
    >
      <TouchableOpacity 
        style={[styles.closeBtn, { alignSelf: closeBtnAlign }]} 
        onPress={onClose}
        accessibilityLabel={t('إغلاق القائمة', 'Close menu')}
      >
        <X size={24} stroke={colors.primary} />
      </TouchableOpacity>
      
      <View style={[styles.userCard, { borderBottomColor: colors.border, flexDirection: isAr ? 'row-reverse' : 'row' }]}>
        <View style={styles.avatar}>
          <Sparkles size={28} stroke={colors.accent} />
        </View>
        <View style={{ flex: 1 }}>
          <Text style={[styles.userName, { color: colors.text, textAlign }]}>
            {twinName || t('توأمك', 'Your Twin')}
          </Text>
          <View style={[styles.bondRow, { flexDirection: isAr ? 'row-reverse' : 'row' }]}>
            <Heart size={14} stroke={colors.bond} fill={colors.bond} />
            <Text style={[styles.bondValue, { color: colors.bond }]}>
              {t('رابطة', 'Bond')} {Math.round(bondLevel)}%
            </Text>
          </View>
          <View style={[styles.energyRow, { flexDirection: isAr ? 'row-reverse' : 'row' }]}>
            {energyIcon}
            <Text style={[styles.energyValue, { color: colors.energyFill }]}>
              {Math.round(energy)}%
            </Text>
          </View>
          <Text style={[styles.tierText, { color: colors.primary, textAlign }]}>
            {TIER_LABELS[tier]?.[isAr ? 'ar' : 'en'] || tier}
          </Text>
        </View>
      </View>

      <TouchableOpacity 
        style={[
          styles.backToChatBtn, 
          { flexDirection: isAr ? 'row-reverse' : 'row' }, 
          isDark && { backgroundColor: '#A855F722' }
        ]} 
        onPress={() => navigate('/chat')}
        accessibilityLabel={t('العودة للمحادثة', 'Back to Chat')}
      >
        <ArrowRight size={18} stroke={colors.accent} />
        <Text style={[styles.backToChatText, { color: colors.accent }]}>
          {t('العودة للمحادثة', 'Back to Chat')}
        </Text>
      </TouchableOpacity>

      {menuItems.map((item, idx) => {
        const Icon = item.icon;
        const active = item.route ? (pathname === item.route || (item.route === '/chat' && pathname === '/')) : false;
        const onPress = item.onPress || (item.route ? () => navigate(item.route) : () => {});
        
        return (
          <TouchableOpacity 
            key={item.route || item.label} 
            style={[
              styles.item, 
              { flexDirection: itemDirection }, 
              active && { 
                backgroundColor: '#F3F0FF', 
                [activeBorderSide]: 3, 
                [activeBorderColor]: '#A855F7' 
              }
            ]} 
            onPress={onPress}
            accessibilityLabel={item.label}
          >
            <Icon size={20} stroke={active ? colors.accent : colors.primary} />
            <Text style={[
              styles.itemLabel, 
              { color: colors.text, textAlign }, 
              active && { color: colors.accent, fontWeight: '600' }
            ]}>
              {item.label}
            </Text>
          </TouchableOpacity>
        );
      })}

      <TouchableOpacity 
        style={[styles.item, { flexDirection: itemDirection }, { marginTop: 20 }]} 
        onPress={() => {
          Alert.alert(
            t('تسجيل الخروج', 'Logout'), 
            t('هل أنت متأكد؟', 'Are you sure?'), 
            [
              { text: t('إلغاء', 'Cancel'), style: 'cancel' },
              { 
                text: t('خروج', 'Logout'), 
                style: 'destructive', 
                onPress: async () => { 
                  await supabase.auth.signOut(); 
                  router.replace('/login'); 
                } 
              }
            ]
          );
        }}
        accessibilityLabel={t('تسجيل الخروج', 'Logout')}
      >
        <LogOut size={20} stroke={colors.danger} />
        <Text style={[styles.itemLabel, { color: colors.danger, textAlign }]}>
          {t('تسجيل الخروج', 'Logout')}
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  closeBtn: { marginBottom: 24 },
  userCard: { alignItems: 'center', paddingBottom: 16, marginBottom: 16, borderBottomWidth: 1 },
  avatar: { width: 48, height: 48, borderRadius: 24, backgroundColor: '#F3F0FF', justifyContent: 'center', alignItems: 'center' },
  userName: { fontSize: 16, fontWeight: '700' },
  bondRow: { alignItems: 'center', gap: 4, marginTop: 4 },
  bondValue: { fontSize: 12, fontWeight: '500' },
  energyRow: { alignItems: 'center', gap: 4, marginTop: 2 },
  energyValue: { fontSize: 12, fontWeight: '500' },
  tierText: { fontSize: 12, fontWeight: '500', marginTop: 2 },
  backToChatBtn: { alignItems: 'center', justifyContent: 'center', gap: 8, padding: 12, borderRadius: 10, backgroundColor: '#F3F0FF', marginBottom: 16 },
  backToChatText: { fontSize: 15, fontWeight: '600' },
  item: { alignItems: 'center', gap: 14, padding: 14, borderRadius: 12, marginBottom: 2 },
  itemLabel: { fontSize: 15, fontWeight: '500' },
});
