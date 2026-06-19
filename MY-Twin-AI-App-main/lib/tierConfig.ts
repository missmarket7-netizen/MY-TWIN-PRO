export interface TierConfig {
  name: string;
  price: number;
  billingPeriod?: string;
  dailyMessages: number;
  dailyFeatures: {
    study: number;
    content: number;
    business: number;
    code: number;
    image: number;
  };
  adsRequired: boolean;
  memoryDays: number;
  models: string[];
  voice: string;
  coaching: boolean;
  dreams: boolean;
}

export const TIERS: Record<string, TierConfig> = {
  free: {
    name: 'Free',
    price: 0,
    dailyMessages: 10,
    dailyFeatures: { study: 1, content: 1, business: 0, code: 0, image: 1 },
    adsRequired: true,
    memoryDays: 3,
    models: ['groq'],
    voice: 'edge_tts',
    coaching: false,
    dreams: false,
  },
  plus: {
    name: 'Plus',
    price: 5.99,
    dailyMessages: 30,
    dailyFeatures: { study: 5, content: 5, business: 2, code: 2, image: 3 },
    adsRequired: false,
    memoryDays: 30,
    models: ['groq', 'gemini'],
    voice: 'edge_tts',
    coaching: false,
    dreams: false,
  },
  premium: {
    name: 'Premium',
    price: 14.99,
    dailyMessages: 100,
    dailyFeatures: { study: 20, content: 20, business: 10, code: 10, image: 10 },
    adsRequired: false,
    memoryDays: 90,
    models: ['gemini', 'groq', 'openrouter'],
    voice: 'elevenlabs',
    coaching: true,
    dreams: true,
  },
  pro: {
    name: 'Pro',
    price: 110,
    billingPeriod: '6_months',
    dailyMessages: 500,
    dailyFeatures: { study: 100, content: 100, business: 50, code: 50, image: 30 },
    adsRequired: false,
    memoryDays: 365,
    models: ['gemini', 'groq', 'openrouter'],
    voice: 'elevenlabs',
    coaching: true,
    dreams: true,
  },
  yearly: {
    name: 'Yearly',
    price: 199,
    billingPeriod: 'yearly',
    dailyMessages: 9999,
    dailyFeatures: { study: 999, content: 999, business: 999, code: 999, image: 999 },
    adsRequired: false,
    memoryDays: 999,
    models: ['gemini', 'groq', 'openrouter'],
    voice: 'elevenlabs',
    coaching: true,
    dreams: true,
  },
};

export const getTierConfig = (tier: string): TierConfig => TIERS[tier] || TIERS.free;
