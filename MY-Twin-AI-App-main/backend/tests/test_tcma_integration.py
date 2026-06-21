"""
اختبار تكامل TCMA الشامل
===========================
يتحقق من أن جميع طبقات الذاكرة تعمل معًا بسلاسة.
"""
import pytest
import asyncio
import uuid

class TestTCMAIntegration:
    """التحقق من عمل الذاكرة معًا."""

    @pytest.mark.asyncio
    async def test_full_memory_pipeline(self):
        """اختبار تدفق الذاكرة: مشاعر -> استنتاج -> هوية -> رسم بياني"""
        user_id = f"test_user_{uuid.uuid4().hex[:8]}"

        # 1. اختبار الذاكرة العاطفية (السياق العربي)
        from app.memory.emotional.emotional_memory import analyze_arabic_context, store_emotional_memory
        analysis = analyze_arabic_context("الحمد لله على كل حال", ["أنا تعبان من الشغل", "الضغوط كتير"])
        assert analysis["real_emotion"] in ["sadness", "fear"]

        emo_result = await store_emotional_memory(
            user_id=user_id, expressed_text="الحمد لله على كل حال",
            detected_emotion={"primary": "sadness", "intensity": 0.8, "valence": -0.5},
            trigger="test"
        )
        assert emo_result.get("id") is not None

        # 2. اختبار الاستنتاجات
        from app.memory.reflection.reflection_engine import process_message_for_reflections, get_user_insights
        await process_message_for_reflections(
            user_id=user_id, message="أنا تعبان من الشغل ومش عارف أنام", language="ar", detected_emotion="sadness"
        )
        insights = await get_user_insights(user_id, min_confidence=0.3)
        assert len(insights.get("insights", [])) > 0

        # 3. اختبار الهوية
        from app.memory.identity.identity_model import analyze_and_update_identity, get_identity
        await analyze_and_update_identity(
            user_id=user_id, message="أنا شخص طموح لكن خايف من الفشل", language="ar"
        )
        identity = await get_identity(user_id)
        assert identity.get("self_view") is not None

        # 4. اختبار الرسم البياني للذاكرة
        from app.memory.graph.memory_graph import auto_create_edges_from_memory, get_connected_memories
        if emo_result.get("id"):
            await auto_create_edges_from_memory(
                user_id=user_id, memory_id=emo_result["id"],
                memory_type="emotional_memory", memory_data=emo_result
            )
            edges = await get_connected_memories(user_id, emo_result["id"], depth=1)
            assert isinstance(edges, list)

        print("✅ جميع طبقات TCMA تعمل معًا بنجاح")

@pytest.mark.asyncio
async def test_multi_feature_context():
    """اختبار Cross-Feature Analyzer"""
    user_id = f"test_cross_{uuid.uuid4().hex[:8]}"
    
    from app.core.cross_feature_analyzer import analyzer
    result = await analyzer.analyze(user_id)
    assert "cross_insights" in result
    print(f"✅ Cross-Feature: {result['cross_insights']}")
