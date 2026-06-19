"""SSE Generator."""
import json
from typing import AsyncGenerator, Optional

async def sse_generator(content_gen: AsyncGenerator[str, None], final_data: Optional[dict] = None) -> AsyncGenerator[str, None]:
    async for chunk in content_gen:
        if chunk:
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
    if final_data:
        yield f"data: {json.dumps({'final': True, **final_data}, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"
