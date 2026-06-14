#!/bin/bash
set -e

RAILWAY_URL="https://my-twin-pro-production-b744.up.railway.app"
TEST_EMAIL="${TEST_EMAIL:-sir.market7@gmail.com}"
TEST_PASSWORD="${TEST_PASSWORD:-M#m2606.1307}"

cd /workspaces/MY-TWIN-PRO/MY-Twin-AI-App-main

echo "========================================="
echo "🔍 المرحلة 1: فحص الواجهة الأمامية (ESLint)"
echo "========================================="
npx eslint app/ lib/ store/ --ext .ts,.tsx 2>&1 | tail -20
echo ""
echo "✅ المرحلة 1 انتهت"

echo ""
echo "========================================="
echo "🔍 المرحلة 2: فحص Python (backend)"
echo "========================================="
cd backend
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
echo "فحص ${#FILES[@]} ملف..."
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    python3 -c "import py_compile; py_compile.compile('$file', doraise=True)" 2>&1 && echo "✅ $file" || echo "❌ خطأ في $file"
  else
    echo "⚠️  غير موجود: $file"
  fi
done

echo ""
echo "فحص الاستيراد الكامل..."
python3 -c "
import sys, traceback
modules = [
    'main', 'twin_brain', 'reasoning_engine', 'memory_retriever', 'memory_graph',
    'memory_summarizer', 'context_manager', 'consciousness_core', 'emotional_engine',
    'relationship_engine', 'attachment_engine', 'model_router', 'self_critic',
    'reranker', 'profile_extractor', 'user_model', 'multi_ai', 'prompt_builder',
    'response_validator', 'tool_router', 'agent_loop', 'agent_metrics',
    'dream_engine', 'voice_personality', 'voice_engine'
]
ok = 0
for m in modules:
    try:
        __import__(m)
        ok += 1
    except Exception as e:
        print(f'❌ {m}: {e}')
print(f'✅ تم استيراد {ok}/{len(modules)}')
"
cd ..
echo "✅ المرحلة 2 انتهت"

echo ""
echo "========================================="
echo "🧪 المرحلة 3: اختبارات الوحدة (pytest)"
echo "========================================="
if [ -f backend/tests/test_tools.py ]; then
  cd backend
  python3 -m pytest tests/test_tools.py -v 2>&1 | tail -20
  cd ..
else
  echo "⚠️ ملف tests/test_tools.py مفقود"
fi
echo "✅ المرحلة 3 انتهت"

echo ""
echo "========================================="
echo "🌐 المرحلة 4: اختبار الخادم الحي"
echo "========================================="

# الحصول على توكن
TOKEN=$(curl -s -X POST \
  'https://cndbzlwitzhldahuooag.supabase.co/auth/v1/token?grant_type=password' \
  -H "apikey: $(grep EXPO_PUBLIC_SUPABASE_ANON_KEY .env | cut -d '=' -f2)" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$sir.market7@gmail.com\",\"password\":\"$M#m2606.1307\"}" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')

if [ -z "$TOKEN" ]; then
  echo "❌ فشل تسجيل الدخول"
  exit 1
fi
echo "✅ التوكن: ${#TOKEN} حرف"

echo ""
echo "🌐 الصحة العامة..."
curl -s $RAILWAY_URL/ | python3 -m json.tool

echo ""
echo "🤖 صحة AI..."
curl -s $RAILWAY_URL/api/health/ai | python3 -m json.tool

echo ""
echo "💬 المحادثة..."
curl -s -X POST $RAILWAY_URL/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"مرحبا","twin_name":"ليليان","bond_level":50,"dims":{},"history":[]}' | python3 -c '
import sys,json
d=json.load(sys.stdin)
print("الرد:", d.get("reply","")[:100])
print("المزود:", d.get("provider","?"))
print("الزمن:", d.get("latency_ms","?"), "ms")
'

echo ""
echo "🎁 الإحالة..."
curl -s -X POST $RAILWAY_URL/api/referral/generate \
  -H "Authorization: Bearer $TOKEN" | python3 -c '
import sys,json; d=json.load(sys.stdin); print("كود:", d.get("code",""))
'

echo ""
echo "📊 الإحصائيات..."
curl -s -H "Authorization: Bearer $TOKEN" \
  $RAILWAY_URL/api/stats | python3 -c '
import sys,json; d=json.load(sys.stdin); print("طلبات اليوم:", d.get("daily_requests","?"))
'

echo ""
echo "🔔 proactive..."
curl -s -H "Authorization: Bearer $TOKEN" \
  $RAILWAY_URL/api/proactive/check | python3 -c '
import sys,json; d=json.load(sys.stdin); print("should_send:", d.get("should_send","?"))
'

echo ""
echo "🖼️ توليد الصور..."
curl -s -X POST $RAILWAY_URL/api/image/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt":"test"}' | python3 -c '
import sys,json; d=json.load(sys.stdin)
if d.get("status")=="success": print("✅ صورة base64 طول:", len(d.get("image_base64","")))
elif "quota" in d.get("message",""): print("⚠️ الحصة منتهية")
else: print("❌", d.get("message",""))
'

echo ""
echo "🎵 يوتيوب..."
curl -s -H "Authorization: Bearer $TOKEN" \
  "$RAILWAY_URL/api/services/youtube?query=music&lang=ar" | python3 -c '
import sys,json; d=json.load(sys.stdin)
if "error" in d: print("❌", d["error"])
else: print("✅ نتيجة:", str(d.get("result",""))[:80])
'

echo ""
echo "🌤️ الطقس..."
curl -s -H "Authorization: Bearer $TOKEN" \
  "$RAILWAY_URL/api/services/weather?city=Cairo" | python3 -c '
import sys,json; d=json.load(sys.stdin)
if "error" in d: print("❌", d["error"])
else: print("✅", str(d.get("result",""))[:80])
'

echo ""
echo "========================================="
echo "✅ تم الانتهاء من جميع الاختبارات"
echo "========================================="
