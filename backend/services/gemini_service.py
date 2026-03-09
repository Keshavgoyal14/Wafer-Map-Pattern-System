from collections import Counter
from statistics import mean
import re

from google import genai

from app.config import GEMINI_API_KEY


client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def _format_percent(value) -> str:
    if not isinstance(value, (int, float)):
        return "unknown"
    return f"{float(value):.1%}"


def _confidence_band(value) -> str:
    if not isinstance(value, (int, float)):
        return "unscored"
    if value >= 0.9:
        return "very high"
    if value >= 0.8:
        return "high"
    if value >= 0.65:
        return "moderate"
    return "low"


def _severity_label(defect_type: str | None) -> str:
    critical = {"Scratch", "Edge-ring", "Edge-loc"}
    elevated = {"Loc", "Center", "Donut"}

    if defect_type in critical:
        return "critical"
    if defect_type in elevated:
        return "elevated"
    if defect_type in {"None", "Near-full"}:
        return "low"
    return "moderate"


def _recommendation(defect_type: str | None, confidence: float | None, trend_strength: str) -> str:
    severity = _severity_label(defect_type)
    confidence_band = _confidence_band(confidence)

    if severity == "critical":
        return "Hold the wafer for engineering review and verify the highlighted region against process and tool logs."
    if severity == "elevated" and trend_strength in {"recurring", "dominant"}:
        return "Review adjacent wafers and recent tool conditions to check whether this pattern is process-linked."
    if confidence_band == "low":
        return "Treat this as a tentative classification and confirm manually before taking corrective action."
    if defect_type in {"None", "Near-full"}:
        return "No immediate escalation is suggested; continue normal monitoring and watch for drift in the next batch."
    return "Confirm the pattern against the heatmap and compare it with recent wafers before deciding on escalation."


def _condense_insight(text: str, empty_message: str = "No AI insight is available for this wafer.") -> str:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return empty_message

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    compact = [sentence.strip() for sentence in sentences if sentence.strip()]

    if not compact:
        return cleaned[:280]

    return " ".join(compact[:3])


def _fallback_insight(current_prediction: dict, history_summary: dict) -> str:
    defect = current_prediction.get("defect_type") or "Unknown"
    confidence = current_prediction.get("confidence")
    average_confidence = history_summary.get("average_confidence")
    sample_size = history_summary.get("sample_size", 0)
    matching_count = history_summary.get("matching_count", 0)
    match_rate = history_summary.get("matching_rate")
    dominant_defect = history_summary.get("top_defect")
    dominant_share = history_summary.get("top_defect_share")

    if dominant_defect == defect and isinstance(match_rate, (int, float)):
        trend_strength = "dominant" if match_rate >= 0.35 else "recurring"
        trend_sentence = (
            f"This aligns with recent history, with {matching_count} of the last {sample_size} wafers showing the same pattern"
            f" ({_format_percent(match_rate)})."
        )
    elif matching_count > 0 and isinstance(match_rate, (int, float)):
        trend_strength = "recurring"
        trend_sentence = (
            f"This pattern appears intermittently in recent history, with {matching_count} of the last {sample_size} wafers matching"
            f" ({_format_percent(match_rate)})."
        )
    else:
        trend_strength = "isolated"
        if dominant_defect and isinstance(dominant_share, (int, float)):
            trend_sentence = (
                f"This looks less common than the current dominant pattern of {dominant_defect}"
                f" ({_format_percent(dominant_share)} of recent wafers)."
            )
        else:
            trend_sentence = "No recent trend match was found, so this may be an isolated case."

    confidence_sentence = (
        f"The wafer is most consistent with {defect} at {_format_percent(confidence)} confidence, which is {_confidence_band(confidence)}"
        f" versus a recent average of {_format_percent(average_confidence)}."
    )
    action_sentence = _recommendation(defect, confidence, trend_strength)

    return _condense_insight(f"{confidence_sentence} {trend_sentence} {action_sentence}")


