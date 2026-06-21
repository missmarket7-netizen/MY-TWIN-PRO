import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiPost } from '../lib/httpClient';
import { cacheResponse, getCachedResponse, addToOfflineQueue, getNetworkStatus } from '../lib/offlineService';

export interface ChatMessage {
  id: string; role: 'user' | 'twin'; content: string; image?: string;
  timestamp: number; failed?: boolean; emotion?: string; provider?: string;
  thinkingStage?: string; memoryRecall?: boolean; offline?: boolean;
}

export interface RelationshipDims {
  trust: number; attachment: number; comfort: number; openness: number;
  romantic: number; humor: number; attStyle: number;
  [key: string]: number | undefined;
}

export type Tier = 'free' | 'plus' | 'premium' | 'pro' | 'yearly';
export type TwinGender = 'female' | 'male';
export type TwinStyle = 'supportive' | 'coach' | 'wise' | 'fun' | 'calm';
export type ReplyStyle = 'short' | 'medium' | 'long';
export type Theme = 'dark' | 'light';
export type Lang = 'ar' | 'en';

export interface StudySession { concept: string; explanation: any; learningPath: string[]; depth: number; accuracy: number; }
export interface BusinessProject { name: string; stage: string; businessModel: any; financials: any; }
export interface LifePlan { goals: any; nutrition: any; fitness: any; mentalHealth: any; }
export interface DreamAnalysis { interpretation: string; symbols: string[]; emotions: string[]; }
export interface TaskItem { id: string; title: string; dueDate?: string; priority: string; status: string; }
export interface UserStats { dailyUsage: any; tcma: any; features: any; }

export interface TwinStoreBase {
  userId: string; twinName: string; twinGender: TwinGender; twinStyle: TwinStyle;
  replyStyle: ReplyStyle; twinTraits: string[]; bondLevel: number;
  relationshipDims: RelationshipDims; tier: Tier; theme: Theme; lang: Lang; calmMode: boolean;
  chatHistory: ChatMessage[]; isThinking: boolean; thinkingStage: string;
  streamingText: string; twinEnergy: number; totalMessages: number; totalMinutes: number;
  streakDays: number; journeyPhase: string; attachmentStyle: string; menuVisible: boolean;
  voiceEnabled: boolean; voicePersonality: string; hasUsedTrial: boolean;
  points: number; badges: string[]; isOnline: boolean;
  activeStudySession: StudySession | null; activeBusinessProject: BusinessProject | null;
  activeLifePlan: LifePlan | null; recentDreams: DreamAnalysis[]; tasks: TaskItem[];
  userStats: UserStats | null; recommendations: string[]; proactiveMessage: string;

  setAuth: (userId: string) => void; setTwinName: (name: string) => void;
  setTwinGender: (gender: TwinGender) => void; setTwinStyle: (style: TwinStyle) => void;
  setReplyStyle: (style: ReplyStyle) => void; setTwinTraits: (traits: string[]) => void;
  setTier: (tier: Tier) => void; updateTier: (tier: Tier) => void;
  addMessage: (msg: Partial<ChatMessage>) => void; sendMessage: (message: string) => Promise<void>;
  setStreamingText: (text: string | ((prev: string) => string)) => void;
  setThinking: (val: boolean) => void; setThinkingStage: (stage: string) => void;
  setTwinEnergy: (val: number) => void; getEnergyPercent: () => number;
  updateBond: (newBond: number) => void; updateRelationshipDims: (dims: Partial<RelationshipDims>) => void;
  setJourneyPhase: (phase: string) => void; setAttachmentStyle: (style: string) => void;
  recordInteraction: (minutes?: number) => void; resetDailyIfNeeded: () => boolean;
  clearHistory: () => void; logout: () => void; toggleTheme: () => void;
  toggleLang: () => void; setLang: (lang: Lang) => void; toggleCalmMode: () => void;
  openMenu: () => void; closeMenu: () => void; setVoiceEnabled: (enabled: boolean) => void;
  setHasUsedTrial: (val: boolean) => void; addPoints: (pts: number) => void;
  addBadge: (badge: string) => void; setOnline: (online: boolean) => void;
}

