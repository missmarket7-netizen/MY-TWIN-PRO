"""
PersonNode – Living Social Graph with NER
=========================================
يستخرج الأشخاص من المحادثة تلقائياً.
يدمج الألقاب + كشف الأسماء المنعزلة.
"""

import re, logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.infrastructure.database.supabase_client import get_db
from app.memory.relationship.ner_engine import detect_names_from_text

logger = logging.getLogger("person_node")
TABLE_PERSONS = "person_nodes"
TABLE_EMOTION_LINKS = "person_emotion_links"

ARABIC_RELATION_TITLES = {
    "family": ["أمي","ماما","والدتي","أبوي","بابا","والدي","أخي","أخويا","أخ","شقيقي","أختي","أخت","شقيقتي","عمي","عم","عمو","خالي","خال","خالو","جدي","جدو","جدتي","تيتا","زوجتي","مراتي","زوجي","جوزي","ابني","بنتي","أولادي"],
    "friend": ["صديقي","صاحبي","رفيقي","أعز أصدقائي"],
    "colleague": ["زميلي","مديري","رئيسي في العمل"],
    "neighbor": ["جاري","جارتي"],
}
WESTERN_RELATION_TITLES = {
    "family": ["mom","mum","mother","dad","father","parent","brother","sister","sibling","uncle","aunt","grandpa","grandma","grandfather","grandmother","wife","husband","spouse","partner","son","daughter","child","kid"],
    "friend": ["friend","buddy","pal","best friend","mate"],
    "colleague": ["colleague","boss","manager","coworker","supervisor"],
    "neighbor": ["neighbor","neighbour","roommate"],
    "partner": ["boyfriend","girlfriend","fiancé","fiancée","lover"],
}

TITLE_TO_TYPE = {}
for rel_type, titles in ARABIC_RELATION_TITLES.items():
    for title in titles: TITLE_TO_TYPE[title] = rel_type
for rel_type, titles in WESTERN_RELATION_TITLES.items():
    for title in titles: TITLE_TO_TYPE[title.lower()] = rel_type

