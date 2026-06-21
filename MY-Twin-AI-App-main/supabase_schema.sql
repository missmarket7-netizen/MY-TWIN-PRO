-- ============================================================
-- MyTwin TCMA - Complete Database Schema
-- ============================================================
-- انسخ هذا الملف كاملاً ونفذه في Supabase SQL Editor
-- ============================================================

-- 1. الأرشيف الخام (Layer 1)
CREATE TABLE IF NOT EXISTS raw_conversation_archive (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'twin')),
    emotion_primary TEXT,
    emotion_intensity FLOAT,
    detected_intent TEXT,
    conversation_id TEXT,
    language TEXT DEFAULT 'ar',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_raw_archive_user ON raw_conversation_archive(user_id, created_at DESC);

-- 2. الذاكرة العاطفية (Layer 4)
CREATE TABLE IF NOT EXISTS emotional_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    expressed_text TEXT NOT NULL,
    expressed_emotion TEXT,
    real_emotion TEXT,
    intensity FLOAT DEFAULT 0.5,
    confidence FLOAT DEFAULT 0.5,
    trigger TEXT,
    cultural_context TEXT,
    valence FLOAT DEFAULT 0.0,
    person_links JSONB DEFAULT '[]',
    arabic_category TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_emotional_user ON emotional_memory(user_id, created_at DESC);
CREATE INDEX idx_emotional_real ON emotional_memory(user_id, real_emotion);

-- 3. ذاكرة العلاقات (Layer 7)
CREATE TABLE IF NOT EXISTS relationship_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    trust FLOAT DEFAULT 0,
    openness FLOAT DEFAULT 0,
    attachment FLOAT DEFAULT 0,
    comfort FLOAT DEFAULT 0,
    relationship_stage TEXT,
    close_circle JSONB DEFAULT '[]',
    sensitive_topics JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_relationship_user ON relationship_memory(user_id, created_at DESC);

-- 4. نموذج الهوية (Layer 9)
CREATE TABLE IF NOT EXISTS identity_model (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    self_view TEXT,
    traits JSONB DEFAULT '[]',
    family_role TEXT,
    social_role TEXT,
    religious_identity TEXT,
    cultural_conflicts JSONB DEFAULT '[]',
    core_values JSONB DEFAULT '[]',
    aspirations JSONB DEFAULT '[]',
    fears JSONB DEFAULT '[]',
    source_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_identity_user ON identity_model(user_id, created_at DESC);

-- 5. عقد الأشخاص (PersonNode)
CREATE TABLE IF NOT EXISTS person_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    specific_name TEXT,
    relationship_type TEXT DEFAULT 'unknown',
    language TEXT DEFAULT 'ar',
    aliases JSONB DEFAULT '[]',
    importance_score FLOAT DEFAULT 30,
    mention_count INT DEFAULT 1,
    first_mentioned TIMESTAMPTZ DEFAULT now(),
    last_mentioned TIMESTAMPTZ DEFAULT now(),
    emotional_associations JSONB DEFAULT '[]',
    sensitive_topics_around_person JSONB DEFAULT '[]'
);
CREATE INDEX idx_person_nodes_user ON person_nodes(user_id, importance_score DESC);

-- 6. روابط العواطف بالأشخاص
CREATE TABLE IF NOT EXISTS person_emotion_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    person_id UUID REFERENCES person_nodes(id) ON DELETE CASCADE,
    emotion TEXT,
    emotion_memory_id UUID,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_person_emotion_person ON person_emotion_links(person_id);

-- 7. استنتاجات التأمل (Layer 8)
CREATE TABLE IF NOT EXISTS reflection_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    insight_type TEXT,
    insight_text TEXT,
    confidence FLOAT DEFAULT 0.5,
    source_message_id TEXT,
    related_person_id UUID REFERENCES person_nodes(id) ON DELETE SET NULL,
    related_emotion TEXT,
    language TEXT DEFAULT 'ar',
    occurrence_count INT DEFAULT 1,
    first_observed TIMESTAMPTZ DEFAULT now(),
    last_observed TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_reflection_user ON reflection_insights(user_id, last_observed DESC);

-- 8. عقد الرسم البياني للذاكرة (Layer 11)
CREATE TABLE IF NOT EXISTS memory_graph_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    user_id TEXT NOT NULL,
    content_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(memory_id, memory_type)
);
CREATE INDEX idx_graph_nodes_user ON memory_graph_nodes(user_id);
CREATE INDEX idx_graph_nodes_memory ON memory_graph_nodes(memory_id, memory_type);

-- 9. حواف الرسم البياني للذاكرة
CREATE TABLE IF NOT EXISTS memory_graph_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    target_type TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    weight FLOAT DEFAULT 1.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_graph_edges_user ON memory_graph_edges(user_id);
CREATE INDEX idx_graph_edges_source ON memory_graph_edges(source_id);
CREATE INDEX idx_graph_edges_target ON memory_graph_edges(target_id);

-- 10. تطور الهوية (اختياري للتحليل الزمني)
CREATE TABLE IF NOT EXISTS identity_evolution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    snapshot_id UUID REFERENCES identity_model(id) ON DELETE CASCADE,
    trait_changes JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- تم. 10 جداول جاهزة.
-- ============================================================
