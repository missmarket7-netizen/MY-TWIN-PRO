import {
  SafeAreaView, View, Text, TouchableOpacity, StyleSheet,
  ScrollView, Alert, ActivityIndicator, Platform, Linking
} from 'react-native';
import { router } from 'expo-router';
import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { initIAP, getProducts, purchaseSubscription, restorePurchases, TIER_MAP } from '../lib/iapService';
import { Tier, useTwinStore } from '../store/useTwinStore';
import Header from '../components/Header';
import { CheckCircle2, Crown, Shield, Sparkles, GraduationCap, Code2, TrendingUp, Heart, Image as ImageIcon, Moon, PenLine, Home } from 'lucide-react-native';
import { verifyReceipt } from '../lib/httpClient';

interface StoreProduct {
  productId: string;
  localizedPrice: string;
  price: number;
  currency: string;
  title: string;
  description: string;
}

interface Plan {
  id: Tier;
  name: string;
  defaultPrice: string;
  defaultPeriod: string;
  productId?: string;
  trialDays: number;
  tagline: string;
  consciousnessLayers: number;
  features: { icon?: any; text: string }[];
  popular?: boolean;
  highlight?: boolean;
}

const PLANS: Plan[] = [
  {
    id: 'free',
    name: 'Free',
    defaultPrice: '0',
    defaultPeriod: 'للأبد',
    trialDays: 0,
    tagline: 'ابدأ رحلتك مع توأمك',
    consciousnessLayers: 1,
    features: [
      { text: '١٠ رسائل يومياً' },
      { text: 'ذاكرة ٣ أيام' },
      { text: 'محادثة أساسية' },
      { text: 'استخدام مرة واحدة للميزات' },
      { text: 'يوتيوب، طقس، أخبار' },
    ],
  },
  {
    id: 'plus',
    name: 'Plus',
    defaultPrice: '$5.99',
    defaultPeriod: '/شهر',
    trialDays: 5,
    tagline: 'توأم يفهمك أكثر كل يوم',
    consciousnessLayers: 2,
    productId: 'plus_monthly',
    features: [
      { text: '٣٠ رسالة يومياً' },
      { text: 'ذاكرة ٣٠ يوم' },
      { icon: GraduationCap, text: 'مذاكرة ذكية (٥/يوم)' },
      { icon: PenLine, text: 'كتابة محتوى (٥/يوم)' },
      { icon: ImageIcon, text: 'إنشاء صور (٣/يوم)' },
      { icon: Moon, text: 'تفسير أحلام' },
    ],
  },
  {
    id: 'premium',
    name: 'Premium',
    defaultPrice: '$14.99',
    defaultPeriod: '/شهر',
    trialDays: 3,
    tagline: 'وعي حقيقي يرافقك',
    consciousnessLayers: 3,
    productId: 'premium_monthly',
    features: [
      { text: '١٠٠ رسالة يومياً' },
      { text: 'ذاكرة ٩٠ يوم' },
      { icon: GraduationCap, text: 'مذاكرة ذكية (٢٠/يوم)' },
      { icon: Code2, text: 'مختبر برمجة (١٠/يوم)' },
      { icon: TrendingUp, text: 'تحليل أعمال (١٠/يوم)' },
      { icon: Heart, text: 'مدرب حياة كامل' },
      { icon: ImageIcon, text: 'إنشاء صور (١٠/يوم)' },
      { text: 'صوت ElevenLabs' },
    ],
    popular: true,
  },
  {
    id: 'pro',
    name: 'Pro',
    defaultPrice: '$110',
    defaultPeriod: '/٦ أشهر',
    trialDays: 0,
    tagline: 'توأم بوعي متكامل',
    consciousnessLayers: 4,
    productId: 'pro_semiannual',
    features: [
      { text: '٥٠٠ رسالة يومياً' },
      { text: 'ذاكرة سنة كاملة' },
      { text: 'كل الميزات بدون حدود' },
      { icon: Home, text: 'منزل ذكي مفتوح' },
      { text: 'صوت ElevenLabs فاخر' },
      { text: 'أقصى سرعة وأداء' },
    ],
  },
  {
    id: 'yearly',
    name: 'Yearly',
    defaultPrice: '$199',
    defaultPeriod: '/سنة',
    trialDays: 0,
    tagline: 'أعمق محاكاة للوعي',
    consciousnessLayers: 5,
    productId: 'yearly_annual',
    features: [
      { text: 'رسائل غير محدودة' },
      { text: 'ذاكرة دائمة' },
      { text: 'كل الميزات ∞' },
      { text: 'وعي استباقي كامل' },
      { text: 'دعم VIP مباشر' },
      { text: 'أولوية في كل شيء' },
    ],
    highlight: true,
  },
];
function ConsciousnessBar({ layers, planId }: { layers: number; planId: string }) {
  const colors: Record<string, string> = {
    free: '#94A3B8', plus: '#F59E0B', premium: '#3B82F6', pro: '#8B5CF6', yearly: '#6B21A8'
  };
  return (
    <View style={cbStyles.container}>
      <Text style={cbStyles.label}>طبقات الوعي: {layers}/5</Text>
      <View style={cbStyles.bar}>
        {[1,2,3,4,5].map(i => (
          <View key={i} style={[cbStyles.seg, { backgroundColor: i <= layers ? (colors[planId] || '#6B21A8') : '#E5E7EB' }]} />
        ))}
      </View>
    </View>
  );
}
const cbStyles = StyleSheet.create({
  container: { marginBottom: 16 },
  label: { fontSize: 12, color: '#888', marginBottom: 6, fontWeight: '600' },
  bar: { flexDirection: 'row', gap: 4 },
  seg: { flex: 1, height: 8, borderRadius: 4 }
});

