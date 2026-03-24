"""
Agent Memory Layer — Dashboard

Streamlit UI that connects to the always-on memory agent.
Visualizes memories, runs queries, and triggers operations.

Usage:
    # First start the agent:
    python agent.py

    # Then start the dashboard:
    streamlit run dashboard.py
"""

import json
import time

import requests
import streamlit as st

AGENT_URL = "http://localhost:8888"

UPLOAD_EXTENSIONS = [
    "txt", "md", "json", "csv", "log", "xml", "yaml", "yml",
    "png", "jpg", "jpeg", "gif", "webp", "bmp", "svg",
    "mp3", "wav", "ogg", "flac", "m4a", "aac",
    "mp4", "webm", "mov", "avi", "mkv",
    "pdf",
]


def api_get(path: str) -> dict | None:
    try:
        r = requests.get(f"{AGENT_URL}{path}", timeout=30)
        if not r.ok:
            # Try to surface any JSON error body, otherwise raw text
            if r.headers.get("Content-Type", "").startswith("application/json"):
                try:
                    err = r.json()
                except Exception:
                    err = r.text[:500]
            else:
                err = r.text[:500]
            st.error(f"Agent error ({r.status_code}): {err}")
            return None
        if r.headers.get("Content-Type", "").startswith("application/json"):
            return r.json()
        # Fallback: show raw text if not JSON
        st.error(f"Unexpected response from agent: {r.text[:500]}")
        return None
    except Exception as e:
        st.error(f"Agent not reachable: {e}")
        return None


def api_post(path: str, data: dict) -> dict | None:
    try:
        r = requests.post(f"{AGENT_URL}{path}", json=data, timeout=60)
        if not r.ok:
            # Try to surface any JSON error body, otherwise raw text
            if r.headers.get("Content-Type", "").startswith("application/json"):
                try:
                    err = r.json()
                except Exception:
                    err = r.text[:500]
            else:
                err = r.text[:500]
            st.error(f"Agent error ({r.status_code}): {err}")
            return None
        if r.headers.get("Content-Type", "").startswith("application/json"):
            return r.json()
        # Fallback: show raw text if not JSON
        st.error(f"Unexpected response from agent: {r.text[:500]}")
        return None
    except Exception as e:
        st.error(f"Agent not reachable: {e}")
        return None


def api_post_multipart(path: str, data: dict, files: dict) -> dict | None:
    """POST helper for multipart form-data (used for text + file queries)."""
    try:
        r = requests.post(f"{AGENT_URL}{path}", data=data, files=files, timeout=60)
        if not r.ok:
            # Try to surface any JSON error body, otherwise raw text
            if r.headers.get("Content-Type", "").startswith("application/json"):
                try:
                    err = r.json()
                except Exception:
                    err = r.text[:500]
            else:
                err = r.text[:500]
            st.error(f"Agent error ({r.status_code}): {err}")
            return None
        if r.headers.get("Content-Type", "").startswith("application/json"):
            return r.json()
        # Fallback: show raw text if not JSON
        st.error(f"Unexpected response from agent: {r.text[:500]}")
        return None
    except Exception as e:
        st.error(f"Agent not reachable: {e}")
        return None


