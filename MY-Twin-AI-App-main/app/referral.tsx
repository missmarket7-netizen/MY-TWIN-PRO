import {
  SafeAreaView, View, Text, TouchableOpacity, StyleSheet,
  Alert, TextInput, Share, ActivityIndicator, ScrollView, RefreshControl
} from 'react-native';
import { useState, useEffect, useCallback } from 'react';
import { useTwinStore } from '../store/useTwinStore';
import { API } from '../lib/api';
import { supabase } from '../lib/supabase';
import Header from '../components/Header';
import { Stack } from 'expo-router';
import {
  Gift, Copy, Share2, Users, Zap, Crown, CheckCircle2,
  UserPlus, Sparkles, TrendingUp, ArrowRight, Ticket
} from 'lucide-react-native';

interface ReferralStats {
  invitedCount: number;
  earnedTokens: number;
}

const REWARD_TIERS = [
  { count: 5, reward_ar: 'أسبوع Premium', reward_en: 'Premium Week', icon: Zap, color: '#F59E0B' },
  { count: 10, reward_ar: 'شهر Premium', reward_en: 'Premium Month', icon: Crown, color: '#8B5CF6' },
  { count: 25, reward_ar: 'Pro Access', reward_en: 'Pro Access', icon: Sparkles, color: '#EC4899' },
];

