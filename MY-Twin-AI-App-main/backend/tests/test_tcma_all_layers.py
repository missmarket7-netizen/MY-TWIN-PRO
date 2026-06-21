"""
اختبارات TCMA – جميع الطبقات
===============================
Emotional, Reflection, Identity, Memory Graph, PersonNode, Archive, Retrieval
"""
import pytest
import asyncio
import uuid

class TestEmotionalMemory:
    """الطبقة 4: الذاكرة العاطفية"""

    def test_arabic_context_analysis(self):
        """تحليل السياق العربي – الحزن المقنع"""
        from app.memory.emotional.emotional_memory import analyze_arabic_context
        result = analyze_arabic_context(
            "الحمد لله على كل حال",
            ["أنا تعبان من الشغل", "الضغوط كتير"]
        )
        assert result["real_emotion"] in ["sadness", "fear"]
        assert result["confidence"] > 0.5

    def test_direct_emotion_detection(self):
        """كشف العاطفة المباشرة"""
        from app.memory.emotional.emotional_memory import detect_direct_emotion_arabic
        assert detect_direct_emotion_arabic("أنا حزين اليوم") == "sadness"
        assert detect_direct_emotion_arabic("أنا مبسوط جداً") == "joy"
        assert detect_direct_emotion_arabic("أنا قلقان من بكرة") == "fear"

    def test_trigger_extraction(self):
        """استخراج المحفز العاطفي"""
        from app.memory.emotional.emotional_memory import extract_trigger
        assert extract_trigger("أنا قلقان على فلوسي") == "money"
        assert extract_trigger("الشغل متعب جداً") == "work"

    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, test_user_id, test_message_ar, sample_emotion):
        """تخزين واسترجاع ذاكرة عاطفية"""
        from app.memory.emotional.emotional_memory import store_emotional_memory, get_emotional_patterns
        result = await store_emotional_memory(
            user_id=test_user_id,
            expressed_text=test_message_ar,
            detected_emotion=sample_emotion,
            trigger="test"
        )
        assert result.get("id") is not None

        patterns = await get_emotional_patterns(test_user_id, days=1)
        assert "dominant_emotion" in patterns

class TestReflectionEngine:
    """الطبقة 8: الاستنتاجات"""

    @pytest.mark.asyncio
    async def test_store_reflection(self, test_user_id):
        """تخزين استنتاج"""
        from app.memory.reflection.reflection_engine import store_reflection
        ref_id = await store_reflection(
            user_id=test_user_id,
            insight_type="test",
            insight_text="هذا اختبار استنتاج",
            confidence=0.8
        )
        assert ref_id is not None

    @pytest.mark.asyncio
    async def test_process_message_for_reflections(self, test_user_id):
        """معالجة رسالة واستخراج استنتاجات"""
        from app.memory.reflection.reflection_engine import process_message_for_reflections
        result = await process_message_for_reflections(
            user_id=test_user_id,
            message="نفسي أتعلم برمجة لكن خايف أفشل",
            language="ar",
            detected_emotion="fear"
        )
        assert isinstance(result, list)

class TestIdentityModel:
    """الطبقة 9: نموذج الهوية"""

    @pytest.mark.asyncio
    async def test_build_and_retrieve_identity(self, test_user_id):
        """بناء واسترجاع الهوية"""
        from app.memory.identity.identity_model import build_identity_model, get_identity
        await build_identity_model(
            user_id=test_user_id,
            self_view="طموح ومجتهد",
            traits=["طموح", "صبور"],
            family_role="الابن الأكبر",
            core_values=["العائلة", "التعليم"]
        )
        identity = await get_identity(test_user_id)
        assert identity is not None
        assert identity.get("self_view") == "طموح ومجتهد"

class TestMemoryGraph:
    """الطبقة 11: الرسم البياني للذاكرة"""

    @pytest.mark.asyncio
    async def test_create_edge(self, test_user_id):
        """إنشاء حافة بين ذكرَيين"""
        from app.memory.graph.memory_graph import create_edge
        edge_id = await create_edge(
            user_id=test_user_id,
            source_id="mem_001",
            source_type="emotional_memory",
            target_id="person_001",
            target_type="person_node",
            relation_type="involves_person",
            weight=1.0
        )
        assert edge_id is not None

    @pytest.mark.asyncio
    async def test_get_connected(self, test_user_id):
        """استرجاع الذكريات المترابطة"""
        from app.memory.graph.memory_graph import get_connected_memories
        edges = await get_connected_memories(test_user_id, "mem_001", depth=1)
        assert isinstance(edges, list)

class TestMemoryRetriever:
    """محرك الاسترجاع"""

    @pytest.mark.asyncio
    async def test_retrieve_context(self, test_user_id):
        """استرجاع السياق من كل الطبقات"""
        from app.memory.retrieval.memory_retriever import retrieve_full_context
        context = await retrieve_full_context(test_user_id, "اختبار")
        assert isinstance(context, dict)
        assert "context_text" in context
