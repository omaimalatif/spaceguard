"""Reusable Plotly figure builders for the dashboard."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _find_date_column(df: pd.DataFrame) -> str | None:
    """DONKI endpoints use different date field names per event type — find the first that fits."""
    candidates = ["beginTime", "startTime", "peakTime", "eventTime", "time21_5"]
    for col in candidates:
        if col in df.columns:
            return col
    return None


def build_timeline_chart(df: pd.DataFrame, label: str) -> go.Figure:
    """A simple event-count-over-time timeline for one event type."""
    date_col = _find_date_column(df)
    if date_col is None:
        return go.Figure().update_layout(title=f"{label}: no timestamp field found")

    plot_df = df.copy()
    plot_df[date_col] = pd.to_datetime(plot_df[date_col], errors="coerce")
    plot_df = plot_df.dropna(subset=[date_col])
    counts = plot_df.groupby(plot_df[date_col].dt.date).size().reset_index(name="count")

    fig = px.bar(counts, x=date_col, y="count", title=f"{label} over time")
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


def build_event_count_chart(flares: pd.DataFrame, cmes: pd.DataFrame, storms: pd.DataFrame) -> go.Figure:
    """Overview bar chart comparing total counts across the three event types."""
    data = {
        "Event Type": ["Solar Flares", "CMEs", "Geomagnetic Storms"],
        "Count": [len(flares), len(cmes), len(storms)],
    }
    fig = px.bar(data, x="Event Type", y="Count", title="Event counts in selected window")
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig
