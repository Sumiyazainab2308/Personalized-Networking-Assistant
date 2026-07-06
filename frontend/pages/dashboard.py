"""
Dashboard Page — Analytics & Visualizations.

Provides aggregate analytics over the interaction history:
  - Total sessions, average rating
  - Theme distribution bar chart
  - Sessions per day time series
  - Rating distribution pie chart
"""

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Dashboard — Networking Assistant",
    page_icon="📊",
    layout="wide",
)

API_BASE = "http://localhost:8000/api/v1"

# Shared CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .page-header {
      background: linear-gradient(135deg, #1e3a5f 0%, #0f3460 50%, #16213e 100%);
      padding: 2rem;
      border-radius: 14px;
      margin-bottom: 2rem;
      border-left: 5px solid #667eea;
    }
    .page-header h2 { color: #e2e8f0; font-size: 1.8rem; margin: 0; }
    .page-header p  { color: #94a3b8; margin: 0.3rem 0 0; font-size: 0.95rem; }
    .metric-card {
      background: linear-gradient(135deg, #1e1e2e, #16213e);
      border: 1px solid rgba(102,126,234,0.2);
      border-radius: 12px;
      padding: 1.2rem;
      text-align: center;
    }
    .metric-val { font-size: 2rem; font-weight: 700; color: #667eea; }
    .metric-lbl { font-size: 0.82rem; color: #94a3b8; font-weight: 500; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=30)
def fetch_analytics() -> dict:
    """Fetch analytics data from the backend (cached for 30 seconds)."""
    try:
        resp = requests.get(f"{API_BASE}/history/analytics", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


def main() -> None:
    """Render the analytics dashboard page."""
    st.markdown(
        """
        <div class="page-header">
          <h2>📊 Analytics Dashboard</h2>
          <p>Aggregate insights from all your networking sessions</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Refresh button
    col_refresh, _ = st.columns([1, 5])
    if col_refresh.button("🔄 Refresh", key="refresh_analytics"):
        st.cache_data.clear()

    data = fetch_analytics()

    if not data:
        st.warning(
            "Could not load analytics. Make sure the FastAPI backend is running."
        )
        return

    # ── Key Metrics ──────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-val">{data.get("total_sessions", 0)}</div>'
            f'<div class="metric-lbl">Total Sessions</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with m2:
        avg = data.get("avg_rating", 0)
        stars = "⭐" * round(avg) if avg > 0 else "—"
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-val">{avg:.1f}</div>'
            f'<div class="metric-lbl">Avg Rating {stars}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-val">{data.get("rated_sessions", 0)}</div>'
            f'<div class="metric-lbl">Rated Sessions</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with m4:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-val">{data.get("unrated_sessions", 0)}</div>'
            f'<div class="metric-lbl">Unrated Sessions</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Theme Distribution ────────────────────────────────────────────────────
    theme_counts: dict = data.get("theme_counts", {})
    sessions_per_day: dict = data.get("sessions_per_day", {})

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown("#### 🏷️ Top Event Themes")
        if theme_counts:
            df_themes = pd.DataFrame(
                list(theme_counts.items()), columns=["Theme", "Count"]
            ).sort_values("Count", ascending=False)
            df_themes["Theme"] = df_themes["Theme"].str.title()
            st.bar_chart(df_themes.set_index("Theme")["Count"], color="#764ba2")
        else:
            st.info("No theme data yet.")

    with chart_right:
        st.markdown("#### 📅 Sessions Over Time")
        if sessions_per_day:
            df_days = pd.DataFrame(
                list(sessions_per_day.items()), columns=["Date", "Sessions"]
            )
            df_days["Date"] = pd.to_datetime(df_days["Date"])
            df_days = df_days.sort_values("Date")
            st.line_chart(df_days.set_index("Date")["Sessions"], color="#48c78e")
        else:
            st.info("No session time-series data yet.")

    # ── Recent Activity Table ─────────────────────────────────────────────────
    st.markdown("#### 📋 Recent Activity")
    try:
        hist_resp = requests.get(
            f"{API_BASE}/history", params={"page": 1, "page_size": 10}, timeout=10
        )
        hist_resp.raise_for_status()
        hist_data = hist_resp.json()
        items = hist_data.get("items", [])
        if items:
            rows = []
            for item in items:
                rows.append(
                    {
                        "Session ID": item["session_id"][:8] + "...",
                        "Event": item["event_description"][:60] + "...",
                        "Themes": ", ".join(item.get("themes", [])[:3]),
                        "Starters": len(item.get("starters", [])),
                        "Rating": "⭐" * item["feedback_rating"]
                        if item.get("feedback_rating")
                        else "—",
                        "Date": item["timestamp"][:10],
                    }
                )
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No sessions recorded yet.")
    except Exception as e:
        st.warning(f"Could not load recent activity: {e}")

    # ── Download Buttons ──────────────────────────────────────────────────────
    st.markdown("#### ⬇️ Export Data")
    dl_col1, dl_col2, _ = st.columns([1, 1, 4])
    with dl_col1:
        if st.button("📥 Download JSON", key="dl_json"):
            try:
                export_resp = requests.get(
                    f"{API_BASE}/history/export/json", timeout=30
                )
                export_resp.raise_for_status()
                st.download_button(
                    label="💾 Save JSON",
                    data=export_resp.content,
                    file_name="networking_history.json",
                    mime="application/json",
                )
            except Exception as e:
                st.error(f"Export failed: {e}")
    with dl_col2:
        if st.button("📥 Download CSV", key="dl_csv"):
            try:
                export_resp = requests.get(
                    f"{API_BASE}/history/export/csv", timeout=30
                )
                export_resp.raise_for_status()
                st.download_button(
                    label="💾 Save CSV",
                    data=export_resp.content,
                    file_name="networking_history.csv",
                    mime="text/csv",
                )
            except Exception as e:
                st.error(f"Export failed: {e}")


if __name__ == "__main__":
    main()
