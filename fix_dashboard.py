import sys

file_path = r"e:\finance-intelligent-copilot\app\ui\dashboard.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

live_copilot_code = """

def _render_live_copilot() -> None:
    st.markdown("## 🔴 Live Interview Copilot")
    st.caption("Chiku AI Stealth Mode — Continuous listening and real-time insights.")
    
    try:
        from streamlit_autorefresh import st_autorefresh
    except ImportError:
        st.error("Please install `streamlit-autorefresh` to use the Live Copilot.")
        return

    transcriber = st.session_state.live_transcriber

    col1, col2 = st.columns([1, 5])
    with col1:
        if not transcriber.is_running:
            if st.button("Start Listening", type="primary"):
                transcriber.start()
                st.rerun()
        else:
            if st.button("Stop Listening"):
                transcriber.stop()
                st.rerun()
                
    with col2:
        if transcriber.is_running:
            st.markdown(f"**Status:** {transcriber.status}")
            st_autorefresh(interval=2000, key="live_copilot_refresh")
        else:
            st.markdown("**Status:** Idle")

    st.divider()

    # Stealth UI overrides specific to this workspace
    st.markdown(
        \"\"\"
        <style>
        /* Stealth Mode */
        .main-header, [data-testid="stSidebar"] { opacity: 0.05 !important; transition: opacity 0.3s; }
        .main-header:hover, [data-testid="stSidebar"]:hover { opacity: 1 !important; }
        
        .live-question {
            font-size: 1.1rem;
            color: #94a3b8;
            margin-bottom: 1rem;
        }
        .live-answer {
            font-size: 2rem !important;
            font-weight: bold;
            color: #ffffff;
            background: #111;
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #333;
            line-height: 1.5;
        }
        .live-followup {
            font-size: 1rem;
            color: #ef4444;
            margin-top: 1rem;
        }
        </style>
        \"\"\",
        unsafe_allow_html=True
    )

    if transcriber.latest_result:
        res = transcriber.latest_result
        if res.transcription:
            st.markdown(f'<div class="live-question">🗣️ "{res.transcription.text}"</div>', unsafe_allow_html=True)
            
        if res.answer:
            answer_text = res.answer.answer.replace('\\n', '<br>')
            st.markdown(f'<div class="live-answer">{answer_text}</div>', unsafe_allow_html=True)
            
        if res.follow_ups and res.follow_ups.questions:
            st.markdown("### 🔮 Predicted Follow-Ups")
            for q in res.follow_ups.questions:
                st.markdown(f'<div class="live-followup">↳ {q}</div>', unsafe_allow_html=True)
    else:
        if transcriber.is_running:
            st.info("Listening for the interviewer...")
        else:
            st.info("Start listening to see real-time answers here.")
"""

if "def _render_live_copilot" not in content:
    content += live_copilot_code
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Function appended.")
else:
    print("Function already exists.")