export default function Referral() {
  const { lang, theme, userId } = useTwinStore();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';
  const t = (ar: string, en: string) => (isAr ? ar : en);

  const [code, setCode] = useState('');
  const [myCode, setMyCode] = useState('');
  const [myLink, setMyLink] = useState('');
  const [stats, setStats] = useState<ReferralStats>({ invitedCount: 0, earnedTokens: 0 });
  const [loadingGenerate, setLoadingGenerate] = useState(false);
  const [loadingActivate, setLoadingActivate] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [copied, setCopied] = useState(false);

  const bg = isDark ? '#1A1A1A' : '#F8F6F2';
  const card = isDark ? '#2A2A2A' : '#FFF';
  const border = isDark ? '#444' : '#F0F0F0';
  const txt = isDark ? '#FFF' : '#1A1A1A';
  const sub = isDark ? '#888' : '#666';
  const primary = isDark ? '#D8B4FE' : '#6B21A8';

  const fetchReferralData = useCallback(async (showRefresh = false) => {
    if (!userId) return;
    if (showRefresh) setRefreshing(true);
    try {
      const { data: profile } = await supabase.from('profiles').select('referral_code').eq('id', userId).single();
      if (profile?.referral_code) {
        setMyCode(profile.referral_code);
        setMyLink(`https://mytwin.app/join?ref=${profile.referral_code}`);
      }
      const { data: referrals, error } = await supabase.from('referral_usage').select('id, activated_at').eq('inviter_id', userId);
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
    <SafeAreaView style={[styles.safe, { backgroundColor: bg }]}>
      <Stack.Screen options={{ headerShown: false }} />
      <Header />

      <ScrollView
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#6B21A8']} />}
      >
        <Text style={[styles.title, { color: txt }]}>{t('نظام الدعوات', 'Referral System')}</Text>
        <Text style={[styles.subtitle, { color: sub }]}>
          {t('ادعُ أصدقاءك واربح مكافآت!', 'Invite friends and earn rewards!')}
        </Text>

        <View style={[styles.statsCard, { backgroundColor: card, borderColor: border }]}>
          <View style={styles.statItem}>
            <Users size={24} stroke="#6B21A8" />
            <Text style={[styles.statValue, { color: txt }]}>{stats.invitedCount}</Text>
            <Text style={[styles.statLabel, { color: sub }]}>{t('صديق مدعو', 'Friends Invited')}</Text>
          </View>
          <View style={[styles.statDivider, { backgroundColor: border }]} />
          <View style={styles.statItem}>
            <Zap size={24} stroke="#F59E0B" />
            <Text style={[styles.statValue, { color: txt }]}>{stats.earnedTokens}</Text>
            <Text style={[styles.statLabel, { color: sub }]}>{t('توكن مكتسب', 'Earned Tokens')}</Text>
          </View>
        </View>

        <View style={[styles.section, { backgroundColor: card, borderColor: border }]}>
          <Text style={[styles.sectionTitle, { color: txt }]}>{t('كود الدعوة الخاص بي', 'My Referral Code')}</Text>
          {myCode ? (
            <>
              <View style={[styles.codeBox, { backgroundColor: isDark ? '#333' : '#F3F0FF' }]}>
                <Text style={[styles.codeText, { color: primary }]}>{myCode}</Text>
              </View>
              <View style={[styles.codeActions, isAr && { flexDirection: 'row-reverse' }]}>
                <TouchableOpacity style={[styles.actionBtn, { backgroundColor: primary }]} onPress={handleCopy}>
                  {copied ? <CheckCircle2 size={18} stroke="#FFF" /> : <Copy size={18} stroke="#FFF" />}
                  <Text style={styles.actionBtnText}>{copied ? t('تم النسخ', 'Copied') : t('نسخ', 'Copy')}</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.actionBtn, { backgroundColor: '#10B981' }]} onPress={handleShare}>
                  <Share2 size={18} stroke="#FFF" />
                  <Text style={styles.actionBtnText}>{t('مشاركة', 'Share')}</Text>
                </TouchableOpacity>
              </View>
              <Text style={[styles.link, { color: sub }]} numberOfLines={1}>{myLink}</Text>
            </>
          ) : (
            <TouchableOpacity style={[styles.generateBtn, { backgroundColor: primary }]} onPress={generateCode} disabled={loadingGenerate}>
              {loadingGenerate ? <ActivityIndicator color="#FFF" /> : (
                <>
                  <Ticket size={20} stroke="#FFF" />
                  <Text style={styles.generateBtnText}>{t('إنشاء كود الدعوة', 'Generate Referral Code')}</Text>
                </>
              )}
            </TouchableOpacity>
          )}
        </View>

        <View style={[styles.section, { backgroundColor: card, borderColor: border }]}>
          <Text style={[styles.sectionTitle, { color: txt }]}>{t('تفعيل كود صديق', 'Activate a Friend Code')}</Text>
          <View style={[styles.activateRow, isAr && { flexDirection: 'row-reverse' }]}>
            <TextInput
              style={[styles.input, { backgroundColor: isDark ? '#333' : '#F8F6F2', color: txt, borderColor: border }]}
              placeholder="MTXXXXXX"
              placeholderTextColor={sub}
              value={code}
              onChangeText={setCode}
              autoCapitalize="characters"
              maxLength={10}
            />
            <TouchableOpacity
              style={[styles.activateBtn, { backgroundColor: code.trim().length >= 6 ? '#6B21A8' : border }]}
              onPress={activateCode}
              disabled={loadingActivate || code.trim().length < 6}
            >
              {loadingActivate ? <ActivityIndicator color="#FFF" /> : (
                <>
                  <ArrowRight size={18} stroke="#FFF" />
                  <Text style={styles.activateBtnText}>{t('تفعيل', 'Activate')}</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        </View>

        <View style={[styles.section, { backgroundColor: card, borderColor: border }]}>
          <Text style={[styles.sectionTitle, { color: txt }]}>{t('مستويات المكافآت', 'Reward Tiers')}</Text>
          {REWARD_TIERS.map((tier, i) => {
            const Icon = tier.icon;
            const achieved = stats.invitedCount >= tier.count;
            return (
              <View key={i} style={[styles.tierRow, { borderColor: border }]}>
                <View style={[styles.tierIcon, { backgroundColor: tier.color + '20' }]}>
                  <Icon size={20} stroke={tier.color} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={[styles.tierReward, { color: txt }]}>
                    {t(`ادعُ ${tier.count} أصدقاء`, `Invite ${tier.count} Friends`)}
                  </Text>
                  <Text style={[styles.tierDesc, { color: sub }]}>
                    {t(`احصل على ${tier.reward_ar}`, `Get ${tier.reward_en}`)}
                  </Text>
                </View>
                {achieved ? (
                  <CheckCircle2 size={22} stroke="#10B981" />
                ) : (
                  <Text style={[styles.tierProgress, { color: sub }]}>
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

const styles = StyleSheet.create({
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
