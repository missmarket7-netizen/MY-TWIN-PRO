#!/bin/bash

BASE="https://my-twin-pro-production-b744.up.railway.app"
PASS=0
FAIL=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 اختبار شامل"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# الحصول على توكن
LOGIN=$(curl -s -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"sir.market7@gmail.com","password":"M#m2606.1307"}')
TOKEN=$(echo "$LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ فشل المصادقة"
    exit 1
fi
echo "✅ توكن: ${TOKEN:0:20}..."
echo ""

test_route() {
    printf "   %-35s ... " "$1"
    RESPONSE=$(curl -s -X POST "$BASE$2" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d "$3" 2>/dev/null)
    if echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); v=d.get('$4',''); exit(0 if v and len(str(v))>10 else 1)" 2>/dev/null; then
        echo "✅"
        echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print('      ',str(d.get('$4',''))[:100])" 2>/dev/null
        PASS=$((PASS+1))
    else
        echo "❌"
        echo "      $(echo "$RESPONSE" | python3 -c "import sys,json; print(str(json.load(sys.stdin))[:100])" 2>/dev/null)"
        FAIL=$((FAIL+1))
    fi
}

echo "📋 الاختبارات:"
test_route "محادثة" "/api/chat" '{"message":"مرحباً","lang":"ar"}' "reply"
test_route "مذاكرة" "/api/features/study" '{"topic":"فيثاغورس","level":"intermediate","type":"explain","lang":"ar"}' "reply"
test_route "برمجة" "/api/features/code" '{"task":"hello world","language":"python","action":"write","lang":"ar"}' "reply"
test_route "أعمال" "/api/features/business" '{"text":"مبيعات 1M","analysis_type":"general","lang":"ar"}' "reply"
test_route "مدرب حياة" "/api/features/coach" '{"topic":"ثقة","domain":"personal","lang":"ar"}' "reply"
test_route "محتوى" "/api/features/content" '{"topic":"تسويق","platform":"instagram","tone":"professional","lang":"ar"}' "reply"
test_route "حلم" "/api/features/dream" '{"dream":"أطير","lang":"ar"}' "interpretation"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 $PASS ✅ / $FAIL ❌"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
