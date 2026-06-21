"""
Background Task Queue v2.0 – قائمة مهام خلفية متقدمة
=======================================================
- تنفيذ غير متزامن مع عدد عمال متعددين (Workers)
- تسجيل المهام وتتبعها (Tracing)
- تكامل مع Metrics و Alerting
- إعادة محاولة عند الفشل (Retry)
"""
import asyncio, logging, time
from typing import Callable

logger = logging.getLogger("background_queue")

_queue: asyncio.Queue = asyncio.Queue(maxsize=2000)
_running = False
_counter = 0
_worker_tasks = []
MAX_RETRIES = 2

async def enqueue(name: str, coro: Callable, *args, **kwargs) -> str:
    """إضافة مهمة إلى القائمة"""
    global _counter; _counter += 1
    job_id = f"job_{_counter}"
    await _queue.put((job_id, name, coro, args, kwargs, 0))
    logger.info(f"📨 Enqueued: {name} ({job_id})")
    _ensure_workers()
    return job_id

async def _worker(worker_id: int):
    """عامل ينفذ المهام من القائمة"""
    logger.info(f"👷 Worker {worker_id} started")
    while True:
        try:
            job_id, name, coro, args, kwargs, attempt = await _queue.get()
            start_time = time.time()
            logger.info(f"⚙️  W{worker_id}: {name} ({job_id}) [attempt {attempt+1}]")

            try:
                await coro(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                try:
                    from app.observability.metrics_service import metrics
                    metrics.record_request(f"bg:{name}", 200, duration)
                except: pass

            except Exception as e:
                if attempt < MAX_RETRIES:
                    logger.warning(f"🔄 Retry {name} ({job_id}): {e}")
                    await _queue.put((job_id, name, coro, args, kwargs, attempt + 1))
                else:
                    logger.error(f"❌ {name} ({job_id}) failed after {MAX_RETRIES} attempts: {e}")
                    try:
                        from app.observability.metrics_service import metrics
                        metrics.record_error(str(e)[:200], name)
                    except: pass
            finally:
                _queue.task_done()

        except asyncio.CancelledError:
            logger.info(f"👷 Worker {worker_id} stopped")
            break

def _ensure_workers(num_workers: int = 2):
    global _running, _worker_tasks
    if not _running:
        _running = True
        for i in range(num_workers):
            task = asyncio.create_task(_worker(i + 1))
            _worker_tasks.append(task)

async def shutdown():
    global _running, _worker_tasks
    if _running:
        _running = False
        await _queue.join()
        for task in _worker_tasks:
            task.cancel()
        _worker_tasks.clear()

def get_queue_size() -> int:
    return _queue.qsize()

logger.info("✅ Background Queue v2.0 initialized")
