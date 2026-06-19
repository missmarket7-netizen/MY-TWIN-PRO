#!/bin/bash

BASE="https://my-twin-pro-production-b744.up.railway.app"
TOKEN=""
PASS=0
FAIL=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 اختبار شامل – MyTwin API (RAILWAY)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 1. الحصول على توكن ──────────────────────
echo "📋 1. المصادقة..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"sir.market7@gmail.com","password":"M#m2606.1307"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "   ⚠️  فشل تسجيل الدخول. جاري إنشاء حساب جديد..."
    SIGNUP_RESPONSE=$(curl -s -X POST "$BASE/api/auth/signup" \
      -H "Content-Type: application/json" \
      -d '{"email":"sir.market7@gmail.com","password":"M#m2606.1307"}')
    TOKEN=$(echo "$SIGNUP_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('token',''))" 2>/dev/null)
    if [ -z "$TOKEN" ]; then
        echo "   ❌ فشل المصادقة تماماً"
        echo "   رد الدخول: $LOGIN_RESPONSE"
        echo "   رد التسجيل: $SIGNUP_RESPONSE"
        exit 1
    fi
    echo "   ✅ تم إنشاء الحساب"
else
    echo "   ✅ تم تسجيل الدخول"
fi

echo "   ✅ توكن صالح (${#TOKEN} حرف)"
echo ""

# ── دالة الاختبار ────────────────────────────
test_route() {
    METHOD=$1
    URL="$BASE$2"
    DESC=$3
    DATA=$4
    
    printf "   %-45s ... " "$DESC"
    
    if [ -n "$DATA" ]; then
        RESPONSE=$(curl -s -o /tmp/resp.txt -w "%{http_code}" -X "$METHOD" "$URL" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "$DATA" 2>/dev/null)
    else
        RESPONSE=$(curl -s -o /tmp/resp.txt -w "%{http_code}" -X "$METHOD" "$URL" \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
    fi
    
    if [ "$RESPONSE" -ge 200 ] && [ "$RESPONSE" -lt 500 ]; then
        echo "✅ $RESPONSE"
        cat /tmp/resp.txt | python3 -c "import sys,json; d=json.load(sys.stdin); print('      ',str(d)[:120])" 2>/dev/null
        PASS=$((PASS + 1))
    else
        echo "❌ $RESPONSE"
        echo "      $(cat /tmp/resp.txt 2>/dev/null)"
        FAIL=$((FAIL + 1))
    fi
}

# ── 2. الصحة ────────────────────────────────
echo "📋 2. الصحة العامة:"
test_route "GET" "/" "الجذر"
test_route "GET" "/health" "فحص الصحة"
echo ""

# ── 3. الميزات المتقدمة ──────────────────────
echo "📋 3. الميزات المتقدمة:"
test_route "POST" "/api/features/study" "مذاكرة" \
    '{"topic":"نظرية فيثاغورس","level":"intermediate","type":"explain","lang":"ar"}'
test_route "POST" "/api/features/code" "برمجة" \
    '{"task":"print hello world","language":"python","action":"write","lang":"ar"}'
test_route "POST" "/api/features/business" "تحليل أعمال" \
    '{"text":"مبيعات 1M","analysis_type":"general","lang":"ar"}'
test_route "POST" "/api/features/coach" "مدرب حياة" \
    '{"topic":"ثقة","domain":"personal","lang":"ar"}'
test_route "POST" "/api/features/content" "كتابة محتوى" \
    '{"topic":"التسويق","platform":"instagram","tone":"professional","lang":"ar"}'
test_route "POST" "/api/features/dream" "تفسير حلم" \
    '{"dream":"حلمت أني أطير","lang":"ar"}'
test_route "POST" "/api/features/smart-home" "منزل ذكي" \
    '{"command":"شغل النور"}'
echo ""

# ── 4. الإحالة ───────────────────────────────
echo "📋 4. الإحالة:"
test_route "POST" "/api/referral/generate" "توليد كود"
test_route "GET" "/api/referral/stats" "إحصائيات الإحالة"
echo ""

# ── 5. البيانات العامة ───────────────────────
echo "📋 5. البيانات العامة:"
test_route "GET" "/api/profile" "الملف الشخصي"
test_route "GET" "/api/moods" "المشاعر"
test_route "GET" "/api/memories" "الذكريات"
test_route "GET" "/api/goals" "الأهداف"
test_route "POST" "/api/goals" "إضافة هدف" '{"title":"هدف اختباري"}'
test_route "GET" "/api/tasks" "المهام"
test_route "POST" "/api/tasks" "إضافة مهمة" '{"title":"مهمة اختبارية","priority":3}'
test_route "GET" "/api/ads/status" "حالة الإعلانات"
echo ""

# ── 6. إحصائيات ──────────────────────────────
echo "📋 6. الإحصائيات:"
test_route "GET" "/api/stats" "إحصائيات المستخدم"
echo ""

# ── 7. المحادثة ──────────────────────────────
echo "📋 7. المحادثة:"
test_route "POST" "/api/chat" "إرسال رسالة" \
    '{"message":"مرحباً، كيف حالك؟","lang":"ar"}'
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 النتيجة النهائية: $PASS ✅ نجح | $FAIL ❌ فشل"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