const generateId = () => 'msg_' + Date.now().toString(36) + '_' + Math.random().toString(36).substr(2, 9);

const initialState = {
  userId: '', twinName: 'توأمك', twinGender: 'female' as TwinGender,
  twinStyle: 'supportive' as TwinStyle, replyStyle: 'medium' as ReplyStyle,
  twinTraits: [] as string[], bondLevel: 0,
  relationshipDims: { trust: 0, attachment: 0, comfort: 0, openness: 0, romantic: 0, humor: 0, attStyle: 0 },
  tier: 'free' as Tier, theme: 'light' as Theme, lang: 'ar' as Lang, calmMode: false,
  chatHistory: [] as ChatMessage[], isThinking: false, thinkingStage: 'idle',
  streamingText: '', twinEnergy: 100, totalMessages: 0, totalMinutes: 0, streakDays: 0,
  journeyPhase: 'introduction', attachmentStyle: 'unknown', menuVisible: false,
  voiceEnabled: false, voicePersonality: 'friend', hasUsedTrial: false,
  points: 0, badges: [] as string[], isOnline: true,
  activeStudySession: null, activeBusinessProject: null, activeLifePlan: null,
  recentDreams: [], tasks: [], userStats: null, recommendations: [], proactiveMessage: '',
};

export const useTwinStore = create<TwinStoreBase>()(
  persist(
    (set, get) => ({
      ...initialState,
      setAuth: (userId) => set({ userId }),
      setTwinName: (name) => set({ twinName: name }),
      setTwinGender: (gender) => set({ twinGender: gender }),
      setTwinStyle: (style) => set({ twinStyle: style }),
      setReplyStyle: (style) => set({ replyStyle: style }),
      setTwinTraits: (traits) => set({ twinTraits: traits }),
      setTier: (tier) => set({ tier }),
      updateTier: (tier) => set({ tier }),
      setLang: (lang) => set({ lang }),
      toggleCalmMode: () => set((s) => ({ calmMode: !s.calmMode })),
      setVoiceEnabled: (enabled) => set({ voiceEnabled: enabled }),
      setHasUsedTrial: (val) => set({ hasUsedTrial: val }),
      setOnline: (online) => set({ isOnline: online }),

      addMessage: (msg) => set((s) => ({
        chatHistory: [...s.chatHistory, {
          id: msg.id || generateId(), role: msg.role || 'user',
          content: msg.content || '', timestamp: msg.timestamp || Date.now(),
          failed: msg.failed, emotion: msg.emotion, provider: msg.provider,
          thinkingStage: msg.thinkingStage, offline: msg.offline || false,
        }].slice(-200),
        totalMessages: s.totalMessages + 1,
      })),

      sendMessage: async (message: string) => {
        const state = get();
        set({ isThinking: true, thinkingStage: 'thinking', streamingText: '' });
        state.addMessage({ role: 'user', content: message });
        const twinMsgId = generateId();
        state.addMessage({ id: twinMsgId, role: 'twin', content: '', thinkingStage: 'thinking' });

        const cached = await getCachedResponse(message);
        if (cached) {
          set((s) => ({
            chatHistory: s.chatHistory.map(m => m.id === twinMsgId ? { ...m, content: cached, provider: 'cache', thinkingStage: 'complete' } : m),
            isThinking: false, thinkingStage: 'complete',
          }));
          return;
        }

        if (!getNetworkStatus()) {
          await addToOfflineQueue(message);
          set((s) => ({
            chatHistory: s.chatHistory.map(m => m.id === twinMsgId ? { ...m, content: '📡 سيتم إرسال رسالتك عند عودة الاتصال 💜', offline: true, thinkingStage: 'complete' } : m),
            isThinking: false, thinkingStage: 'complete',
          }));
          return;
        }

        try {
          const response = await apiPost('/api/chat', {
            message, history: state.chatHistory.slice(-10).map(m => ({ role: m.role, content: m.content })), lang: state.lang,
          });
          await cacheResponse(message, response.reply);
          set((s) => ({
            chatHistory: s.chatHistory.map(m => m.id === twinMsgId ? { ...m, content: response.reply, emotion: response.emotion?.primary, provider: response.provider || 'orchestrator', thinkingStage: 'complete' } : m),
            isThinking: false, thinkingStage: 'complete', twinEnergy: Math.max(0, s.twinEnergy - 2),
          }));
          if (response.relationship) set({ bondLevel: response.relationship.bond || state.bondLevel, journeyPhase: response.relationship.phase || state.journeyPhase });
        } catch (error: any) {
          if (error.message?.includes('Network') || error.message?.includes('fetch')) await addToOfflineQueue(message);
          set((s) => ({
            chatHistory: s.chatHistory.map(m => m.id === twinMsgId ? { ...m, content: 'عذراً، حدث خطأ في الاتصال. حاول مرة أخرى 💜', failed: true, thinkingStage: 'complete' } : m),
            isThinking: false, thinkingStage: 'complete',
          }));
        }
      },

      setStreamingText: (text) => set((s) => ({ streamingText: typeof text === 'function' ? text(s.streamingText) : text })),
      setThinking: (val) => set({ isThinking: val }),
      setThinkingStage: (stage) => set({ thinkingStage: stage }),
      setTwinEnergy: (val) => set({ twinEnergy: Math.max(0, Math.min(100, Math.round(val))) }),
      getEnergyPercent: () => get().twinEnergy,
      updateBond: (bond) => set({ bondLevel: Math.round(bond) }),
      updateRelationshipDims: (dims) => set((s) => ({ relationshipDims: { ...s.relationshipDims, ...dims } })),
      setJourneyPhase: (phase) => set({ journeyPhase: phase }),
      setAttachmentStyle: (style) => set({ attachmentStyle: style }),
      recordInteraction: (minutes = 0) => set((s) => ({ totalMinutes: s.totalMinutes + minutes })),
      resetDailyIfNeeded: () => false,
      clearHistory: () => set({ chatHistory: [] }),
      logout: () => set({ ...initialState, chatHistory: [] }),
      toggleTheme: () => set((s) => ({ theme: s.theme === 'dark' ? 'light' : 'dark' })),
      toggleLang: () => set((s) => ({ lang: s.lang === 'ar' ? 'en' : 'ar' })),
      openMenu: () => set({ menuVisible: true }),
      closeMenu: () => set({ menuVisible: false }),
      addPoints: (pts) => set((s) => ({ points: s.points + pts })),
      addBadge: (badge) => set((s) => s.badges.includes(badge) ? s : { badges: [...s.badges, badge] }),
    }),
    { name: 'mytwin-store', version: 5, storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        userId: state.userId, twinName: state.twinName, twinGender: state.twinGender,
        twinStyle: state.twinStyle, replyStyle: state.replyStyle, twinTraits: state.twinTraits,
        bondLevel: state.bondLevel, relationshipDims: state.relationshipDims,
        tier: state.tier, theme: state.theme, lang: state.lang, calmMode: state.calmMode,
        journeyPhase: state.journeyPhase, attachmentStyle: state.attachmentStyle,
        voiceEnabled: state.voiceEnabled, hasUsedTrial: state.hasUsedTrial,
        points: state.points, badges: state.badges,
      }),
    }
  )
);

