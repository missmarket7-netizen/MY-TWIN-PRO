import {
  SafeAreaView, View, Text, TouchableOpacity, StyleSheet,
  Alert, TextInput, Share, ActivityIndicator, ScrollView, RefreshControl
} from 'react-native';
import { useState, useEffect, useCallback } from 'react';
import { useTwinStore } from '../store/useTwinStore';
import { API } from '../lib/api';
import { supabase } from '../lib/supabase';
import {
  Gift, Copy, Share2, Users, Zap, Crown, CheckCircle2,
  UserPlus, Sparkles, TrendingUp, ArrowRight, Ticket
} from 'lucide-react-native';

interface ReferralStats {
  invitedCount: number;
  earnedTokens: number;
}

const REWARD_TIERS = [
  { count: 5, reward: 'Premium Week', icon: Zap, color: '#F59E0B' },
  { count: 10, reward: 'Premium Month', icon: Crown, color: '#8B5CF6' },
  { count: 25, reward: 'Pro Access', icon: Sparkles, color: '#EC4899' },
];

export default function Referral() {
  const { lang, theme, userId } = useTwinStore();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';
  const t = (ar: string, en: string) => (isAr ? ar : en);
  const colors = isDark ? darkColors : lightColors;

  const [code, setCode] = useState('');
  const [myCode, setMyCode] = useState('');
  const [myLink, setMyLink] = useState('');
  const [stats, setStats] = useState<ReferralStats>({ invitedCount: 0, earnedTokens: 0 });
  const [loadingGenerate, setLoadingGenerate] = useState(false);
  const [loadingActivate, setLoadingActivate] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [copied, setCopied] = useState(false);

  // جلب بيانات الإحالة عند التحميل
  const fetchReferralData = useCallback(async (showRefresh = false) => {
    if (!userId) return;
    if (showRefresh) setRefreshing(true);

    try {
      // جلب كود الإحالة الحالي من Supabase
      const { data: profile } = await supabase
        .from('profiles')
        .select('referral_code')
        .eq('id', userId)
        .single();

      if (profile?.referral_code) {
        setMyCode(profile.referral_code);
        setMyLink(`https://mytwin.app/join?ref=${profile.referral_code}`);
      }

      // جلب إحصائيات الدعوات
      const { data: referrals, error } = await supabase
        .from('referral_usage')
        .select('id, activated_at')
        .eq('inviter_id', userId);

      if (!error && referrals) {
        setStats({
          invitedCount: referrals.length,
          earnedTokens: referrals.length * 500,
        });
      }
    } catch (e) {
      console.error('Fetch referral error:', e);
    } finally {
      if (showRefresh) setRefreshing(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchReferralData();
  }, [fetchReferralData]);

  const generateCode = async () => {
    if (!userId) return;
    setLoadingGenerate(true);
    try {
      const { data } = await API.post('/api/referral/generate');
      if (data.code) {
        setMyCode(data.code);
        setMyLink(`https://mytwin.app/join?ref=${data.code}`);
      }
    } catch {
      Alert.alert(t('خطأ', 'Error'), t('تعذر إنشاء كود الدعوة.', 'Could not generate code.'));
    } finally {
      setLoadingGenerate(false);
    }
  };

  const activateCode = async () => {
    if (!code.trim() || code.trim().length < 6) {
      Alert.alert(t('خطأ', 'Error'), t('أدخل كوداً صحيحاً (6 أحرف على الأقل).', 'Enter a valid code (min 6 chars).'));
      return;
    }
    if (!userId) return;
    setLoadingActivate(true);
    try {
      const { data } = await API.post('/api/referral/activate', { code: code.trim().toUpperCase() });
      if (data.success) {
        Alert.alert(
          t('🎉 تم!', '🎉 Success!'),
          t(`حصلت على ${data.bonus_tokens || 500} توكن!`, `You earned ${data.bonus_tokens || 500} tokens!`)
        );
        setCode('');
        fetchReferralData(true);
      } else {
        Alert.alert(t('خطأ', 'Error'), t('كود غير صالح أو مستخدم.', 'Invalid or already used code.'));
      }
    } catch {
      Alert.alert(t('خطأ', 'Error'), t('تعذر تفعيل الكود.', 'Could not activate code.'));
    } finally {
      setLoadingActivate(false);
    }
  };

  const handleShare = async () => {
    if (!myLink) return;
    try {
      await Share.share({
        message: isAr
          ? `استخدم كود الدعوة ${myCode} للانضمام إلى MyTwin! 💜 ${myLink}`
          : `Use my invite code ${myCode} to join MyTwin! 💜 ${myLink}`,
      });
    } catch (e) {
      console.error('Share error:', e);
    }
  };

  const handleCopy = () => {
    if (!myCode) return;
    try {
      // استخدام Clipboard API
      const Clipboard = require('expo-clipboard');
      Clipboard.setStringAsync(myCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      Alert.alert(t('تم', 'Copied'), t('تم نسخ الكود!', 'Code copied!'));
    }
  };

  const onRefresh = () => fetchReferralData(true);

  return (
    <SafeAreaView style={[s.safe, { backgroundColor: colors.bg }]}>
      <ScrollView
        contentContainerStyle={s.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#6B21A8']} />}
      >
        {/* العنوان */}
        <Text style={[s.title, { color: colors.text }]}>{t('نظام الدعوات', 'Referral System')}</Text>
        <Text style={[s.subtitle, { color: colors.subtext }]}>
          {t('ادعُ أصدقاءك واربح مكافآت!', 'Invite friends and earn rewards!')}
        </Text>

        {/* بطاقة الإحصائيات */}
        <View style={[s.statsCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={s.statItem}>
            <Users size={24} stroke="#6B21A8" />
            <Text style={[s.statValue, { color: colors.text }]}>{stats.invitedCount}</Text>
            <Text style={[s.statLabel, { color: colors.subtext }]}>{t('صديق مدعو', 'Friends Invited')}</Text>
          </View>
          <View style={[s.statDivider, { backgroundColor: colors.border }]} />
          <View style={s.statItem}>
            <Zap size={24} stroke="#F59E0B" />
            <Text style={[s.statValue, { color: colors.text }]}>{stats.earnedTokens}</Text>
            <Text style={[s.statLabel, { color: colors.subtext }]}>{t('توكن مكتسب', 'Earned Tokens')}</Text>
          </View>
        </View>

        {/* كودي */}
        <View style={[s.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <Text style={[s.sectionTitle, { color: colors.text }]}>{t('كود الدعوة الخاص بي', 'My Referral Code')}</Text>
          {myCode ? (
            <>
              <View style={[s.codeBox, { backgroundColor: isDark ? '#333' : '#F3F0FF' }]}>
                <Text style={[s.codeText, { color: colors.primary }]}>{myCode}</Text>
              </View>
              <View style={[s.codeActions, isAr && { flexDirection: 'row-reverse' }]}>
                <TouchableOpacity style={[s.actionBtn, { backgroundColor: colors.primary }]} onPress={handleCopy}>
                  {copied ? <CheckCircle2 size={18} stroke="#FFF" /> : <Copy size={18} stroke="#FFF" />}
                  <Text style={s.actionBtnText}>{copied ? t('تم النسخ', 'Copied') : t('نسخ', 'Copy')}</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[s.actionBtn, { backgroundColor: '#10B981' }]} onPress={handleShare}>
                  <Share2 size={18} stroke="#FFF" />
                  <Text style={s.actionBtnText}>{t('مشاركة', 'Share')}</Text>
                </TouchableOpacity>
              </View>
              <Text style={[s.link, { color: colors.subtext }]} numberOfLines={1}>{myLink}</Text>
            </>
          ) : (
            <TouchableOpacity style={[s.generateBtn, { backgroundColor: colors.primary }]} onPress={generateCode} disabled={loadingGenerate}>
              {loadingGenerate ? <ActivityIndicator color="#FFF" /> : (
                <>
                  <Ticket size={20} stroke="#FFF" />
                  <Text style={s.generateBtnText}>{t('إنشاء كود الدعوة', 'Generate Referral Code')}</Text>
                </>
              )}
            </TouchableOpacity>
          )}
        </View>

        {/* تفعيل كود */}
        <View style={[s.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <Text style={[s.sectionTitle, { color: colors.text }]}>{t('تفعيل كود صديق', 'Activate a Friend Code')}</Text>
          <View style={[s.activateRow, isAr && { flexDirection: 'row-reverse' }]}>
            <TextInput
              style={[s.input, { backgroundColor: isDark ? '#333' : '#F8F6F2', color: colors.text, borderColor: colors.border }]}
              placeholder="MTXXXXXX"
              placeholderTextColor={colors.subtext}
              value={code}
              onChangeText={setCode}
              autoCapitalize="characters"
              maxLength={10}
            />
            <TouchableOpacity
              style={[s.activateBtn, { backgroundColor: code.trim().length >= 6 ? '#6B21A8' : colors.border }]}
              onPress={activateCode}
              disabled={loadingActivate || code.trim().length < 6}
            >
              {loadingActivate ? <ActivityIndicator color="#FFF" /> : (
                <>
                  <ArrowRight size={18} stroke="#FFF" />
                  <Text style={s.activateBtnText}>{t('تفعيل', 'Activate')}</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        </View>

        {/* مستويات المكافآت */}
        <View style={[s.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <Text style={[s.sectionTitle, { color: colors.text }]}>{t('مستويات المكافآت', 'Reward Tiers')}</Text>
          {REWARD_TIERS.map((tier, i) => {
            const Icon = tier.icon;
            const achieved = stats.invitedCount >= tier.count;
            return (
              <View key={i} style={[s.tierRow, { borderColor: colors.border }]}>
                <View style={[s.tierIcon, { backgroundColor: tier.color + '20' }]}>
                  <Icon size={20} stroke={tier.color} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={[s.tierReward, { color: colors.text }]}>
                    {t(`ادعُ ${tier.count} أصدقاء`, `Invite ${tier.count} Friends`)}
                  </Text>
                  <Text style={[s.tierDesc, { color: colors.subtext }]}>
                    {t(`احصل على ${tier.reward}`, `Get ${tier.reward}`)}
                  </Text>
                </View>
                {achieved ? (
                  <CheckCircle2 size={22} stroke="#10B981" />
                ) : (
                  <Text style={[s.tierProgress, { color: colors.subtext }]}>
                    {stats.invitedCount}/{tier.count}
                  </Text>
                )}
              </View>
            );
          })}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const lightColors = {
  bg: '#F8F6F2',
  card: '#FFFFFF',
  border: '#F0F0F0',
  text: '#1A1A1A',
  subtext: '#666',
  primary: '#6B21A8',
};

const darkColors = {
  bg: '#1A1A1A',
  card: '#2A2A2A',
  border: '#444',
  text: '#FFFFFF',
  subtext: '#888',
  primary: '#D8B4FE',
};

const s = StyleSheet.create({
  safe: { flex: 1 },
  container: { padding: 20, paddingBottom: 40 },
  title: { fontSize: 24, fontWeight: '800', marginBottom: 6 },
  subtitle: { fontSize: 14, marginBottom: 24 },
  statsCard: { flexDirection: 'row', padding: 20, borderRadius: 20, borderWidth: 1, marginBottom: 20 },
  statItem: { flex: 1, alignItems: 'center' },
  statDivider: { width: 1, marginHorizontal: 12 },
  statValue: { fontSize: 28, fontWeight: '800', marginTop: 8 },
  statLabel: { fontSize: 13, marginTop: 4 },
  section: { padding: 20, borderRadius: 20, borderWidth: 1, marginBottom: 20 },
  sectionTitle: { fontSize: 17, fontWeight: '700', marginBottom: 16 },
  codeBox: { paddingVertical: 16, paddingHorizontal: 24, borderRadius: 14, alignItems: 'center', marginBottom: 14 },
  codeText: { fontSize: 28, fontWeight: '800', letterSpacing: 3 },
  codeActions: { flexDirection: 'row', gap: 10, marginBottom: 14 },
  actionBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 12, borderRadius: 12 },
  actionBtnText: { color: '#FFF', fontWeight: '700', fontSize: 15 },
  link: { fontSize: 13, textAlign: 'center' },
  generateBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 16, borderRadius: 14 },
  generateBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  activateRow: { flexDirection: 'row', gap: 10 },
  input: { flex: 1, padding: 14, borderRadius: 12, borderWidth: 1, fontSize: 16, letterSpacing: 1 },
  activateBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 20, borderRadius: 12 },
  activateBtnText: { color: '#FFF', fontWeight: '700', fontSize: 15 },
  tierRow: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 12, borderBottomWidth: 1 },
  tierIcon: { width: 40, height: 40, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  tierReward: { fontSize: 15, fontWeight: '600' },
  tierDesc: { fontSize: 13, marginTop: 2 },
  tierProgress: { fontSize: 14, fontWeight: '600' },
});
