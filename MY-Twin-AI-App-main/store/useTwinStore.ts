import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Haptics from 'expo-haptics';

const generateId = () => Math.random().toString(36).substr(2, 9) + Date.now().toString(36);

// ==================== TYPES ====================

export interface EmotionState {
  primary: string; secondary: string; intensity: number; valence: number; arousal: number;
  trend?: 'improving' | 'worsening' | 'stable'; riskLevel?: 'low' | 'medium' | 'high'; needsSupport: boolean;
}

export interface ConsciousnessState {
  mood: string; energy: number; curiosity: number; activeGoals: string[]; lastThought: string;
}

export interface ChatMessage {
  id: string; role: 'user' | 'twin'; content: string; image?: string; timestamp: number;
  failed?: boolean; emotion?: string; journeyPhase?: string; relationshipStage?: string;
  memoryRecall?: boolean; thinkingStage?: string;
  youtubeVideo?: string; provider?: string;
}

export interface RelationshipDims {
  trust: number; attachment: number; comfort: number; openness: number;
  romantic: number; humor: number; attStyle: number;
  empathy?: number; support?: number; communication?: number;
  affection?: number; dependency?: number;
  [key: string]: number | undefined;
}

export type Tier = 'free' | 'free_trial_14d' | 'premium_trial' | 'premium' | 'pro' | 'yearly' | 'plus';
export type Theme = 'dark' | 'light';
export type Lang = 'ar' | 'en';
export type TwinGender = 'female' | 'male' | 'unspecified';
export type TwinStyle = 'supportive' | 'coach' | 'wise' | 'fun' | 'calm';
export type ReplyStyle = 'short' | 'medium' | 'long';
export type JourneyPhase = 'introduction' | 'trust_building' | 'deepening' | 'growth' | 'mature';
export type AttachmentStyle = 'secure' | 'anxious' | 'avoidant' | 'disorganized' | 'unknown';
export type VoicePersonality = 'mentor' | 'friend' | 'romantic' | 'energetic' | 'calm';
export type TTSProvider = 'edge_tts' | 'expo_speech' | 'elevenlabs';

export interface VoiceConfig {
  provider: TTSProvider;
  voiceId: string;
  language: string;
  pitch: number;
  rate: number;
  gender: 'male' | 'female';
}

export interface TwinStore {
  userId: string; setAuth: (userId: string) => void;
  twinName: string; setTwinName: (name: string) => void;
  twinGender: TwinGender; setTwinGender: (gender: TwinGender) => void;
  twinStyle: TwinStyle; setTwinStyle: (style: TwinStyle) => void;
  
  twinEnergy: number;
  dailyMessagesUsed: number;
  dailyMessagesLimit: number;
  dailyTokensUsed: number;
  dailyTokensLimit: number;
  lastMessageTimestamp: number;
  lastResetDate: string;
  
  bondLevel: number;
  relationshipDims: RelationshipDims;
  totalMessages: number;
  totalMinutes: number;
  streakDays: number;
  lastInteractionDate: string;
  memoryCount: number;
  
  voiceEnabled: boolean;
  voicePersonality: VoicePersonality;
  ttsProvider: TTSProvider;
  customVoiceId?: string;
  
  energy: number; setEnergy: (value: number) => void;
  emotionState: EmotionState | null;
  journeyPhase: JourneyPhase;
  attachmentStyle: AttachmentStyle;
  consciousnessState: ConsciousnessState | null;
  isThinking: boolean; thinkingStage: string;
  chatHistory: ChatMessage[];
  calmMode: boolean;
  theme: Theme; lang: Lang;
  tier: Tier; points: number; badges: string[];
  replyStyle: ReplyStyle;
  voiceDialect: string; voiceSpeed: number; voicePitch: number;
  menuVisible: boolean;
  hasUsedTrial: boolean;
  twinTraits: string[];
  personalityTraits: { dominant: string; secondary: string } | null;
  favoriteTopics: string[];
  preferredResponseLength: 'short' | 'medium' | 'long';
  tonePreference: 'casual' | 'formal' | 'emotional' | 'humorous';
  subscriptionTier?: string;