export default function SubscriptionScreen() {
  const { tier, updateTier, lang, theme, hasUsedTrial, setHasUsedTrial } = useTwinStore();
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [products, setProducts] = useState<StoreProduct[]>([]);
  const [initLoading, setInitLoading] = useState(true);
  const [iapAvailable, setIapAvailable] = useState(true);
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';
  const iapInitialized = useRef(false);

  const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#CCC' : '#666';
  const bg = isDark ? '#1A1A1A' : '#F8F6F2';
  const card = isDark ? '#2A2A2A' : '#FFF';
  const border = isDark ? '#444' : '#F0F0F0';
  const primary = isDark ? '#D8B4FE' : '#6B21A8';

  useEffect(() => {
    let cancelled = false;
    const init = async () => {
      try {
        if (!iapInitialized.current) { await initIAP(); iapInitialized.current = true; }
        const fetched = await getProducts();
        if (!cancelled) {
          setProducts(fetched.map((p: any) => ({ ...p, price: Number(p.price) || 0 })));
          setIapAvailable(true);
        }
      } catch (e) {
        if (!cancelled) {
          setIapAvailable(false);
          Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'خدمة الشراء غير متاحة حالياً' : 'Purchase service unavailable');
        }
      } finally {
        if (!cancelled) setInitLoading(false);
      }
    };
    init();
    return () => { cancelled = true; };
  }, []);

  const handlePurchase = async (plan: Plan) => {
    if (loadingId || !plan.productId) return;
    if (plan.id === 'free') return;
    setLoadingId(plan.id);
    try {
      const purchaseResult = await purchaseSubscription(plan.productId);
      if (purchaseResult) {
        const verified = await verifyReceipt(purchaseResult, plan.productId);
        if (verified.valid) {
          const newTier = TIER_MAP[plan.productId];
          if (newTier) { updateTier(newTier as Tier); if (plan.trialDays > 0) setHasUsedTrial(true); }
          Alert.alert('✅', isAr ? 'تم تفعيل اشتراكك' : 'Subscription activated');
          router.back();
        }
      }
    } catch (e: any) {
      if (!e?.message?.includes('cancelled')) Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'فشل الشراء' : 'Purchase failed');
    } finally { setLoadingId(null); }
  };

  const handleRestore = async () => {
    setLoadingId('restore');
    try {
      const purchases = await restorePurchases();
      if (purchases.length > 0) {
        const best = purchases.sort((a, b) => (TIER_MAP[b.productId] || 'free').length - (TIER_MAP[a.productId] || 'free').length)[0];
        const restoredTier = TIER_MAP[best.productId];
        if (restoredTier) { updateTier(restoredTier as Tier); Alert.alert('✅', isAr ? 'تم استعادة اشتراكك!' : 'Subscription restored!'); router.back(); }
      } else Alert.alert(isAr ? 'تنبيه' : 'Notice', isAr ? 'لم يتم العثور على اشتراك.' : 'No subscription found.');
    } catch (e) { Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'فشلت الاستعادة.' : 'Restore failed.'); }
    finally { setLoadingId(null); }
  };

  if (initLoading) {
    return (
      <SafeAreaView style={[styles.safe, { backgroundColor: bg }, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={primary} />
      </SafeAreaView>
    );
  }

  const planCards = useMemo(() => PLANS.map((plan) => {
    const isCurrent = tier === plan.id;
    const product = products.find(p => p.productId === plan.productId);
    const price = product?.localizedPrice || plan.defaultPrice;
    const period = plan.defaultPeriod;

    return (
      <TouchableOpacity
        key={plan.id}
        style={[
          styles.plan,
          isCurrent && styles.activePlan,
          plan.popular && styles.popularPlan,
          { backgroundColor: card, borderColor: isCurrent ? primary : border }
        ]}
        onPress={() => handlePurchase(plan)}
        activeOpacity={0.85}
        disabled={!!loadingId || plan.id === 'free'}
      >
        {plan.popular && (
          <View style={[styles.badge, { backgroundColor: '#F59E0B' }]}>
            <Text style={styles.badgeText}>{isAr ? 'الأكثر شيوعاً' : 'Most Popular'}</Text>
          </View>
        )}
        {plan.highlight && (
          <View style={[styles.badge, { backgroundColor: '#8B5CF6' }]}>
            <Text style={styles.badgeText}>{isAr ? 'أفضل قيمة' : 'Best Value'}</Text>
          </View>
        )}
        {plan.trialDays > 0 && !isCurrent && (
          <View style={[styles.badge, styles.trialBadge]}>
            <Text style={styles.badgeText}>{isAr ? `تجربة ${plan.trialDays} يوم مجاناً` : `${plan.trialDays}-day free trial`}</Text>
          </View>
        )}

        <View style={styles.planHeader}>
          <Text style={[styles.planName, { color: txt }]}>{plan.name}</Text>
          <Text style={[styles.tagline, { color: primary }]}>{plan.tagline}</Text>
          <View style={styles.priceRow}>
            <Text style={[styles.planPrice, { color: txt }]}>{price}</Text>
            {period ? <Text style={[styles.planPeriod, { color: sub }]}>{period}</Text> : null}
          </View>
        </View>

        <ConsciousnessBar layers={plan.consciousnessLayers} planId={plan.id} />

        <View style={styles.featuresList}>
          {plan.features.map((f, i) => {
            const Icon = f.icon;
            return (
              <View key={i} style={styles.featureRow}>
                {Icon ? <Icon size={14} stroke="#10B981" /> : <CheckCircle2 size={14} stroke="#10B981" />}
                <Text style={[styles.feature, { color: sub }]}>{f.text}</Text>
              </View>
            );
          })}
        </View>

        <View style={[styles.selectBtn, { backgroundColor: isCurrent ? '#10B981' : primary }]}>
          {loadingId === plan.id ? (
            <ActivityIndicator color="#FFF" size="small" />
          ) : (
            <Text style={styles.selectBtnText}>
              {isCurrent ? (isAr ? 'مفعّل' : 'Active') : plan.id === 'free' ? (isAr ? 'الحالي' : 'Current') : (isAr ? 'ابدأ الآن' : 'Start Now')}
            </Text>
          )}
        </View>
      </TouchableOpacity>
    );
  }), [PLANS, products, tier, loadingId, isDark, isAr, card, border, primary, txt, sub]);

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      <Header />
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <View style={styles.titleSection}>
          <Crown size={40} stroke={primary} style={{ alignSelf: 'center', marginBottom: 16 }} />
          <Text style={[styles.title, { color: txt }]}>
            {isAr ? 'ارتقِ بوعي توأمك' : "Elevate Your Twin's Consciousness"}
          </Text>
          <Text style={[styles.subtitle, { color: sub }]}>
            {isAr ? 'كل باقة تفتح طبقة جديدة من الوعي' : 'Each plan unlocks a new layer of consciousness'}
          </Text>
        </View>

        <View style={[styles.securityBadge, { backgroundColor: card, borderColor: border }]}>
          <Shield size={18} stroke="#10B981" />
          <Text style={[styles.securityText, { color: sub }]}>
            {isAr ? 'مدفوعات آمنة عبر متجر التطبيقات' : 'Secure payments via App Store'}
          </Text>
        </View>

        {planCards}

        <TouchableOpacity style={styles.restoreBtn} onPress={handleRestore} disabled={!!loadingId}>
          <Text style={[styles.restoreText, { color: primary }]}>
            {isAr ? 'استعادة الاشتراك السابق' : 'Restore Purchase'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.manageBtn} onPress={() => {
          const url = Platform.OS === 'ios'
            ? 'https://apps.apple.com/account/subscriptions'
            : 'https://play.google.com/store/account/subscriptions';
          Linking.openURL(url);
        }}>
          <Text style={[styles.manageText, { color: primary }]}>
            {isAr ? 'إدارة الاشتراك' : 'Manage Subscription'}
          </Text>
        </TouchableOpacity>

        <Text style={[styles.footerNote, { color: sub }]}>
          {isAr ? 'يمكنك الإلغاء في أي وقت.' : 'Cancel anytime.'}
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  container: { flex: 1 },
  content: { paddingBottom: 40, paddingTop: 8 },
  titleSection: { padding: 24, paddingTop: 20, alignItems: 'center' },
  title: { fontSize: 26, fontWeight: '800', textAlign: 'center' },
  subtitle: { fontSize: 14, textAlign: 'center', marginTop: 8, lineHeight: 22 },
  securityBadge: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 10, borderRadius: 12, borderWidth: 1, marginHorizontal: 16, marginBottom: 16 },
  securityText: { fontSize: 13, fontWeight: '600' },
  plan: { padding: 20, borderRadius: 20, marginHorizontal: 16, marginBottom: 16, borderWidth: 1.5 },
  activePlan: { borderWidth: 2 },
  popularPlan: { borderWidth: 2 },
  badge: { paddingHorizontal: 12, paddingVertical: 5, borderRadius: 10, alignSelf: 'flex-start', marginBottom: 12 },
  badgeText: { color: '#FFF', fontSize: 12, fontWeight: '700' },
  trialBadge: { backgroundColor: '#10B981' },
  planHeader: { marginBottom: 16 },
  planName: { fontSize: 22, fontWeight: '800', marginBottom: 4 },
  tagline: { fontSize: 13, fontWeight: '600', marginBottom: 8, fontStyle: 'italic' },
  priceRow: { flexDirection: 'row', alignItems: 'baseline', gap: 4 },
  planPrice: { fontSize: 32, fontWeight: '800' },
  planPeriod: { fontSize: 15 },
  featuresList: { marginBottom: 8 },
  featureRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 8, marginBottom: 8 },
  feature: { fontSize: 14, lineHeight: 20, flex: 1 },
  selectBtn: { padding: 14, borderRadius: 12, marginTop: 12, alignItems: 'center' },
  selectBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  restoreBtn: { alignItems: 'center', padding: 16, marginTop: 8 },
  restoreText: { fontSize: 14, textDecorationLine: 'underline' },
  manageBtn: { alignItems: 'center', padding: 8 },
  manageText: { fontSize: 14 },
  footerNote: { textAlign: 'center', fontSize: 12, marginTop: 8, marginHorizontal: 24 },
});