import { apiPost, apiGet } from '../lib/httpClient';

export interface TwinStoreFull extends TwinStoreBase {
  startStudySession: (concept: string) => Promise<void>;
  answerStudyQuestion: (answer: string) => Promise<string | null>;
  endStudySession: () => Promise<void>;
  generateBusinessIdea: (budget: number, interests: string, location: string) => Promise<any>;
  analyzeMarket: (idea: string) => Promise<any>;
  generateFeasibility: (idea: string, budget: number) => Promise<any>;
  generateBusinessCanvas: (idea: string) => Promise<any>;
  generateMarketingPlan: (idea: string, budget: number) => Promise<any>;
  interpretDream: (dreamText: string) => Promise<void>;
  createLifePlan: (goals: string) => Promise<void>;
  startCoachingSession: (topic: string) => Promise<any>;
  getNutritionPlan: (goal: string, restrictions: string) => Promise<any>;
  getFitnessPlan: (goal: string, level: string, equipment: string) => Promise<any>;
  createTask: (title: string) => Promise<void>;
  listTasks: () => Promise<void>;
  completeTask: (taskId: string) => Promise<void>;
  generateImage: (prompt: string, style: string) => Promise<string | null>;
  generateCode: (prompt: string, language: string) => Promise<any>;
  debugCode: (error: string, language: string) => Promise<any>;
  generateContent: (type: string, title: string) => Promise<any>;
  getDailyRecommendations: () => Promise<void>;
  getProactiveMessage: () => Promise<void>;
  getUserStats: () => Promise<void>;
  smartHomeCommand: (command: string) => Promise<any>;
  getWeeklyReport: () => Promise<any>;
  getRelationshipHealth: () => Promise<any>;
}

