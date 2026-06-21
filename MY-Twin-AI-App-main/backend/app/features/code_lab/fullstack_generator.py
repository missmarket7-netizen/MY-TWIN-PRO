"""
FullStack Generator – مهندس تطبيقات الويب الكاملة
=====================================================
يحول فكرة إلى: Frontend، Backend، Database، Deployment.
يستخدم أفضل الممارسات: React + FastAPI، تصميم جذاب، كود نظيف.
"""
import logging
from typing import Dict, Any, Optional, List

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

logger = logging.getLogger("fullstack_generator")

class FullStackArchitect:
    """يخطط ويبني مشروع Full-Stack بالكامل"""
    
    async def generate_entire_project(
        self,
        idea: str,
        frontend: str = "react",
        backend: str = "fastapi",
        database: str = "postgresql",
        styling: str = "tailwind",
        language: str = "ar"
    ) -> Dict[str, Any]:
        """
        يولد مشروعاً كاملاً: Frontend + Backend + Database + Deployment
        """
        if not AI_AVAILABLE:
            return {"error": "الذكاء الاصطناعي غير متاح"}

        # 1. توليد هيكل المشروع الكامل
        structure_prompt = f"""
أنشئ هيكل ملفات كامل لمشروع '{idea}' باستخدام:
- Frontend: {frontend} ({styling})
- Backend: {backend}
- Database: {database}
قدم قائمة بكل الملفات مع وصف مختصر لكل ملف.
اللغة: {language}.
"""
        structure = await provider_router.generate(structure_prompt, language=language)

        # 2. توليد كود الواجهة الأمامية
        frontend_prompt = f"""
اكتب كود {frontend} كاملاً لمشروع '{idea}' باستخدام {styling}.
شمل: App.jsx، المكونات (Components)، الصفحات (Pages)، وملفات الخدمات (Services).
اكتب كوداً نظيفاً، جميلاً، وجاهزاً للإنتاج.
"""
        frontend_code = await provider_router.generate(frontend_prompt, language=language)

        # 3. توليد كود الواجهة الخلفية
        backend_prompt = f"""
اكتب كود {backend} كاملاً لمشروع '{idea}'.
شمل: main.py، models.py، routes.py، schemas.py، database.py.
اكتب كوداً آمناً، منظماً، مع تعليقات.
"""
        backend_code = await provider_router.generate(backend_prompt, language=language)

        # 4. توليد مخطط قاعدة البيانات
        db_prompt = f"""
اكتب مخطط قاعدة بيانات SQL كاملاً لمشروع '{idea}' باستخدام {database}.
شمل: CREATE TABLE، العلاقات، الفهارس.
"""
        database_schema = await provider_router.generate(db_prompt, language=language)

        # 5. توليد ملفات النشر
        deploy_prompt = f"""
اكتب ملفات النشر لمشروع '{idea}':
- Dockerfile للـ frontend والـ backend
- docker-compose.yml
- تعليمات النشر على Vercel (frontend) و Railway (backend)
"""
        deployment = await provider_router.generate(deploy_prompt, language=language)

        return {
            "idea": idea,
            "stack": f"{frontend} + {backend} + {database}",
            "structure": structure,
            "frontend_code": frontend_code,
            "backend_code": backend_code,
            "database_schema": database_schema,
            "deployment_guide": deployment,
            "ready_to_use": True
        }

class UIGenerator:
    """مصمم واجهات المستخدم"""
    
    async def generate_landing_page(
        self,
        business_name: str,
        description: str,
        colors: str = "modern",
        language: str = "ar"
    ) -> Dict[str, Any]:
        """يولد صفحة هبوط كاملة بـ HTML + Tailwind"""
        prompt = f"""
أنشئ صفحة هبوط (Landing Page) كاملة وجذابة لـ '{business_name}' ({description}).
استخدم Tailwind CSS. اجعلها عصرية، سريعة، ومتوافقة مع الجوال.
شمل: Header، Hero Section، Features، Pricing، Footer.
الألوان: {colors}. اللغة: {language}.
أعد كود HTML + CSS فقط.
"""
        html_code = await provider_router.generate(prompt, language=language) if AI_AVAILABLE else ""
        return {"business": business_name, "html_code": html_code}

    async def generate_react_component(
        self,
        component_name: str,
        description: str,
        styling: str = "tailwind"
    ) -> Dict[str, Any]:
        """يولد مكون React جاهز"""
        prompt = f"""
اكتب مكون React '{component_name}' ({description}).
استخدم {styling}. اكتب كوداً نظيفاً مع PropTypes.
أعد كود JSX فقط.
"""
        code = await provider_router.generate(prompt) if AI_AVAILABLE else ""
        return {"component": component_name, "code": code}

class DeploymentAutomation:
    """أتمتة النشر على السحابة"""
    
    async def deploy_to_vercel(self, project_path: str) -> Dict[str, Any]:
        """تعليمات النشر على Vercel"""
        return {
            "steps": [
                "npm install -g vercel",
                f"cd {project_path} && vercel",
                "اختر الإعدادات الافتراضية"
            ],
            "note": "تأكد من وجود vercel.json في المشروع"
        }
    
    async def deploy_to_railway(self, project_path: str) -> Dict[str, Any]:
        """تعليمات النشر على Railway"""
        return {
            "steps": [
                "railway login",
                f"railway link",
                "railway up"
            ],
            "note": "تأكد من وجود railway.json أو Dockerfile"
        }
