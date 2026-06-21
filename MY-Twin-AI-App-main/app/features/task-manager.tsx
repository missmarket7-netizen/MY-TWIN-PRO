import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, RefreshControl, Modal, Platform,
  KeyboardAvoidingView, TextInput, Alert,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTwinStore, useTwinStoreFull } from '../../store/useTwinStore';
import { useTheme } from '../../utils/theme';
import { router } from 'expo-router';
import {
  ArrowLeft, Plus, CheckCircle2, Circle, Trash2, Calendar,
  Target, Clock, X, Cloud, TrendingUp, DollarSign,
  Search, Sun, Moon,
} from 'lucide-react-native';
import { speakResponse } from '../../utils/voice_engine';

interface TaskItem {
  id: string;
  title: string;
  due_date?: string;
  priority: string;
  status: string;
  category?: string;
}

const PRIORITY_COLORS: Record<string, string> = {
  low: '#9CA3AF', medium: '#60A5FA', high: '#F59E0B', urgent: '#F97316', critical: '#EF4444',
};

export default function TaskManager() {
  const insets = useSafeAreaInsets();
  const theme = useTheme();
  const { lang } = useTwinStore();
  const { createTask, listTasks, completeTask } = useTwinStoreFull();
  const isAr = lang === 'ar';
  const isDark = theme === 'dark';

  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newPriority, setNewPriority] = useState('medium');
  const [saving, setSaving] = useState(false);

  // خدمات خارجية
  const [weather, setWeather] = useState<any>(null);
  const [news, setNews] = useState<any>(null);
  const [currency, setCurrency] = useState<any>(null);
  const [showServices, setShowServices] = useState(false);

  const colors = {
    bg: isDark ? '#0F0A1A' : '#FAFAF8',
    card: isDark ? '#1A1226' : '#FFFFFF',
    text: isDark ? '#FFFFFF' : '#2D2D2D',
    subtext: isDark ? '#8B7BA3' : '#6B6B6B',
    accent: '#7C3AED',
    border: isDark ? '#2D1B4D' : '#E8E8E3',
    inputBg: isDark ? '#161122' : '#FDFDF9',
    success: '#10B981',
    danger: '#EF4444',
  };

  const fetchTasks = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true); else setLoading(true);
    try {
      // استخدام دالة listTasks من المتجر
      await listTasks();
      const store = useTwinStore.getState();
      setTasks(store.tasks || []);
    } catch (e) {
      setTasks([]);
    } finally { setLoading(false); setRefreshing(false); }
  }, [listTasks]);

  const fetchServices = useCallback(async () => {
    try {
      const [w, n, c] = await Promise.all([
        fetch('https://my-twin-pro-production-b744.up.railway.app/api/pass/weather?city=Cairo&lang=ar').then(r => r.json()),
        fetch('https://my-twin-pro-production-b744.up.railway.app/api/pass/news?lang=ar').then(r => r.json()),
        fetch('https://my-twin-pro-production-b744.up.railway.app/api/pass/currency?base=USD&symbols=EGP,SAR,EUR').then(r => r.json()),
      ]);
      setWeather(w);
      setNews(n);
      setCurrency(c);
    } catch (e) {}
  }, []);

  useEffect(() => {
    fetchTasks();
    fetchServices();
  }, [fetchTasks, fetchServices]);

  const handleAddTask = async () => {
    if (!newTitle.trim()) return;
    setSaving(true);
    try {
      await createTask(newTitle.trim());
      setNewTitle('');
      setShowAddModal(false);
      fetchTasks(true);
    } catch (e: any) {
      Alert.alert(isAr ? 'خطأ' : 'Error', e.message);
    } finally { setSaving(false); }
  };

  const handleComplete = async (taskId: string) => {
    try {
      await completeTask(taskId);
      fetchTasks(true);
    } catch (e) { console.error(e); }
  };

  if (loading) {
    return (
      <View style={[st.container, { paddingTop: insets.top, backgroundColor: colors.bg, justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={colors.accent} />
      </View>
    );
  }

  return (
    <View style={[st.container, { paddingTop: insets.top, backgroundColor: colors.bg }]}>
      {/* الهيدر */}
      <View style={[st.header, { borderBottomColor: colors.border }]}>
        <TouchableOpacity onPress={() => router.back()}>
          <ArrowLeft size={24} stroke={colors.text} />
        </TouchableOpacity>
        <Text style={[st.headerTitle, { color: colors.text }]}>
          {isAr ? 'المساعد الشخصي' : 'P.A.S.S.'}
        </Text>
        <TouchableOpacity onPress={() => setShowAddModal(true)} style={[st.addBtn, { backgroundColor: colors.accent }]}>
          <Plus size={22} stroke="#FFF" />
        </TouchableOpacity>
      </View>

      <ScrollView
        contentContainerStyle={st.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => fetchTasks(true)} colors={[colors.accent]} />}
      >
        {/* الخدمات الخارجية */}
        <TouchableOpacity
          style={[st.servicesToggle, { backgroundColor: colors.card, borderColor: colors.border }]}
          onPress={() => setShowServices(!showServices)}
        >
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
            <Sun size={18} stroke={colors.accent} />
            <Text style={[st.servicesToggleText, { color: colors.text }]}>
              {isAr ? 'الخدمات السريعة' : 'Quick Services'}
            </Text>
          </View>
          <Text style={[st.servicesToggleText, { color: colors.subtext }]}>
            {showServices ? '▲' : '▼'}
          </Text>
        </TouchableOpacity>

        {showServices && (
          <View style={st.servicesGrid}>
            {/* الطقس */}
            <View style={[st.serviceCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <Cloud size={24} stroke="#06B6D4" />
              <Text style={[st.serviceTitle, { color: colors.text }]}>
                {weather?.city || 'Cairo'}
              </Text>
              <Text style={[st.serviceValue, { color: colors.subtext }]}>
                {weather?.temperature ? `${weather.temperature}°C` : '--'}
              </Text>
            </View>

            {/* العملات */}
            <View style={[st.serviceCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <DollarSign size={24} stroke="#10B981" />
              <Text style={[st.serviceTitle, { color: colors.text }]}>
                {isAr ? 'عملات' : 'Currency'}
              </Text>
              <Text style={[st.serviceValue, { color: colors.subtext }]}>
                {currency?.rates?.EGP ? `EGP ${currency.rates.EGP}` : '--'}
              </Text>
            </View>

            {/* الأخبار */}
            <View style={[st.serviceCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <TrendingUp size={24} stroke="#8B5CF6" />
              <Text style={[st.serviceTitle, { color: colors.text }]}>
                {isAr ? 'أخبار' : 'News'}
              </Text>
              <Text style={[st.serviceValue, { color: colors.subtext }]}>
                {news?.articles?.length ? `${news.articles.length} ${isAr ? 'خبر' : 'news'}` : '--'}
              </Text>
            </View>
          </View>
        )}

        {/* إحصائيات سريعة */}
        <View style={[st.statsRow, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={st.statItem}>
            <Text style={[st.statValue, { color: colors.accent }]}>{tasks.length}</Text>
            <Text style={[st.statLabel, { color: colors.subtext }]}>{isAr ? 'مهام' : 'Tasks'}</Text>
          </View>
          <View style={st.statItem}>
            <Text style={[st.statValue, { color: colors.success }]}>
              {tasks.filter(t => t.status === 'completed').length}
            </Text>
            <Text style={[st.statLabel, { color: colors.subtext }]}>{isAr ? 'مكتملة' : 'Done'}</Text>
          </View>
          <View style={st.statItem}>
            <Text style={[st.statValue, { color: colors.danger }]}>
              {tasks.filter(t => t.status === 'pending').length}
            </Text>
            <Text style={[st.statLabel, { color: colors.subtext }]}>{isAr ? 'معلقة' : 'Pending'}</Text>
          </View>
        </View>

        {/* قائمة المهام */}
        <Text style={[st.sectionTitle, { color: colors.text }]}>
          {isAr ? '📋 المهام' : '📋 Tasks'}
        </Text>

        {tasks.length === 0 ? (
          <View style={st.empty}>
            <Target size={48} stroke={colors.subtext} />
            <Text style={[st.emptyText, { color: colors.subtext }]}>
              {isAr ? 'لا توجد مهام بعد' : 'No tasks yet'}
            </Text>
          </View>
        ) : (
          tasks.map(task => (
            <View
              key={task.id}
              style={[
                st.taskCard,
                {
                  backgroundColor: colors.card,
                  borderColor: colors.border,
                  borderLeftColor: PRIORITY_COLORS[task.priority] || colors.accent,
                },
              ]}
            >
              <TouchableOpacity onPress={() => handleComplete(task.id)}>
                {task.status === 'completed' ? (
                  <CheckCircle2 size={22} stroke={colors.success} fill={colors.success + '20'} />
                ) : (
                  <Circle size={22} stroke={PRIORITY_COLORS[task.priority] || colors.subtext} />
                )}
              </TouchableOpacity>

              <View style={{ flex: 1 }}>
                <Text
                  style={[
                    st.taskTitle,
                    { color: colors.text },
                    task.status === 'completed' && { textDecorationLine: 'line-through', color: colors.subtext },
                  ]}
                >
                  {task.title}
                </Text>
                {task.due_date && (
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 4 }}>
                    <Calendar size={12} stroke={colors.subtext} />
                    <Text style={[st.dueDate, { color: colors.subtext }]}>{task.due_date}</Text>
                  </View>
                )}
              </View>

              <TouchableOpacity onPress={() => speakResponse(task.title).catch(() => {})}>
                <Text style={{ fontSize: 18 }}>🔊</Text>
              </TouchableOpacity>
            </View>
          ))
        )}
      </ScrollView>

      {/* مودال إضافة مهمة */}
      <Modal visible={showAddModal} transparent animationType="fade" onRequestClose={() => setShowAddModal(false)}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={st.modalOverlay}>
          <View style={[st.modalContent, { backgroundColor: colors.card }]}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <Text style={[st.modalTitle, { color: colors.text }]}>
                {isAr ? 'مهمة جديدة' : 'New Task'}
              </Text>
              <TouchableOpacity onPress={() => setShowAddModal(false)}>
                <X size={22} stroke={colors.subtext} />
              </TouchableOpacity>
            </View>

            <TextInput
              style={[st.input, { backgroundColor: colors.inputBg, color: colors.text, borderColor: colors.border }]}
              placeholder={isAr ? 'عنوان المهمة' : 'Task title'}
              placeholderTextColor={colors.subtext}
              value={newTitle}
              onChangeText={setNewTitle}
              autoFocus
            />

            <Text style={[st.label, { color: colors.subtext }]}>
              {isAr ? 'الأولوية' : 'Priority'}
            </Text>
            <View style={st.priorityRow}>
              {['low', 'medium', 'high'].map(p => (
                <TouchableOpacity
                  key={p}
                  style={[
                    st.priorityBtn,
                    { borderColor: newPriority === p ? PRIORITY_COLORS[p] : colors.border },
                    newPriority === p && { backgroundColor: PRIORITY_COLORS[p] + '20' },
                  ]}
                  onPress={() => setNewPriority(p)}
                >
                  <Text style={[st.priorityBtnText, { color: newPriority === p ? PRIORITY_COLORS[p] : colors.subtext }]}>
                    {isAr ? (p === 'low' ? 'منخفض' : p === 'medium' ? 'متوسط' : 'عالي') : p}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <TouchableOpacity
              style={[st.saveBtn, { backgroundColor: colors.accent, opacity: newTitle.trim() ? 1 : 0.6 }]}
              onPress={handleAddTask}
              disabled={saving || !newTitle.trim()}
            >
              {saving ? (
                <ActivityIndicator color="#FFF" />
              ) : (
                <Text style={st.saveBtnText}>{isAr ? 'حفظ' : 'Save'}</Text>
              )}
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </View>
  );
}

const st = StyleSheet.create({
  container: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 0.5 },
  headerTitle: { fontSize: 18, fontWeight: '700' },
  addBtn: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  content: { padding: 16, paddingBottom: 40 },
  // خدمات
  servicesToggle: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 14, borderRadius: 14, borderWidth: 1, marginBottom: 12 },
  servicesToggleText: { fontSize: 15, fontWeight: '600' },
  servicesGrid: { flexDirection: 'row', gap: 10, marginBottom: 16 },
  serviceCard: { flex: 1, alignItems: 'center', padding: 14, borderRadius: 14, borderWidth: 1 },
  serviceTitle: { fontSize: 13, fontWeight: '600', marginTop: 8 },
  serviceValue: { fontSize: 15, fontWeight: '700', marginTop: 4 },
  // إحصائيات
  statsRow: { flexDirection: 'row', borderRadius: 14, borderWidth: 1, padding: 14, marginBottom: 20 },
  statItem: { flex: 1, alignItems: 'center' },
  statValue: { fontSize: 22, fontWeight: '800' },
  statLabel: { fontSize: 12, marginTop: 4 },
  // مهام
  sectionTitle: { fontSize: 18, fontWeight: '700', marginBottom: 12 },
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { fontSize: 15, marginTop: 12 },
  taskCard: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 14, borderRadius: 14, borderWidth: 1, borderLeftWidth: 4, marginBottom: 8 },
  taskTitle: { fontSize: 15, fontWeight: '600' },
  dueDate: { fontSize: 12 },
  // مودال
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' },
  modalContent: { width: '90%', borderRadius: 20, padding: 20 },
  modalTitle: { fontSize: 18, fontWeight: '700' },
  input: { borderRadius: 12, padding: 14, fontSize: 15, borderWidth: 1, marginBottom: 10 },
  label: { fontSize: 14, fontWeight: '600', marginBottom: 8, marginTop: 8 },
  priorityRow: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  priorityBtn: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, borderWidth: 1.5 },
  priorityBtnText: { fontSize: 12, fontWeight: '500' },
  saveBtn: { padding: 14, borderRadius: 12, alignItems: 'center' },
  saveBtnText: { color: '#FFF', fontWeight: '700', fontSize: 16 },
});
