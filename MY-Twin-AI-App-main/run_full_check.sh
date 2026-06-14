#!/bin/bash
set -e

# ========== إعدادات ==========
RAILWAY_URL="https://my-twin-pro-production-b744.up.railway.app"
TEST_EMAIL="${TEST_EMAIL:-sir.market7@gmail.com}"
TEST_PASSWORD="${TEST_PASSWORD:-M#m2606.1307}"

cd /workspaces/MY-TWIN-PRO/MY-Twin-AI-App-main

echo "========================================="
echo "🔍 المرحلة 1: فحص TypeScript (الواجهة)"
echo "========================================="
# فحص مجزأ لتفادي terminated (3 ملفات أساسية فقط)
echo "• فحص app/chat/index.tsx ..."
npx tsc --noEmit app/chat/index.tsx 2>&1 | tail -5
echo "• فحص store/useTwinStore.ts ..."
npx tsc --noEmit store/useTwinStore.ts 2>&1 | tail -5
echo "• فحص lib/api.ts ..."
npx tsc --noEmit lib/api.ts 2>&1 | tail -5
echo "✅ فحص TypeScript الجزئي انتهى (لتفادي تعارض DOM وterminated)"

echo ""
echo "========================================="
echo "🔍 المرحلة 2: فحص Python (backend)"
echo "========================================="
cd backend
# الملفات الأساسية الحقيقية
FILES=(
  main.py twin_brain.py multi_ai.py model_router.py
  memory_retriever.py memory_graph.py memory_summarizer.py
  context_manager.py consciousness_core.py emotional_engine.py
  dialect_engine.py relationship_engine.py attachment_engine.py
  prompt_builder.py reasoning_engine.py profile_extractor.py
  self_critic.py reranker.py user_model.py response_validator.py
  voice_personality.py voice_engine.py dream_engine.py
  growth_tracker.py twin_journey.py safety_engine.py
  proactive_engine.py product_recommender.py
  referral.py rate_limiter.py cache.py message_limits.py
  telegram_webhook.py
  tools/__init__.py tools/tool_router.py tools/tool_executor.py
  tools/external_services.py tools/agent_loop.py tools/agent_metrics.py
  tools/final_synthesizer.py tools/scratchpad.py tools/agent_budget.py
  tools/tool_argument_builder.py
)
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    python3 -c "import py_compile; py_compile.compile('$file', doraise=True)" 2>&1 && echo "✅ $file" || echo "❌ خطأ في $file"
  else
    echo "⚠️  الملف غير موجود: $file"
  fi
done
cd ..

echo ""
echo "========================================="
echo "🧪 المرحلة 3: اختبار الخادم الحي"
echo "========================================="

# الحصول على توكن
TOKEN=$(curl -s -X POST \
  'https://cndbzlwitzhldahuooag.supabase.co/auth/v1/token?grant_type=password' \
  -H "apikey: $(grep EXPO_PUBLIC_SUPABASE_ANON_KEY .env | cut -d '=' -f2)" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')

if [ -z "$TOKEN" ]; then
  echo "❌ فشل الحصول على توكن (تأكد من email/password)"
  exit 1
fi
echo "✅ التوكن: ${#TOKEN} حرف"

echo ""
echo "🌐 اختبار الصحة العامة..."
curl -s $RAILWAY_URL/ | python3 -m json.tool

echo ""
echo "🤖 اختبار صحة AI..."
curl -s $RAILWAY_URL/api/health/ai | python3 -m json.tool

echo ""
echo "💬 اختبار المحادثة..."
curl -s -X POST $RAILWAY_URL/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"مرحبا، كيف حالك؟","twin_name":"ليليان","bond_level":50,"dims":{},"history":[]}' | python3 -c '
import sys,json
d=json.load(sys.stdin)
print("✅ الرد:", d.get("reply","")[:100])
print("🔌 المزود:", d.get("provider","unknown"))
print("⏱️  زمن الاستجابة:", d.get("latency_ms","?"), "ms")
'

echo ""
echo "🎁 اختبار الإحالة..."
curl -s -X POST $RAILWAY_URL/api/referral/generate \
  -H "Authorization: Bearer $TOKEN" | python3 -c '
import sys,json
d=json.load(sys.stdin)
print("✅ الكود:", d.get("code",""))
'

echo ""
echo "📊 اختبار AI Stats..."
curl -s -H "Authorization: Bearer $TOKEN" \
  $RAILWAY_URL/api/stats | python3 -c '
import sys,json
d=json.load(sys.stdin)
print("✅ طلبات اليوم:", d.get("daily_requests","?"))
'

echo ""
echo "🔔 اختبار Proactive Check..."
curl -s -H "Authorization: Bearer $TOKEN" \
  $RAILWAY_URL/api/proactive/check | python3 -c '
import sys,json
d=json.load(sys.stdin)
print("✅ should_send:", d.get("should_send","?"), "| user_id:", d.get("user_id","?"))
'

echo ""
echo "🖼️ اختبار توليد الصور..."
curl -s -X POST $RAILWAY_URL/api/image/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt":"A purple cybernetic logo"}' | python3 -c '
import sys,json
d=json.load(sys.stdin)
if d.get("status")=="success":
    print("✅ الصورة تم توليدها (base64 length:",len(d.get("image_base64","")),")")
elif "quota" in d.get("message","").lower():
    print("⚠️  الحصة اليومية للصور استنفدت (طبيعي)")
else:
    print("❌ خطأ:",d.get("message",""))
'

echo ""
echo "========================================="
echo "✅ تم الانتهاء من جميع الاختبارات"
echo "========================================="