def _fallback_process_insight(current_prediction: dict, history_summary: dict) -> str:
    defect = current_prediction.get("defect_type") or "Unknown"
    distribution = history_summary.get("defect_distribution") or {}
    sample_size = history_summary.get("sample_size", 0)
    top_defect = history_summary.get("top_defect")
    top_share = history_summary.get("top_defect_share")
    match_rate = history_summary.get("matching_rate")
    average_confidence = history_summary.get("average_confidence")

    if sample_size == 0:
        return "Manufacturing process insight is unavailable because there is no recent wafer history to compare against."

    if top_defect == defect and isinstance(top_share, (int, float)) and top_share >= 0.3:
        process_signal = (
            f"The recent wafer window is being driven by {defect}, which accounts for {_format_percent(top_share)} of the last {sample_size} wafers."
        )
    elif isinstance(match_rate, (int, float)) and match_rate >= 0.2:
        process_signal = (
            f"{defect} is recurring in the recent production window, appearing in {_format_percent(match_rate)} of the last {sample_size} wafers."
        )
    else:
        process_signal = (
            f"The current wafer does not strongly match the dominant recent pattern, so the issue may be localized rather than process-wide."
        )

    confidence_signal = (
        f"Recent classification confidence averages {_format_percent(average_confidence)}, which suggests {'stable' if isinstance(average_confidence, (int, float)) and average_confidence >= 0.8 else 'potentially noisy'} signal quality in the current line data."
    )

    if _severity_label(defect) == "critical":
        action = "Check the associated tool, recipe, and the neighboring wafers in the same lot for a manufacturing excursion."
    elif top_defect == defect and isinstance(top_share, (int, float)) and top_share >= 0.3:
        action = "Review lot-level process conditions and equipment drift because the same defect pattern is repeating across recent wafers."
    else:
        action = "Continue monitoring the next wafers in sequence to determine whether this remains isolated or develops into a process trend."

    return _condense_insight(f"{process_signal} {confidence_signal} {action}")


def build_history_summary(records):
    defect_types = []
    confidences = []
    recent_samples = []

    for record in records:
        prediction = record.get("prediction") or {}
        defect_type = prediction.get("defect_type")
        confidence = prediction.get("confidence")

        if defect_type:
            defect_types.append(defect_type)

        if isinstance(confidence, (int, float)):
            confidences.append(float(confidence))

        recent_samples.append(
            {
                "timestamp": str(record.get("timestamp")),
                "defect_type": defect_type,
                "confidence": confidence,
            }
        )

    defect_distribution = dict(Counter(defect_types))
    top_defect, top_count = next(iter(Counter(defect_types).most_common(1)), (None, 0))

    return {
        "sample_size": len(records),
        "defect_distribution": defect_distribution,
        "average_confidence": round(mean(confidences), 4) if confidences else None,
        "top_defect": top_defect,
        "top_defect_share": round((top_count / len(records)), 4) if records else 0,
        "recent_samples": recent_samples[:5],
    }


