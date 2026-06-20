import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Modal, ActivityIndicator } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import { apiPost } from '../lib/httpClient';
import { Play, BatteryCharging, X } from 'lucide-react-native';

export function AdModal({ visible, onClose, onReward }: { visible: boolean; onClose: () => void; onReward: (energy: number) => void }) {
  const { lang } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const [loading, setLoading] = useState(false);

  const handleWatchAd = async () => {
    setLoading(true);
    try {
      const data = await apiPost('/api/ads/reward', { ad_type: 'rewarded' });
      if (data.success) {
        onReward(data.reward || 3);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); onClose(); }
  };

  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.overlay}>
        <View style={styles.card}>
          <TouchableOpacity onPress={onClose} style={styles.closeBtn}><X size={20} stroke="#6B7280" /></TouchableOpacity>
          <BatteryCharging size={48} stroke="#6B21A8" style={{ alignSelf: 'center', marginBottom: 16 }} />
          <Text style={styles.title}>{t('الطاقة منتهية', 'Out of Energy')}</Text>
          <Text style={styles.body}>{t('شاهد إعلاناً واحصل على 3 رسائل إضافية', 'Watch an ad and get 3 extra messages')}</Text>
          <TouchableOpacity style={styles.watchBtn} onPress={handleWatchAd} disabled={loading}>
            {loading ? <ActivityIndicator color="#FFF" /> : <><Play size={18} stroke="#FFF" /><Text style={styles.watchText}>{t('مشاهدة', 'Watch')}</Text></>}
          </TouchableOpacity>
          <TouchableOpacity onPress={onClose} style={styles.skipBtn}>
            <Text style={styles.skipText}>{t('تخطي', 'Skip')}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)', padding: 24 },
  card: { backgroundColor: '#FFF', borderRadius: 24, padding: 28, width: '100%', maxWidth: 350, alignItems: 'center' },
  closeBtn: { position: 'absolute', top: 12, right: 12, padding: 4 },
  title: { fontSize: 20, fontWeight: '800', color: '#1A1226', marginBottom: 12 },
  body: { fontSize: 15, color: '#6B7280', textAlign: 'center', lineHeight: 22, marginBottom: 24 },
  watchBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: '#6B21A8', paddingHorizontal: 28, paddingVertical: 14, borderRadius: 14, width: '100%', justifyContent: 'center' },
  watchText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
  skipBtn: { marginTop: 12, padding: 8 },
  skipText: { color: '#9CA3AF', fontSize: 14 },
});
