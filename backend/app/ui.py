from html import escape
from math import cos, pi, sin

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

        :root {
            --bg: #f4efe6;
            --panel: rgba(255, 252, 247, 0.78);
            --panel-strong: #fffaf2;
            --border: rgba(39, 54, 59, 0.12);
            --text: #152427;
            --muted: #5f6b6d;
            --accent: #d96c2f;
            --accent-soft: rgba(217, 108, 47, 0.12);
            --secondary: #0f766e;
            --secondary-soft: rgba(15, 118, 110, 0.12);
            --shadow: 0 24px 60px rgba(21, 36, 39, 0.08);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(217, 108, 47, 0.18), transparent 32%),
                radial-gradient(circle at top right, rgba(15, 118, 110, 0.14), transparent 26%),
                linear-gradient(180deg, #fbf8f2 0%, var(--bg) 100%);
            color: var(--text);
            font-family: 'IBM Plex Sans', sans-serif;
        }

        .main .block-container {
            padding-top: 2.5rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }

        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif;
            color: var(--text);
            letter-spacing: -0.03em;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #17353b 0%, #10252a 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        [data-testid="stSidebarNav"] {
            display: none;
        }

        [data-testid="stSidebar"] * {
            color: #f3ede2;
        }

        .sidebar-nav-shell {
            margin: 0 0 1rem;
            padding: 0.2rem 0 0;
        }

        .sidebar-nav-title {
            margin: 0 0 0.7rem;
            color: rgba(243, 237, 226, 0.66);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
            border-radius: 18px;
            padding: 0.72rem 0.9rem;
            margin-bottom: 0.35rem;
            background: transparent;
            border: 1px solid transparent;
            transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
            background: rgba(255,255,255,0.06);
            border-color: rgba(255,255,255,0.08);
            transform: translateX(2px);
        }

        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1rem;
            font-weight: 600;
            color: #f8f2e9;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {
            background: linear-gradient(135deg, rgba(255,255,255,0.18), rgba(255,255,255,0.08));
            border-color: rgba(255,255,255,0.12);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        }

        .sidebar-brand {
            position: relative;
            margin: 0.2rem 0 1.15rem;
            padding: 1rem 1rem 0.95rem;
            border-radius: 22px;
            background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
            border: 1px solid rgba(255,255,255,0.1);
            overflow: hidden;
        }

        .sidebar-brand::after {
            content: '';
            position: absolute;
            right: -30px;
            top: -25px;
            width: 110px;
            height: 110px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(242,155,75,0.25), transparent 68%);
        }

        .sidebar-brand-head {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            margin-bottom: 0.75rem;
        }

        .sidebar-brand-copy strong {
            display: block;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.1rem;
            line-height: 1.05;
            color: #fff7ec;
        }

        .sidebar-brand-copy span {
            display: block;
            margin-top: 0.18rem;
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: rgba(243, 237, 226, 0.68);
        }

        .sidebar-brand p {
            margin: 0;
            color: rgba(243, 237, 226, 0.84);
            font-size: 0.9rem;
            line-height: 1.45;
        }

        .sidebar-note {
            margin-top: 0.85rem;
            padding-top: 0.8rem;
            border-top: 1px solid rgba(255,255,255,0.08);
            color: rgba(243, 237, 226, 0.74);
            font-size: 0.84rem;
        }

        [data-testid="stFileUploader"] {
            background: rgba(255, 250, 242, 0.72);
            border-radius: 22px;
            padding: 0.35rem;
        }

        div[data-baseweb="button"] > button,
        .stButton > button {
            border: 0;
            border-radius: 999px;
            padding: 0.72rem 1.4rem;
            background: linear-gradient(135deg, #d96c2f 0%, #f29b4b 100%);
            color: white;
            font-weight: 700;
            box-shadow: 0 14px 30px rgba(217, 108, 47, 0.26);
        }

        .hero {
            position: relative;
            overflow: hidden;
            padding: 1.7rem 1.9rem;
            margin-bottom: 1.25rem;
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(255,255,255,0.74), rgba(255,250,242,0.95)),
                linear-gradient(120deg, rgba(217,108,47,0.15), rgba(15,118,110,0.12));
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
        }

        .hero::after {
            content: '';
            position: absolute;
            right: -36px;
            top: -28px;
            width: 180px;
            height: 180px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(15,118,110,0.18), transparent 65%);
        }

        .eyebrow {
            display: inline-block;
            margin-bottom: 0.6rem;
            padding: 0.28rem 0.72rem;
            border-radius: 999px;
            background: rgba(15, 118, 110, 0.12);
            color: var(--secondary);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(2rem, 3vw, 3.2rem);
            line-height: 1;
        }

        .hero p {
            margin: 0.85rem 0 0;
            max-width: 760px;
            color: var(--muted);
            font-size: 1rem;
        }

        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.9rem;
            margin: 1rem 0 1.4rem;
        }

        .stat-card,
        .panel,
        .table-shell {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 24px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(14px);
        }

        .stat-card {
            padding: 1rem 1.1rem;
        }

        .stat-label {
            color: var(--muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
        }

        .stat-value {
            margin-top: 0.45rem;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text);
        }

        .stat-caption {
            margin-top: 0.3rem;
            color: var(--muted);
            font-size: 0.9rem;
        }

        .panel {
            padding: 1.15rem 1.2rem;
            margin-bottom: 1rem;
        }

        .panel h3 {
            margin: 0 0 0.45rem;
            font-size: 1.1rem;
        }

        .panel p {
            margin: 0;
            color: var(--muted);
        }

        .section-title {
            margin: 1rem 0 0.8rem;
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text);
        }

        .table-shell {
            overflow: hidden;
            margin-top: 1rem;
        }

        .history-table {
            width: 100%;
            border-collapse: collapse;
        }

        .history-table thead th {
            background: rgba(15, 118, 110, 0.08);
            color: var(--secondary);
            text-align: left;
            padding: 0.95rem 1rem;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .history-table tbody td {
            padding: 0.95rem 1rem;
            border-top: 1px solid rgba(39, 54, 59, 0.08);
            color: var(--text);
            vertical-align: top;
        }

        .history-table tbody tr:nth-child(even) {
            background: rgba(255,255,255,0.42);
        }

        .pill {
            display: inline-block;
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            background: var(--accent-soft);
            color: var(--accent);
            font-size: 0.82rem;
            font-weight: 700;
        }

        .link-chip {
            display: inline-block;
            padding: 0.36rem 0.78rem;
            border-radius: 999px;
            background: rgba(15, 118, 110, 0.12);
            color: var(--secondary);
            text-decoration: none;
            font-weight: 700;
        }

        .kv-list {
            display: grid;
            grid-template-columns: 1fr;
            gap: 0.7rem;
        }

        .kv-item {
            padding: 0.8rem 0.95rem;
            border-radius: 18px;
            background: rgba(255,255,255,0.52);
            border: 1px solid rgba(39, 54, 59, 0.08);
        }

        .kv-key {
            margin-bottom: 0.2rem;
            color: var(--muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            font-weight: 700;
        }

        .kv-value {
            color: var(--text);
            font-weight: 600;
            word-break: break-word;
        }

        .pie-layout {
            display: grid;
            grid-template-columns: minmax(240px, 340px) 1fr;
            gap: 1.2rem;
            align-items: center;
        }

        .pie-card {
            background: rgba(255,255,255,0.42);
            border: 1px solid rgba(39, 54, 59, 0.08);
            border-radius: 22px;
            padding: 1rem;
        }

        .pie-legend {
            display: grid;
            gap: 0.7rem;
        }

        .pie-legend-row {
            display: grid;
            grid-template-columns: auto 1fr auto;
            gap: 0.7rem;
            align-items: center;
            padding: 0.75rem 0.85rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.48);
            border: 1px solid rgba(39, 54, 59, 0.07);
        }

        .pie-swatch {
            width: 0.8rem;
            height: 0.8rem;
            border-radius: 50%;
        }

        .pie-label {
            color: var(--text);
            font-weight: 600;
        }

        .pie-meta {
            color: var(--muted);
            font-size: 0.9rem;
            text-align: right;
        }

        .mini-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.8rem;
            margin-top: 0.9rem;
        }

        .mini-card {
            padding: 0.9rem 1rem;
            border-radius: 18px;
            background: rgba(255,255,255,0.52);
            border: 1px solid rgba(39, 54, 59, 0.08);
        }

        .mini-card strong {
            display: block;
            color: var(--text);
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.05rem;
            margin-bottom: 0.25rem;
        }

        .mini-card span {
            color: var(--muted);
            font-size: 0.9rem;
        }

        .insight-snippet {
            max-width: 320px;
            color: var(--muted);
            line-height: 1.45;
        }

        @media (max-width: 768px) {
            .main .block-container {
                padding-top: 1.4rem;
            }

            .hero {
                padding: 1.35rem;
                border-radius: 22px;
            }

            .pie-layout {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, description: str, eyebrow: str) -> None:
    st.markdown(
        f"""
        <section class="hero">
            <div class="eyebrow">{escape(eyebrow)}</div>
            <h1>{escape(title)}</h1>
            <p>{escape(description)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    st.sidebar.markdown(
        """
        <section class="sidebar-brand">
            <div class="sidebar-brand-head">
                <svg width="54" height="54" viewBox="0 0 54 54" aria-hidden="true">
                    <defs>
                        <linearGradient id="waferGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#f29b4b"></stop>
                            <stop offset="100%" stop-color="#0f766e"></stop>
                        </linearGradient>
                    </defs>
                    <circle cx="27" cy="27" r="22" fill="none" stroke="url(#waferGradient)" stroke-width="3.5"></circle>
                    <circle cx="27" cy="27" r="13" fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.35)" stroke-width="1.4"></circle>
                    <circle cx="27" cy="27" r="3.6" fill="#f29b4b"></circle>
                    <path d="M27 5 L27 49 M5 27 L49 27 M12 12 L42 42 M42 12 L12 42" stroke="rgba(255,255,255,0.16)" stroke-width="1"></path>
                </svg>
                <div class="sidebar-brand-copy">
                    <strong>WaferVision AI</strong>
                    <span>Defect Intelligence Suite</span>
                </div>
            </div>
            <p>Semiconductor wafer classification, trend review, and operator-ready insight in one dashboard.</p>
            <div class="sidebar-note">Use the navigation panel to move between live analysis, defect analytics, history, and system overview.</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_navigation() -> None:
    st.sidebar.markdown(
        """
        <div class="sidebar-nav-shell">
            <div class="sidebar-nav-title">Navigation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.page_link("main.py", label="Dashboard Home", icon="🏠")
    st.sidebar.page_link("pages/Analyze_Wafer.py", label="Analyze Wafer", icon="🔬")
    st.sidebar.page_link("pages/Defect_Analytics.py", label="Defect Analytics", icon="📊")
    st.sidebar.page_link("pages/Wafer_History.py", label="Wafer History", icon="🗃")
    st.sidebar.page_link("pages/System_Overview.py", label="System Overview", icon="🧠")


def render_stat_cards(cards: list[dict[str, str]]) -> None:
    card_html = []
    for card in cards:
        card_html.append(
            "<div class='stat-card'>"
            f"<div class='stat-label'>{escape(str(card['label']))}</div>"
            f"<div class='stat-value'>{escape(str(card['value']))}</div>"
            f"<div class='stat-caption'>{escape(str(card.get('caption', '')))}</div>"
            "</div>"
        )
    st.markdown(f"<section class='stat-grid'>{''.join(card_html)}</section>", unsafe_allow_html=True)


def render_panel(title: str, body: str) -> None:
    st.markdown(
        f"""
        <section class="panel">
            <h3>{escape(title)}</h3>
            <p>{escape(body)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_key_value_block(title: str, items: list[tuple[str, str]]) -> None:
    rows = []
    for key, value in items:
        rows.append(
            "<div class='kv-item'>"
            f"<div class='kv-key'>{escape(str(key))}</div>"
            f"<div class='kv-value'>{escape(str(value))}</div>"
            "</div>"
        )
    st.markdown(
        f"""
        <section class="panel">
            <h3>{escape(title)}</h3>
            <div class="kv-list">{''.join(rows)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_mini_cards(items: list[tuple[str, str]]) -> None:
    cards = []
    for title, body in items:
        cards.append(
            "<div class='mini-card'>"
            f"<strong>{escape(str(title))}</strong>"
            f"<span>{escape(str(body))}</span>"
            "</div>"
        )
    st.markdown(f"<section class='mini-grid'>{''.join(cards)}</section>", unsafe_allow_html=True)


def _polar_to_cartesian(center_x: float, center_y: float, radius: float, angle_deg: float) -> tuple[float, float]:
    angle_rad = (angle_deg - 90) * pi / 180
    return center_x + radius * cos(angle_rad), center_y + radius * sin(angle_rad)


def _describe_arc(center_x: float, center_y: float, radius: float, start_angle: float, end_angle: float) -> str:
    start_x, start_y = _polar_to_cartesian(center_x, center_y, radius, end_angle)
    end_x, end_y = _polar_to_cartesian(center_x, center_y, radius, start_angle)
    large_arc_flag = "1" if end_angle - start_angle > 180 else "0"
    return (
        f"M {center_x} {center_y} "
        f"L {start_x:.4f} {start_y:.4f} "
        f"A {radius} {radius} 0 {large_arc_flag} 0 {end_x:.4f} {end_y:.4f} Z"
    )


def render_pie_chart(title: str, items: list[tuple[str, int]], total: int) -> None:
    if not items or total <= 0:
        return

    palette = [
        "#d96c2f",
        "#0f766e",
        "#f29b4b",
        "#295f98",
        "#7c5cfa",
        "#c2410c",
        "#14859b",
        "#8f3f71",
    ]

    start_angle = 0.0
    slices = []
    legend_rows = []

    for index, (label, count) in enumerate(items):
        fraction = count / total
        end_angle = start_angle + (fraction * 360)
        color = palette[index % len(palette)]
        path = _describe_arc(120, 120, 100, start_angle, end_angle)
        slices.append(f"<path d='{path}' fill='{color}'></path>")
        legend_rows.append(
            "<div class='pie-legend-row'>"
            f"<span class='pie-swatch' style='background:{color};'></span>"
            f"<span class='pie-label'>{escape(label)}</span>"
            f"<span class='pie-meta'>{count} | {fraction:.1%}</span>"
            "</div>"
        )
        start_angle = end_angle

    markup = (
        "<section class='panel'>"
        f"<h3>{escape(title)}</h3>"
        "<div class='pie-layout'>"
        "<div class='pie-card'>"
        "<svg viewBox='0 0 240 240' width='100%' role='img' aria-label='Defect distribution pie chart'>"
        + "".join(slices)
        + "<circle cx='120' cy='120' r='48' fill='#fffaf2'></circle>"
        + f"<text x='120' y='110' text-anchor='middle' font-size='14' fill='#5f6b6d'>Wafers</text>"
        + f"<text x='120' y='132' text-anchor='middle' font-size='26' font-weight='700' fill='#152427'>{total}</text>"
        + "</svg></div>"
        + f"<div class='pie-legend'>{''.join(legend_rows)}</div>"
        + "</div></section>"
    )
    st.markdown(markup, unsafe_allow_html=True)