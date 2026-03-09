import base64
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.aws_service import upload_bytes
from services.gemini_service import generate_wafer_insights
from services.mongo_service import get_history, save_analysis
from services.inference_service import run_inference


app = FastAPI(title="WaferVision AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _serialize_record(record: dict) -> dict:
    prediction = record.get("prediction") or {}
    return {
        "id": str(record.get("_id") or ""),
        "timestamp": record.get("timestamp").isoformat() if record.get("timestamp") else None,
        "defect_type": prediction.get("defect_type") or "Unknown",
        "confidence": prediction.get("confidence"),
        "image_url": record.get("image_url"),
        "heatmap_url": record.get("heatmap_url"),
        "insight": record.get("insight") or "",
        "process_insight": record.get("process_insight") or "",
    }


def _build_analytics(records: list[dict]) -> dict:
    defect_counts = Counter()
    confidence_values = []

    for record in records:
        prediction = record.get("prediction") or {}
        defect_type = prediction.get("defect_type") or "Unknown"
        defect_counts[defect_type] += 1

        confidence = prediction.get("confidence")
        if isinstance(confidence, (int, float)):
            confidence_values.append(float(confidence))

    total = sum(defect_counts.values())
    top_defect = defect_counts.most_common(1)[0][0] if defect_counts else None
    top_count = defect_counts.most_common(1)[0][1] if defect_counts else 0

    return {
        "total": total,
        "top_defect": top_defect,
        "top_share": (top_count / total) if total else 0,
        "average_confidence": (sum(confidence_values) / len(confidence_values)) if confidence_values else None,
        "distribution": [
            {
                "label": label,
                "count": count,
                "ratio": (count / total) if total else 0,
            }
            for label, count in defect_counts.most_common()
        ],
    }


def _optional_upload(data: bytes, filename: str, folder: str, content_type: str | None = None) -> str | None:
    try:
        return upload_bytes(data=data, filename=filename, folder=folder, content_type=content_type)
    except Exception:
        return None


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@app.get("/overview")
def get_overview() -> dict:
    records = get_history(limit=1000)
    analytics = _build_analytics(records)
    return {
        "total_wafers": len(records),
        "models": ["ResNet18", "MobileNetV2", "EfficientNetB0"],
        "insight_engine": "Gemini 2.0 Flash",
        "average_confidence": analytics["average_confidence"],
        "dominant_defect": analytics["top_defect"],
    }


@app.get("/analytics")
def get_analytics(limit: int = 500) -> dict:
    records = get_history(limit=limit)
    return _build_analytics(records)


@app.get("/history")
def history(limit: int = 100) -> dict:
    records = get_history(limit=limit)
    serialized = [_serialize_record(record) for record in records]
    return {"items": serialized}


@app.post("/analyze")
async def analyze_wafer(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required")

    suffix = Path(file.filename).suffix or ".png"
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        inference = run_inference(temp_path)
        history_records = get_history(limit=40)
        insights = generate_wafer_insights(
            current_prediction=inference["prediction"],
            detections=inference.get("detections", []),
            recent_records=history_records,
        )
        insight = insights["current_wafer_insight"]
        process_insight = insights["process_insight"]

        image_url = _optional_upload(
            data=file_bytes,
            filename=file.filename,
            folder="analysis",
            content_type=file.content_type,
        )
        heatmap_url = _optional_upload(
            data=inference["heatmap_bytes"],
            filename=f"heatmap_{Path(file.filename).stem}.png",
            folder="heatmaps",
            content_type="image/png",
        )

        record_id = save_analysis(
            image_url=image_url,
            heatmap_url=heatmap_url,
            prediction=inference["prediction"],
            detections=inference.get("detections", []),
            insight=insight,
            process_insight=process_insight,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    recent_match_count = sum(
        1
        for record in history_records
        if (record.get("prediction") or {}).get("defect_type") == inference["prediction"].get("defect_type")
    )

    return {
        "record_id": record_id,
        "prediction": inference["prediction"],
        "detections": inference.get("detections", []),
        "heatmap_base64": base64.b64encode(inference["heatmap_bytes"]).decode("utf-8"),
        "insight": insight,
        "current_wafer_insight": insight,
        "process_insight": process_insight,
        "recent_similar_wafers": recent_match_count,
        "image_url": image_url,
        "heatmap_url": heatmap_url,
    }