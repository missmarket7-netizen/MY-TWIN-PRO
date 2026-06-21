"""
ATHENA Orchestrator - نظام التعلّم التكيّفي الشامل
===================================================
يدير جلسات الدراسة بالكامل، يربط بين طبقات الذاكرة والمشاعر والهوية
لتقديم تجربة تعليمية شخصية عميقة. متكامل مع TCMA.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field

try:
    from app.memory.retrieval.memory_retriever import retrieve_full_context
    from app.memory.relationship.person_node import process_message_for_persons, get_person_network
    from app.memory.emotional.emotional_memory import get_emotional_state_for_response, store_emotional_memory
    from app.memory.identity.identity_model import get_identity, analyze_and_update_identity
    from app.memory.reflection.reflection_engine import process_message_for_reflections, get_user_insights
    from app.memory.graph.memory_graph import auto_create_edges_from_memory, get_memory_cluster
    from app.memory.relationship.attachment_model import detect_attachment_style
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

try:
    from app.features.study.tool_registry import get_registered_tools
    from app.features.study.tool_router import route_study_tool
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False

try:
    from app.features.study.scaffold_explainer import scaffold
    from app.features.study.bloom_question_generator import bloom_gen
    from app.features.study.spaced_repetition_sm2 import scheduler
    from app.features.study.study_knowledge_graph import knowledge_graph
    ATHENA_SERVICES_READY = True
except ImportError:
    ATHENA_SERVICES_READY = False

logger = logging.getLogger("athena_orchestrator")

@dataclass
class StudentProfile:
    age_group: str = "unknown"
    language: str = "ar"
    identity_traits: List[str] = field(default_factory=list)
    important_people: List[Dict] = field(default_factory=list)
    current_emotion: str = "neutral"
    attachment_style: str = "secure"
    learning_style: str = "visual"
    mastered_concepts: List[str] = field(default_factory=list)
    struggling_concepts: List[str] = field(default_factory=list)

@dataclass
class SessionState:
    concept: str
    age_group: str
    current_depth: int = 0
    emotion_snapshot: Dict = field(default_factory=dict)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    questions_asked: int = 0
    correct_answers: int = 0
    scaffold_level: int = 0

class ATHENAOrchestrator:
    def __init__(self):
        self.active_sessions: Dict[str, SessionState] = {}
        self._init_default_concepts()
    
    def _init_default_concepts(self):
        if not ATHENA_SERVICES_READY: return
        knowledge_graph.add_concept("numbers", "الأعداد", "رياضيات", [], "easy", "child")
        knowledge_graph.add_concept("addition", "الجمع", "رياضيات", ["numbers"], "easy", "child")
        knowledge_graph.add_concept("subtraction", "الطرح", "رياضيات", ["numbers"], "easy", "child")
        knowledge_graph.add_concept("multiplication", "الضرب", "رياضيات", ["addition"], "medium", "child")
        knowledge_graph.add_concept("division", "القسمة", "رياضيات", ["multiplication"], "medium", "child")
        knowledge_graph.add_concept("fractions", "الكسور", "رياضيات", ["division"], "medium", "teen")
        knowledge_graph.add_concept("algebra", "الجبر", "رياضيات", ["fractions"], "hard", "teen")
        knowledge_graph.add_concept("geometry", "الهندسة", "رياضيات", ["algebra"], "hard", "teen")
        knowledge_graph.add_concept("calculus", "التفاضل والتكامل", "رياضيات", ["algebra", "geometry"], "hard", "young_adult")
    
    async def initialize_student_profile(self, user_id: str, lang: str = "ar") -> StudentProfile:
        profile = StudentProfile(language=lang)
        if not MEMORY_AVAILABLE: return profile
        try:
            identity = await get_identity(user_id)
            if identity:
                profile.identity_traits = identity.get("traits", [])
                profile.learning_style = self._infer_learning_style(identity)
            emotion_state = await get_emotional_state_for_response(user_id, "")
            if emotion_state: profile.current_emotion = emotion_state.get("current_emotion", "neutral")
            attachment = await detect_attachment_style(user_id)
            if attachment: profile.attachment_style = attachment.get("style", "secure")
            network = await get_person_network(user_id, min_importance=30)
            if network:
                profile.important_people = [{"name": p.get("name"), "relation": p.get("relationship_type")} for p in network[:5]]
        except Exception as e:
            logger.error(f"فشل بناء ملف الطالب: {e}")
        return profile
    
    def _infer_learning_style(self, identity: Dict) -> str:
        traits = identity.get("traits", [])
        if any(t in ["بصري", "visual", "فنان"] for t in traits): return "visual"
        elif any(t in ["سمعي", "auditory", "موسيقي"] for t in traits): return "auditory"
        elif any(t in ["حركي", "kinesthetic", "رياضي"] for t in traits): return "kinesthetic"
        return "visual"
    
    def _get_age_config(self, age_group: str) -> Dict:
        configs = {
            "child": {"fragment_count": 3, "session_length_minutes": 10},
            "teen": {"fragment_count": 4, "session_length_minutes": 25},
            "young_adult": {"fragment_count": 5, "session_length_minutes": 35},
            "adult": {"fragment_count": 5, "session_length_minutes": 45},
        }
        return configs.get(age_group, configs["teen"])
    
    def _calculate_duration(self, started_at: str) -> float:
        start = datetime.fromisoformat(started_at)
        elapsed = datetime.now(timezone.utc) - start
        return round(elapsed.total_seconds() / 60, 1)
    
    def _evaluate_answer_basic(self, answer: str) -> bool:
        return len(answer.split()) > 5

logger.info("✅ ATHENA Orchestrator Part 1 loaded")

    async def start_study_session(self, user_id: str, concept: str, age_group: str = "teen", language: str = "ar") -> Dict[str, Any]:
        student = await self.initialize_student_profile(user_id, language)
        student.age_group = age_group
        try:
            if MEMORY_AVAILABLE:
                mentioned = await process_message_for_persons(user_id, f"أنا أدرس {concept}", None)
                if mentioned: student.important_people = mentioned
        except: pass
        session = SessionState(concept=concept, age_group=age_group)
        self.active_sessions[user_id] = session
        explanation = await self._generate_explanation(user_id, concept, student, 1)
        learning_path = knowledge_graph.get_learning_path(concept) if ATHENA_SERVICES_READY else []
        return {
            "session_id": f"{user_id}_{concept}", "concept": concept,
            "explanation": explanation, "learning_path": learning_path,
            "student_emotion": student.current_emotion, "student_style": student.learning_style,
            "next_step": "ask_understanding",
        }

    async def _generate_explanation(self, user_id, concept, student, depth):
        if ATHENA_SERVICES_READY:
            student_dict = {"important_people": student.important_people, "identity_traits": student.identity_traits}
            return await scaffold.explain(concept=concept, student_profile=student_dict, age_group=student.age_group, language=student.language, current_emotion=student.current_emotion, depth=depth)
        return {"simplified": f"شرح {concept}", "layers_applied": 1}

    async def process_answer(self, user_id: str, answer: str) -> Dict[str, Any]:
        if user_id not in self.active_sessions: return {"error": "لا توجد جلسة نشطة"}
        session = self.active_sessions[user_id]
        session.questions_asked += 1
        is_correct = await self._evaluate_answer_ai(answer, session)
        if is_correct:
            session.correct_answers += 1
            session.current_depth = min(session.current_depth + 1, 6)
            next_action = "deepen"
        else:
            session.scaffold_level += 1
            next_action = "scaffold"
        next_question = None
        if ATHENA_SERVICES_READY and is_correct:
            q = await bloom_gen.generate_question(session.concept, min(session.current_depth + 1, 6), session.age_group)
            next_question = q.get("question")
        if MEMORY_AVAILABLE: await self._deep_memory_update(user_id, session, answer, is_correct)
        return {
            "is_correct": is_correct, "next_action": next_action,
            "current_depth": session.current_depth, "correct_count": session.correct_answers,
            "total_asked": session.questions_asked, "next_question": next_question,
            "accuracy": f"{(session.correct_answers / max(session.questions_asked, 1)) * 100:.0f}%",
        }

    async def _evaluate_answer_ai(self, answer: str, session: SessionState) -> bool:
        try:
            from app.infrastructure.ai.provider_router import provider_router
            prompt = f"""أنت مقيم تعليمي. السؤال كان عن: {session.concept}\nإجابة الطالب: "{answer}"\nهل الإجابة صحيحة بشكل عام؟ أجب بكلمة واحدة فقط: "نعم" أو "لا"."""
            response = await provider_router.generate(prompt, language="ar")
            if response: return "نعم" in response
        except: pass
        return self._evaluate_answer_basic(answer)

    async def _deep_memory_update(self, user_id, session, answer, is_correct):
        emotion = "joy" if is_correct else "frustration"
        emo_id = None
        try:
            emo_result = await store_emotional_memory(user_id=user_id, expressed_text=answer, detected_emotion={"primary": emotion, "intensity": 0.6, "valence": 0.5}, trigger="study", cultural_context=f"دراسة: {session.concept}")
            emo_id = emo_result.get("id") if emo_result else None
        except: pass
        try: await process_message_for_reflections(user_id=user_id, message=f"في جلسة دراسة {session.concept}، {'أجاب بشكل صحيح' if is_correct else 'واجه صعوبة'}", language="ar", detected_emotion=emotion)
        except: pass
        try: await analyze_and_update_identity(user_id=user_id, message=f"{'أتقن' if is_correct else 'يجد صعوبة في'} {session.concept}", language="ar")
        except: pass
        if emo_id and MEMORY_AVAILABLE:
            try: await auto_create_edges_from_memory(user_id=user_id, memory_id=emo_id, memory_type="emotional_memory", memory_data={"trigger": f"study_{session.concept}"})
            except: pass
        if ATHENA_SERVICES_READY:
            try:
                quality = 4 if is_correct else 2
                await knowledge_graph.update_user_knowledge(user_id=user_id, concept_id=session.concept, quality=quality, concept_name=session.concept, emotional_state=emotion)
            except: pass

    async def end_session(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self.active_sessions: return {"error": "لا توجد جلسة نشطة"}
        session = self.active_sessions.pop(user_id)
        accuracy = (session.correct_answers / max(session.questions_asked, 1)) * 100
        if MEMORY_AVAILABLE:
            try: await process_message_for_reflections(user_id=user_id, message=f"أنهى جلسة دراسة {session.concept} بنسبة دقة {accuracy:.0f}%", language="ar", detected_emotion="neutral")
            except: pass
        if ATHENA_SERVICES_READY:
            try: await knowledge_graph.update_user_knowledge(user_id=user_id, concept_id=session.concept, quality=5 if accuracy >= 80 else 3, concept_name=session.concept)
            except: pass
        next_concept = None
        if ATHENA_SERVICES_READY:
            try: next_concept = knowledge_graph.suggest_next_concept([session.concept])
            except: pass
        return {
            "concept": session.concept, "questions_asked": session.questions_asked,
            "correct_answers": session.correct_answers, "accuracy": f"{accuracy:.0f}%",
            "depth_reached": session.current_depth, "duration_minutes": self._calculate_duration(session.started_at),
            "suggested_next_concept": next_concept,
        }

athena = ATHENAOrchestrator()
logger.info("✅ ATHENA Orchestrator deeply integrated with TCMA")
