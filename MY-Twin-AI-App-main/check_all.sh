#!/bin/bash
echo "🔍 بدء الفحص الشامل لمشروع MyTwin AI"
echo "========================================"

# 1. Backend syntax check
echo ""
echo "📦 1. فحص صحة ملفات Python في backend/"
cd backend
for f in main.py twin_brain.py reasoning_engine.py memory_retriever.py memory_graph.py memory_summarizer.py context_manager.py consciousness_core.py emotional_engine.py relationship_engine.py attachment_engine.py model_router.py self_critic.py reranker.py profile_extractor.py user_model.py multi_ai.py prompt_builder.py response_validator.py external_services.py tool_router.py tool_executor.py agent_loop.py agent_budget.py agent_metrics.py final_synthesizer.py scratchpad.py dream_engine.py voice_personality.py voice_engine.py; do
    if [ -f "$f" ]; then
        python3 -m py_compile "$f" 2>/dev/null && echo "    ✅ $f" || echo "    ❌ $f"
    fi
done
cd ..

# 2. Frontend file existence
echo ""
echo "📱 2. فحص وجود ملفات الواجهة الأساسية"
for f in app/_layout.tsx app/chat/index.tsx app/chat/ChatBubbles.tsx app/chat/ChatInput.tsx app/profile.tsx app/relationship.tsx app/memories.tsx app/settings.tsx app/subscription.tsx app/login.tsx app/onboarding.tsx app/customize.tsx app/referral.tsx app/history.tsx app/privacy.tsx app/terms.tsx app/feedback.tsx app/splash.tsx; do
    [ -f "$f" ] && echo "    ✅ $f" || echo "    ❌ $f مفقود"
done

for f in store/useTwinStore.ts lib/api.ts lib/iapService.ts lib/notifications.ts lib/supabase.ts lib/analytics.ts components/SideMenu.tsx components/ErrorBoundary.tsx utils/voice_engine.ts utils/voice_profiles.ts utils/theme.ts; do
    [ -f "$f" ] && echo "    ✅ $f" || echo "    ❌ $f مفقود"
done

# 3. Backend import test
echo ""
echo "🌐 3. اختبار استيراد المحركات"
cd backend
python3 -c "
import sys
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
        print(f'    ❌ {m}: {e}')
print(f'    ✅ تم استيراد {ok}/{len(modules)} محرك بنجاح')
" 2>/dev/null
cd ..

# 4. Unit tests
echo ""
echo "🧪 4. اختبارات الوحدة"
if [ -f backend/tests/test_tools.py ]; then
    cd backend
    python3 -m pytest tests/test_tools.py -v 2>&1 | tail -15
    cd ..
else
    echo "  ⚠️ ملف الاختبارات غير موجود"
fi

echo ""
echo "✅ الفحص الشامل انتهى"