def generate_wafer_insight(current_prediction, detections, recent_records):
    history_summary = build_history_summary(recent_records)
    defect = current_prediction.get("defect_type") or "Unknown"
    confidence = current_prediction.get("confidence")
    defect_distribution = history_summary.get("defect_distribution") or {}
    matching_count = defect_distribution.get(defect, 0)
    sample_size = history_summary.get("sample_size", 0)
    matching_rate = (matching_count / sample_size) if sample_size else 0
    history_summary["matching_count"] = matching_count
    history_summary["matching_rate"] = round(matching_rate, 4) if sample_size else 0

    recent_pattern_examples = ", ".join(
        f"{sample.get('defect_type') or 'Unknown'} @ {_format_percent(sample.get('confidence'))}"
        for sample in history_summary.get("recent_samples", [])
    ) or "No recent examples available"

    prompt = f"""
You are generating operator-facing semiconductor wafer insights for a manufacturing dashboard.
Be specific, factual, and concise. Avoid generic AI phrasing.

Current wafer prediction:
defect_type: {defect}
confidence: {_format_percent(confidence)}
confidence_band: {_confidence_band(confidence)}
severity: {_severity_label(defect)}

Historical summary from the last {history_summary["sample_size"]} wafers:
dominant_defect: {history_summary.get("top_defect")}
dominant_share: {_format_percent(history_summary.get("top_defect_share"))}
matching_defect_count: {matching_count}
matching_defect_share: {_format_percent(matching_rate)}
average_confidence: {_format_percent(history_summary.get("average_confidence"))}
distribution: {history_summary.get("defect_distribution")}
recent_examples: {recent_pattern_examples}

Write exactly 3 short sentences in plain text:
1. State the predicted wafer condition and confidence quality.
2. Compare it to recent history and say whether it appears isolated, recurring, or dominant.
3. Give one concrete next action for an operator or engineer.

Do not mention YOLO, JSON, or internal model names.
""".strip()

    if client is None:
        return _fallback_insight(current_prediction, history_summary)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
    except Exception as exc:
        return _fallback_insight(current_prediction, history_summary)

    if not response.text:
        return _fallback_insight(current_prediction, history_summary)

    return _condense_insight(response.text)


def generate_process_insight(current_prediction, recent_records):
    history_summary = build_history_summary(recent_records)
    defect = current_prediction.get("defect_type") or "Unknown"
    defect_distribution = history_summary.get("defect_distribution") or {}
    sample_size = history_summary.get("sample_size", 0)
    matching_count = defect_distribution.get(defect, 0)
    matching_rate = (matching_count / sample_size) if sample_size else 0
    history_summary["matching_count"] = matching_count
    history_summary["matching_rate"] = round(matching_rate, 4) if sample_size else 0

    prompt = f"""
You are generating a manufacturing-process insight for a semiconductor wafer dashboard.
Focus on whether the current wafer suggests an isolated defect or a process issue affecting recent wafers.

Current wafer:
defect_type: {defect}
confidence: {_format_percent(current_prediction.get('confidence'))}
severity: {_severity_label(defect)}

Recent production window: last {sample_size} wafers
dominant_defect: {history_summary.get('top_defect')}
dominant_share: {_format_percent(history_summary.get('top_defect_share'))}
matching_defect_count: {matching_count}
matching_defect_share: {_format_percent(matching_rate)}
average_confidence: {_format_percent(history_summary.get('average_confidence'))}
defect_distribution: {history_summary.get('defect_distribution')}

Write exactly 3 short sentences in plain text:
1. Describe the manufacturing-process signal suggested by the recent wafer window.
2. State whether the current wafer supports a recurring process issue or looks isolated.
3. Give one concrete manufacturing-focused action, such as tool check, lot review, or continued monitoring.

Do not mention AI, YOLO, JSON, or internal model names.
""".strip()

    if client is None:
        return _fallback_process_insight(current_prediction, history_summary)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
    except Exception:
        return _fallback_process_insight(current_prediction, history_summary)

    if not response.text:
        return _fallback_process_insight(current_prediction, history_summary)

    condensed = _condense_insight(
        response.text,
        empty_message="Manufacturing process insight could not be generated from the model response.",
    )

    if condensed in {
        "Manufacturing process insight could not be generated from the model response.",
        "No AI insight is available for this wafer.",
    }:
        return _fallback_process_insight(current_prediction, history_summary)

    return condensed


def generate_wafer_insights(current_prediction, detections, recent_records):
    current_wafer_insight = generate_wafer_insight(current_prediction, detections, recent_records)
    process_insight = generate_process_insight(current_prediction, recent_records)
    return {
        "current_wafer_insight": current_wafer_insight,
        "process_insight": process_insight,
    }