  incrementDailyMessage: (tokenCount?: number) => void;
  resetDailyIfNeeded: () => boolean;
  getEnergyPercent: () => number;
  getRemainingMessages: () => number;
  getRemainingTokens: () => number;
  
  recordInteraction: (minutes?: number) => void;
  addMemory: () => void;
  calculateBond: () => number;
  
  getVoiceConfig: () => VoiceConfig;
  
  updateBond: (newBond: number) => void;
  updateRelationshipDims: (dims: Partial<RelationshipDims>) => void;
  setEmotionState: (emotion: EmotionState) => void;
  setJourneyPhase: (phase: JourneyPhase) => void;
  setAttachmentStyle: (style: AttachmentStyle) => void;
  setConsciousnessState: (state: ConsciousnessState) => void;
  setThinking: (val: boolean) => void;
  setThinkingStage: (stage: string) => void;
  addMessage: (msg: Partial<ChatMessage>) => void;
  clearHistory: () => void;
  toggleCalmMode: () => void;
  toggleTheme: () => void;
  setLang: (lang: Lang) => void;
  toggleLang: () => void;
  updateTier: (tier: Tier) => void;
  addPoints: (pts: number) => void;
  addBadge: (badge: string) => void;
  setVoiceEnabled: (enabled: boolean) => void;
  setReplyStyle: (style: ReplyStyle) => void;
  setVoiceDialect: (dialect: string) => void;
  setVoiceSpeed: (speed: number) => void;
  setVoicePitch: (pitch: number) => void;
  setVoicePersonality: (p: VoicePersonality) => void;
  setTTSProvider: (provider: TTSProvider) => void;
  setCustomVoiceId: (id: string) => void;
  openMenu: () => void;
  closeMenu: () => void;
  setHasUsedTrial: (val: boolean) => void;
  setTwinTraits: (traits: string[]) => void;
  setTotalMessages: (val: number) => void;
  setTotalMinutes: (val: number) => void;
  setStreakDays: (val: number) => void;
  setDailyMessagesUsed: (val: number) => void;
  setDailyMessagesLimit: (val: number) => void;
  setTwinEnergy: (val: number) => void;
  setPersonalityTraits: (traits: any) => void;
  setFavoriteTopics: (topics: string[]) => void;
  setPreferredResponseLength: (len: 'short' | 'medium' | 'long') => void;
  setTonePreference: (tone: 'casual' | 'formal' | 'emotional' | 'humorous') => void;
  triggerHaptic: () => void;
  logout: () => void;
}

// ==================== CONSTANTS ====================

const HOURS_20_MS = 20 * 60 * 60 * 1000;

const EDGE_TTS_VOICES: Record<string, VoiceConfig> = {
  'ar-male':    { provider: 'edge_tts', voiceId: 'ar-SA-HamedNeural',    language: 'ar-SA', pitch: 1.0, rate: 0.9, gender: 'male' },
  'ar-female':  { provider: 'edge_tts', voiceId: 'ar-SA-ZariyahNeural',  language: 'ar-SA', pitch: 1.1, rate: 0.95, gender: 'female' },
  'en-male':    { provider: 'edge_tts', voiceId: 'en-US-GuyNeural',      language: 'en-US', pitch: 1.0, rate: 0.9, gender: 'male' },
  'en-female':  { provider: 'edge_tts', voiceId: 'en-US-JennyNeural',    language: 'en-US', pitch: 1.1, rate: 0.95, gender: 'female' },
};

const EXPO_SPEECH_VOICES: Record<string, VoiceConfig> = {
  'ar-male':    { provider: 'expo_speech', voiceId: 'ar-SA', language: 'ar-SA', pitch: 0.9, rate: 0.85, gender: 'male' },
  'ar-female':  { provider: 'expo_speech', voiceId: 'ar-SA', language: 'ar-SA', pitch: 1.2, rate: 0.9, gender: 'female' },
  'en-male':    { provider: 'expo_speech', voiceId: 'en-US', language: 'en-US', pitch: 0.9, rate: 0.85, gender: 'male' },
  'en-female':  { provider: 'expo_speech', voiceId: 'en-US', language: 'en-US', pitch: 1.2, rate: 0.9, gender: 'female' },
};

