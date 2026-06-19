#!/bin/bash

BASE="https://my-twin-pro-production-b744.up.railway.app"
TOKEN=""
PASS=0
FAIL=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 اختبار شامل – كل الميزات والأدوات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 1. المصادقة ───────────────────────────────
echo "📋 1. المصادقة..."
LOGIN=$(curl -s -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"sir.market7@gmail.com","password":"M#m2606.1307"}')
TOKEN=$(echo "$LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "   ❌ فشل المصادقة. الرد: $LOGIN"
    exit 1
fi
echo "   ✅ تم تسجيل الدخول"
echo ""

# ── دالة الاختبار ────────────────────────────
test_feature() {
    NAME=$1
    URL="$BASE$2"
    DATA=$3
    EXTRACT=$4
    
    printf "   %-35s ... " "$NAME"
    
    RESPONSE=$(curl -s -X POST "$URL" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d "$DATA" 2>/dev/null)
    
    HTTP_CODE=$(echo "$RESPONSE" | python3 -c "import sys; print('200')" 2>/dev/null)
    
    if echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
val = d.get('$EXTRACT', '')
if val and len(str(val)) > 10:
    print('OK')
else:
    print('EMPTY')
" 2>/dev/null | grep -q "OK"; then
        echo "✅ نجح"
        echo "      $(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(str(d.get('$EXTRACT',''))[:120])" 2>/dev/null)"
        PASS=$((PASS + 1))
    else
        echo "❌ فشل (رد فارغ أو خطأ)"
        echo "      $(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(str(d)[:150])" 2>/dev/null)"
        FAIL=$((FAIL + 1))
    fi
}

# ── 2. المحادثة الأساسية ──────────────────────
echo "📋 2. المحادثة الأساسية:"
test_feature "محادثة عامة" "/api/chat" \
    '{"message":"مرحباً، كيف حالك؟","lang":"ar"}' "reply"
echo ""

# ── 3. المذاكرة الذكية ────────────────────────
echo "📋 3. المذاكرة الذكية:"
test_feature "شرح" "/api/features/study" \
    '{"topic":"نظرية فيثاغورس","level":"intermediate","type":"explain","lang":"ar"}' "reply"
test_feature "تلخيص" "/api/features/study" \
    '{"topic":"الحرب العالمية الثانية","level":"advanced","type":"summarize","lang":"ar"}' "reply"
test_feature "حل مسألة" "/api/features/study" \
    '{"topic":"2x + 5 = 15","level":"beginner","type":"solve","lang":"ar"}' "reply"
test_feature "خطة دراسية" "/api/features/study" \
    '{"topic":"تعلم بايثون","level":"beginner","type":"plan","lang":"ar"}' "reply"
echo ""

# ── 4. مختبر البرمجة ──────────────────────────
echo "📋 4. مختبر البرمجة:"
test_feature "كتابة كود" "/api/features/code" \
    '{"task":"دالة تجمع رقمين","language":"python","action":"write","lang":"ar"}' "reply"
test_feature "شرح كود" "/api/features/code" \
    '{"task":"for i in range(10): print(i)","language":"python","action":"explain","lang":"ar"}' "reply"
test_feature "تصحيح كود" "/api/features/code" \
    '{"task":"prin(hello)","language":"python","action":"debug","lang":"ar"}' "reply"
test_feature "مراجعة كود" "/api/features/code" \
    '{"task":"def add(a,b): return a+b","language":"python","action":"review","lang":"ar"}' "reply"
echo ""

# ── 5. تحليل الأعمال ──────────────────────────
echo "📋 5. تحليل الأعمال:"
test_feature "تحليل عام" "/api/features/business" \
    '{"text":"مبيعات الشركة 1M هذا الربع","analysis_type":"general","lang":"ar"}' "reply"
test_feature "تحليل مالي" "/api/features/business" \
    '{"text":"الإيرادات 500K والمصروفات 300K","analysis_type":"financial","lang":"ar"}' "reply"
test_feature "تحليل تسويقي" "/api/features/business" \
    '{"text":"نريد زيادة المبيعات 20%","analysis_type":"marketing","lang":"ar"}' "reply"
echo ""

# ── 6. مدرب الحياة ────────────────────────────
echo "📋 6. مدرب الحياة:"
test_feature "دعم نفسي" "/api/features/coach" \
    '{"topic":"أشعر بالقلق","domain":"psychological","lang":"ar"}' "reply"
test_feature "دعم اجتماعي" "/api/features/coach" \
    '{"topic":"علاقاتي الاجتماعية","domain":"social","lang":"ar"}' "reply"
test_feature "دعم عملي" "/api/features/coach" \
    '{"topic":"تطوير مسيرتي","domain":"professional","lang":"ar"}' "reply"
echo ""

# ── 7. كتابة المحتوى ──────────────────────────
echo "📋 7. كتابة المحتوى:"
test_feature "انستغرام" "/api/features/content" \
    '{"topic":"التسويق الرقمي","platform":"instagram","tone":"professional","lang":"ar"}' "reply"
test_feature "تويتر" "/api/features/content" \
    '{"topic":"الذكاء الاصطناعي","platform":"twitter","tone":"casual","lang":"ar"}' "reply"
test_feature "لينكدإن" "/api/features/content" \
    '{"topic":"القيادة","platform":"linkedin","tone":"professional","lang":"ar"}' "reply"
echo ""

# ── 8. تفسير الأحلام ──────────────────────────
echo "📋 8. تفسير الأحلام:"
test_feature "تفسير حلم" "/api/features/dream" \
    '{"dream":"حلمت أني أطير في السماء","lang":"ar"}' "interpretation"
echo ""

# ── 9. الإحالة ────────────────────────────────
echo "📋 9. الإحالة:"
test_feature "توليد كود" "/api/referral/generate" '{}' "code"
test_feature "إحصائيات" "/api/referral/stats" '{}' "earnedTokens"
echo ""

# ── 10. نقاط النهاية العامة ──────────────────
echo "📋 10. البيانات العامة:"
printf "   %-35s ... " "الملف الشخصي"
PROFILE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/profile")
if echo "$PROFILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "✅ نجح"
    PASS=$((PASS + 1))
else
    echo "❌ فشل"
    FAIL=$((FAIL + 1))
fi

printf "   %-35s ... " "الإحصائيات"
STATS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/stats")
if echo "$STATS" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "✅ نجح"
    PASS=$((PASS + 1))
else
    echo "❌ فشل"
    FAIL=$((FAIL + 1))
fi

echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 النتيجة النهائية: $PASS ✅ نجح | $FAIL ❌ فشل"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAIL -eq 0 ]; then
    echo "🎉 كل الاختبارات نجحت! النظام جاهز للإطلاق."
else
    echo "⚠️  $FAIL اختبار فشل. راجع النتائج أعلاه."
fi
