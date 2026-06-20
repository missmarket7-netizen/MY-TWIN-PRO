import { useState, useEffect, useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert, RefreshControl, Modal, Platform, KeyboardAvoidingView, TextInput } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiGet, apiPost, apiPut, apiDelete } from '../../lib/httpClient';
import { ArrowLeft, Plus, CheckCircle2, Circle, Trash2, Calendar, Target, Clock, X, ExternalLink } from 'lucide-react-native';
import { FeatureErrorBoundary } from '../../components/FeatureErrorBoundary';
import { useFeatureColors } from '../../lib/useFeatureColors';
import { speakResponse } from '../../utils/voice_engine';

interface Task {
  id: string;
  title: string;
  due_date: string | null;
  priority: number;
  status: string;
  type: 'task' | 'google_calendar';
}

const PRIORITY_COLORS: Record<number, string> = { 1: '#9CA3AF', 2: '#60A5FA', 3: '#F59E0B', 4: '#F97316', 5: '#EF4444' };
const PRIORITY_LABELS: Record<number, { ar: string; en: string }> = {
  1: { ar: 'منخفض', en: 'Low' }, 2: { ar: 'متوسط', en: 'Medium' }, 3: { ar: 'عالي', en: 'High' },
  4: { ar: 'عاجل', en: 'Urgent' }, 5: { ar: 'حرج', en: 'Critical' },
};

