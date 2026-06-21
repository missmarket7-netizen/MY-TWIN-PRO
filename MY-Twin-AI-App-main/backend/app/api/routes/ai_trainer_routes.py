"""
AI Trainer API Routes - مسارات تدريب النموذج الخاص
=====================================================
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional

try:
    from app.ai_trainer.training_data_exporter import TrainingDataExporter
    from app.ai_trainer.model_trainer import ModelTrainer
    TRAINER_READY = True
except ImportError:
    TRAINER_READY = False

router = APIRouter(prefix="/api/ai-trainer", tags=["ai-trainer"])

exporter = TrainingDataExporter()
trainer = ModelTrainer()

@router.post("/export")
async def export_training_data(
    limit: int = Query(1000),
    format: str = "jsonl",
    include_emotions: bool = True,
    include_identity: bool = False,
) -> Dict[str, Any]:
    """تصدير بيانات التدريب من المحادثات"""
    if not TRAINER_READY:
        raise HTTPException(status_code=503, detail="خدمة التدريب غير متوفرة")
    try:
        filepath = await exporter.export_conversations(
            limit=limit, format=format,
            include_emotions=include_emotions,
            include_identity=include_identity,
        )
        return {"status": "success", "file": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def start_training(
    training_file: str = Query(...),
    base_model: Optional[str] = None,
    epochs: int = 3,
    learning_rate: float = 2e-4,
) -> Dict[str, Any]:
    """بدء تدريب النموذج الخاص"""
    if not TRAINER_READY:
        raise HTTPException(status_code=503, detail="خدمة التدريب غير متوفرة")
    return await trainer.start_training(
        training_file=training_file,
        base_model=base_model,
        num_epochs=epochs,
        learning_rate=learning_rate,
    )

@router.get("/status")
async def training_status():
    """حالة نظام التدريب"""
    return {
        "trainer_ready": TRAINER_READY,
        "default_base_model": trainer.default_base_model,
        "output_dir": trainer.output_dir,
    }
