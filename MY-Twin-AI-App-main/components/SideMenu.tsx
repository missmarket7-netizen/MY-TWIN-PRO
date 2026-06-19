import React, { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, Alert, ScrollView,
  Animated, Dimensions, LayoutAnimation, Platform, UIManager,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Haptics from 'expo-haptics';
import { useTwinStore } from '../store/useTwinStore';
import { router, usePathname } from 'expo-router';
import { removeToken } from '../lib/auth';
import {
  Home, MessageCircle, Heart, Brain, Smile, User, Palette, Diamond,
  Settings, LogOut, Gift, Sparkles, BatteryFull, BatteryMedium,
  BatteryLow, ChevronRight, Zap, Crown, Star, X,
  GraduationCap, Code2, TrendingUp, Image as ImageIcon, Moon,
  PenLine, ChevronDown,
} from 'lucide-react-native';

// تفعيل LayoutAnimation على Android
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

const { width: SCREEN_W } = Dimensions.get('window');
const MENU_W = Math.min(SCREEN_W * 0.82, 340);

const TIER_CONFIG: Record<string, { ar: string; en: string; color: string; bg: string; icon: any }> = {
  free:              { ar: 'مجاني',         en: 'Free',           color: '#6B7280', bg: '#F3F4F6', icon: Star     },
  free_trial_14d:   { ar: 'تجربة مجانية',  en: 'Free Trial',     color: '#F59E0B', bg: '#FEF3C7', icon: Star     },
  premium_trial:    { ar: 'تجربة مميزة',   en: 'Premium Trial',  color: '#8B5CF6', bg: '#EDE9FE', icon: Crown    },
  plus:             { ar: 'Plus ✨',        en: 'Plus ✨',         color: '#6366F1', bg: '#EEF2FF', icon: Crown    },
  premium:          { ar: 'Premium 💜',     en: 'Premium 💜',     color: '#A855F7', bg: '#F5F3FF', icon: Crown    },
  pro:              { ar: 'Pro 🔥',         en: 'Pro 🔥',          color: '#EF4444', bg: '#FEF2F2', icon: Crown    },
  yearly:           { ar: 'سنوي ⚡',        en: 'Yearly ⚡',       color: '#F59E0B', bg: '#FFFBEB', icon: Crown    },
};

const FREE_TIERS = ['free', 'free_trial_14d'];

// ========== مكونات فرعية ==========
const AvatarRing = memo(({ accent, accentSoft }: { accent: string; accentSoft: string }) => {
  const ringAnim = useRef(new Animated.Value(0.6)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  useEffect(() => {
    const ring = Animated.loop(Animated.sequence([
      Animated.timing(ringAnim, { toValue: 1, duration: 1400, useNativeDriver: true }),
      Animated.timing(ringAnim, { toValue: 0.6, duration: 1400, useNativeDriver: true }),
    ]));
    const scale = Animated.loop(Animated.sequence([
      Animated.timing(scaleAnim, { toValue: 1.05, duration: 1400, useNativeDriver: true }),
      Animated.timing(scaleAnim, { toValue: 1,    duration: 1400, useNativeDriver: true }),
    ]));
    ring.start(); scale.start();
    return () => { ring.stop(); scale.stop(); };
  }, []);
  return (
    <View style={av.outer}>
      <Animated.View style={[av.pulseRing, { borderColor: accent, opacity: ringAnim, transform: [{ scale: scaleAnim }] }]} />
      <View style={[av.innerRing, { borderColor: accent + '60' }]}>
        <View style={[av.avatar, { backgroundColor: accentSoft }]}>
          <Sparkles size={30} stroke={accent} />
        </View>
      </View>
    </View>
  );
});
const av = StyleSheet.create({
  outer: { width: 76, height: 76, justifyContent: 'center', alignItems: 'center', marginBottom: 14 },
  pulseRing: { position: 'absolute', width: 76, height: 76, borderRadius: 38, borderWidth: 2 },
  innerRing: { width: 68, height: 68, borderRadius: 34, borderWidth: 1.5, justifyContent: 'center', alignItems: 'center' },
  avatar: { width: 58, height: 58, borderRadius: 29, justifyContent: 'center', alignItems: 'center' },
});

const AnimBar = memo(({ value, color, trackColor }: { value: number; color: string; trackColor: string }) => {
  const barAnim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.spring(barAnim, { toValue: Math.max(0, Math.min(1, value / 100)), tension: 60, friction: 10, useNativeDriver: false }).start();
  }, [value]);
  return (
    <View style={[bs.track, { backgroundColor: trackColor }]}>
      <Animated.View style={[bs.fill, { backgroundColor: color, width: barAnim.interpolate({ inputRange: [0, 1], outputRange: ['0%', '100%'] }) }]} />
    </View>
  );
});
const bs = StyleSheet.create({ track: { flex: 1, height: 5, borderRadius: 3, overflow: 'hidden' }, fill: { height: '100%', borderRadius: 3 } });

