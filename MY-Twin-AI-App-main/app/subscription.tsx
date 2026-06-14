import {
  SafeAreaView, View, Text, TouchableOpacity, StyleSheet,
  ScrollView, Alert, ActivityIndicator, Platform, Linking
} from 'react-native';
import { router } from 'expo-router';
import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { initIAP, getProducts, purchaseSubscription, restorePurchases, TIER_MAP } from '../lib/iapService';
import { Tier, useTwinStore } from '../store/useTwinStore';
import { CheckCircle2, Crown, ArrowLeft, Shield, CreditCard } from 'lucide-react-native';
import { supabase } from '../lib/supabase';

interface StoreProduct {
  productId: string;
  localizedPrice: string;
  price: number;
  currency: string;
  title: string;
  description: string;
}

const TIER_RANK: Record<string, number> = {
  free: 0, plus: 1, premium: 2, pro: 3, yearly: 4,
};

interface Plan {
  id: Tier;
  name: string;
  defaultPrice: string;
  defaultPeriod: string;
  productId?: string;
  trialDays: number;
  tagline: string;
  consciousnessLayers: number;
  features: string[];
  popular?: boolean;
}

const PLANS: Plan[] = [
  {
    id: 'free', name: 'Free', defaultPrice: '0', defaultPeriod: 'للأبد',
    trialDays: 0, tagline: 'ابدأ رحلتك مع توأمك', consciousnessLayers: 1,
    features: ['طبقة وعي واحدة', '15 رسالة يومياً', 'ذاكرة 3 أيام', 'عربي وإنجليزي']
  },
  {
    id: 'plus', name: 'Plus', defaultPrice: '9', defaultPeriod: '/شهر',
    trialDays: 5, tagline: 'توأم يفهمك أكثر كل يوم', consciousnessLayers: 2,
    productId: 'plus_monthly',
    features: ['طبقتا وعي', '50 رسالة يومياً', 'ذاكرة 30 يوم', 'التحدث بصوتك', 'إشعارات يومية', 'تخصيص التوأم']
  },
  {
    id: 'premium', name: 'Premium', defaultPrice: '19', defaultPeriod: '/شهر',
    trialDays: 3, tagline: 'وعي حقيقي يرافقك', consciousnessLayers: 3,
    productId: 'premium_monthly',
    features: ['3 طبقات وعي', '150 رسالة يومياً', 'ذاكرة 6 أشهر', 'تحليل أحلامك', 'تدريب حياتي', 'موسيقى وترفيه', 'تقويم ذكي']
  },
  {
    id: 'pro', name: 'Pro', defaultPrice: '110', defaultPeriod: '/6 أشهر',
    trialDays: 0, tagline: 'توأم بوعي متكامل', consciousnessLayers: 4,
    productId: 'pro_semiannual',
    features: ['4 طبقات وعي', '500 رسالة يومياً', 'ذاكرة عميقة', 'منزل ذكي', 'إدارة البريد', 'كاميرا مفتوحة']
  },
  {
    id: 'yearly', name: 'Yearly', defaultPrice: '199', defaultPeriod: '/سنة',
    trialDays: 0, popular: true, tagline: 'أعمق محاكاة للوعي', consciousnessLayers: 5,
    productId: 'yearly_annual',
    features: ['5 طبقات وعي كاملة', 'رسائل غير محدودة', 'ذاكرة دائمة', 'وعي استباقي', 'كل الميزات', 'أقصى سرعة', 'دعم VIP']
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
        if (!iapInitialized.current) {
          await initIAP();
          iapInitialized.current = true;
        }
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

  const getPlanDisplay = useCallback((plan: Plan) => {
    const product = products.find(p => p.productId === plan.productId);
    if (product) {
      return { price: product.localizedPrice || `$${plan.defaultPrice}`, period: '', currency: product.currency, originalPrice: '' };
    }
    return { price: `$${plan.defaultPrice}`, period: plan.defaultPeriod, currency: 'USD', originalPrice: '' };
  }, [products]);

  // ✅ تحقق أمني من الإيصال عبر Supabase Edge Function
  const verifyReceipt = async (receipt: string, productId: string): Promise<boolean> => {
    try {
      const { data, error } = await supabase.functions.invoke('verify-receipt', {
        body: { receipt, productId, platform: Platform.OS },
      });
      if (error) throw error;
      return data?.valid === true;
    } catch (e) {
      console.warn('⚠️ فشل التحقق من الإيصال:', e);
      // في بيئة التطوير: نقبل الإيصال. في الإنتاج: نرفضه.
      return __DEV__ ? true : false;
    }
  };

  // ✅ تأكيد وجود وسيلة دفع (للتجارب المجانية)
  const checkPaymentMethod = async (): Promise<boolean> => {
    // في بيئة حقيقية، هذا يتحقق عبر Google Play / App Store API
    // للمحاكاة: نتحقق من وجود products كدليل على توفر IAP
    return iapAvailable && products.length > 0;
  };

  const handlePurchase = async (plan: Plan) => {
    if (loadingId || !plan.productId) return;
    if (plan.id === 'free') {
      Alert.alert('Free', isAr ? 'أنت على الباقة المجانية.' : 'You are on the free plan.');
      return;
    }
    if (!iapAvailable) {
      Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'خدمة الشراء غير متاحة' : 'Purchase unavailable');
      return;
    }

    // ✅ التحقق من وسيلة الدفع قبل التجربة المجانية
    if (plan.trialDays > 0) {
      const hasPayment = await checkPaymentMethod();
      if (!hasPayment) {
        Alert.alert(
          isAr ? 'وسيلة دفع مطلوبة' : 'Payment Method Required',
          isAr
            ? 'يجب إضافة وسيلة دفع لتفعيل الفترة التجريبية. سيتم خصم المبلغ بعد انتهاء التجربة في حال عدم الإلغاء.'
            : 'A payment method is required to activate the trial. You will be charged after the trial ends unless cancelled.',
          [
            { text: isAr ? 'إلغاء' : 'Cancel', style: 'cancel' },
            { text: isAr ? 'متابعة' : 'Continue', onPress: async () => await executePurchase(plan) },
          ]
        );
        return;
      }
    }

    await executePurchase(plan);
  };

  const executePurchase = async (plan: Plan) => {
    if (!plan.productId) return;
    setLoadingId(plan.id);
    try {
      const purchaseResult = await purchaseSubscription(plan.productId);
      if (!purchaseResult) throw new Error('Purchase failed');

      if (typeof purchaseResult === 'string') {
        const verified = await verifyReceipt(purchaseResult, plan.productId);
        if (!verified) {
          Alert.alert(
            isAr ? 'فشل التحقق' : 'Verification Failed',
            isAr ? 'تعذر التحقق من عملية الشراء. تم إلغاء العملية.' : 'Could not verify purchase. Transaction cancelled.'
          );
          return;
        }
      }

      const newTier = TIER_MAP[plan.productId];
      if (newTier) {
        updateTier(newTier as Tier);
        if (plan.trialDays > 0) setHasUsedTrial(true);
        Alert.alert(isAr ? '✅ تم!' : '✅ Done!', isAr ? 'تم تفعيل اشتراكك بنجاح' : 'Subscription activated successfully');
        router.back();
      }
    } catch (e: any) {
      const msg = e?.message || '';
      if (msg.includes('cancelled') || msg.includes('Cancel')) {
        // المستخدم ألغى بنفسه — لا نعرض خطأ
        return;
      }
      Alert.alert(isAr ? 'خطأ' : 'Error', msg || (isAr ? 'فشل الشراء' : 'Purchase failed'));
    } finally {
      setLoadingId(null);
    }
  };

  const handleRestore = async () => {
    setLoadingId('restore');
    try {
      const purchases = await restorePurchases();
      if (purchases.length > 0) {
        const best = purchases
          .map(p => ({ ...p, rank: TIER_RANK[TIER_MAP[p.productId] || 'free'] || 0 }))
          .sort((a, b) => b.rank - a.rank)[0];
        const restoredTier = TIER_MAP[best.productId];
        if (restoredTier) {
          updateTier(restoredTier as Tier);
          Alert.alert(isAr ? '✅ تم' : '✅ Done', isAr ? 'تم استعادة اشتراكك!' : 'Subscription restored!');
          router.back();
        }
      } else {
        Alert.alert(isAr ? 'تنبيه' : 'Notice', isAr ? 'لم يتم العثور على اشتراك.' : 'No subscription found.');
      }
    } catch (e) {
      Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'فشلت الاستعادة.' : 'Restore failed.');
    } finally {
      setLoadingId(null);
    }
  };

  const planCards = useMemo(() => PLANS.map((plan) => {
    const { price, period } = getPlanDisplay(plan);
    const isCurrent = tier === plan.id;
    const showTrial: boolean = plan.trialDays > 0 && !isCurrent && !hasUsedTrial;
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
        accessibilityRole="button"
        accessibilityLabel={`${plan.name} ${price}`}
      >
        {plan.popular && <View style={[styles.badge, { backgroundColor: '#F59E0B' }]}><Text style={styles.badgeText}>{isAr ? 'الأفضل قيمة' : 'Best Value'}</Text></View>}
        {showTrial && <View style={[styles.badge, styles.trialBadge]}><Text style={styles.badgeText}>{isAr ? `تجربة ${plan.trialDays} يوم` : `${plan.trialDays}-day trial`}</Text></View>}
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
          {plan.features.map((f, i) => (
            <View key={i} style={styles.featureRow}>
              <CheckCircle2 size={15} stroke="#10B981" />
              <Text style={[styles.feature, { color: sub }]}>{f}</Text>
            </View>
          ))}
        </View>
        <View style={[styles.selectBtn, { backgroundColor: isCurrent ? '#10B981' : primary }]}>
          {loadingId === plan.id ? (
            <ActivityIndicator color="#FFF" size="small" />
          ) : (
            <Text style={styles.selectBtnText}>
              {isCurrent ? (isAr ? 'مفعّل' : 'Active') : (isAr ? 'ابدأ الآن' : 'Start Now')}
            </Text>
          )}
        </View>
      </TouchableOpacity>
    );
  }), [PLANS, getPlanDisplay, tier, loadingId, isDark, isAr, hasUsedTrial, card, border, primary, txt, sub]);

  if (initLoading) {
    return (
      <SafeAreaView style={[styles.safe, { backgroundColor: bg }, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={primary} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      {/* Header احترافي */}
      <View style={[styles.header, { borderBottomColor: border }]}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <ArrowLeft size={24} stroke={txt} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: txt }]}>
          {isAr ? 'الاشتراكات' : 'Subscriptions'}
        </Text>
        <View style={styles.backBtn} />
      </View>

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

        {/* ✅ أيقونة الأمان */}
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
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1 },
  backBtn: { width: 36, height: 36, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { fontSize: 20, fontWeight: '700', textAlign: 'center', flex: 1 },
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
