/**
 * MyTwin – Memory Helpers v2.0
 * دوال مساعدة لحفظ واسترجاع الذكريات من Supabase.
 * مع Validation كامل، معالجة أخطاء، وتسجيل.
 */

// ── الثوابت ──────────────────────────────────────
const MAX_CONTENT_LENGTH = 300;
const MAX_DAYS = 365; // حد أقصى للفترة الزمنية
const DEFAULT_DAYS = 7;
const MAX_MEMORIES = 10;

// ─ـ واجهات ───────────────────────────────────────
export interface MemoryResult {
  success: boolean;
  id?: string;
  error?: string;
}

export interface MemoryRecord {
  id: string;
  content: string;
  importance_score: number;
  created_at: string;
}

// ─ـ تسجيل الأخطاء ───────────────────────────────
function logError(context: string, error: unknown): void {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`[MemoryHelper] ${context}:`, message);
  // يمكن إرسال الخطأ إلى Sentry أو أي خدمة مراقبة هنا
}

// ─ـ التحقق من صحة المدخلات ──────────────────────
function validateMemoryInput(userId: string, content: string, importance: number): string | null {
  if (!userId || typeof userId !== 'string' || !userId.trim()) {
    return 'userId is required and must be a non-empty string';
  }
  if (!content || typeof content !== 'string' || !content.trim()) {
    return 'content is required and must be a non-empty string';
  }
  if (importance === undefined || importance === null) {
    return 'importance is required';
  }
  if (typeof importance !== 'number' || !isFinite(importance)) {
    return 'importance must be a valid finite number';
  }
  return null; // صالح
}

function validateGetMemoriesInput(userId: string, days: number): string | null {
  if (!userId || typeof userId !== 'string' || !userId.trim()) {
    return 'userId is required and must be a non-empty string';
  }
  if (typeof days !== 'number' || !isFinite(days)) {
    return 'days must be a valid finite number';
  }
  return null; // صالح
}

// ─ـ قص النص بذكاء (لا يقطع الكلمات أو الإيموجي) ──
function smartTruncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text.trim();

  // محاولة القص عند آخر مسافة قبل الحد
  const truncated = text.slice(0, maxLength);
  const lastSpaceIndex = truncated.lastIndexOf(' ');

  // إذا لم نجد مسافة، نقص عند الحد تماماً
  return (lastSpaceIndex > 0 ? truncated.slice(0, lastSpaceIndex) : truncated).trim() + '…';
}

// ─ـ حفظ ذكرى جديدة ──────────────────────────────
export async function saveMemory(
  userId: string,
  content: string,
  importance: number
): Promise<MemoryResult> {
  // 1. التحقق من الصحة
  const validationError = validateMemoryInput(userId, content, importance);
  if (validationError) {
    logError('saveMemory validation', validationError);
    return { success: false, error: validationError };
  }

  try {
    // 2. تنظيف المحتوى
    const cleanedContent = content.trim();
    const truncatedContent = smartTruncate(cleanedContent, MAX_CONTENT_LENGTH);
    const safeImportance = Math.max(0, Math.min(1, importance));

    // 3. حفظ في قاعدة البيانات
    const { data, error } = await supabase
      .from('memories')
      .insert({
        user_id: userId,
        content: truncatedContent,
        importance_score: safeImportance,
        // لا نمرر created_at يدوياً – نستخدم default now() في قاعدة البيانات
      })
      .select('id, created_at')
      .single();

    if (error) {
      logError('saveMemory insert', error);
      return { success: false, error: error.message };
    }

    return {
      success: true,
      id: data?.id,
    };
  } catch (error) {
    logError('saveMemory unexpected', error);
    return { success: false, error: 'Unexpected error occurred while saving memory' };
  }
}

// ─ـ جلب أحدث ذكريات المستخدم ────────────────────
export async function getMemories(
  userId: string,
  days: number = DEFAULT_DAYS
): Promise<MemoryRecord[]> {
  // 1. التحقق من الصحة
  const validationError = validateGetMemoriesInput(userId, days);
  if (validationError) {
    logError('getMemories validation', validationError);
    return [];
  }

  try {
    // 2. تحديد الفترة الزمنية مع حد أقصى
    const safeDays = Math.max(1, Math.min(days, MAX_DAYS));
    const cutoff = new Date(Date.now() - safeDays * 24 * 60 * 60 * 1000).toISOString();

    // 3. استعلام من قاعدة البيانات
    const { data, error } = await supabase
      .from('memories')
      .select('id, content, importance_score, created_at')
      .eq('user_id', userId)
      .gte('created_at', cutoff)
      .order('importance_score', { ascending: false })
      .limit(MAX_MEMORIES);

    if (error) {
      logError('getMemories query', error);
      return [];
    }

    return (data || []) as MemoryRecord[];
  } catch (error) {
    logError('getMemories unexpected', error);
    return [];
  }
}

// ─ـ حذف ذكرى ─────────────────────────────────────
export async function deleteMemory(memoryId: string): Promise<boolean> {
  if (!memoryId || typeof memoryId !== 'string' || !memoryId.trim()) {
    logError('deleteMemory validation', 'memoryId is required');
    return false;
  }

  try {
    const { error } = await supabase
      .from('memories')
      .delete()
      .eq('id', memoryId);

    if (error) {
      logError('deleteMemory delete', error);
      return false;
    }

    return true;
  } catch (error) {
    logError('deleteMemory unexpected', error);
    return false;
  }
}