// ========== المكون الرئيسي (يُستكمل في part2) ==========
// ========== تابع المكون الرئيسي ==========
export default function SideMenu({ onClose }: { onClose: () => void }) {
  const insets   = useSafeAreaInsets();
  const pathname = usePathname();
  const { lang, theme, twinName, bondLevel, tier, clearHistory, chatHistory, getEnergyPercent, logout: storeLogout } = useTwinStore((s) => ({
    lang: s.lang, theme: s.theme, twinName: s.twinName, bondLevel: s.bondLevel,
    tier: s.tier, clearHistory: s.clearHistory, chatHistory: s.chatHistory,
    getEnergyPercent: s.getEnergyPercent, logout: s.logout,
  }));

  const isAr  = lang === 'ar';
  const isDark = theme === 'dark';
  const t     = useCallback((ar: string, en: string) => (isAr ? ar : en), [isAr]);

  const energy    = Math.max(0, Math.min(100, getEnergyPercent()));
  const bond      = Math.max(0, Math.min(100, bondLevel));
  const tierCfg   = TIER_CONFIG[tier] ?? TIER_CONFIG.free;
  const isFree    = FREE_TIERS.includes(tier);

  const c = useMemo(() => ({
    bg: isDark ? '#141416' : '#FFFFFF', headerBg: isDark ? '#1C1C1E' : '#F9F6FF',
    border: isDark ? '#2C2C2E' : '#EDE9F6', text: isDark ? '#F5F5F5' : '#1A1A1A',
    subtext: isDark ? '#8E8E93' : '#6B7280', accent: isDark ? '#A78BFA' : '#7C3AED',
    accentSoft: isDark ? '#2D1B69' : '#EDE9FE', bond: '#EC4899', bondTrack: isDark ? '#3B1F2B' : '#FCE7F3',
    energyColor: energy > 60 ? '#10B981' : energy > 25 ? '#F59E0B' : '#EF4444',
    energyTrack: isDark ? '#1F2937' : '#F3F4F6', cardBg: isDark ? '#1C1C1E' : '#FFFFFF',
    danger: '#EF4444', sectionHdr: isDark ? '#48484A' : '#9CA3AF', divider: isDark ? '#2C2C2E' : '#F3F4F6',
    upgradeBg: isDark ? '#2D1B69' : '#F5F3FF', upgradeBorder: isDark ? '#5B21B6' : '#C4B5FD',
  }), [isDark, energy]);

  // ========== حالة القوائم المنسدلة ==========
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    essentials: false,
    powers: false,
    account: false,
  });

  const toggleSection = useCallback((key: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpandedSections(prev => ({ ...prev, [key]: !prev[key] }));
  }, []);

  // ========== أحداث ==========
  const navigate = useCallback((route: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    router.push(route as any);
    onClose();
  }, [onClose]);

  const startNewChat = useCallback(() => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    clearHistory();
    onClose();
    router.push('/chat');
  }, [clearHistory, onClose]);

  const handleLogout = useCallback(() => {
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    Alert.alert(t('تسجيل الخروج', 'Log Out'), t('هل تريد تسجيل الخروج؟', 'Are you sure?'), [
      { text: t('إلغاء', 'Cancel'), style: 'cancel' },
      { text: t('خروج', 'Log Out'), style: 'destructive', onPress: async () => { await removeToken(); storeLogout(); router.replace('/login' as any); } },
    ]);
  }, [t, storeLogout]);

  // ========== مكونات القائمة ==========
  const MenuItem = useCallback(({ icon: Icon, label, route, onPress, badge, isActive }: { icon: any, label: string, route?: string, onPress?: () => void, badge?: string, isActive?: boolean }) => (
    <TouchableOpacity style={[mi.item, isActive && { backgroundColor: c.accent + '15' }]} onPress={onPress || (() => route && navigate(route))} activeOpacity={0.7}>
      <View style={[mi.iconWrap, { backgroundColor: isActive ? c.accent + '18' : c.bg }]}>
        <Icon size={20} stroke={isActive ? c.accent : c.subtext} />
      </View>
      <Text style={[mi.label, { color: isActive ? c.accent : c.text }, isActive && { fontWeight: '700' }]}>{label}</Text>
      {badge && <View style={mi.badge}><Text style={mi.badgeText}>{badge}</Text></View>}
    </TouchableOpacity>
  ), [c, navigate]);

  const SectionHeader = useCallback(({ label, sectionKey }: { label: string, sectionKey: string }) => (
    <TouchableOpacity style={[sh.header, { backgroundColor: c.bg }]} onPress={() => toggleSection(sectionKey)} activeOpacity={0.7}>
      <Text style={[sh.headerText, { color: c.sectionHdr }]}>{label}</Text>
      <Animated.View style={{ transform: [{ rotate: expandedSections[sectionKey] ? '90deg' : '0deg' }] }}>
        <ChevronRight size={16} stroke={c.subtext} />
      </Animated.View>
    </TouchableOpacity>
  ), [c, expandedSections, toggleSection]);

  const EnergyIcon = useMemo(() => {
    if (energy >= 70) return <BatteryFull size={14} stroke={c.energyColor} />;
    if (energy >= 30) return <BatteryMedium size={14} stroke={c.energyColor} />;
    return <BatteryLow size={14} stroke={c.energyColor} />;
  }, [energy, c.energyColor]);

  return (
    <View style={[styles.root, { backgroundColor: c.bg, width: MENU_W }]}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={[styles.scroll, { paddingTop: insets.top + 16, paddingBottom: insets.bottom + 32 }]}>
        {/* الصف العلوي */}
        <View style={[styles.topRow, { flexDirection: isAr ? 'row-reverse' : 'row' }]}>
          <TouchableOpacity onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); onClose(); }} style={[styles.closeBtn, { backgroundColor: c.accentSoft }]} activeOpacity={0.75}>
            <X size={20} stroke={c.accent} />
          </TouchableOpacity>
          <Text style={[styles.appName, { color: c.accent }]}>My Twin</Text>
        </View>

        {/* بطاقة الملف الشخصي */}
        <View style={[styles.profileCard, { backgroundColor: c.headerBg, borderColor: c.border }]}>
          <View style={[styles.blobTop, { backgroundColor: c.accent + '12' }]} />
          <View style={[styles.blobBottom, { backgroundColor: c.bond + '08' }]} />
          <AvatarRing accent={c.accent} accentSoft={c.accentSoft} />
          <Text style={[styles.twinName, { color: c.text }]}>{twinName || t('توأمك', 'Your Twin')}</Text>
          <View style={[styles.tierBadge, { backgroundColor: tierCfg.bg, borderColor: tierCfg.color + '40' }]}>
            <tierCfg.icon size={12} stroke={tierCfg.color} />
            <Text style={[styles.tierText, { color: tierCfg.color }]}>{isAr ? tierCfg.ar : tierCfg.en}</Text>
          </View>
          <View style={[styles.statsRow, { borderColor: c.border }]}>
            <View style={styles.statItem}>
              <View style={[styles.statLabelRow, { flexDirection: isAr ? 'row-reverse' : 'row' }]}>
                <Heart size={12} stroke={c.bond} fill={c.bond} />
                <Text style={[styles.statLabel, { color: c.subtext }]}>{t('رابطة', 'Bond')}</Text>
                <Text style={[styles.statValue, { color: c.bond }]}>{Math.round(bond)}%</Text>
              </View>
              <AnimBar value={bond} color={c.bond} trackColor={c.bondTrack} />
            </View>
            <View style={[styles.statDivider, { backgroundColor: c.border }]} />
            <View style={styles.statItem}>
              <View style={[styles.statLabelRow, { flexDirection: isAr ? 'row-reverse' : 'row' }]}>
                {EnergyIcon}
                <Text style={[styles.statLabel, { color: c.subtext }]}>{t('طاقة', 'Energy')}</Text>
                <Text style={[styles.statValue, { color: c.energyColor }]}>{Math.round(energy)}%</Text>
              </View>
              <AnimBar value={energy} color={c.energyColor} trackColor={c.energyTrack} />
            </View>
          </View>
        </View>

        {/* زر العودة للمحادثة ومحادثة جديدة */}
        <TouchableOpacity style={[styles.chatBtn, { backgroundColor: c.accentSoft, borderColor: c.accent + '40' }]} onPress={() => navigate('/chat')} activeOpacity={0.8}>
          <Zap size={16} stroke={c.accent} fill={c.accent} />
          <Text style={[styles.chatBtnText, { color: c.accent }]}>{t('العودة للمحادثة', 'Back to Chat')}</Text>
          <ChevronRight size={16} stroke={c.accent} />
        </TouchableOpacity>

        <TouchableOpacity style={[styles.newChatBtn, { borderColor: c.accent + '40' }]} onPress={startNewChat} activeOpacity={0.8}>
          <Sparkles size={16} stroke={c.accent} />
          <Text style={[styles.newChatBtnText, { color: c.accent }]}>{t('محادثة جديدة', 'New Chat')}</Text>
        </TouchableOpacity>

        {/* القسم ١: الأساسيات */}
        <SectionHeader label={t('الأساسيات', 'Essentials')} sectionKey="essentials" />
        {expandedSections.essentials && (
          <View style={styles.sectionContent}>
            <MenuItem icon={Home} label={t('الرئيسية', 'Home')} route="/welcome" />
            <MenuItem icon={MessageCircle} label={t('دردشة', 'Chat')} route="/chat" />
            <MenuItem icon={Heart} label={t('علاقتي', 'My Relationship')} route="/relationship" />
            <MenuItem icon={Brain} label={t('ذكرياتنا', 'Memories')} route="/memories" />
            <MenuItem icon={Smile} label={t('المشاعر', 'Mood')} route="/mood" />
          </View>
        )}

        {/* القسم ٢: قدرات التوأم */}
        <SectionHeader label={t('🚀 قدرات التوأم', '🚀 Twin Powers')} sectionKey="powers" />
        {expandedSections.powers && (
          <View style={styles.sectionContent}>
            <MenuItem icon={GraduationCap} label={t('المذاكرة الذكية', 'Smart Study')} route="/features/study-mode" />
            <MenuItem icon={Code2} label={t('مختبر البرمجة', 'Code Lab')} route="/features/code-lab" />
            <MenuItem icon={TrendingUp} label={t('تحليل الأعمال', 'Business Analyzer')} route="/features/business-analyzer" />
            <MenuItem icon={Heart} label={t('مدرب الحياة', 'Life Coach')} route="/features/life-coach" />
            <MenuItem icon={ImageIcon} label={t('إنشاء الصور', 'Image Creator')} route="/features/image-creator" />
            <MenuItem icon={Moon} label={t('تفسير الأحلام', 'Dream Journal')} route="/features/dreams" />
            <MenuItem icon={PenLine} label={t('كتابة المحتوى', 'Content Creator')} route="/features/content-creator" />
          </View>
        )}

        {/* القسم ٣: الحساب */}
        <SectionHeader label={t('👤 الحساب', '👤 Account')} sectionKey="account" />
        {expandedSections.account && (
          <View style={styles.sectionContent}>
            <MenuItem icon={User} label={t('الملف الشخصي', 'Profile')} route="/profile" />
            <MenuItem icon={Palette} label={t('تخصيص التوأم', 'Customize Twin')} route="/customize" />
            <MenuItem icon={Diamond} label={t('الاشتراكات', 'Subscription')} route="/subscription" />
            <MenuItem icon={Gift} label={t('دعوة الأصدقاء', 'Refer Friends')} route="/referral" />
          </View>
        )}

        {/* الإعدادات */}
        <MenuItem icon={Settings} label={t('الإعدادات', 'Settings')} route="/settings" />

        {/* بانر الترقية للمجانيين */}
        {isFree && (
          <TouchableOpacity style={[styles.upgradeBanner, { backgroundColor: c.upgradeBg, borderColor: c.upgradeBorder }]} onPress={() => navigate('/subscription')} activeOpacity={0.85}>
            <View style={[styles.upgradeIconWrap, { backgroundColor: c.accent + '20' }]}><Crown size={22} stroke={c.accent} /></View>
            <View style={{ flex: 1 }}>
              <Text style={[styles.upgradeTitle, { color: c.accent }]}>{t('ارتقِ لـ Premium', 'Upgrade to Premium')}</Text>
              <Text style={[styles.upgradeSub, { color: c.subtext }]}>{t('محادثات غير محدودة، صوت، ذاكرة ذكية', 'Unlimited chats, voice & smart memory')}</Text>
            </View>
            <ChevronRight size={18} stroke={c.accent} />
          </TouchableOpacity>
        )}

        <View style={[styles.divider, { backgroundColor: c.divider }]} />

        {/* تسجيل الخروج */}
        <TouchableOpacity style={[styles.logoutBtn, { flexDirection: isAr ? 'row-reverse' : 'row' }]} onPress={handleLogout} activeOpacity={0.7}>
          <View style={[styles.logoutIconWrap, { backgroundColor: c.danger + '12' }]}><LogOut size={18} stroke={c.danger} /></View>
          <Text style={[styles.logoutText, { color: c.danger, textAlign: isAr ? 'right' : 'left' }]}>{t('تسجيل الخروج', 'Log Out')}</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

