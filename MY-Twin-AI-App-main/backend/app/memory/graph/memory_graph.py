"""
Memory Graph with Pattern Miner
================================
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.infrastructure.database.supabase_client import get_db
from app.memory.graph.graph_pattern_miner import mine_patterns, compress_graph

logger = logging.getLogger("memory_graph")
TABLE_EDGES = "memory_graph_edges"
TABLE_NODES = "memory_graph_nodes"

async def ensure_node(memory_id: str, memory_type: str, user_id: str, content_summary: Optional[str] = None) -> str:
    db = get_db()
    try:
        existing = db.table(TABLE_NODES).select("id").eq("memory_id", memory_id).eq("memory_type", memory_type).execute()
        if existing.data: return existing.data[0]["id"]
        payload = {"memory_id": memory_id, "memory_type": memory_type, "user_id": user_id, "content_summary": content_summary or f"{memory_type}:{memory_id[:8]}", "created_at": datetime.now(timezone.utc).isoformat()}
        res = db.table(TABLE_NODES).insert(payload).execute()
        return res.data[0]["id"] if res.data else ""
    except Exception as e:
        logger.error(f"ensure_node failed: {e}")
        return ""

async def create_edge(user_id, source_id, source_type, target_id, target_type, relation_type, weight=1.0, metadata=None) -> str:
    db = get_db()
    try:
        exist = db.table(TABLE_EDGES).select("id").eq("user_id", user_id).eq("source_id", source_id).eq("target_id", target_id).eq("relation_type", relation_type).execute()
        if exist.data:
            old_w = exist.data[0].get("weight", 1.0)
            db.table(TABLE_EDGES).update({"weight": min(old_w + 0.2, 3.0), "updated_at": datetime.now(timezone.utc).isoformat()}).eq("id", exist.data[0]["id"]).execute()
            return exist.data[0]["id"]
        payload = {"user_id": user_id, "source_id": source_id, "source_type": source_type, "target_id": target_id, "target_type": target_type, "relation_type": relation_type, "weight": weight, "metadata": metadata or {}, "created_at": datetime.now(timezone.utc).isoformat()}
        res = db.table(TABLE_EDGES).insert(payload).execute()
        return res.data[0]["id"] if res.data else ""
    except Exception as e:
        logger.error(f"create_edge failed: {e}")
        return ""

async def get_connected_memories(user_id, memory_id, depth=2, relation_types=None) -> List[Dict[str, Any]]:
    db = get_db()
    connected = []
    visited = {memory_id}
    current_layer = [memory_id]
    for _ in range(depth):
        if not current_layer: break
        next_layer = []
        for mid in current_layer:
            query = db.table(TABLE_EDGES).select("*").eq("user_id", user_id).or_(f"source_id.eq.{mid},target_id.eq.{mid}")
            if relation_types: query = query.in_("relation_type", relation_types)
            res = query.execute()
            if res.data:
                for edge in res.data:
                    connected.append(edge)
                    other = edge["target_id"] if edge["source_id"] == mid else edge["source_id"]
                    if other not in visited:
                        visited.add(other)
                        next_layer.append(other)
        current_layer = next_layer
    return connected

async def auto_create_edges_from_memory(user_id, memory_id, memory_type, memory_data) -> int:
    edges_created = 0
    db = get_db()
    if memory_type == "emotional_memory":
        for link in memory_data.get("person_links", []):
            pid = link.get("person_id")
            if pid:
                await ensure_node(pid, "person_node", user_id)
                await create_edge(user_id, memory_id, "emotional_memory", pid, "person_node", "involves_person", weight=1.5, metadata={"emotion": link.get("emotion_toward_person")})
                edges_created += 1
        trigger = memory_data.get("trigger")
        if trigger:
            similar = db.table(TABLE_NODES).select("memory_id").eq("user_id", user_id).eq("memory_type", "emotional_memory").like("content_summary", f"%{trigger}%").limit(5).execute()
            if similar.data:
                for s in similar.data:
                    if s["memory_id"] != memory_id:
                        await create_edge(user_id, memory_id, "emotional_memory", s["memory_id"], "emotional_memory", "triggered_by", weight=0.8)
                        edges_created += 1
    elif memory_type == "reflection_insight":
        related_person = memory_data.get("related_person_id")
        if related_person:
            await ensure_node(related_person, "person_node", user_id)
            await create_edge(user_id, memory_id, "reflection", related_person, "person_node", "involves_person", weight=1.2)
            edges_created += 1
        related_emotion = memory_data.get("related_emotion")
        if related_emotion:
            await create_edge(user_id, memory_id, "reflection", related_emotion, "emotional_memory", "leads_to", weight=1.0)
            edges_created += 1
    elif memory_type == "identity_model":
        recent = db.table(TABLE_NODES).select("memory_id").eq("user_id", user_id).eq("memory_type", "reflection").order("created_at", desc=True).limit(5).execute()
        if recent.data:
            for r in recent.data:
                await create_edge(user_id, memory_id, "identity", r["memory_id"], "reflection", "linked_to_identity", weight=0.7)
                edges_created += 1
    return edges_created

async def get_memory_cluster(user_id, center_memory_id, radius=2):
    edges = await get_connected_memories(user_id, center_memory_id, depth=radius)
    db = get_db()
    node_ids = {center_memory_id}
    for e in edges:
        node_ids.add(e["source_id"]); node_ids.add(e["target_id"])
    nodes = []
    for nid in node_ids:
        node = db.table(TABLE_NODES).select("*").eq("memory_id", nid).single().execute()
        if node.data: nodes.append(node.data)
    nodes.sort(key=lambda x: x.get("created_at", ""))
    return {"center": center_memory_id, "nodes": nodes, "edges": edges, "total_nodes": len(nodes), "total_edges": len(edges)}

async def get_graph_context_for_response(user_id, recent_memory_ids):
    all_edges = []
    for mid in recent_memory_ids[-5:]:
        edges = await get_connected_memories(user_id, mid, depth=1)
        all_edges.extend(edges)
    summary = {}
    for e in all_edges:
        rtype = e.get("relation_type", "unknown")
        summary[rtype] = summary.get(rtype, 0) + 1
    return {"active_memories": len(recent_memory_ids), "active_edges": len(all_edges), "relation_summary": summary}

# دالة تنقيب الأنماط (تستدعى دورياً)
async def run_graph_mining(user_id: str) -> Dict[str, Any]:
    patterns = await mine_patterns(user_id)
    compression = await compress_graph(user_id)
    return {"patterns": patterns, "compression": compression}

logger.info("✅ Memory Graph with Pattern Miner initialized")