def detect_language(text: str) -> str:
    arabic_chars = len(re.findall(r'[\u0600-\u06ff]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    if arabic_chars > english_chars: return "ar"
    elif english_chars > arabic_chars: return "en"
    return "mixed" if arabic_chars > 0 else "en"

def extract_persons_from_text(text: str) -> List[Dict[str, Any]]:
    found_persons = []
    text_clean = text.strip()
    lang = detect_language(text_clean)

    # 1. الألقاب
    for title, rel_type in TITLE_TO_TYPE.items():
        pattern = re.compile(re.escape(title), re.IGNORECASE)
        for match in pattern.finditer(text_clean):
            after_title = text_clean[match.end():].strip()
            name = None
            if after_title:
                first_word = after_title.split()[0]
                clean_word = re.sub(r'[^\u0621-\u064a\w]', '', first_word)
                if clean_word and len(clean_word) > 1:
                    name = clean_word
            person_key = f"{title} {name}" if name else title
            found_persons.append({
                "name": person_key, "title": title.lower(), "specific_name": name,
                "relationship_type": rel_type, "confidence": 0.9 if name else 0.7,
                "language": lang, "source": "title"
            })

    # 2. my X (English)
    my_pattern = re.compile(r'\bmy\s+(\w+)\b', re.IGNORECASE)
    for word in my_pattern.findall(text_clean):
        wl = word.lower()
        for rel_type, titles in WESTERN_RELATION_TITLES.items():
            if wl in titles and not any(p.get("title") == wl for p in found_persons):
                found_persons.append({
                    "name": f"my {wl}", "title": wl, "specific_name": None,
                    "relationship_type": rel_type, "confidence": 0.8,
                    "language": "en", "source": "my"
                })

    # 3. NER – أسماء منعزلة
    ner_names = detect_names_from_text(text, lang)
    for ner in ner_names:
        if not any(p["name"] == ner["name"] for p in found_persons):
            found_persons.append({
                "name": ner["name"], "title": None, "specific_name": ner["name"],
                "relationship_type": "unknown", "confidence": ner["confidence"],
                "language": ner.get("language", lang), "source": "ner"
            })

    return found_persons

async def get_or_create_person(
    user_id: str, name: str, relationship_type: str = "unknown",
    specific_name: Optional[str] = None, importance_delta: int = 1,
    language: str = "en",
) -> Dict[str, Any]:
    db = get_db()
    try:
        result = db.table(TABLE_PERSONS).select("*").eq("user_id", user_id).eq("name", name).execute()
        if result.data:
            person = result.data[0]
            new_count = person.get("mention_count", 0) + 1
            new_importance = min(person.get("importance_score", 50) + importance_delta, 100)
            db.table(TABLE_PERSONS).update({
                "mention_count": new_count,
                "importance_score": new_importance,
                "last_mentioned": datetime.now(timezone.utc).isoformat(),
            }).eq("id", person["id"]).execute()
            person["mention_count"] = new_count
            person["importance_score"] = new_importance
            return person
        payload = {
            "user_id": user_id, "name": name, "specific_name": specific_name,
            "relationship_type": relationship_type, "language": language,
            "aliases": [name], "importance_score": 30 + importance_delta,
            "mention_count": 1,
            "first_mentioned": datetime.now(timezone.utc).isoformat(),
            "last_mentioned": datetime.now(timezone.utc).isoformat(),
            "emotional_associations": [], "sensitive_topics_around_person": [],
        }
        res = db.table(TABLE_PERSONS).insert(payload).execute()
        return res.data[0] if res.data else {"id": "", "name": name, "importance_score": 0}
    except Exception as e:
        logger.error(f"فشل جلب/إنشاء شخص: {e}")
        return {"id": "", "name": name, "importance_score": 0}

async def get_person_network(user_id: str, min_importance: int = 10) -> List[Dict[str, Any]]:
    db = get_db()
    try:
        res = db.table(TABLE_PERSONS).select("*").eq("user_id", user_id).gte("importance_score", min_importance).order("importance_score", desc=True).limit(20).execute()
        return res.data or []
    except: return []

async def link_emotion_to_person(user_id: str, person_id: str, emotion: str, emotion_memory_id: Optional[str] = None) -> bool:
    db = get_db()
    try:
        db.table(TABLE_EMOTION_LINKS).insert({"user_id": user_id, "person_id": person_id, "emotion": emotion, "emotion_memory_id": emotion_memory_id, "created_at": datetime.now(timezone.utc).isoformat()}).execute()
        person = db.table(TABLE_PERSONS).select("emotional_associations").eq("id", person_id).single().execute()
        if person.data:
            assoc = person.data.get("emotional_associations", []) or []
            for a in assoc:
                if a.get("emotion") == emotion:
                    a["count"] = a.get("count", 0) + 1
                    break
            else:
                assoc.append({"emotion": emotion, "count": 1})
            db.table(TABLE_PERSONS).update({"emotional_associations": assoc}).eq("id", person_id).execute()
        return True
    except Exception as e:
        logger.error(f"فشل ربط العاطفة: {e}")
        return False

SENSITIVE_TOPIC_PATTERNS = {
    "المال / Money": {"ar": ["فلوس","مال","راتب","دخل","مصروف","غني","فقير"], "en": ["money","salary","income","debt","rich","poor","finance"]},
    "الزواج / Marriage": {"ar": ["زواج","جواز","عريس","عروسة","متزوج","خطوبة"], "en": ["marriage","wedding","fiancé","bride","groom","divorce"]},
    "الصحة / Health": {"ar": ["مرض","تعبان","مستشفى","دكتور","عملية","علاج"], "en": ["sick","illness","hospital","doctor","surgery","therapy"]},
    "السمعة / Reputation": {"ar": ["قالوا","كلام الناس","سمعة","فضيحة","شائعة"], "en": ["rumor","gossip","reputation","scandal"]},
    "الدين / Religion": {"ar": ["صلاة","دين","حرام","حلال","ربنا","إيمان"], "en": ["prayer","religion","sin","faith","god","church"]},
}

async def detect_and_store_sensitive_topic(user_id: str, person_id: str, message: str, language: str = "ar") -> Optional[str]:
    db = get_db()
    for topic, lang_dict in SENSITIVE_TOPIC_PATTERNS.items():
        keywords = lang_dict.get(language, []) + lang_dict.get("en", [])
        for kw in keywords:
            if kw.lower() in message.lower():
                person = db.table(TABLE_PERSONS).select("sensitive_topics_around_person").eq("id", person_id).single().execute()
                if person.data:
                    topics = person.data.get("sensitive_topics_around_person", []) or []
                    if topic not in topics:
                        topics.append(topic)
                        db.table(TABLE_PERSONS).update({"sensitive_topics_around_person": topics}).eq("id", person_id).execute()
                return topic
    return None

async def process_message_for_persons(user_id: str, message: str, detected_emotion: Optional[str] = None) -> List[Dict[str, Any]]:
    extracted = extract_persons_from_text(message)
    if not extracted: return []
    processed = []
    for pdata in extracted:
        person = await get_or_create_person(
            user_id=user_id, name=pdata["name"],
            relationship_type=pdata.get("relationship_type", "unknown"),
            specific_name=pdata.get("specific_name"),
            importance_delta=2 if pdata.get("confidence", 0) > 0.8 else 1,
            language=pdata.get("language", "en"),
        )
        if not person.get("id"): continue
        if detected_emotion:
            await link_emotion_to_person(user_id, person["id"], detected_emotion)
        await detect_and_store_sensitive_topic(user_id, person["id"], message, pdata.get("language", "en"))
        processed.append({"id": person["id"], "name": pdata["name"], "relationship_type": pdata.get("relationship_type", "unknown"), "importance_score": person.get("importance_score", 0)})
    return processed

logger.info("✅ PersonNode with NER initialized")
