"""
Study API Routes - مسارات واجهة برمجة التطبيقات للدراسة
=========================================================
تربط ATHENA بالواجهة الأمامية.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any

try:
    from app.features.study.athena_orchestrator import athena
    from app.features.study.scaffold_explainer import scaffold
    from app.features.study.bloom_question_generator import bloom_gen
    from app.features.study.spaced_repetition_sm2 import scheduler
    from app.features.study.study_knowledge_graph import knowledge_graph
    STUDY_READY = True
except ImportError as e:
    print(f"Study imports failed: {e}")
    STUDY_READY = False

router = APIRouter(prefix="/api/study", tags=["study"])

# ============================================================
# نماذج الطلب والاستجابة
# ============================================================
class StudyRequest(BaseModel):
    user_id: str
    concept: str
    age_group: str = "teen"
    language: str = "ar"

class AnswerRequest(BaseModel):
    user_id: str
    answer: str

class QuestionRequest(BaseModel):
    concept: str
    bloom_level: int = 1
    age_group: str = "teen"
    language: str = "ar"
    count: int = 1

class ReviewRequest(BaseModel):
    concept: str
    quality: int  # 0-5
    current_ease: Optional[float] = None
    current_interval: int = 0
    repetition_count: int = 0
    emotional_state: str = "neutral"

# ============================================================
# مسارات API
# ============================================================

@router.post("/start")
async def start_study_session(request: StudyRequest) -> Dict[str, Any]:
    """بدء جلسة دراسة جديدة"""
    if not STUDY_READY:
        raise HTTPException(status_code=503, detail="خدمة الدراسة غير متوفرة")
    
    return await athena.start_study_session(
        user_id=request.user_id,
        concept=request.concept,
        age_group=request.age_group,
        language=request.language,
    )

@router.post("/answer")
async def process_study_answer(request: AnswerRequest) -> Dict[str, Any]:
    """معالجة إجابة الطالب"""
    if not STUDY_READY:
        raise HTTPException(status_code=503, detail="خدمة الدراسة غير متوفرة")
    
    return await athena.process_answer(
        user_id=request.user_id,
        answer=request.answer,
    )

@router.post("/end")
async def end_study_session(user_id: str = Query(...)) -> Dict[str, Any]:
    """إنهاء جلسة الدراسة"""
    if not STUDY_READY:
        raise HTTPException(status_code=503, detail="خدمة الدراسة غير متوفرة")
    
    return await athena.end_session(user_id=user_id)

@router.post("/explain")
async def generate_explanation(request: StudyRequest) -> Dict[str, Any]:
    """توليد شرح باستخدام S.C.A.F.F.O.L.D"""
    if not STUDY_READY:
        raise HTTPException(status_code=503, detail="خدمة الدراسة غير متوفرة")
    
    # بناء ملف طالب بسيط للشرح
    student_profile = {
        "important_people": [],
        "identity_traits": [],
    }
    
    return await scaffold.explain(
        concept=request.concept,
        student_profile=student_profile,
        age_group=request.age_group,
        language=request.language,
    )

@router.post("/questions")
async def generate_questions(request: QuestionRequest) -> Dict[str, Any]:
    """توليد أسئلة تعليمية"""
    if not STUDY_READY:
        raise HTTPException(status_code=503, detail="خدمة الدراسة غير متوفرة")
    
    if request.count == 1:
        questions = [bloom_gen.generate_question(
            concept=request.concept,
            bloom_level=request.bloom_level,
            age_group=request.age_group,
            language=request.language,
        )]
    else:
        levels = list(range(request.bloom_level, min(request.bloom_level + request.count, 7)))
        questions = bloom_gen.generate_question_set(
            concept=request.concept,
            levels=levels,
            language=request.language,
            age_group=request.age_group,
            count=request.count,
        )
    
    return {
        "concept": request.concept,
        "questions": questions,
        "count": len(questions),
    }

@router.post("/schedule-review")
async def schedule_review(request: ReviewRequest) -> Dict[str, Any]:
    """جدولة مراجعة لمفهوم"""
    if not STUDY_READY:
        raise HTTPException(status_code=503, detail="خدمة الدراسة غير متوفرة")
    
    return scheduler.calculate_next_review(
        concept=request.concept,
        quality=request.quality,
        current_ease=request.current_ease,
        current_interval=request.current_interval,
        repetition_count=request.repetition_count,
        emotional_state=request.emotional_state,
    )

@router.get("/knowledge-path")
async def get_knowledge_path(concept_id: str = Query(...)) -> Dict[str, Any]:
    """الحصول على مسار التعلم لمفهوم"""
    if not STUDY_READY:
        raise HTTPException(status_code=503, detail="خدمة الدراسة غير متوفرة")
    
    path = knowledge_graph.get_learning_path(concept_id)
    return {
        "concept_id": concept_id,
        "learning_path": path,
        "steps": len(path),
    }

