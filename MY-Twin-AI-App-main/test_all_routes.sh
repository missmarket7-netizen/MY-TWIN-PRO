#!/bin/bash

BASE="http://localhost:8000"
PASS=0
FAIL=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 اختبار شامل لجميع نقاط النهاية"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_route() {
    METHOD=$1
    URL="$BASE$2"
    DESC=$3
    DATA=$4
    
    echo -n "  $DESC ... "
    
    if [ -n "$DATA" ]; then
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X "$METHOD" "$URL" -H "Content-Type: application/json" -d "$DATA" 2>/dev/null)
    else
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X "$METHOD" "$URL" 2>/dev/null)
    fi
    
    if [ "$RESPONSE" -ge 200 ] && [ "$RESPONSE" -lt 500 ]; then
        echo "✅ $RESPONSE"
        PASS=$((PASS + 1))
    else
        echo "❌ $RESPONSE"
        FAIL=$((FAIL + 1))
    fi
}

echo "📋 اختبار الصحة العامة:"
test_route "GET" "/" "الجذر"
test_route "GET" "/health" "الصحة"
test_route "GET" "/docs" "Swagger UI"
echo ""

echo "📋 اختبار المصادقة:"
test_route "POST" "/api/auth/signup" "إنشاء حساب" '{"email":"test@test.com","password":"123456"}'
test_route "POST" "/api/auth/login" "تسجيل الدخول" '{"email":"test@test.com","password":"123456"}'
echo ""

echo "📋 اختبار الميزات:"
test_route "POST" "/api/chat" "محادثة" '{"message":"مرحباً","lang":"ar"}'
test_route "POST" "/api/features/study" "مذاكرة" '{"topic":"رياضيات","level":"intermediate","type":"explain","lang":"ar"}'
test_route "POST" "/api/features/code" "برمجة" '{"task":"hello world","language":"python","action":"write","lang":"ar"}'
test_route "POST" "/api/features/business" "تحليل أعمال" '{"text":"مبيعات 1M","analysis_type":"general","lang":"ar"}'
test_route "POST" "/api/features/coach" "مدرب حياة" '{"topic":"ثقة","domain":"personal","lang":"ar"}'
test_route "POST" "/api/features/image" "توليد صورة" '{"prompt":"غروب"}'
test_route "POST" "/api/features/dream" "تفسير حلم" '{"dream":"أطير","lang":"ar"}'
test_route "POST" "/api/features/content" "كتابة محتوى" '{"topic":"تسويق","platform":"instagram","tone":"professional","lang":"ar"}'
test_route "POST" "/api/features/smart-home" "منزل ذكي" '{"command":"شغل النور"}'
echo ""

echo "📋 اختبار نقاط النهاية العامة:"
test_route "GET" "/api/profile" "الملف الشخصي"
test_route "GET" "/api/memories" "الذكريات"
test_route "GET" "/api/moods" "المشاعر"
test_route "GET" "/api/goals" "الأهداف"
test_route "GET" "/api/feedback" "التقييمات"
test_route "GET" "/api/stats" "الإحصائيات"
test_route "GET" "/api/ads/status" "حالة الإعلانات"
echo ""

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 النتيجة: $PASS ✅ نجح | $FAIL ❌ فشل"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
