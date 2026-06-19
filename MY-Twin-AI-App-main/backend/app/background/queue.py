"""Background Task Queue – non‑blocking job processing."""
import asyncio, logging
from typing import Callable

logger = logging.getLogger("background_queue")
_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
_running = False
_counter = 0

async def enqueue(name: str, coro: Callable, *args, **kwargs) -> str:
    global _counter; _counter += 1
    job_id = f"job_{_counter}"
    await _queue.put((job_id, name, coro, args, kwargs))
    logger.info(f"📨 Enqueued: {name} ({job_id})")
    _ensure_worker()
    return job_id

async def _worker():
    global _running; _running = True
    logger.info("👷 Background worker started")
    while True:
        try:
            job_id, name, coro, args, kwargs = await _queue.get()
            logger.info(f"⚙️  Processing: {name} ({job_id})")
            try: await coro(*args, **kwargs)
            except Exception as e: logger.error(f"❌ {name} ({job_id}): {e}")
            finally: _queue.task_done()
        except asyncio.CancelledError:
            _running = False; break

def _ensure_worker():
    global _running
    if not _running: asyncio.create_task(_worker())

async def shutdown():
    global _running
    if _running:
        await _queue.join()
        _running = False