def render_memory_card(m: dict):
    entities = m.get("entities", [])
    topics = m.get("topics", [])
    connections = m.get("connections", [])
    importance = m.get("importance", 0.5)

    border_color = "#7c3aed" if importance >= 0.7 else "#a855f7" if importance >= 0.4 else "#9ca3af"

    st.markdown(
        f"""<div style="border-left: 3px solid {border_color}; padding: 8px 16px;
        margin: 8px 0; background: #fdfcff; border-radius: 0 8px 8px 0; border: 1px solid rgba(148, 163, 184, 0.4);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="color: #111827;">Memory #{m['id']}</strong>
            <span style="font-size: 11px; color: #6b7280;">{m.get('created_at', '')[:16]}
            {' | ' + m.get('source', '') if m.get('source') else ''}</span>
        </div>
        <p style="color: #374151; margin: 8px 0; font-size: 14px;">{m['summary']}</p>
        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            {''.join(f'<span style="background: rgba(196,181,253,0.35); color: #5b21b6; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{t}</span>' for t in topics)}
            {''.join(f'<span style="background: rgba(191,219,254,0.5); color: #1d4ed8; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{e}</span>' for e in entities[:5])}
        </div>
        {'<div style="margin-top: 6px; font-size: 11px; color: #6b7280;">🔗 ' + str(len(connections)) + ' connections</div>' if connections else ''}
        </div>""",
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="Addressing the Challenges of GenAI", layout="wide", initial_sidebar_state="expanded")

    st.markdown(
        """<style>
        /* Overall app background: light purple gradient */
        .stApp {
            background: linear-gradient(135deg, #f9f5ff 0%, #f5e9ff 40%, #f7f3ff 100%);
        }
        /* Hide default Streamlit top banner and toolbar */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stToolbar"] {
            display: none !important;
        }
        .stMarkdown { color: #111827; }

        /* Tabs: non-selected = black, selected = purple */
        div[role="tablist"] button[role="tab"] {
            color: #111827 !important;
        }
        div[role="tablist"] button[role="tab"][aria-selected="true"] {
            color: #7c3aed !important;
            font-weight: 600;
        }

        /* Inputs: high-contrast boxes + visible caret + clear selection */
        .stTextInput > div > div > input {
            background: #ffffff;
            color: #111827;
            border: 1px solid #8b5cf6;
            border-radius: 8px;
            caret-color: #111827;
        }
        .stTextInput > div > div > input::selection {
            background: #4c1d95;  /* dark purple highlight */
            color: #f9fafb;
        }
        .stTextArea > div > div > textarea {
            background: #ffffff;
            color: #111827;
            border: 1px solid #8b5cf6;
            border-radius: 8px;
            caret-color: #111827;
        }
        .stTextArea > div > div > textarea::selection {
            background: #4c1d95;
            color: #f9fafb;
        }

        /* File uploader: blue background + white text for strong contrast */
        [data-testid="stFileUploader"] > div:first-child,
        [data-testid="stFileUploader"] > div:first-child > div,
        [data-testid="stFileUploaderDropzone"],
        [data-testid="stFileUploaderDropzoneInput"] ~ div,
        section[data-testid="stFileUploader"] > label + div {
            background: #2563eb !important;  /* blue-600, matches buttons */
            background-color: #2563eb !important;
            border-color: #1d4ed8 !important;
            border-radius: 8px;
        }
        [data-testid="stFileUploader"] .uploadedFileName,
        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploaderDropzone"] span,
        [data-testid="stFileUploaderDropzone"] p,
        [data-testid="stFileUploaderDropzone"] small {
            color: #f9fafb !important;
        }
        [data-testid="stFileUploaderDropzone"] svg {
            fill: #f9fafb !important;
            color: #f9fafb !important;
        }
        /* Browse files button: white with black text */
        [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stFileUploaderDropzone"] button:hover,
        [data-testid="stFileUploaderDropzone"] button:focus {
            background-color: #ffffff !important;
            border-color: #ffffff !important;
            color: #111827 !important;
        }

        /* Uploaded file chips/list (bottom of screen): dark text/icon on light background */
        [data-testid="stFileUploaderFile"],
        [data-testid="stFileUploaderFile"] > div {
            background-color: #f1f5f9 !important;
            border-radius: 6px !important;
        }
        [data-testid="stFileUploaderFile"] span,
        [data-testid="stFileUploaderFile"] p,
        [data-testid="stFileUploaderFile"] small,
        [data-testid="stFileUploaderFile"] div,
        [data-testid="stFileUploaderFile"] * {
            color: #111827 !important;
        }
        [data-testid="stFileUploaderFile"] svg {
            color: #111827 !important;
            fill: none !important;
        }
        [data-testid="stFileUploaderFile"] svg path,
        [data-testid="stFileUploaderFile"] svg polyline,
        [data-testid="stFileUploaderFile"] svg line,
        [data-testid="stFileUploaderFile"] svg rect,
        [data-testid="stFileUploaderFile"] svg circle {
            stroke: #111827 !important;
            fill: none !important;
        }

        /* Generic message / alert boxes: high-contrast text on light backgrounds */
        [data-testid="stNotification"],
        [data-testid="stAlert"] {
            color: #111827 !important;
        }
        section[data-testid="stSidebar"] {
            background: #f3e8ff;
        }

        /* Stat cards: clearly outlined, clickable look */
        .stat-card {
            background: #fdfcff;
            border: 1px solid rgba(139, 92, 246, 0.5);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }
        .stat-number {
            font-size: 28px;
            font-weight: 700;
            color: #7c3aed;
        }
        .stat-label {
            font-size: 11px;
            color: #4b5563;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        /* Spinner text: ensure high-contrast black */
        [data-testid="stSpinner"] p {
            color: #111827 !important;
        }

        /* Buttons: blue default, darker on hover for contrast */
        .stButton > button {
            background-color: #2563eb !important;  /* blue-600 */
            border-color: #2563eb !important;
            color: #f9fafb !important;
        }
        .stButton > button:hover {
            background-color: #1d4ed8 !important;  /* blue-700 */
            border-color: #1d4ed8 !important;
            color: #f9fafb !important;
        }

        /* Danger Zone expander: solid black header + container */
        [data-testid="stExpander"] {
            background: #000000;
            border-radius: 8px;
            border: 1px solid #111827;
        }
        [data-testid="stExpander"] > details > summary {
            background: #000000 !important;
            color: #f9fafb !important;
        }
        [data-testid="stExpander"] > details > div {
            background: #000000;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    # Main
    st.markdown(
        """<div style="text-align: center; padding: 20px 0 10px;">
        <span class="material-symbols-rounded", style="font-size: 48px;">The Adversarial Provenance Agent</span>
        <h1 style="color: #4c1d95;
            font-size: 36px; margin: 8px 0 4px;">Addressing the Challenges of GenAI</h1>
        <p style="color: #4b5563; font-size: 14px; max-width: 600px; margin: 0 auto;">
            An agentic solution that both understands and identifies <strong style="color: #7c3aed;">Generated</strong> & <strong style="color: #7c3aed;">Synthetic</strong> Content.<br>
            Ask it and identify the provenance of any content.
        </p>
        </div>""",
        unsafe_allow_html=True,
    )

    tab_query, tab_memories, tab_stats = st.tabs(["Query", "Memory Bank", "Stats"])

    with tab_query:
        st.markdown("#### Ask your memory anything")
        st.markdown("<p style='color: #4b5563; font-size: 13px;'>The <strong>QueryAgent</strong> searches all memories and synthesizes answers with citations.</p>", unsafe_allow_html=True)

        question = st.text_input("Question", placeholder="What do you know about AI agents?", label_visibility="collapsed")

        sample_qs = [
            "What are the main themes across everything you remember?",
            "What connections do you see between different memories?",
            "What should I focus on based on what you know?",
            "Summarize everything in 3 bullet points.",
        ]
        cols = st.columns(2)
        for i, sq in enumerate(sample_qs):
            with cols[i % 2]:
                if st.button(f"💬 {sq}", use_container_width=True):
                    question = sq

        if question:
            with st.spinner("QueryAgent searching memory..."):
                t0 = time.time()
                result = api_get(f"/query?q={question}")
                elapsed = time.time() - t0
            if result:
                st.markdown(
                    f"""<div style="background: #fdfcff; border: 1px solid rgba(139,92,246,0.4);
                    border-radius: 12px; padding: 20px; margin: 16px 0;">
                    <span style="font-size: 12px; color: #7c3aed;">{elapsed:.1f}s</span>
                    <div style="color: #111827; line-height: 1.7; margin-top: 8px;">{result.get('answer', '')}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        st.markdown("#### Ask with file context")
        st.markdown("<p style='color: #4b5563; font-size: 13px;'>Optionally attach an image, audio, video, PDF, or text file. The agent will use both your long-term memory and the file contents to answer.</p>", unsafe_allow_html=True)

        col_q_file, col_btn = st.columns([3, 1])
        with col_q_file:
            question_file = st.text_input(
                "Question with file",
                key="question_with_file",
                placeholder="What do you know about this document?",
                label_visibility="collapsed",
            )
            uploaded_query_file = st.file_uploader(
                "Attach file",
                type=UPLOAD_EXTENSIONS,
                key="query_file",
                label_visibility="collapsed",
            )
        with col_btn:
            run_with_file = st.button("🔍 Ask with File", use_container_width=True)

        if run_with_file:
            if not question_file.strip():
                st.warning("Please enter a question.")
            elif uploaded_query_file is None:
                st.warning("Please attach a file.")
            else:
                files = {
                    "file": (
                        uploaded_query_file.name,
                        uploaded_query_file.getvalue(),
                        uploaded_query_file.type or "application/octet-stream",
                    )
                }
                data = {"q": question_file}
                with st.spinner("QueryAgent searching memory + file..."):
                    t0 = time.time()
                    result = api_post_multipart("/query_multimodal", data=data, files=files)
                    elapsed = time.time() - t0
                if not result:
                    st.error("Multimodal query failed. Check agent errors above.")
                elif "error" in result and not result.get("answer"):
                    st.error(f"Agent returned an error: {result}")
                else:
                    answer_text = result.get("answer", "").strip()
                    if not answer_text:
                        answer_text = "(Agent returned an empty answer.)"
                    st.markdown(
                        f"""<div style="background: #fdfcff; border: 1px solid rgba(139,92,246,0.4);
                        border-radius: 12px; padding: 20px; margin: 16px 0;">
                        <span style="font-size: 12px; color: #7c3aed;">{elapsed:.1f}s</span>
                        <div style="color: #111827; line-height: 1.7; margin-top: 8px;">{answer_text}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

    with tab_memories:
        st.markdown("#### Stored Memories")
        data = api_get("/memories")
        if data and data.get("memories"):
            for m in data["memories"]:
                render_memory_card(m)

        else:
            st.info("No memories yet. Ingest some information or drop files in ./inbox")

    with tab_stats:
        st.markdown("#### Agent & Memory Stats")
        stats = api_get("/status")
        if not stats:
            st.info("Agent not reachable. Make sure the backend agent is running.")
            return

        st.markdown(
            "<p style='color: #4b5563; font-size: 13px; text-align:center;'>Overview of the always-on memory agent.</p>",
            unsafe_allow_html=True,
        )

        # Centered agent status indicator
        col_status = st.columns(1)[0]
        with col_status:
            online_color = "#4ade80"
            st.markdown(
                f'<div class="stat-card" style="margin: 8px auto;"><div class="stat-number" style="color:{online_color};">●</div><div class="stat-label">Agent Online</div></div>',
                unsafe_allow_html=True,
            )

        # Memory stats row across the page
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f'<div class="stat-card" style="margin-top:8px;"><div class="stat-number">{stats.get("total_memories", 0)}</div><div class="stat-label">Memories</div></div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="stat-card" style="margin-top:8px;"><div class="stat-number">{stats.get("unconsolidated", 0)}</div><div class="stat-label">Pending</div></div>',
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f'<div class="stat-card" style="margin-top:8px;"><div class="stat-number">{stats.get("consolidations", 0)}</div><div class="stat-label">Consolidations</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown(
            "<p style='color: #4b5563; font-size: 13px; text-align:center;'>Used to view and to quickly confirm the health of the agent and memory store.</p>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()