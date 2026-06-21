"""
اختبارات البنية التحتية – AI, Cache, Security, Events
=========================================================
"""
import pytest

class TestProviderRouter:
    """موجه المزودين"""

    def test_api_key_manager(self):
        from app.infrastructure.ai.provider_router import APIKeyManager
        manager = APIKeyManager()
        assert isinstance(manager._keys, dict)

    @pytest.mark.asyncio
    async def test_generate_with_fallback(self):
        from app.infrastructure.ai.provider_router_internal import generate_with_fallback
        response, provider = await generate_with_fallback("مرحباً", "ar", False, "general")
        assert isinstance(response, str)
        assert provider in ["external_api", "fallback"]

class TestCache:
    """خدمة التخزين المؤقت"""

    def test_cache_set_get(self):
        from app.infrastructure.cache.cache_service import set, get, delete
        set("test_key", "test_value", 60)
        assert get("test_key") == "test_value"
        delete("test_key")
        assert get("test_key") is None

    def test_cached_response(self):
        from app.infrastructure.cache.cache_service import set_cached_response, get_cached_response
        set_cached_response("مرحباً", "MyTwin", "ar", "أهلاً بك", 60)
        assert get_cached_response("مرحباً", "MyTwin", "ar") == "أهلاً بك"

class TestSecurity:
    """الأمان"""

    def test_safety_check(self):
        from app.domain.services.safety_service import check_safety
        result = check_safety("مرحباً")
        assert result["safe"] is True

    def test_safety_critical(self):
        from app.domain.services.safety_service import check_safety
        result = check_safety("أريد الانتحار")
        assert result["safe"] is False
        assert result["severity"] == "critical"

    def test_sanitize_input(self):
        from app.domain.services.safety_service import sanitize_input
        clean = sanitize_input("مرحباً <script>alert('xss')</script>")
        assert "<script>" not in clean

    def test_security_audit(self):
        from app.middleware.security_audit import security_audit
        result = security_audit.scan_payload("SELECT * FROM users")
        assert result is not None

class TestEventBus:
    """نظام الأحداث"""

    @pytest.mark.asyncio
    async def test_emit_event(self):
        from app.events.event_bus import emit
        await emit({"type": "test_event", "user_id": "test", "data": "test"})
        assert True

class TestDialectService:
    """خدمة اللهجات"""

    def test_detect_egyptian(self):
        from app.infrastructure.ai.dialect_service import get_dialect_for_user
        dialect, confidence = get_dialect_for_user("ازيك يا عم عامل ايه")
        assert dialect == "egyptian"

    def test_detect_english(self):
        from app.infrastructure.ai.dialect_service import get_dialect_for_user
        dialect, _ = get_dialect_for_user("Hello how are you doing today")
        assert dialect == "modern_arabic"  # because no arabic chars

class TestPromptBuilder:
    """بناء الموجه"""

    @pytest.mark.asyncio
    async def test_build_prompt(self, test_user_id):
        from app.prompts.prompt_builder import prompt_builder
        prompt = await prompt_builder.build(test_user_id, "مرحباً", "ar", "توأمي")
        assert isinstance(prompt, str)
        assert len(prompt) > 100

class TestVoiceProfile:
    """ملف الصوت"""

    def test_voice_personality(self):
        from utils.voice_profiles import get_voice_personality
        result = get_voice_personality("mentor", "male")
        assert "pitch" in result
        assert "rate" in result

    def test_voice_genders(self):
        from utils.voice_profiles import get_available_genders
        genders = get_available_genders()
        assert len(genders) >= 2
