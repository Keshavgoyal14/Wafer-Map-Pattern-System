from datetime import datetime


def wafer_document(
    image_url,
    heatmap_url,
    prediction,
    detections,
    insight,
    process_insight=None,
):
    return {
        "timestamp": datetime.utcnow(),
        "image_url": image_url,
        "heatmap_url": heatmap_url,
        "prediction": prediction,
        "detections": detections,
        "insight": insight,
        "process_insight": process_insight,
        "human_feedback": {
            "engineer_label": None,
            "verified": False,
            "note": None,
        },
    }