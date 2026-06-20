import { useTwinStore } from '../store/useTwinStore';

export function useRTL() {
  const lang = useTwinStore(s => s.lang);
  return {
    isRTL: lang === 'ar',
    flexDirection: (lang === 'ar' ? 'row-reverse' : 'row') as 'row' | 'row-reverse',
    textAlign: (lang === 'ar' ? 'right' : 'left') as 'right' | 'left',
    writingDirection: (lang === 'ar' ? 'rtl' : 'ltr') as 'rtl' | 'ltr',
  };
}
