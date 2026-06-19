import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiPost } from '../lib/httpClient';

// ==================== TYPES ====================
export interface ChatMessage {
  id: string;
  role: 'user' | 'twin';
  content: string;
  image?: string;
  timestamp: number;
  failed?: boolean;
  emotion?: string;
  provider?: string;
  thinkingStage?: string;
  memoryRecall?: boolean;
}

export interface RelationshipDims {
  trust: number;
  attachment: number;
  comfort: number;
  openness: number;
  romantic: number;
  humor: number;
  attStyle: number;
  affection?: number;
  support?: number;
  empathy?: number;
  communication?: number;
  dependency?: number;
  [key: string]: number | undefined;
}

export type Tier = 'free' | 'free_trial_14d' | 'plus' | 'premium' | 'pro' | 'yearly';
export type TwinGender = 'female' | 'male' | 'unspecified';
export type TwinStyle = 'supportive' | 'coach' | 'wise' | 'fun' | 'calm';
export type ReplyStyle = 'short' | 'medium' | 'long';
export type Theme = 'dark' | 'light';
export type Lang = 'ar' | 'en';

// ==================== STORE ====================
export interface TwinStore {
  // State
  userId: string;
  twinName: string;
  twinGender: TwinGender;
  twinStyle: TwinStyle;
  replyStyle: ReplyStyle;
  twinTraits: string[];
  bondLevel: number;
  relationshipDims: RelationshipDims;
  tier: Tier;
  theme: Theme;
  lang: Lang;
  calmMode: boolean;
  chatHistory: ChatMessage[];
  isThinking: boolean;
  thinkingStage: string;
  streamingText: string;
  twinEnergy: number;
  totalMessages: number;
  totalMinutes: number;
  streakDays: number;
  journeyPhase: string;
  attachmentStyle: string;
  menuVisible: boolean;
  voiceEnabled: boolean;
  voicePersonality: string;
  hasUsedTrial: boolean;
  points: number;
  badges: string[];

  // Actions
  setAuth: (userId: string) => void;
  setTwinName: (name: string) => void;
  setTwinGender: (gender: TwinGender) => void;
  setTwinStyle: (style: TwinStyle) => void;
  setReplyStyle: (style: ReplyStyle) => void;
  setTwinTraits: (traits: string[]) => void;
  setTier: (tier: Tier) => void;
  updateTier: (tier: Tier) => void;
  addMessage: (msg: Partial<ChatMessage>) => void;
  sendMessage: (message: string) => Promise<void>;
  setStreamingText: (text: string | ((prev: string) => string)) => void;
  setThinking: (val: boolean) => void;
  setThinkingStage: (stage: string) => void;
  setTwinEnergy: (val: number) => void;
  getEnergyPercent: () => number;
  updateBond: (newBond: number) => void;
  updateRelationshipDims: (dims: Partial<RelationshipDims>) => void;
  setJourneyPhase: (phase: string) => void;
  setAttachmentStyle: (style: string) => void;
  incrementDailyMessage: (tokenCount?: number) => void;
  recordInteraction: (minutes?: number) => void;
  resetDailyIfNeeded: () => boolean;
  clearHistory: () => void;
  logout: () => void;
  toggleTheme: () => void;
  toggleLang: () => void;
  setLang: (lang: Lang) => void;
  toggleCalmMode: () => void;
  openMenu: () => void;
  closeMenu: () => void;
  setVoiceEnabled: (enabled: boolean) => void;
  setHasUsedTrial: (val: boolean) => void;
  addPoints: (pts: number) => void;
  addBadge: (badge: string) => void;
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
  points: 0, badges: [] as string[],
};

export const useTwinStore = create<TwinStore>()(
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

      addMessage: (msg) => set((s) => ({
        chatHistory: [...s.chatHistory, {
          id: msg.id || generateId(), role: msg.role || 'user',
          content: msg.content || '', image: msg.image, timestamp: msg.timestamp || Date.now(),
          failed: msg.failed, emotion: msg.emotion, provider: msg.provider,
          thinkingStage: msg.thinkingStage, memoryRecall: msg.memoryRecall,
        }].slice(-200),
        totalMessages: s.totalMessages + 1,
      })),

      sendMessage: async (message: string) => {
        const state = get();
        set({ isThinking: true, thinkingStage: 'thinking', streamingText: '' });
        state.addMessage({ role: 'user', content: message });
        const twinMsgId = generateId();
        state.addMessage({ id: twinMsgId, role: 'twin', content: '' });

        try {
          const response = await apiPost('/api/chat', {
            message,
            history: state.chatHistory.slice(-10).map(m => ({ role: m.role, content: m.content })),
            lang: state.lang,
          });
          set((s) => ({
            chatHistory: s.chatHistory.map(m =>
              m.id === twinMsgId ? { ...m, content: response.reply, emotion: response.emotion?.primary, provider: response.provider || 'multi_ai' } : m
            ),
            isThinking: false, thinkingStage: 'complete',
          }));
        } catch (error: any) {
          set((s) => ({
            chatHistory: s.chatHistory.map(m =>
              m.id === twinMsgId ? { ...m, content: 'عذراً، حدث خطأ في الاتصال. حاول مرة أخرى 💜', failed: true, provider: 'error' } : m
            ),
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
      incrementDailyMessage: (tokenCount = 0) => set((s) => ({ twinEnergy: Math.max(0, s.twinEnergy - 5), totalMessages: s.totalMessages + 1 })),
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
    {
      name: 'mytwin-store',
      version: 3,
      storage: createJSONStorage(() => AsyncStorage),
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
