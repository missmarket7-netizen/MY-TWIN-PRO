"""
اختبارات مسارات API – التحقق من نقاط النهاية
=================================================
"""
import pytest
from httpx import AsyncClient, ASGITransport

# استيراد التطبيق
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

class TestStatusEndpoints:
    """نقاط الحالة"""

    @pytest.mark.asyncio
    async def test_root(self, client):
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "version" in resp.json()

    @pytest.mark.asyncio
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["api"] == "healthy"

    @pytest.mark.asyncio
    async def test_ready(self, client):
        resp = await client.get("/ready")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_live(self, client):
        resp = await client.get("/live")
        assert resp.status_code == 200

class TestMemoryEndpoints:
    """نقاط الذاكرة"""

    @pytest.mark.asyncio
    async def test_get_memories(self, client):
        resp = await client.get("/api/memories/")
        assert resp.status_code in [200, 401]  # 401 if no auth

    @pytest.mark.asyncio
    async def test_get_emotional(self, client):
        resp = await client.get("/api/memories/emotional")
        assert resp.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_get_reflections(self, client):
        resp = await client.get("/api/memories/reflections")
        assert resp.status_code in [200, 401]

class TestFeatureEndpoints:
    """نقاط الميزات"""

    @pytest.mark.asyncio
    async def test_features_study(self, client):
        resp = await client.post("/api/features/study", json={
            "topic": "test", "level": "beginner", "type": "explain", "lang": "ar"
        })
        assert resp.status_code in [200, 401, 503]

    @pytest.mark.asyncio
    async def test_features_code(self, client):
        resp = await client.post("/api/features/code", json={
            "task": "test", "language": "python", "action": "write", "lang": "ar"
        })
        assert resp.status_code in [200, 401, 503]

    @pytest.mark.asyncio
    async def test_features_business(self, client):
        resp = await client.post("/api/features/business", json={
            "text": "test", "analysis_type": "general", "lang": "ar"
        })
        assert resp.status_code in [200, 401, 503]

class TestStudyEndpoints:
    """نقاط الدراسة"""

    @pytest.mark.asyncio
    async def test_study_start(self, client):
        resp = await client.post("/api/study/start", json={
            "user_id": "test", "concept": "test", "age_group": "teen", "language": "ar"
        })
        assert resp.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_study_questions(self, client):
        resp = await client.post("/api/study/questions", json={
            "concept": "test", "bloom_level": 1, "age_group": "teen", "language": "ar", "count": 1
        })
        assert resp.status_code in [200, 503]

class TestBusinessEndpoints:
    """نقاط الأعمال"""

    @pytest.mark.asyncio
    async def test_business_ideas(self, client):
        resp = await client.post("/api/business/generate-ideas", json={
            "user_id": "test", "budget": 5000, "interests": "برمجة", "location": "مصر", "language": "ar"
        })
        assert resp.status_code in [200, 503]

class TestLifeCoachEndpoints:
    """نقاط مدرب الحياة"""

    @pytest.mark.asyncio
    async def test_life_coach_session(self, client):
        resp = await client.post("/api/life-coach/session", json={
            "user_id": "test", "topic": "أشعر بالقلق", "lang": "ar"
        })
        assert resp.status_code in [200, 503]

class TestDreamEndpoints:
    """نقاط الأحلام"""

    @pytest.mark.asyncio
    async def test_dream_interpret(self, client):
        resp = await client.post("/api/dreams/interpret", json={
            "user_id": "test", "dream_text": "حلمت بماء", "lang": "ar"
        })
        assert resp.status_code in [200, 503]

class TestSmartHomeEndpoints:
    """نقاط المنزل الذكي"""

    @pytest.mark.asyncio
    async def test_smart_home_command(self, client):
        resp = await client.post("/api/smart-home/command", json={
            "user_id": "test", "command": "شغل النور", "lang": "ar"
        })
        assert resp.status_code in [200, 503]

class TestPASSEndpoints:
    """نقاط المساعد الشخصي"""

    @pytest.mark.asyncio
    async def test_pass_create_task(self, client):
        resp = await client.post("/api/pass/task", json={
            "user_id": "test", "title": "اختبار"
        })
        assert resp.status_code in [200, 503]

class TestAdminEndpoints:
    """نقاط الإدارة"""

    @pytest.mark.asyncio
    async def test_admin_stats(self, client):
        resp = await client.get("/api/admin/stats", headers={"x-admin-key": "admin-secret-key"})
        assert resp.status_code in [200, 403]
