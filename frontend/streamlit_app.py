"""
Personalized Networking Assistant — Main Streamlit Application.

Premium dark/light themed interface with:
  - Profile Bio & Event Description inputs
  - Generate Starters workflow
  - Fact-Check panel
  - Inline history and feedback
  - Navigation to Dashboard and History pages
"""

from typing import Any, Dict, List, Optional

import requests
import streamlit as st

# ─── Page Config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="Networking Assistant",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com/your-org/networking-assistant",
        "Report a bug": "https://github.com/your-org/networking-assistant/issues",
        "About": "# Personalized Networking Assistant\nAI-powered conversation starter generator.",
    },
)

# ─── Constants ───────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"
REQUEST_TIMEOUT = 60

# ─── CSS Injection ───────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* ── Gradient header ── */
  .hero-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    padding: 2.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.35);
  }
  .hero-header h1 {
    color: white;
    font-size: 2.4rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .hero-header p {
    color: rgba(255,255,255,0.88);
    font-size: 1.05rem;
    margin: 0.5rem 0 0;
    font-weight: 300;
  }

  /* ── Starter cards ── */
  .starter-card {
    background: linear-gradient(135deg, #1e1e2e 0%, #16213e 100%);
    border: 1px solid rgba(102, 126, 234, 0.3);
    border-left: 4px solid #667eea;
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin: 0.6rem 0;
    color: #e2e8f0;
    font-size: 0.97rem;
    line-height: 1.6;
    transition: border-color 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  }
  .starter-card:hover {
    border-left-color: #f093fb;
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25);
  }
  .starter-number {
    color: #667eea;
    font-weight: 700;
    font-size: 0.85rem;
    margin-bottom: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  /* ── Fact-check cards ── */
  .fact-card-verified {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
    border: 1px solid rgba(72, 199, 142, 0.4);
    border-left: 4px solid #48c78e;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin: 0.6rem 0;
    color: #e2e8f0;
  }
  .fact-card-not-found {
    background: linear-gradient(135deg, #2d1515 0%, #16213e 100%);
    border: 1px solid rgba(255, 107, 107, 0.35);
    border-left: 4px solid #ff6b6b;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin: 0.6rem 0;
    color: #e2e8f0;
  }

  /* ── Theme badge ── */
  .theme-badge {
    display: inline-block;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 0.2rem;
    letter-spacing: 0.3px;
  }

  /* ── Section header ── */
  .section-header {
    font-size: 1.15rem;
    font-weight: 600;
    color: #e2e8f0;
    border-bottom: 2px solid #667eea;
    padding-bottom: 0.4rem;
    margin: 1.5rem 0 1rem;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0e17 0%, #1a1a2e 100%) !important;
  }

  /* ── Button style ── */
  .stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.5rem !important;
    transition: opacity 0.2s, transform 0.15s !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
  }
  .stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
  }

  /* ── Success/error callouts ── */
  .success-banner {
    background: linear-gradient(135deg, rgba(72, 199, 142, 0.15), rgba(72, 199, 142, 0.05));
    border: 1px solid rgba(72, 199, 142, 0.4);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    color: #48c78e;
    font-weight: 500;
    margin: 1rem 0;
  }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ─── Session State Initialisation ────────────────────────────────────────────
def init_session_state() -> None:
    """Initialise Streamlit session state defaults."""
    defaults: Dict[str, Any] = {
        "current_session_id": None,
        "analysis_result": None,
        "starters": [],
        "themes_used": [],
        "fact_check_results": [],
        "history_items": [],
        "feedback_submitted": set(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ─── API Helpers ─────────────────────────────────────────────────────────────
def api_post(endpoint: str, payload: dict) -> Optional[Dict]:
    """POST to the FastAPI backend and return parsed JSON or None on error."""
    try:
        resp = requests.post(
            f"{API_BASE}{endpoint}", json=payload, timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error(
            "⚠️ Cannot connect to backend. Make sure the FastAPI server is running: "
            "`uvicorn app.main:app --reload`"
        )
        return None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("message", str(e))
        except Exception:
            detail = str(e)
        st.error(f"API Error: {detail}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def api_get(endpoint: str, params: Optional[dict] = None) -> Optional[Dict]:
    """GET from the FastAPI backend and return parsed JSON or None on error."""
    try:
        resp = requests.get(
            f"{API_BASE}{endpoint}", params=params, timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error(
            "⚠️ Cannot connect to backend. Make sure the FastAPI server is running."
        )
        return None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("message", str(e))
        except Exception:
            detail = str(e)
        st.error(f"API Error: {detail}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def check_api_health() -> Optional[Dict]:
    """Check API health directly (separate from api_get to use /health not /api/v1/health)."""
    try:
        resp = requests.get(HEALTH_URL, timeout=3)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


# ─── Sidebar ─────────────────────────────────────────────────────────────────
def render_sidebar() -> Dict[str, Any]:
    """Render sidebar and return collected user profile data."""
    with st.sidebar:
        st.markdown(
            """
            <div style='text-align:center; padding: 1rem 0 0.5rem;'>
              <div style='font-size: 2.8rem; margin-bottom: 0.3rem;'>🤝</div>
              <div style='font-size: 1.1rem; font-weight: 700; color: #667eea;'>
                Networking Assistant
              </div>
              <div style='font-size: 0.75rem; color: #64748b; margin-top: 0.2rem;'>
                AI-Powered Conversation Starters
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown("### 👤 Your Profile")
        user_bio = st.text_area(
            "Professional Bio",
            placeholder=(
                "e.g., Senior software engineer with 8 years in NLP and distributed "
                "systems. Passionate about open-source AI."
            ),
            height=120,
            help="Your bio personalizes the conversation starters generated for you.",
            key="sidebar_bio",
        )

        st.divider()

        st.markdown("### ⚙️ Settings")
        num_starters = st.slider(
            "Number of Starters",
            min_value=1,
            max_value=10,
            value=5,
            help="How many conversation starters to generate.",
            key="num_starters_slider",
        )

        st.divider()

        st.markdown("### 🔗 Quick Links")
        st.markdown("🏠 **[Home](/)** | 📊 **[Dashboard](/dashboard)** | 📜 **[History](/history)**")

        st.divider()

        # API Health status
        health_data = check_api_health()
        if health_data:
            st.success(f"✅ API Online (v{health_data.get('version', '?')})")
            col1, col2 = st.columns(2)
            models = health_data.get("models_loaded", {})
            col1.metric(
                "Classifier",
                "✅" if models.get("zero_shot_classifier") else "⏳",
            )
            col2.metric(
                "Generator",
                "✅" if models.get("text_generator") else "⏳",
            )
        else:
            st.error("❌ API Offline")
            st.caption("Start: `uvicorn app.main:app --reload`")

        return {
            "user_bio": user_bio.strip() or None,
            "num_starters": num_starters,
        }


# ─── Main Content ─────────────────────────────────────────────────────────────
def render_hero() -> None:
    """Render the gradient hero header."""
    st.markdown(
        """
        <div class="hero-header">
          <h1>🤝 Personalized Networking Assistant</h1>
          <p>AI-powered conversation starters tailored to your event &amp; bio — powered by BART &amp; GPT-2</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_input_panel(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Render the event input panel and return form values."""
    st.markdown('<div class="section-header">📋 Event Details</div>', unsafe_allow_html=True)

    event_description = st.text_area(
        "Event Description",
        placeholder=(
            "Describe the networking event you're attending...\n\n"
            "e.g., 'NeurIPS 2024 — A premier machine learning conference bringing "
            "together researchers and practitioners to discuss advances in deep learning, "
            "NLP, computer vision, and reinforcement learning.'"
        ),
        height=150,
        key="event_description_input",
        help="Describe the event in detail for better-targeted conversation starters.",
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        analyze_clicked = st.button(
            "🔍 Analyze Event Themes",
            key="btn_analyze",
            use_container_width=True,
        )
    with col2:
        generate_clicked = st.button(
            "✨ Generate Starters",
            key="btn_generate",
            use_container_width=True,
        )

    return {
        "event_description": event_description,
        "analyze_clicked": analyze_clicked,
        "generate_clicked": generate_clicked,
    }


def render_analysis_result(analysis: Dict) -> None:
    """Render the event theme analysis results."""
    if not analysis:
        return

    st.markdown('<div class="section-header">🎯 Event Themes</div>', unsafe_allow_html=True)

    themes = analysis.get("themes", [])
    top_theme = analysis.get("top_theme", "")

    # Top theme highlight
    if top_theme:
        st.info(f"**Top Theme:** {top_theme.title()} 🏆")

    # All themes as badges
    if themes:
        badge_html = "".join(
            f'<span class="theme-badge">{t["label"].title()} '
            f'({t["score"]*100:.0f}%)</span>'
            for t in themes[:6]
            if isinstance(t, dict) and "label" in t
        )
        st.markdown(f'<div style="margin: 0.5rem 0;">{badge_html}</div>', unsafe_allow_html=True)

        # Bar chart of top themes
        try:
            import pandas as pd  # noqa: PLC0415
            theme_data = [t for t in themes[:8] if isinstance(t, dict) and "label" in t]
            if theme_data:
                df = pd.DataFrame(theme_data).rename(
                    columns={"label": "Theme", "score": "Confidence"}
                )
                df["Theme"] = df["Theme"].str.title()
                st.bar_chart(df.set_index("Theme")["Confidence"], color="#667eea", height=200)
        except Exception:
            pass


def render_starters(starters: List[str], session_id: Optional[str]) -> None:
    """Render generated conversation starters as styled cards with feedback."""
    if not starters:
        return

    st.markdown(
        '<div class="section-header">💬 Conversation Starters</div>',
        unsafe_allow_html=True,
    )

    for i, starter in enumerate(starters):
        card_html = (
            f'<div class="starter-card">'
            f'<div class="starter-number">Starter #{i+1}</div>'
            f"{starter}"
            f"</div>"
        )
        st.markdown(card_html, unsafe_allow_html=True)

    # Download starters as text
    all_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(starters))
    st.download_button(
        label="📋 Download Starters (.txt)",
        data=all_text,
        file_name="conversation_starters.txt",
        mime="text/plain",
        use_container_width=False,
    )

    # Inline feedback
    if session_id and session_id not in st.session_state.feedback_submitted:
        st.markdown(
            '<div class="section-header">⭐ Rate These Starters</div>',
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns([1, 2])
        with col1:
            rating = st.select_slider(
                "Rating",
                options=[1, 2, 3, 4, 5],
                value=4,
                format_func=lambda x: "⭐" * x,
                key="feedback_rating",
            )
        with col2:
            comment = st.text_input(
                "Comment (optional)",
                placeholder="What did you like or dislike?",
                key="feedback_comment",
            )

        if st.button("Submit Feedback", key="btn_feedback"):
            result = api_post(
                "/feedback",
                {
                    "session_id": session_id,
                    "rating": rating,
                    "comment": comment or None,
                },
            )
            if result:
                st.session_state.feedback_submitted.add(session_id)
                st.markdown(
                    '<div class="success-banner">🎉 Thank you for your feedback!</div>',
                    unsafe_allow_html=True,
                )
    elif session_id and session_id in st.session_state.feedback_submitted:
        st.markdown(
            '<div class="success-banner">✅ Feedback already submitted for this session.</div>',
            unsafe_allow_html=True,
        )


def render_fact_check_panel(themes_used: List[str]) -> None:
    """Render the fact-check panel with theme-based queries."""
    st.markdown(
        '<div class="section-header">🔎 Fact Verification</div>',
        unsafe_allow_html=True,
    )

    # Pre-populate with themes but allow custom input
    default_queries = ", ".join(themes_used) if themes_used else ""
    fact_queries_raw = st.text_input(
        "Topics to verify (comma-separated)",
        value=default_queries,
        placeholder="e.g., artificial intelligence, machine learning, GPT",
        key="fact_check_input",
        help="Enter topics from the event to fact-check via Wikipedia.",
    )

    if st.button("🔍 Fact Check", key="btn_fact_check"):
        queries = [q.strip() for q in fact_queries_raw.split(",") if q.strip()]
        if not queries:
            st.warning("Please enter at least one topic to fact-check.")
            return

        with st.spinner("Querying Wikipedia..."):
            # Build list of (key, value) tuples for repeated params
            params = [("query", q) for q in queries]
            try:
                resp = requests.get(
                    f"{API_BASE}/fact-check", params=params, timeout=30
                )
                resp.raise_for_status()
                data = resp.json()
                st.session_state.fact_check_results = data.get("results", [])
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend API.")
                return
            except Exception as e:
                st.error(f"Fact-check error: {e}")
                return

    results = st.session_state.fact_check_results
    if results:
        for result in results:
            if result.get("found"):
                url = result.get("url", "")
                card = (
                    f'<div class="fact-card-verified">'
                    f'<strong>✅ {result["query"].title()}</strong><br/>'
                    f'<span style="color:#94a3b8; font-size:0.85rem;">Confidence: {result["confidence"].upper()}</span><br/>'
                    f'<p style="margin: 0.5rem 0 0.3rem; font-size:0.9rem;">{result.get("summary", "")}</p>'
                    + (f'<a href="{url}" target="_blank" style="color:#667eea; font-size:0.82rem;">📖 Read on Wikipedia →</a>' if url else "")
                    + f"</div>"
                )
            else:
                card = (
                    f'<div class="fact-card-not-found">'
                    f'<strong>❌ {result["query"].title()}</strong><br/>'
                    f'<span style="color:#94a3b8; font-size:0.85rem;">Not found on Wikipedia</span>'
                    f"</div>"
                )
            st.markdown(card, unsafe_allow_html=True)


def render_recent_history() -> None:
    """Render a brief recent sessions panel."""
    st.markdown(
        '<div class="section-header">🕓 Recent Sessions</div>',
        unsafe_allow_html=True,
    )

    data = api_get("/history", params={"page": 1, "page_size": 5})
    if not data or not data.get("items"):
        st.info("No sessions yet. Generate your first starters above!")
        return

    for item in data["items"]:
        event_desc = item.get("event_description", "")
        preview = event_desc[:70] + "..." if len(event_desc) > 70 else event_desc
        with st.expander(f"📌 {preview}", expanded=False):
            cols = st.columns(3)
            themes = item.get("themes", [])
            cols[0].write(f"**Themes:** {', '.join(themes)}" if themes else "**Themes:** —")
            starters = item.get("starters", [])
            cols[1].write(f"**Starters:** {len(starters)}")
            rating = item.get("feedback_rating")
            cols[2].write(f"**Rating:** {'⭐' * rating if rating else '—'}")
            if starters:
                st.write("**Top Starter:**", starters[0])


# ─── Main Layout ─────────────────────────────────────────────────────────────
def main() -> None:
    """Entry point: render the full application layout."""
    profile = render_sidebar()
    render_hero()

    # Two-column layout
    left_col, right_col = st.columns([1.05, 0.95], gap="large")

    with left_col:
        form_data = render_input_panel(profile)
        event_description = form_data["event_description"]

        # ── Analyze event ──────────────────────────────────────────────────
        if form_data["analyze_clicked"]:
            if not event_description or len(event_description.strip()) < 10:
                st.warning("Please enter at least 10 characters for the event description.")
            else:
                with st.spinner("🧠 Analyzing event with BART zero-shot classification..."):
                    result = api_post(
                        "/analyze-event",
                        {
                            "event_description": event_description,
                            "user_bio": profile["user_bio"],
                        },
                    )
                if result:
                    st.session_state.analysis_result = result
                    st.session_state.current_session_id = result.get("session_id")
                    st.success("✅ Event analyzed successfully!")

        # ── Generate starters ──────────────────────────────────────────────
        if form_data["generate_clicked"]:
            if not event_description or len(event_description.strip()) < 10:
                st.warning("Please enter at least 10 characters for the event description.")
            else:
                # Use pre-analyzed themes if available
                pre_themes = None
                if st.session_state.analysis_result:
                    raw_themes = st.session_state.analysis_result.get("themes", [])
                    pre_themes = [
                        t["label"] for t in raw_themes[:3]
                        if isinstance(t, dict) and "label" in t
                    ] or None

                with st.spinner("✨ Generating conversation starters with GPT-2..."):
                    result = api_post(
                        "/generate-conversation",
                        {
                            "event_description": event_description,
                            "user_bio": profile["user_bio"],
                            "num_starters": profile["num_starters"],
                            "themes": pre_themes,
                        },
                    )
                if result:
                    st.session_state.starters = result.get("starters", [])
                    st.session_state.themes_used = result.get("themes_used", [])
                    st.session_state.current_session_id = result.get("session_id")
                    # Synthesize analysis result for display if not yet available
                    if not st.session_state.analysis_result:
                        st.session_state.analysis_result = {
                            "themes": [
                                {"label": t, "score": 0.8}
                                for t in result.get("themes_used", [])
                            ],
                            "top_theme": result.get("themes_used", ["unknown"])[0]
                            if result.get("themes_used")
                            else "unknown",
                        }
                    st.success(f"✅ Generated {len(st.session_state.starters)} starters!")

        # Display analysis result
        if st.session_state.analysis_result:
            render_analysis_result(st.session_state.analysis_result)

    with right_col:
        tab1, tab2, tab3 = st.tabs(
            ["💬 Starters", "🔎 Fact Check", "🕓 History"]
        )

        with tab1:
            if st.session_state.starters:
                render_starters(
                    st.session_state.starters,
                    st.session_state.current_session_id,
                )
            else:
                st.markdown(
                    """
                    <div style='text-align:center; padding: 3rem 1rem; color: #475569;'>
                      <div style='font-size:3rem; margin-bottom:1rem;'>💬</div>
                      <div style='font-size:1rem; font-weight:500;'>
                        No starters yet.<br>Fill in the event details and click
                        <strong>Generate Starters</strong>.
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with tab2:
            render_fact_check_panel(st.session_state.themes_used)

        with tab3:
            render_recent_history()


if __name__ == "__main__":
    main()
