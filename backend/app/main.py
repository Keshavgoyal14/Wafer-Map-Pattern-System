import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ui import apply_theme, render_hero, render_panel, render_sidebar_brand, render_sidebar_navigation, render_stat_cards

st.set_page_config(
    page_title="Wafer Defect Intelligence",
    page_icon="🧠",
    layout="wide"
)

apply_theme()
render_sidebar_brand()
render_sidebar_navigation()

render_hero(
    title="Semiconductor Wafer Intelligence",
    description="A cleaner control surface for defect detection, inspection history, and model-assisted diagnostics across the wafer pipeline.",
    eyebrow="Manufacturing AI Control Room",
)

render_stat_cards([
    {"label": "Primary Flow", "value": "Upload -> Infer", "caption": "Run a wafer image through detection and insight generation."},
    {"label": "Analytics", "value": "Defect Mix", "caption": "Track defect distribution and recent process drift."},
    {"label": "History", "value": "Inspection Log", "caption": "Review previously processed wafers and image artifacts."},
])

left_col, right_col = st.columns([1.35, 1], gap="large")

with left_col:
    render_panel(
        "How to use the dashboard",
        "Start with Analyze Wafer to upload an inspection image, then move to Analytics and History to compare the result with the broader defect pattern in the database.",
    )

with right_col:
    render_panel(
        "Pages",
        "Analyze Wafer for inference, Defect Analytics for distribution, Wafer History for traceability, and System Overview for platform-level status.",
    )