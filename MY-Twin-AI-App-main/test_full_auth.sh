#!/bin/bash

BASE="http://localhost:8000"
PASS=0
FAIL=0
TOKEN=""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 اختبار شامل بمصادقة كاملة"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. إنشاء حساب جديد
echo "📋 1. إنشاء حساب اختباري..."
SIGNUP=$(curl -s -X POST "$BASE/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"sir.market7@gmail.com","password":"M#m2606.1307"}')

echo "   رد: $SIGNUP"

# استخراج التوكن من الرد
TOKEN=$(echo "$SIGNUP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    # ربما الحساب موجود مسبقاً، جرب تسجيل الدخول
    echo "   ⚠️  الحساب موجود. تجربة تسجيل الدخول..."
    LOGIN=$(curl -s -X POST "$BASE/api/auth/login" \
      -H "Content-Type: application/json" \
      -d '{"email":"sir.market7@gmail.com","password":"M#m2606.1307"}')
    echo "   رد: $LOGIN"
    TOKEN=$(echo "$LOGIN" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('token',''))" 2>/dev/null)
fi

if [ -z "$TOKEN" ]; then
    echo "   ❌ فشل الحصول على توكن"
    exit 1
fi

echo "   ✅ توكن: ${TOKEN:0:30}..."
echo ""

# 2. اختبار المسارات المحمية بالتوكن
test_protected() {
    METHOD=$1
    URL="$BASE$2"
    DESC=$3
    DATA=$4
    
    echo -n "   $DESC ... "
    
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
        cat /tmp/resp.txt | python3 -c "import sys,json; d=json.load(sys.stdin); print('      ',str(d)[:100])" 2>/dev/null
        PASS=$((PASS + 1))
    else
        echo "❌ $RESPONSE"
        FAIL=$((FAIL + 1))
    fi
}

echo "📋 2. اختبار المسارات المحمية:"
test_protected "GET" "/api/profile" "الملف الشخصي"
test_protected "GET" "/api/moods" "المشاعر"
test_protected "GET" "/api/memories" "الذكريات"
test_protected "GET" "/api/goals" "الأهداف"
test_protected "POST" "/api/goals" "إضافة هدف" '{"title":"اختبار"}'
test_protected "GET" "/api/tasks" "المهام"
test_protected "POST" "/api/tasks" "إضافة مهمة" '{"title":"اختبار"}'
test_protected "GET" "/api/stats" "الإحصائيات"
echo ""

echo "📋 3. اختبار الميزات المتقدمة:"
test_protected "POST" "/api/features/study" "مذاكرة" '{"topic":"الفضاء","level":"intermediate","type":"explain","lang":"ar"}'
test_protected "POST" "/api/features/code" "برمجة" '{"task":"print hello","language":"python","action":"write","lang":"ar"}'
test_protected "POST" "/api/features/business" "تحليل أعمال" '{"text":"مبيعات 1M","analysis_type":"general","lang":"ar"}'
test_protected "POST" "/api/features/coach" "مدرب حياة" '{"topic":"ثقة","domain":"personal","lang":"ar"}'
echo ""

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 النتيجة: $PASS ✅ نجح | $FAIL ❌ فشل"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
