"""
History Browser Page.

Allows users to:
  - Browse paginated session history
  - Search sessions by keyword
  - View full details of each session (starters, themes, feedback)
  - Download full history as JSON or CSV
"""

from typing import Optional

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="History — Networking Assistant",
    page_icon="📜",
    layout="wide",
)

API_BASE = "http://localhost:8000/api/v1"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .page-header {
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      padding: 2rem;
      border-radius: 14px;
      margin-bottom: 2rem;
      border-left: 5px solid #f093fb;
    }
    .page-header h2 { color: #e2e8f0; font-size: 1.8rem; margin: 0; }
    .page-header p  { color: #94a3b8; margin: 0.3rem 0 0; font-size: 0.95rem; }
    .history-card {
      background: linear-gradient(135deg, #1e1e2e, #16213e);
      border: 1px solid rgba(240,147,251,0.2);
      border-radius: 12px;
      padding: 1.2rem 1.5rem;
      margin: 0.7rem 0;
    }
    .history-card h4 { color: #e2e8f0; margin: 0 0 0.5rem; }
    .badge {
      display: inline-block;
      background: rgba(102,126,234,0.2);
      border: 1px solid rgba(102,126,234,0.4);
      color: #a5b4fc;
      border-radius: 16px;
      padding: 0.15rem 0.6rem;
      font-size: 0.76rem;
      margin: 0.1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def fetch_history(
    page: int, page_size: int, search: Optional[str] = None
) -> dict:
    """Fetch a page of history from the backend."""
    params = {"page": page, "page_size": page_size}
    if search:
        params["search"] = search
    try:
        resp = requests.get(f"{API_BASE}/history", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}


def main() -> None:
    """Render the history browser page."""
    st.markdown(
        """
        <div class="page-header">
          <h2>📜 Session History</h2>
          <p>Browse, search, and export your past networking sessions</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Controls ──────────────────────────────────────────────────────────────
    col_search, col_size = st.columns([3, 1])
    with col_search:
        search = st.text_input(
            "🔍 Search sessions",
            placeholder="Search by event description or theme...",
            key="history_search",
        )
    with col_size:
        page_size = st.selectbox(
            "Items per page", options=[5, 10, 20, 50], index=1
        )

    # Pagination state
    if "history_page" not in st.session_state:
        st.session_state.history_page = 1

    data = fetch_history(
        page=st.session_state.history_page,
        page_size=page_size,
        search=search or None,
    )
    items = data.get("items", [])
    total = data.get("total", 0)
    total_pages = max(1, (total + page_size - 1) // page_size)

    st.caption(f"Showing {len(items)} of {total} sessions | Page {st.session_state.history_page} of {total_pages}")

    # ── History Items ─────────────────────────────────────────────────────────
    if not items:
        st.info("No sessions found. Start by generating conversation starters on the Home page!")
    else:
        for item in items:
            themes_html = "".join(
                f'<span class="badge">{t.title()}</span>'
                for t in item.get("themes", [])[:5]
            )
            rating = item.get("feedback_rating")
            rating_str = "⭐" * rating if rating else "Not rated"
            timestamp = item.get("timestamp", "")[:16].replace("T", " ")

            with st.expander(
                f"📌 {item['event_description'][:75]}... — {timestamp}",
                expanded=False,
            ):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("**Event Description**")
                    st.write(item.get("event_description", ""))

                    if item.get("user_bio"):
                        st.markdown("**Your Bio**")
                        st.write(item["user_bio"])

                    st.markdown("**Themes**")
                    if item.get("themes"):
                        st.markdown(
                            f'<div>{themes_html}</div>', unsafe_allow_html=True
                        )
                    else:
                        st.write("—")

                with col2:
                    st.markdown(f"**Session ID**  \n`{item['session_id'][:16]}...`")
                    st.markdown(f"**Date**  \n{timestamp}")
                    st.markdown(f"**Rating**  \n{rating_str}")
                    if item.get("feedback_comment"):
                        st.markdown(f"**Comment**  \n_{item['feedback_comment']}_")

                starters = item.get("starters", [])
                if starters:
                    st.markdown("**Conversation Starters**")
                    for i, s in enumerate(starters):
                        st.markdown(f"**{i+1}.** {s}")

    # ── Pagination Controls ───────────────────────────────────────────────────
    st.markdown("---")
    nav_cols = st.columns([1, 2, 1])
    with nav_cols[0]:
        if st.button("← Previous", disabled=st.session_state.history_page <= 1):
            st.session_state.history_page -= 1
            st.rerun()
    with nav_cols[1]:
        st.markdown(
            f"<div style='text-align:center; color:#94a3b8; padding:0.4rem;'>"
            f"Page {st.session_state.history_page} of {total_pages}"
            f"</div>",
            unsafe_allow_html=True,
        )
    with nav_cols[2]:
        if st.button(
            "Next →",
            disabled=st.session_state.history_page >= total_pages,
        ):
            st.session_state.history_page += 1
            st.rerun()

    # ── Export Buttons ────────────────────────────────────────────────────────
    st.markdown("### ⬇️ Export Full History")
    export_cols = st.columns(2)

    with export_cols[0]:
        try:
            json_resp = requests.get(
                f"{API_BASE}/history/export/json", timeout=30
            )
            if json_resp.status_code == 200:
                st.download_button(
                    label="📥 Download JSON",
                    data=json_resp.content,
                    file_name="networking_history.json",
                    mime="application/json",
                    use_container_width=True,
                )
        except Exception:
            st.warning("JSON export unavailable.")

    with export_cols[1]:
        try:
            csv_resp = requests.get(
                f"{API_BASE}/history/export/csv", timeout=30
            )
            if csv_resp.status_code == 200:
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_resp.content,
                    file_name="networking_history.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except Exception:
            st.warning("CSV export unavailable.")


if __name__ == "__main__":
    main()
