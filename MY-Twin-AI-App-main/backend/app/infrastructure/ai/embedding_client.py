"""Embedding client – generates vectors for semantic memory using Gemini."""
import os
import logging
from typing import List

logger = logging.getLogger("embedding_client")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for text using Gemini's text-embedding-004.
    Returns 768-dimensional vector.
    Falls back to mock vector if key is missing.
    """
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set – using mock embedding")
        import hashlib
        h = hashlib.md5(text.encode()).digest()
        return list(h.ljust(768 // 8, b'\x00'))[:768]

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        result = await client.aio.models.embed_content(
            model="text-embedding-004",
            contents=text,
        )
        if result.embeddings and len(result.embeddings) > 0:
            return list(result.embeddings[0].values)
        return []
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return []


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts."""
    results = []
    for text in texts:
        emb = await generate_embedding(text)
        results.append(emb)
    return results