const ELEVENLABS_VOICES: Record<string, VoiceConfig> = {
  'ar-male':    { provider: 'elevenlabs', voiceId: 'YOUR_AR_MALE_VOICE_ID',   language: 'ar', pitch: 1.0, rate: 0.9, gender: 'male' },
  'ar-female':  { provider: 'elevenlabs', voiceId: 'YOUR_AR_FEMALE_VOICE_ID', language: 'ar', pitch: 1.0, rate: 0.95, gender: 'female' },
  'en-male':    { provider: 'elevenlabs', voiceId: 'YOUR_EN_MALE_VOICE_ID',   language: 'en', pitch: 1.0, rate: 0.9, gender: 'male' },
  'en-female':  { provider: 'elevenlabs', voiceId: 'YOUR_EN_FEMALE_VOICE_ID', language: 'en', pitch: 1.0, rate: 0.95, gender: 'female' },
};

const TIER_LIMITS: Record<Tier, { messages: number; tokens: number }> = {
  free:             { messages: 10,  tokens: 2000 },
  free_trial_14d:   { messages: 50,  tokens: 10000 },
  premium_trial:    { messages: 100, tokens: 20000 },
  plus:             { messages: 200, tokens: 50000 },
  premium:          { messages: 500, tokens: 100000 },
  pro:              { messages: 9999, tokens: 999999 },
  yearly:           { messages: 9999, tokens: 999999 },
};

// ==================== INITIAL STATE ====================

const initialState = {
  userId: '', twinName: 'توأمك', twinGender: 'female' as TwinGender,
  twinStyle: 'supportive' as TwinStyle, bondLevel: 0, energy: 50,
  relationshipDims: { trust: 0, attachment: 0, comfort: 0, openness: 0, romantic: 0, humor: 0, attStyle: 0 } as RelationshipDims,
  subscriptionTier: 'free',
  emotionState: null as EmotionState | null,
  journeyPhase: 'introduction' as JourneyPhase, attachmentStyle: 'unknown' as AttachmentStyle,
  consciousnessState: null as ConsciousnessState | null, isThinking: false, thinkingStage: 'thinking',
  chatHistory: [] as ChatMessage[],
  calmMode: false, theme: 'light' as Theme, lang: 'ar' as Lang, tier: 'free' as Tier,
  points: 0, badges: [] as string[], voiceEnabled: false, replyStyle: 'medium' as ReplyStyle,
  voiceDialect: 'modern_arabic', voiceSpeed: 0.9, voicePitch: 1.0, voicePersonality: 'friend' as VoicePersonality,
  ttsProvider: 'edge_tts' as TTSProvider, customVoiceId: undefined as string | undefined,
  menuVisible: false, hasUsedTrial: false, twinTraits: [] as string[],
  totalMessages: 0, totalMinutes: 0, streakDays: 0,
  dailyMessagesUsed: 0, dailyMessagesLimit: 10, dailyTokensUsed: 0, dailyTokensLimit: 2000,
  twinEnergy: 100, lastMessageTimestamp: 0, lastResetDate: '', lastInteractionDate: '',
  memoryCount: 0, personalityTraits: null,
  favoriteTopics: [], preferredResponseLength: 'medium' as const, tonePreference: 'emotional' as const,
};


