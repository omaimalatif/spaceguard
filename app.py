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
from src.processing.transform import clean_events
from src.risk.rules import compute_risk_level
from src.viz.charts import build_event_count_chart, build_timeline_chart

st.set_page_config(
    page_title="SpaceGuard — Space Weather Monitor",
    page_icon="🛰️",
    layout="wide",
)

RISK_COLORS = {"Low": "#2ecc71", "Moderate": "#f1c40f", "High": "#e74c3c", "Unknown": "#95a5a6"}


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .risk-badge {
            display: inline-block;
            padding: 0.4rem 1.2rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 1.1rem;
            color: white;
        }
        .last-updated {
            color: #888;
            font-size: 0.85rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_risk_badge(level: str) -> None:
    color = RISK_COLORS.get(level, RISK_COLORS["Unknown"])
    st.markdown(
        f'<span class="risk-badge" style="background-color:{color};">Current Risk: {level}</span>',
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_css()
    init_db()

    st.title("🛰️ SpaceGuard")
    st.caption("Real-time space weather monitoring — solar flares, CMEs, and geomagnetic activity.")

    with st.sidebar:
        st.header("Filters")
        days_back = st.slider("Look back (days)", min_value=1, max_value=30, value=7)
        start_date = (date.today() - timedelta(days=days_back)).isoformat()
        end_date = date.today().isoformat()
        st.markdown("---")
        st.markdown(
            "**About**\n\n"
            "Data source: NASA DONKI. This dashboard shows monitoring information only — "
            "it is a student/internship prototype, not an official forecasting service."
        )

    # --- Fetch (with graceful fallback to cached/local data on API failure) ---
    try:
        flares = clean_events(get_solar_flares(start_date, end_date))
        cmes = clean_events(get_cme_events(start_date, end_date))
        storms = clean_events(get_geomagnetic_storms(start_date, end_date))
        save_events(flares, "flare")
        save_events(cmes, "cme")
        save_events(storms, "storm")
        data_source_note = "live"
    except Exception as exc:  # noqa: BLE001 — surface a friendly fallback, not a stack trace
        st.warning(f"Live data fetch failed ({exc}). Showing last cached data instead.")
        flares = load_events("flare")
        cmes = load_events("cme")
        storms = load_events("storm")
        data_source_note = "cached"

    risk_level = compute_risk_level(flares, cmes, storms)

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
        st.plotly_chart(
            build_event_count_chart(flares, cmes, storms), use_container_width=True
        )

    with tab2:
        st.subheader("Solar Flares")
        if flares.empty:
            st.info("No solar flares recorded in this window.")
        else:
            st.plotly_chart(build_timeline_chart(flares, "Solar Flares"), use_container_width=True)
            st.dataframe(flares, use_container_width=True)

    with tab3:
        st.subheader("Coronal Mass Ejections (CMEs)")
        if cmes.empty:
            st.info("No CMEs recorded in this window.")
        else:
            st.plotly_chart(build_timeline_chart(cmes, "CMEs"), use_container_width=True)
            st.dataframe(cmes, use_container_width=True)

    with tab4:
        st.subheader("Geomagnetic Storms")
        if storms.empty:
            st.info("No geomagnetic storms recorded in this window.")
        else:
            st.plotly_chart(build_timeline_chart(storms, "Geomagnetic Storms"), use_container_width=True)
            st.dataframe(storms, use_container_width=True)


if __name__ == "__main__":
    main()
