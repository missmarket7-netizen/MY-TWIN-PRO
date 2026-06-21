"""
اختبارات المحركات المتقدمة – Proactive, Temporal, Meta, CrossFeature, Recommendation
======================================================================================
"""
import pytest

class TestTemporalContext:
    """السياق الزماني"""

    def test_temporal_greeting(self):
        from app.features.temporal_context import temporal_engine
        ctx = temporal_engine.get_current_context("test_user")
        assert "greeting" in ctx
        assert "time_of_day" in ctx
        assert "season" in ctx

class TestProactiveEngine:
    """المحرك الاستباقي"""

    @pytest.mark.asyncio
    async def test_proactive_message(self, test_user_id):
        from app.features.proactive_engine import proactive_engine
        result = await proactive_engine.generate_proactive_message(test_user_id, "ar")
        assert "message" in result
        assert result["send_notification"] is True

class TestMetaReflection:
    """المراجعة الذاتية"""

    @pytest.mark.asyncio
    async def test_relationship_health(self, test_user_id):
        from app.features.meta_reflection import meta_engine
        result = await meta_engine.analyze_relationship_health(test_user_id)
        assert "style" in result or "status" in result

class TestUnifiedRecommendations:
    """التوصيات الموحدة"""

    @pytest.mark.asyncio
    async def test_daily_recommendations(self, test_user_id):
        from app.core.unified_recommendation_engine import engine
        result = await engine.get_daily_recommendation(test_user_id)
        assert "recommendations" in result

class TestCrossFeatureAnalyzer:
    """محلل العلاقات بين الميزات"""

    @pytest.mark.asyncio
    async def test_cross_feature(self, test_user_id):
        from app.core.cross_feature_analyzer import analyzer
        result = await analyzer.analyze(test_user_id)
        assert "cross_insights" in result

class TestShadowMode:
    """وضع الظل"""

    @pytest.mark.asyncio
    async def test_shadow_analysis(self, test_user_id):
        from app.features.shadow_mode import shadow_engine
        result = await shadow_engine.run_daily_analysis(test_user_id)
        assert "insights_added" in result