export const useTwinStore = create<TwinStore>()(persist((set, get) => ({
  ...initialState,

  setAuth: (userId) => { console.log('🔑 setAuth:', userId); set({ userId }); },
  setTwinName: (name) => set({ twinName: name }),
  setTwinGender: (gender) => { console.log('👤 setTwinGender:', gender); set({ twinGender: gender }); },
  setTwinStyle: (style) => set({ twinStyle: style }),
  setEnergy: (value) => set({ energy: Math.max(0, Math.min(value, 100)) }),

  incrementDailyMessage: (tokenCount = 0) => set((state) => {
    const now = Date.now();
    const newMessages = state.dailyMessagesUsed + 1;
    const newTokens = state.dailyTokensUsed + tokenCount;
    
    const msgPercent = Math.min(1, newMessages / state.dailyMessagesLimit);
    const tokenPercent = Math.min(1, newTokens / state.dailyTokensLimit);
    const usedPercent = (msgPercent * 0.6) + (tokenPercent * 0.4);
    const newEnergy = Math.max(0, Math.round((1 - usedPercent) * 100));
    
    console.log('⚡ Energy:', newEnergy, '| Messages:', newMessages, '| Tokens:', newTokens);
    
    return {
      dailyMessagesUsed: newMessages,
      dailyTokensUsed: newTokens,
      twinEnergy: newEnergy,
      lastMessageTimestamp: now,
      totalMessages: state.totalMessages + 1,
    };
  }),

  resetDailyIfNeeded: () => {
    const state = get();
    const now = Date.now();
    const timeSinceLastMessage = now - state.lastMessageTimestamp;
    
    if (timeSinceLastMessage >= HOURS_20_MS) {
      const limits = TIER_LIMITS[state.tier] || TIER_LIMITS.free;
      const today = new Date().toISOString().split('T')[0];
      
      if (state.lastResetDate !== today) {
        console.log('🔄 Resetting daily energy after 20h...');
        set({
          dailyMessagesUsed: 0,
          dailyTokensUsed: 0,
          twinEnergy: 100,
          lastResetDate: today,
          lastMessageTimestamp: now,
        });
        return true;
      }
    }
    return false;
  },

  getEnergyPercent: () => {
    get().resetDailyIfNeeded();
    return get().twinEnergy;
  },

  getRemainingMessages: () => {
    const state = get();
    return Math.max(0, state.dailyMessagesLimit - state.dailyMessagesUsed);
  },

  getRemainingTokens: () => {
    const state = get();
    return Math.max(0, state.dailyTokensLimit - state.dailyTokensUsed);
  },

  recordInteraction: (minutes = 0) => set((state) => {
    const now = new Date().toISOString().split('T')[0];
    let newStreak = state.streakDays;
    
    if (state.lastInteractionDate) {
      const lastDate = new Date(state.lastInteractionDate);
      const todayDate = new Date(now);
      const diffDays = Math.floor((todayDate.getTime() - lastDate.getTime()) / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) {
        newStreak = state.streakDays + 1;
      } else if (diffDays > 1) {
        newStreak = 1;
      }
    } else {
      newStreak = 1;
    }
    
    const newTotalMinutes = state.totalMinutes + minutes;
    const newTotalMessages = state.totalMessages;
    
    const msgFactor = Math.min(1, newTotalMessages / 500) * 40;
    const timeFactor = Math.min(1, newTotalMinutes / 300) * 30;
    const memoryFactor = Math.min(1, state.memoryCount / 50) * 20;
    const streakFactor = Math.min(1, newStreak / 30) * 10;
    
    const newBond = Math.min(100, msgFactor + timeFactor + memoryFactor + streakFactor);
    
    const badges = [...state.badges];
    if (newBond >= 20 && !badges.includes('acquaintance')) badges.push('acquaintance');
    if (newBond >= 40 && !badges.includes('friend')) badges.push('friend');
    if (newBond >= 60 && !badges.includes('trusted')) badges.push('trusted');
    if (newBond >= 80 && !badges.includes('soulmate')) badges.push('soulmate');
    if (newBond >= 95 && !badges.includes('champion')) badges.push('champion');
    if (newStreak >= 7 && !badges.includes('week_streak')) badges.push('week_streak');
    if (newStreak >= 30 && !badges.includes('month_streak')) badges.push('month_streak');
    
    console.log('💕 Bond:', Math.round(newBond), '| Streak:', newStreak, '| Memories:', state.memoryCount);
    
    return {
      bondLevel: Math.round(newBond),
      streakDays: newStreak,
      lastInteractionDate: now,
      totalMinutes: newTotalMinutes,
      badges,
    };
  }),

  addMemory: () => set((state) => {
    const newCount = state.memoryCount + 1;
    const msgFactor = Math.min(1, state.totalMessages / 500) * 40;
    const timeFactor = Math.min(1, state.totalMinutes / 300) * 30;
    const memoryFactor = Math.min(1, newCount / 50) * 20;
    const streakFactor = Math.min(1, state.streakDays / 30) * 10;
    const newBond = Math.min(100, msgFactor + timeFactor + memoryFactor + streakFactor);
    
    return { memoryCount: newCount, bondLevel: Math.round(newBond) };
  }),

  calculateBond: () => {
    const state = get();
    const msgFactor = Math.min(1, state.totalMessages / 500) * 40;
    const timeFactor = Math.min(1, state.totalMinutes / 300) * 30;
    const memoryFactor = Math.min(1, state.memoryCount / 50) * 20;
    const streakFactor = Math.min(1, state.streakDays / 30) * 10;
    return Math.min(100, msgFactor + timeFactor + memoryFactor + streakFactor);
  },

  getVoiceConfig: () => {
    const state = get();
    const langCode = state.lang === 'ar' ? 'ar' : 'en';
    const gender = state.twinGender === 'male' ? 'male' : 'female';
    const key = `${langCode}-${gender}`;
    
    switch (state.ttsProvider) {
      case 'expo_speech':
        return EXPO_SPEECH_VOICES[key] || EXPO_SPEECH_VOICES['ar-female'];
      case 'elevenlabs':
        if (state.customVoiceId) {
          return {
            provider: 'elevenlabs',
            voiceId: state.customVoiceId,
            language: langCode,
            pitch: state.voicePitch,
            rate: state.voiceSpeed,
            gender,
          };
        }
        return ELEVENLABS_VOICES[key] || ELEVENLABS_VOICES['ar-female'];
      case 'edge_tts':
      default:
        return EDGE_TTS_VOICES[key] || EDGE_TTS_VOICES['ar-female'];
    }
  },

  updateBond: (newBond) => set((state) => {
    const safeBond = Math.max(0, Math.min(newBond, 100));
    const badges = [...state.badges];
    if (safeBond >= 40 && !badges.includes('friend')) badges.push('friend');
    if (safeBond >= 60 && !badges.includes('trusted')) badges.push('trusted');
    if (safeBond >= 80 && !badges.includes('soulmate')) badges.push('soulmate');
    if (safeBond >= 95 && !badges.includes('champion')) badges.push('champion');
    return { bondLevel: safeBond, badges };
  }),

  updateRelationshipDims: (dims) => set((state) => ({ 
    relationshipDims: { ...state.relationshipDims, ...dims } 
  })),
  setEmotionState: (emotion) => set({ emotionState: emotion }),
  setJourneyPhase: (phase) => set({ journeyPhase: phase }),
  setAttachmentStyle: (style) => set({ attachmentStyle: style }),
  setConsciousnessState: (state) => set({ consciousnessState: state }),
  setThinking: (val) => set({ isThinking: val }),
  setThinkingStage: (stage) => set({ thinkingStage: stage }),

  addMessage: (msg) => set((state) => ({ 
    chatHistory: [...state.chatHistory, {
      id: msg.id || generateId(), role: msg.role || 'user', content: msg.content || '',
      image: msg.image || undefined, timestamp: msg.timestamp || Date.now(),
      failed: msg.failed || false, emotion: msg.emotion || undefined,
      journeyPhase: msg.journeyPhase || undefined, relationshipStage: msg.relationshipStage || undefined,
      memoryRecall: msg.memoryRecall || undefined, thinkingStage: msg.thinkingStage || undefined,
      youtubeVideo: msg.youtubeVideo || undefined, provider: msg.provider || undefined,
    }].slice(-200) 
  })),

  clearHistory: () => set({ chatHistory: [] }),
  toggleCalmMode: () => set((s) => ({ calmMode: !s.calmMode })),
  toggleTheme: () => set((s) => ({ theme: s.theme === 'dark' ? 'light' : 'dark' })),
  setLang: (lang) => set({ lang }),
  toggleLang: () => set((s) => ({ lang: s.lang === 'ar' ? 'en' : 'ar' })),
  updateTier: (tier) => {
    const limits = TIER_LIMITS[tier] || TIER_LIMITS.free;
    set({ tier, dailyMessagesLimit: limits.messages, dailyTokensLimit: limits.tokens });
  },
  addPoints: (pts) => set((s) => ({ points: s.points + pts })),
  addBadge: (badge) => set((s) => s.badges.includes(badge) ? s : { badges: [...s.badges, badge] }),
  setVoiceEnabled: (enabled) => set({ voiceEnabled: enabled }),
  setReplyStyle: (style) => set({ replyStyle: style }),
  setVoiceDialect: (dialect) => set({ voiceDialect: dialect }),
  setVoiceSpeed: (speed) => set({ voiceSpeed: speed }),
  setVoicePitch: (pitch) => set({ voicePitch: pitch }),
  setVoicePersonality: (p) => set({ voicePersonality: p }),
  setTTSProvider: (provider) => set({ ttsProvider: provider }),
  setCustomVoiceId: (id) => set({ customVoiceId: id }),
  openMenu: () => set({ menuVisible: true }),
  closeMenu: () => set({ menuVisible: false }),
  setHasUsedTrial: (val) => set({ hasUsedTrial: val }),
  setTwinTraits: (traits) => set({ twinTraits: traits }),
  setTotalMessages: (val) => set({ totalMessages: val }),
  setTotalMinutes: (val) => set({ totalMinutes: val }),
  setStreakDays: (val) => set({ streakDays: val }),
  setDailyMessagesUsed: (val) => set({ dailyMessagesUsed: val }),
  setDailyMessagesLimit: (val) => set({ dailyMessagesLimit: val }),
  setTwinEnergy: (val) => set({ twinEnergy: val }),
  setPersonalityTraits: (traits) => set({ personalityTraits: traits }),
  setFavoriteTopics: (topics) => set({ favoriteTopics: topics }),
  setPreferredResponseLength: (len) => set({ preferredResponseLength: len }),
  setTonePreference: (tone) => set({ tonePreference: tone }),

  triggerHaptic: () => { 
    if (!get().calmMode) Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); 
  },
  
  logout: () => set({ ...initialState, chatHistory: [] }),
}), {
  name: 'mytwin-store',
  storage: createJSONStorage(() => AsyncStorage),
  partialize: (state) => ({
    userId: state.userId, twinName: state.twinName, twinGender: state.twinGender,
    twinStyle: state.twinStyle, bondLevel: state.bondLevel, relationshipDims: state.relationshipDims,
    subscriptionTier: state.subscriptionTier,
    energy: state.energy, emotionState: state.emotionState,
    journeyPhase: state.journeyPhase, attachmentStyle: state.attachmentStyle,
    calmMode: state.calmMode, theme: state.theme, lang: state.lang,
    tier: state.tier, points: state.points, badges: state.badges,
    voiceEnabled: state.voiceEnabled, replyStyle: state.replyStyle,
    voiceDialect: state.voiceDialect, voiceSpeed: state.voiceSpeed, voicePitch: state.voicePitch,
    voicePersonality: state.voicePersonality, ttsProvider: state.ttsProvider, customVoiceId: state.customVoiceId,
    hasUsedTrial: state.hasUsedTrial, twinTraits: state.twinTraits,
    totalMessages: state.totalMessages, totalMinutes: state.totalMinutes, streakDays: state.streakDays,
    dailyMessagesUsed: state.dailyMessagesUsed, dailyMessagesLimit: state.dailyMessagesLimit,
    dailyTokensUsed: state.dailyTokensUsed, dailyTokensLimit: state.dailyTokensLimit,
    twinEnergy: state.twinEnergy, lastMessageTimestamp: state.lastMessageTimestamp,
    lastResetDate: state.lastResetDate, lastInteractionDate: state.lastInteractionDate,
    memoryCount: state.memoryCount, personalityTraits: state.personalityTraits,
    favoriteTopics: state.favoriteTopics, preferredResponseLength: state.preferredResponseLength,
    tonePreference: state.tonePreference,
  }),
}));