export const addFeatureActions = () => {
  const state = useTwinStore.getState();
  
  const actions = {
    // ========== ATHENA ==========
    startStudySession: async (concept: string) => {
      try {
        const result = await apiPost('/api/study/start', { user_id: state.userId, concept, age_group: 'young_adult', language: state.lang });
        useTwinStore.setState({ activeStudySession: { concept, explanation: result.explanation, learningPath: result.learning_path || [], depth: 0, accuracy: 0 } });
      } catch (e) { console.error('Study start failed:', e); }
    },

    answerStudyQuestion: async (answer: string) => {
      try {
        const result = await apiPost('/api/study/answer', { user_id: state.userId, answer });
        const s = useTwinStore.getState().activeStudySession;
        if (s) useTwinStore.setState({ activeStudySession: { ...s, depth: result.current_depth || s.depth, accuracy: result.accuracy ? parseFloat(result.accuracy) : s.accuracy } });
        return result.next_question || null;
      } catch (e) { console.error('Study answer failed:', e); return null; }
    },

    endStudySession: async () => {
      try { await apiPost('/api/study/end', {}, { user_id: state.userId }); useTwinStore.setState({ activeStudySession: null }); } catch (e) { console.error('Study end failed:', e); }
    },

    // ========== GROWTH-HIVE ==========
    generateBusinessIdea: async (budget: number, interests: string, location: string) => {
      try { return await apiPost('/api/business/generate-ideas', { user_id: state.userId, budget, interests, location, language: state.lang }); } catch (e) { return null; }
    },
    analyzeMarket: async (idea: string) => {
      try { return await apiPost('/api/business/analyze-market', { user_id: state.userId, idea, language: state.lang }); } catch (e) { return null; }
    },
    generateFeasibility: async (idea: string, budget: number) => {
      try { return await apiPost('/api/business/feasibility', { user_id: state.userId, idea, budget, language: state.lang }); } catch (e) { return null; }
    },
    generateBusinessCanvas: async (idea: string) => {
      try { return await apiPost('/api/business/canvas', { user_id: state.userId, idea, language: state.lang }); } catch (e) { return null; }
    },
    generateMarketingPlan: async (idea: string, budget: number) => {
      try { return await apiPost('/api/business/marketing-plan', { user_id: state.userId, idea, budget, language: state.lang }); } catch (e) { return null; }
    },

    // ========== DREAMS ==========
    interpretDream: async (dreamText: string) => {
      try {
        const result = await apiPost('/api/dreams/interpret', { user_id: state.userId, dream_text: dreamText, lang: state.lang });
        useTwinStore.setState((s) => ({ recentDreams: [...s.recentDreams, result].slice(-10) }));
      } catch (e) { console.error('Dream interpretation failed:', e); }
    },

    // ========== LIFE COACH ==========
    startCoachingSession: async (topic: string) => {
      try { return await apiPost('/api/life-coach/session', { user_id: state.userId, topic, lang: state.lang }); } catch (e) { return null; }
    },
    createLifePlan: async (goals: string) => {
      try { const result = await apiPost('/api/life-coach/plan', { user_id: state.userId, goals, lang: state.lang }); useTwinStore.setState({ activeLifePlan: result }); } catch (e) { console.error('Life plan failed:', e); }
    },
    getNutritionPlan: async (goal: string, restrictions: string) => {
      try { return await apiPost('/api/life-coach/nutrition', { user_id: state.userId, goal, restrictions, lang: state.lang }); } catch (e) { return null; }
    },
    getFitnessPlan: async (goal: string, level: string, equipment: string) => {
      try { return await apiPost('/api/life-coach/fitness', { user_id: state.userId, goal, level, equipment, lang: state.lang }); } catch (e) { return null; }
    },

    // ========== P.A.S.S. ==========
    createTask: async (title: string) => {
      try { await apiPost('/api/pass/task', { user_id: state.userId, title }); await actions.listTasks(); } catch (e) { console.error('Task creation failed:', e); }
    },
    listTasks: async () => {
      try { const result = await apiGet(`/api/pass/tasks?user_id=${state.userId}&status=all`); useTwinStore.setState({ tasks: result.tasks || [] }); } catch (e) { console.error('Task list failed:', e); }
    },
    completeTask: async (taskId: string) => {
      try { await apiPost(`/api/pass/task/complete?user_id=${state.userId}&task_id=${taskId}`); await actions.listTasks(); } catch (e) { console.error('Task completion failed:', e); }
    },

    // ========== IMAGE LAB ==========
    generateImage: async (prompt: string, style: string) => {
      try { const result = await apiPost(`/api/image-lab/generate?user_id=${state.userId}&prompt=${encodeURIComponent(prompt)}&style=${style}`); return result.image_url || null; } catch (e) { return null; }
    },

    // ========== CODE LAB ==========
    generateCode: async (prompt: string, language: string) => {
      try { return await apiPost('/api/code-lab/generate-code', { user_id: state.userId, prompt, lang: language }); } catch (e) { return null; }
    },
    debugCode: async (error: string, language: string) => {
      try { return await apiPost('/api/code-lab/debug', { user_id: state.userId, error, lang: language }); } catch (e) { return null; }
    },

    // ========== CREATOR ==========
    generateContent: async (type: string, title: string) => {
      try { return await apiPost('/api/creator/outline', { user_id: state.userId, type, title, language: state.lang }); } catch (e) { return null; }
    },

    // ========== محركات متقدمة ==========
    getDailyRecommendations: async () => {
      try { const result = await apiGet(`/api/recommendations/daily?user_id=${state.userId}`); useTwinStore.setState({ recommendations: result.recommendations?.map((r: any) => r.message) || [] }); } catch (e) { console.error('Recommendations failed:', e); }
    },
    getProactiveMessage: async () => {
      try { const result = await apiGet(`/api/meta/proactive-message?user_id=${state.userId}&lang=${state.lang}`); useTwinStore.setState({ proactiveMessage: result.message || '' }); } catch (e) { console.error('Proactive message failed:', e); }
    },
    getUserStats: async () => {
      try { const result = await apiGet(`/api/stats/dashboard?user_id=${state.userId}`); useTwinStore.setState({ userStats: result }); } catch (e) { console.error('User stats failed:', e); }
    },
    smartHomeCommand: async (command: string) => {
      try { return await apiPost('/api/smart-home/command', { user_id: state.userId, command, lang: state.lang }); } catch (e) { return null; }
    },
    getWeeklyReport: async () => {
      try { return await apiGet(`/api/reports/weekly?user_id=${state.userId}`); } catch (e) { return null; }
    },
    getRelationshipHealth: async () => {
      try { return await apiGet(`/api/relationship/health?user_id=${state.userId}`); } catch (e) { return null; }
    },
  };

  return actions;
};

export const useFeatureActions = () => addFeatureActions();