// ========== الأنماط ==========
const styles = StyleSheet.create({
  root: { flex: 1 },
  scroll: { paddingHorizontal: 16 },
  topRow: { alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 },
  closeBtn: { width: 38, height: 38, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  appName: { fontSize: 18, fontWeight: '800', letterSpacing: -0.5 },
  profileCard: { borderRadius: 24, borderWidth: 1, padding: 20, marginBottom: 14, alignItems: 'center', overflow: 'hidden' },
  blobTop: { position: 'absolute', top: -30, right: -30, width: 100, height: 100, borderRadius: 50 },
  blobBottom: { position: 'absolute', bottom: -20, left: -20, width: 80, height: 80, borderRadius: 40 },
  twinName: { fontSize: 18, fontWeight: '800', letterSpacing: -0.4, marginBottom: 8 },
  tierBadge: { flexDirection: 'row', alignItems: 'center', gap: 5, paddingHorizontal: 12, paddingVertical: 5, borderRadius: 20, borderWidth: 1, marginBottom: 16 },
  tierText: { fontSize: 12, fontWeight: '700' },
  statsRow: { flexDirection: 'row', alignItems: 'stretch', borderTopWidth: StyleSheet.hairlineWidth, paddingTop: 14, gap: 12, width: '100%' },
  statItem: { flex: 1, gap: 6 },
  statDivider: { width: 1, borderRadius: 1 },
  statLabelRow: { alignItems: 'center', gap: 4 },
  statLabel: { fontSize: 11, fontWeight: '600', flex: 1 },
  statValue: { fontSize: 12, fontWeight: '800' },
  chatBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, padding: 13, borderRadius: 16, borderWidth: 1, marginBottom: 8 },
  chatBtnText: { fontSize: 14, fontWeight: '700', flex: 1 },
  newChatBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, padding: 13, borderRadius: 16, borderWidth: 1, borderStyle: 'dashed', marginBottom: 16 },
  newChatBtnText: { fontSize: 14, fontWeight: '600' },
  sectionContent: { marginBottom: 8, marginLeft: 8 },
  divider: { height: 1, marginVertical: 16 },
  upgradeBanner: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16, borderRadius: 18, borderWidth: 1.5, marginTop: 8 },
  upgradeIconWrap: { width: 40, height: 40, borderRadius: 14, justifyContent: 'center', alignItems: 'center' },
  upgradeTitle: { fontSize: 14, fontWeight: '700' },
  upgradeSub: { fontSize: 11, marginTop: 2 },
  logoutBtn: { flexDirection: 'row', alignItems: 'center', gap: 14, paddingVertical: 14, paddingHorizontal: 12, borderRadius: 12 },
  logoutIconWrap: { width: 36, height: 36, borderRadius: 10, justifyContent: 'center', alignItems: 'center' },
  logoutText: { fontSize: 15, fontWeight: '500' },
});

const mi = StyleSheet.create({
  item: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingHorizontal: 14, paddingVertical: 12, borderRadius: 14, marginBottom: 2 },
  iconWrap: { width: 36, height: 36, borderRadius: 11, justifyContent: 'center', alignItems: 'center' },
  label: { fontSize: 15, fontWeight: '500', flex: 1 },
  badge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 10, minWidth: 22, alignItems: 'center', backgroundColor: '#7C3AED' },
  badgeText: { color: '#FFF', fontSize: 11, fontWeight: '700' },
});

const sh = StyleSheet.create({
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: 12, paddingHorizontal: 4, marginTop: 4 },
  headerText: { fontSize: 11, fontWeight: '700', letterSpacing: 0.8, textTransform: 'uppercase' },
});
