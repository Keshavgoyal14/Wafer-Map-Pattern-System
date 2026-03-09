from datetime import datetime
from bson import ObjectId

from database.schema import wafer_document
from database.mongodb import wafer_collection


# ----------------------------------------
# Save new wafer analysis
# ----------------------------------------
def save_analysis(
    image_url,
    heatmap_url,
    prediction,
    detections,
    insight,
    process_insight=None
):
    """
    Save wafer analysis result to MongoDB
    """

    document = wafer_document(
        image_url=image_url,
        heatmap_url=heatmap_url,
        prediction=prediction,
        detections=detections,
        insight=insight,
        process_insight=process_insight,
    )

    result = wafer_collection.insert_one(document)

    return str(result.inserted_id)


# ----------------------------------------
# Get single wafer record
# ----------------------------------------
def get_analysis(record_id):

    record = wafer_collection.find_one(
        {"_id": ObjectId(record_id)}
    )

    if record:
        record["_id"] = str(record["_id"])

    return record


# ----------------------------------------
# Get analysis history
# ----------------------------------------
def get_history(limit=50):

    results = list(
        wafer_collection.find()
        .sort("timestamp", -1)
        .limit(limit)
    )

    history = []

    for r in results:

        r["_id"] = str(r["_id"])

        history.append(r)

    return history


# ----------------------------------------
# Get recent defects for Gemini
# ----------------------------------------
def get_recent_defects(limit=30):

    results = list(
        wafer_collection.find()
        .sort("timestamp", -1)
        .limit(limit)
    )

    defects = []

    for r in results:

        prediction = r.get("prediction")

        if prediction and "defect_type" in prediction:
            defects.append(prediction["defect_type"])

    return defects


# ----------------------------------------
# Add human feedback
# ----------------------------------------
def add_feedback(
    record_id,
    engineer_label,
    note
):

    result = wafer_collection.update_one(
        {"_id": ObjectId(record_id)},
        {
            "$set": {
                "human_feedback.engineer_label": engineer_label,
                "human_feedback.verified": True,
                "human_feedback.note": note,
                "human_feedback.timestamp": datetime.utcnow()
            }
        }
    )

    return result.modified_count


# ----------------------------------------
# Get corrected samples (for retraining)
# ----------------------------------------
def get_verified_samples():

    results = list(
        wafer_collection.find(
            {"human_feedback.verified": True}
        )
    )

    samples = []

    for r in results:

        r["_id"] = str(r["_id"])

        samples.append(r)

    return samples


# ----------------------------------------
# Delete record (optional)
# ----------------------------------------
def delete_record(record_id):

    result = wafer_collection.delete_one(
        {"_id": ObjectId(record_id)}
    )

    return result.deleted_count