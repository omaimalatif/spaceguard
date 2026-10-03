"""
SpaceGuard — Real-Time Space Weather Monitoring Dashboard
Entry point: layout and wiring only. All logic lives in src/.
"""

from datetime import date, timedelta

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.data.donki_client import get_geomagnetic_storms, get_cme_events, get_solar_flares
from src.data.storage import init_db, load_events, save_events
from src.processing.transform import clean_cmes, clean_flares, clean_storms
from src.risk.rules import compute_risk_level
from src.viz.charts import (
    build_cme_speed_chart,
    build_event_count_chart,
    build_flare_class_chart,
    build_kp_index_chart,
)

st.set_page_config(
    page_title="SpaceGuard — Space Weather Monitor",
    page_icon="",
    layout="wide",
)

RISK_COLORS = {"Low": "#2ecc71", "Moderate": "#f1c40f", "High": "#e74c3c", "Unknown": "#95a5a6"}

DARK_CSS = """
<style>
.stApp { background-color: #0e1117; color: #fafafa; }
.risk-badge { display:inline-block; padding:0.4rem 1.2rem; border-radius:999px; font-weight:700; font-size:1.1rem; color:white; }
.last-updated { color:#9a9a9a; font-size:0.85rem; }
.methodology { color:#c9c9c9; }

/* --- Mobile responsiveness fixes --- */
@media (max-width: 640px) {
    /* Stack side-by-side columns vertically on small screens */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    /* Shrink title and tighten spacing */
    h1 { font-size: 1.6rem !important; }
    .risk-badge { font-size: 0.95rem !important; padding: 0.35rem 0.9rem !important; }
    /* Let Plotly charts and tables scroll horizontally instead of overflowing */
    .stPlotlyChart, .stDataFrame { overflow-x: auto !important; }
}
</style>
"""


@st.cache_data(ttl=900, show_spinner="Fetching NASA DONKI data...")
def fetch_clean_events(start_date: str, end_date: str):
    """Fetch + clean all three feeds. Cached 15 min per window so slider/tab
    interactions don't re-hit the API (DONKI rate-limits, esp. DEMO_KEY).
    Exceptions are not cached, so a failed call is retried on the next run."""
    return (
        clean_flares(get_solar_flares(start_date, end_date)),
        clean_cmes(get_cme_events(start_date, end_date)),
        clean_storms(get_geomagnetic_storms(start_date, end_date)),
    )


def render_risk_badge(level: str) -> None:
    color = RISK_COLORS.get(level, RISK_COLORS["Unknown"])
    st.markdown(
        f'<span class="risk-badge" style="background-color:{color};">Current Risk: {level}</span>',
        unsafe_allow_html=True,
    )


def main() -> None:
    init_db()
    st.markdown(DARK_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.header("Filters")
        days_back = st.slider("Look back (days)", min_value=1, max_value=30, value=7)
        start_date = (date.today() - timedelta(days=days_back)).isoformat()
        end_date = date.today().isoformat()

        st.markdown("---")
        with st.expander("About & Methodology"):
            st.markdown(
                "**Data source:** NASA DONKI.\n\n"
                "**Risk levels** are based on the *strongest* event in the window, not raw counts:\n"
                "- Solar flares: X-class → High, M-class → Moderate\n"
                "- CMEs: 1000+ km/s → High, 500+ km/s → Moderate\n"
                "- Geomagnetic storms: Kp 7+ → High, Kp 5+ → Moderate\n\n"
                "This is a monitoring/visualization prototype, not an official forecasting service."
            )

    st.title("SpaceGuard")
    st.caption("Real-time space weather monitoring — solar flares, CMEs, and geomagnetic activity.")

    # --- Fetch, clean, cache (with graceful fallback on API failure) ---
    try:
        flares, cmes, storms = fetch_clean_events(start_date, end_date)
        save_events(flares, "flare")
        save_events(cmes, "cme")
        save_events(storms, "storm")
        data_source_note = "live"
    except Exception as exc:  # noqa: BLE001 — friendly fallback, not a stack trace
        st.warning(f"Live data fetch failed ({exc}). Showing last cached data instead.")
        flares = load_events("flare")
        cmes = load_events("cme")
        storms = load_events("storm")
        data_source_note = "cached (last successful fetch; may not match the selected window)"

    no_data = flares.empty and cmes.empty and storms.empty
    if data_source_note != "live" and no_data:
        # API failed AND nothing cached: don't claim "Low" on zero information.
        risk_level = "Unknown"
    else:
        risk_level = compute_risk_level(flares, cmes, storms)
    theme = "dark"

    col1, col2 = st.columns([1, 3])
    with col1:
        render_risk_badge(risk_level)
    with col2:
        st.markdown(
            f'<span class="last-updated">Data: {data_source_note} · Window: {start_date} → {end_date}</span>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Solar Flares", "CMEs", "Geomagnetic Storms"])

    with tab1:
        m1, m2, m3 = st.columns(3)
        m1.metric("Solar Flares", len(flares))
        m2.metric("CMEs", len(cmes))
        m3.metric("Geomagnetic Storms", len(storms))
        st.plotly_chart(build_event_count_chart(flares, cmes, storms, theme), use_container_width=True)

    with tab2:
        st.subheader("Solar Flares")
        if flares.empty:
            st.info("No solar flares recorded in this window.")
        else:
            st.plotly_chart(build_flare_class_chart(flares, theme), use_container_width=True)
            st.dataframe(
                flares.rename(columns={
                    "classType": "Class", "flareClassLetter": "Letter", "flareMagnitude": "Magnitude",
                    "beginTime": "Begin", "peakTime": "Peak", "endTime": "End", "sourceLocation": "Source Location",
                }),
                use_container_width=True,
            )

    with tab3:
        st.subheader("Coronal Mass Ejections (CMEs)")
        if cmes.empty:
            st.info("No CMEs recorded in this window.")
        else:
            st.plotly_chart(build_cme_speed_chart(cmes, theme), use_container_width=True)
            st.dataframe(
                cmes.rename(columns={"startTime": "Start", "speedKmS": "Speed (km/s)",
                                      "sourceLocation": "Source Location", "note": "Note"}),
                use_container_width=True,
            )

    with tab4:
        st.subheader("Geomagnetic Storms")
        if storms.empty:
            st.info("No geomagnetic storms recorded in this window.")
        else:
            st.plotly_chart(build_kp_index_chart(storms, theme), use_container_width=True)
            st.dataframe(
                storms.rename(columns={"startTime": "Start", "maxKpIndex": "Max Kp-index"}),
                use_container_width=True,
            )


if __name__ == "__main__":
    main()