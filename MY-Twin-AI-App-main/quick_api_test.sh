#!/bin/bash
set -e

RAILWAY_URL="https://my-twin-pro-production-b744.up.railway.app"
EMAIL="sir.market7@gmail.com"
PASSWORD="M#m2606.1307"

echo "🔑 تسجيل الدخول..."
TOKEN=$(curl -s -X POST \
  'https://cndbzlwitzhldahuooag.supabase.co/auth/v1/token?grant_type=password' \
  -H "apikey: $(grep EXPO_PUBLIC_SUPABASE_ANON_KEY .env | cut -d '=' -f2)" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')

if [ -z "$TOKEN" ]; then
  echo "❌ فشل تسجيل الدخول"
  exit 1
fi
echo "✅ تم تسجيل الدخول"

echo ""
echo "🤖 صحة AI..."
curl -s $RAILWAY_URL/api/health/ai | python3 -m json.tool

echo ""
echo "💬 المحادثة..."
curl -s -X POST $RAILWAY_URL/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"مرحبا، كيف حالك؟","twin_name":"ليليان","bond_level":50,"dims":{},"history":[]}' | python3 -c '
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
echo "✅ تم الانتهاء من جميع الاختبارات"
