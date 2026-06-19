import { useState, useEffect, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert, RefreshControl, Modal, Platform, KeyboardAvoidingView } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore } from '../../store/useTwinStore';
import { router } from 'expo-router';
import { apiGet, apiPost, apiPut, apiDelete } from '../../lib/httpClient';
import { ArrowLeft, Plus, CheckCircle2, Circle, Trash2, Calendar, Target, Clock, X } from 'lucide-react-native';

interface Task {
  id: string;
  title: string;
  due_date: string | null;
  priority: number;
  status: string;
  category: string;
}

const PRIORITY_COLORS: Record<number, string> = { 1: '#9CA3AF', 2: '#60A5FA', 3: '#F59E0B', 4: '#F97316', 5: '#EF4444' };
const PRIORITY_LABELS: Record<number, { ar: string; en: string }> = {
  1: { ar: 'منخفض', en: 'Low' },
  2: { ar: 'متوسط', en: 'Medium' },
  3: { ar: 'عالي', en: 'High' },
  4: { ar: 'عاجل', en: 'Urgent' },
  5: { ar: 'حرج', en: 'Critical' },
};

export default function TaskManager() {
  const insets = useSafeAreaInsets();
  const { lang } = useTwinStore();
  const isAr = lang === 'ar';
  const t = (ar: string, en: string) => isAr ? ar : en;
  const primary = '#6B21A8';

  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDueDate, setNewDueDate] = useState('');
  const [newPriority, setNewPriority] = useState(3);
  const [saving, setSaving] = useState(false);

  const fetchTasks = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true); else setLoading(true);
    try {
      const data = await apiGet('/api/tasks');
      setTasks(data || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); setRefreshing(false); }
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

  const handleComplete = async (taskId: string, currentStatus: string) => {
    const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    try {
      await apiPut(`/api/tasks/${taskId}`, { status: newStatus });
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (taskId: string) => {
    Alert.alert(t('حذف', 'Delete'), t('هل أنت متأكد؟', 'Are you sure?'), [
      { text: t('إلغاء', 'Cancel'), style: 'cancel' },
      { text: t('حذف', 'Delete'), style: 'destructive', onPress: async () => {
        try { await apiDelete(`/api/tasks/${taskId}`); setTasks(prev => prev.filter(t => t.id !== taskId)); }
        catch (e) { console.error(e); }
      }},
    ]);
  };

  const pendingTasks = tasks.filter(t => t.status !== 'completed');
  const completedTasks = tasks.filter(t => t.status === 'completed');

  if (loading) {
    return (
      <View style={[s.container, { paddingTop: insets.top, justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={primary} />
      </View>
    );
  }

  return (
    <View style={[s.container, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}><ArrowLeft size={24} stroke={primary} /></TouchableOpacity>
        <Text style={s.headerTitle}>{t('إدارة المهام', 'Task Manager')}</Text>
        <TouchableOpacity onPress={() => setShowAddModal(true)} style={s.addBtn}><Plus size={22} stroke="#FFF" /></TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={s.content} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => fetchTasks(true)} colors={[primary]} />}>
        {pendingTasks.length === 0 && completedTasks.length === 0 ? (
          <View style={s.empty}>
            <Target size={48} stroke="#7C6B99" />
            <Text style={s.emptyText}>{t('لا توجد مهام', 'No tasks yet')}</Text>
            <Text style={s.emptySub}>{t('أضف مهمتك الأولى', 'Add your first task')}</Text>
          </View>
        ) : (
          <>
            {pendingTasks.length > 0 && (
              <View style={s.section}>
                <Text style={s.sectionTitle}>{t('قيد التنفيذ', 'In Progress')} ({pendingTasks.length})</Text>
                {pendingTasks.map(task => (
                  <View key={task.id} style={[s.taskCard, { borderLeftColor: PRIORITY_COLORS[task.priority] }]}>
                    <TouchableOpacity onPress={() => handleComplete(task.id, task.status)}>
                      <Circle size={22} stroke={PRIORITY_COLORS[task.priority]} />
                    </TouchableOpacity>
                    <View style={{ flex: 1 }}>
                      <Text style={s.taskTitle}>{task.title}</Text>
                      <View style={{ flexDirection: 'row', gap: 8, alignItems: 'center' }}>
                        <Text style={[s.priorityBadge, { backgroundColor: PRIORITY_COLORS[task.priority] + '20', color: PRIORITY_COLORS[task.priority] }]}>
                          {isAr ? PRIORITY_LABELS[task.priority]?.ar : PRIORITY_LABELS[task.priority]?.en}
                        </Text>
                        {task.due_date && (
                          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
                            <Calendar size={12} stroke="#7C6B99" />
                            <Text style={s.dueDate}>{task.due_date}</Text>
                          </View>
                        )}
                      </View>
                    </View>
                    <TouchableOpacity onPress={() => handleDelete(task.id)}><Trash2 size={16} stroke="#EF4444" /></TouchableOpacity>
                  </View>
                ))}
              </View>
            )}

            {completedTasks.length > 0 && (
              <View style={s.section}>
                <Text style={s.sectionTitle}>{t('مكتملة', 'Completed')} ({completedTasks.length})</Text>
                {completedTasks.map(task => (
                  <View key={task.id} style={[s.taskCard, { opacity: 0.7, borderLeftColor: '#10B981' }]}>
                    <TouchableOpacity onPress={() => handleComplete(task.id, task.status)}>
                      <CheckCircle2 size={22} stroke="#10B981" fill="#10B98120" />
                    </TouchableOpacity>
                    <View style={{ flex: 1 }}>
                      <Text style={[s.taskTitle, { textDecorationLine: 'line-through', color: '#7C6B99' }]}>{task.title}</Text>
                    </View>
                    <TouchableOpacity onPress={() => handleDelete(task.id)}><Trash2 size={16} stroke="#EF4444" /></TouchableOpacity>
                  </View>
                ))}
              </View>
            )}
          </>
        )}
      </ScrollView>

      <Modal visible={showAddModal} transparent animationType="fade" onRequestClose={() => setShowAddModal(false)}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={s.modalOverlay}>
          <View style={s.modalContent}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <Text style={s.modalTitle}>{t('مهمة جديدة', 'New Task')}</Text>
              <TouchableOpacity onPress={() => setShowAddModal(false)}><X size={22} stroke="#7C6B99" /></TouchableOpacity>
            </View>
            <TextInput style={s.input} placeholder={t('عنوان المهمة', 'Task title')} placeholderTextColor="#7C6B99" value={newTitle} onChangeText={setNewTitle} autoFocus />
            <TextInput style={s.input} placeholder={t('تاريخ التسليم (اختياري)', 'Due date (optional)')} placeholderTextColor="#7C6B99" value={newDueDate} onChangeText={setNewDueDate} />
            <Text style={s.label}>{t('الأولوية', 'Priority')}</Text>
            <View style={s.priorityRow}>
              {[1,2,3,4,5].map(p => (
                <TouchableOpacity key={p} style={[s.priorityBtn, newPriority === p && { borderColor: PRIORITY_COLORS[p], backgroundColor: PRIORITY_COLORS[p] + '20' }]} onPress={() => setNewPriority(p)}>
                  <Text style={[s.priorityBtnText, newPriority === p && { color: PRIORITY_COLORS[p], fontWeight: '700' }]}>
                    {isAr ? PRIORITY_LABELS[p]?.ar : PRIORITY_LABELS[p]?.en}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
            <TouchableOpacity style={[s.saveBtn, { opacity: newTitle.trim() ? 1 : 0.6 }]} onPress={handleAddTask} disabled={saving || !newTitle.trim()}>
              {saving ? <ActivityIndicator color="#FFF" /> : <Text style={s.saveBtnText}>{t('حفظ', 'Save')}</Text>}
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5, borderBottomColor: '#EDE9F6' },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'flex-start' },
  headerTitle: { fontSize: 18, fontWeight: '700', color: '#6B21A8' },
  addBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: '#6B21A8', justifyContent: 'center', alignItems: 'center' },
  content: { padding: 20, paddingBottom: 40 },
  empty: { alignItems: 'center', marginTop: 60 },
  emptyText: { fontSize: 18, fontWeight: '700', color: '#1A1226', marginTop: 16 },
  emptySub: { fontSize: 14, color: '#7C6B99', marginTop: 4 },
  section: { marginBottom: 24 },
  sectionTitle: { fontSize: 15, fontWeight: '700', color: '#1A1226', marginBottom: 12 },
  taskCard: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 14, borderRadius: 14, backgroundColor: '#FAFAFE', borderWidth: 1, borderColor: '#EDE9F6', borderLeftWidth: 4, marginBottom: 8 },
  taskTitle: { fontSize: 15, fontWeight: '600', color: '#1A1226' },
  priorityBadge: { fontSize: 11, fontWeight: '600', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10 },
  dueDate: { fontSize: 12, color: '#7C6B99' },
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' },
  modalContent: { width: '90%', backgroundColor: '#FFF', borderRadius: 20, padding: 20 },
  modalTitle: { fontSize: 18, fontWeight: '700', color: '#1A1226' },
  input: { backgroundColor: '#FAFAFE', borderRadius: 12, padding: 14, fontSize: 15, color: '#1A1226', borderWidth: 1, borderColor: '#EDE9F6', marginBottom: 10 },
  label: { fontSize: 14, fontWeight: '600', color: '#1A1226', marginBottom: 8, marginTop: 8 },
  priorityRow: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  priorityBtn: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, borderWidth: 1.5, borderColor: '#EDE9F6' },
  priorityBtnText: { fontSize: 12, fontWeight: '500', color: '#7C6B99' },
  saveBtn: { backgroundColor: '#6B21A8', padding: 14, borderRadius: 12, alignItems: 'center' },
  saveBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
});
