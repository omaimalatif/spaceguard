"""Reusable Plotly figure builders for the dashboard, theme-aware (dark/light)."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

FLARE_COLOR_MAP = {"A": "#2ecc71", "B": "#2ecc71", "C": "#f1c40f", "M": "#e67e22", "X": "#e74c3c", "?": "#95a5a6"}


def _template(theme: str) -> str:
    return "plotly_dark" if theme == "dark" else "plotly_white"


def build_event_count_chart(flares: pd.DataFrame, cmes: pd.DataFrame, storms: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """Overview bar chart comparing total counts across the three event types."""
    data = {
        "Event Type": ["Solar Flares", "CMEs", "Geomagnetic Storms"],
        "Count": [len(flares), len(cmes), len(storms)],
    }
    fig = px.bar(data, x="Event Type", y="Count", title="Event counts in selected window", template=_template(theme))
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


def build_flare_class_chart(flares: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """Distribution of solar flares by class letter (A/B/C/M/X) — severity, not just count."""
    if flares.empty or "flareClassLetter" not in flares.columns:
        return go.Figure().update_layout(title="Solar flare class distribution: no data", template=_template(theme))

    order = ["A", "B", "C", "M", "X"]
    if (flares["flareClassLetter"] == "?").any():
        order.append("?")  # keep unparsable classes visible so chart total == metric total
    counts = flares["flareClassLetter"].value_counts().reindex(order).fillna(0).reset_index()
    counts.columns = ["Class", "Count"]
    fig = px.bar(
        counts, x="Class", y="Count", title="Solar flares by class (severity)",
        color="Class", color_discrete_map=FLARE_COLOR_MAP, template=_template(theme),
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
    return fig


def build_cme_speed_chart(cmes: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """CME speed over time — speed is the meaningful severity signal, not raw count."""
    if cmes.empty or "speedKmS" not in cmes.columns or "startTime" not in cmes.columns:
        return go.Figure().update_layout(title="CME speed over time: no data", template=_template(theme))

    plot_df = cmes.copy()
    plot_df["startTime"] = pd.to_datetime(plot_df["startTime"], errors="coerce")
    plot_df = plot_df.dropna(subset=["startTime", "speedKmS"])
    if plot_df.empty:
        return go.Figure().update_layout(title="CME speed over time: no data", template=_template(theme))

    fig = px.scatter(
        plot_df, x="startTime", y="speedKmS", title="CME speed over time (km/s)",
        template=_template(theme),
    )
    fig.add_hline(y=1000, line_dash="dot", line_color="#e74c3c", annotation_text="High (1000+ km/s)")
    fig.add_hline(y=500, line_dash="dot", line_color="#f1c40f", annotation_text="Moderate (500+ km/s)")
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


def build_kp_index_chart(storms: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """Max Kp-index per geomagnetic storm — the standard severity scale (0-9)."""
    if storms.empty or "maxKpIndex" not in storms.columns or "startTime" not in storms.columns:
        return go.Figure().update_layout(title="Geomagnetic Kp-index: no data", template=_template(theme))

    plot_df = storms.copy()
    plot_df["startTime"] = pd.to_datetime(plot_df["startTime"], errors="coerce")
    plot_df = plot_df.dropna(subset=["startTime", "maxKpIndex"])
    if plot_df.empty:
        return go.Figure().update_layout(title="Geomagnetic Kp-index: no data", template=_template(theme))

    fig = px.bar(
        plot_df, x="startTime", y="maxKpIndex", title="Max Kp-index per storm (0-9 scale)",
        template=_template(theme),
    )
    fig.add_hline(y=7, line_dash="dot", line_color="#e74c3c", annotation_text="High (Kp 7+)")
    fig.add_hline(y=5, line_dash="dot", line_color="#f1c40f", annotation_text="Moderate (Kp 5+)")
    fig.update_yaxes(range=[0, 9])
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), bargap=0.4)
    return fig