export default function TaskManager() {
  const insets = useSafeAreaInsets();
  const { lang } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const colors = useFeatureColors();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDueDate, setNewDueDate] = useState('');
  const [newPriority, setNewPriority] = useState(3);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const fetchTasks = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true); else setLoading(true);
    setError('');
    try {
      const data = await apiGet('/api/calendar/all');
      setTasks(data.events || []);
    } catch (e) {
      setError(t('فشل تحميل المهام', 'Failed to load tasks'));
    } finally { setLoading(false); setRefreshing(false); }
  }, []);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const handleAddTask = async () => {
    if (!newTitle.trim()) return;
    setSaving(true);
    try {
      await apiPost('/api/tasks', { title: newTitle.trim(), priority: newPriority, due_date: newDueDate || null });
      setNewTitle(''); setNewDueDate(''); setNewPriority(3); setShowAddModal(false);
      fetchTasks(true);
    } catch (e: any) { Alert.alert(t('خطأ', 'Error'), e.message); }
    finally { setSaving(false); }
  };

  const handleComplete = async (taskId: string, currentStatus: string, type: string) => {
    if (type === 'google_calendar') return;
    const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    try {
      await apiPut(`/api/tasks/${taskId}`, { status: newStatus });
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (taskId: string, type: string) => {
    if (type === 'google_calendar') return;
    Alert.alert(t('حذف', 'Delete'), t('هل أنت متأكد؟', 'Are you sure?'), [
      { text: t('إلغاء', 'Cancel'), style: 'cancel' },
      { text: t('حذف', 'Delete'), style: 'destructive', onPress: async () => {
        try { await apiDelete(`/api/tasks/${taskId}`); setTasks(prev => prev.filter(t => t.id !== taskId)); }
        catch (e) { console.error(e); }
      }},
    ]);
  };

  const handleSpeak = (text: string) => {
    speakResponse(text).catch(() => {});
  };

  if (loading) {
    return (
      <View style={[st.container, { paddingTop: insets.top, justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color="#6B21A8" />
      </View>
    );
  }

  return (
    <FeatureErrorBoundary featureName={t('إدارة المهام', 'Task Manager')}>
      <View style={[st.container, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
        <View style={st.header}>
          <TouchableOpacity onPress={() => router.back()}><ArrowLeft size={24} stroke="#6B21A8" /></TouchableOpacity>
          <Text style={[st.headerTitle, { color: colors.text }]}>{t('إدارة المهام', 'Task Manager')}</Text>
          <TouchableOpacity onPress={() => setShowAddModal(true)} style={st.addBtn}><Plus size={22} stroke="#FFF" /></TouchableOpacity>
        </View>

        <ScrollView contentContainerStyle={st.content} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => fetchTasks(true)} colors={['#6B21A8']} />}>
          {error ? (
            <View style={st.errorCard}>
              <Text style={st.errorText}>{error}</Text>
              <TouchableOpacity onPress={() => fetchTasks(true)}><Text style={st.retryText}>{t('إعادة', 'Retry')}</Text></TouchableOpacity>
            </View>
          ) : tasks.length === 0 ? (
            <View style={st.empty}>
              <Target size={48} stroke="#7C6B99" />
              <Text style={[st.emptyText, { color: colors.subtext }]}>{t('لا توجد مهام', 'No tasks yet')}</Text>
            </View>
          ) : (
            tasks.map(task => (
              <View key={task.id} style={[st.taskCard, { backgroundColor: colors.card, borderColor: colors.border, borderLeftColor: task.type === 'google_calendar' ? '#4285F4' : PRIORITY_COLORS[task.priority] }]}>
                <TouchableOpacity onPress={() => handleComplete(task.id, task.status, task.type)}>
                  {task.status === 'completed' ? <CheckCircle2 size={22} stroke="#10B981" fill="#10B98120" /> : task.type === 'google_calendar' ? <Calendar size={22} stroke="#4285F4" /> : <Circle size={22} stroke={PRIORITY_COLORS[task.priority]} />}
                </TouchableOpacity>
                <View style={{ flex: 1 }}>
                  <Text style={[st.taskTitle, { color: colors.text }, task.status === 'completed' && { textDecorationLine: 'line-through', color: '#9CA3AF' }]}>{task.title}</Text>
                  <View style={{ flexDirection: 'row', gap: 8, alignItems: 'center', marginTop: 4 }}>
                    {task.type === 'google_calendar' ? (
                      <View style={[st.calendarBadge]}><ExternalLink size={10} stroke="#4285F4" /><Text style={[st.calendarText]}>Google</Text></View>
                    ) : (
                      <Text style={[st.priorityBadge, { backgroundColor: PRIORITY_COLORS[task.priority] + '20', color: PRIORITY_COLORS[task.priority] }]}>{isAr ? PRIORITY_LABELS[task.priority]?.ar : PRIORITY_LABELS[task.priority]?.en}</Text>
                    )}
                    {task.due_date && <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}><Calendar size={12} stroke="#7C6B99" /><Text style={st.dueDate}>{task.due_date}</Text></View>}
                  </View>
                </View>
                <View style={{ flexDirection: 'row', gap: 4 }}>
                  <TouchableOpacity onPress={() => handleSpeak(task.title)}><Text style={{ fontSize: 18 }}>🔊</Text></TouchableOpacity>
                  {task.type !== 'google_calendar' && <TouchableOpacity onPress={() => handleDelete(task.id, task.type)}><Trash2 size={16} stroke="#EF4444" /></TouchableOpacity>}
                </View>
              </View>
            ))
          )}
        </ScrollView>

        <Modal visible={showAddModal} transparent animationType="fade" onRequestClose={() => setShowAddModal(false)}>
          <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={st.modalOverlay}>
            <View style={[st.modalContent, { backgroundColor: colors.card }]}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <Text style={[st.modalTitle, { color: colors.text }]}>{t('مهمة جديدة', 'New Task')}</Text>
                <TouchableOpacity onPress={() => setShowAddModal(false)}><X size={22} stroke={colors.subtext} /></TouchableOpacity>
              </View>
              <TextInput style={[st.input, { backgroundColor: colors.inputBg, color: colors.text, borderColor: colors.border }]} placeholder={t('عنوان المهمة', 'Task title')} placeholderTextColor={colors.subtext} value={newTitle} onChangeText={setNewTitle} autoFocus />
              <TextInput style={[st.input, { backgroundColor: colors.inputBg, color: colors.text, borderColor: colors.border }]} placeholder={t('تاريخ التسليم (اختياري)', 'Due date (optional)')} placeholderTextColor={colors.subtext} value={newDueDate} onChangeText={setNewDueDate} />
              <Text style={[st.label, { color: colors.subtext }]}>{t('الأولوية', 'Priority')}</Text>
              <View style={st.priorityRow}>
                {[1,2,3,4,5].map(p => (
                  <TouchableOpacity key={p} style={[st.priorityBtn, newPriority === p && { borderColor: PRIORITY_COLORS[p], backgroundColor: PRIORITY_COLORS[p] + '20' }]} onPress={() => setNewPriority(p)}>
                    <Text style={[st.priorityBtnText, newPriority === p && { color: PRIORITY_COLORS[p], fontWeight: '700' }]}>{isAr ? PRIORITY_LABELS[p]?.ar : PRIORITY_LABELS[p]?.en}</Text>
                  </TouchableOpacity>
                ))}
              </View>
              <TouchableOpacity style={[st.saveBtn, { opacity: newTitle.trim() ? 1 : 0.6 }]} onPress={handleAddTask} disabled={saving || !newTitle.trim()}>
                {saving ? <ActivityIndicator color="#FFF" /> : <Text style={st.saveBtnText}>{t('حفظ', 'Save')}</Text>}
              </TouchableOpacity>
            </View>
          </KeyboardAvoidingView>
        </Modal>
      </View>
    </FeatureErrorBoundary>
  );
}

const st = StyleSheet.create({
  container: { flex: 1 }, header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5, borderBottomColor: '#EDE9F6' },
  headerTitle: { fontSize: 18, fontWeight: '700' }, addBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: '#6B21A8', justifyContent: 'center', alignItems: 'center' },
  content: { padding: 20, paddingBottom: 40 },
  empty: { alignItems: 'center', marginTop: 60 }, emptyText: { fontSize: 16, marginTop: 12 },
  errorCard: { padding: 20, alignItems: 'center' }, errorText: { color: '#EF4444', fontSize: 14, marginBottom: 8 }, retryText: { color: '#6B21A8', fontWeight: '600' },
  taskCard: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 14, borderRadius: 14, borderWidth: 1, borderLeftWidth: 4, marginBottom: 8 },
  taskTitle: { fontSize: 15, fontWeight: '600' },
  priorityBadge: { fontSize: 11, fontWeight: '600', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10 },
  calendarBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10, backgroundColor: '#4285F420' },
  calendarText: { fontSize: 11, color: '#4285F4', fontWeight: '600' },
  dueDate: { fontSize: 12, color: '#7C6B99' },
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' },
  modalContent: { width: '90%', borderRadius: 20, padding: 20 },
  modalTitle: { fontSize: 18, fontWeight: '700' }, input: { borderRadius: 12, padding: 14, fontSize: 15, borderWidth: 1, marginBottom: 10 },
  label: { fontSize: 14, fontWeight: '600', marginBottom: 8, marginTop: 8 },
  priorityRow: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  priorityBtn: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, borderWidth: 1.5, borderColor: '#EDE9F6' },
  priorityBtnText: { fontSize: 12, fontWeight: '500' },
  saveBtn: { backgroundColor: '#6B21A8', padding: 14, borderRadius: 12, alignItems: 'center' },
  saveBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
});
