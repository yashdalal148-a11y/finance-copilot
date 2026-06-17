"""
Streamlit Dashboard — Finance Intelligence Copilot.

This is the main UI module.  It renders the professional dashboard,
manages audio recording and text input, runs the orchestrator pipeline,
and displays results with metrics.
"""

from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.agents.context_agent import ContextAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.finance_expert_agent import FinanceExpertAgent
from app.agents.follow_up_agent import FollowUpAgent
from app.agents.interview_agent import InterviewAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.listener_agent import ListenerAgent
from app.agents.orchestrator import Orchestrator
from app.core.config import AppConfig, load_config
from app.core.llm_router import LLMRouter
from app.core.provider_registry import ProviderRegistry
from app.core.logging_config import setup_logging
from app.core.models import PipelineResult, ProviderName
from app.core.session import SessionMemory
from app.core.speech_client import SpeechClient

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════
# Initialisation (runs once per Streamlit session)
# ═════════════════════════════════════════════════════════════════════════

def _init_session() -> None:
    """Bootstrap config, clients, agents, and orchestrator into session state."""
    if "initialised" in st.session_state:
        return

    cfg: AppConfig = load_config()
    setup_logging(log_dir=cfg.log_dir, level=cfg.log_level)
    logger.info("Initialising session — mode=%s", cfg.active_mode.value)

    # Clients
    registry = ProviderRegistry(
        gemini_key=cfg.gemini_api_key,
        groq_key=cfg.groq_api_key,
        openrouter_key=cfg.openrouter_api_key
    )
    llm = LLMRouter(registry=registry)
    speech = SpeechClient(
        model_size=cfg.whisper_model_size,
        device=cfg.whisper_device,
        compute_type=cfg.whisper_compute_type,
    )

    # Session memory
    memory = SessionMemory()

    # Agents
    listener = ListenerAgent(speech_client=speech)
    context = ContextAgent(memory=memory)
    interview = InterviewAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    knowledge_ag = KnowledgeAgent(
        knowledge_dir=cfg.knowledge_dir,
        max_passages=cfg.max_knowledge_passages,
    )
    expert = FinanceExpertAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    follow_up = FollowUpAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    evaluation = EvaluationAgent(llm=llm, prompts_dir=cfg.prompts_dir)

    orchestrator = Orchestrator(
        listener=listener,
        context=context,
        interview=interview,
        knowledge=knowledge_ag,
        expert=expert,
        follow_up=follow_up,
        evaluation=evaluation,
        memory=memory,
    )
    
    from app.agents.resume_agent import ResumeIntelligenceAgent
    from app.agents.jd_agent import JobDescriptionIntelligenceAgent
    from app.agents.fit_agent import FitAnalysisAgent
    
    # V1.3 Agents
    from app.agents.story_agent import StoryIntelligenceAgent
    from app.agents.battlefield_agent import BattlefieldMapAgent
    from app.agents.red_flag_agent import RedFlagAgent
    from app.agents.intent_agent import IntentVerdictAgent
    from app.agents.gap_agent import CareerGapAgent
    from app.agents.offer_agent import OfferProbabilityAgent
    
    st.session_state.resume_agent = ResumeIntelligenceAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    st.session_state.jd_agent = JobDescriptionIntelligenceAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    st.session_state.fit_agent = FitAnalysisAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    
    st.session_state.story_agent = StoryIntelligenceAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    st.session_state.battlefield_agent = BattlefieldMapAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    st.session_state.red_flag_agent = RedFlagAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    st.session_state.intent_agent = IntentVerdictAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    st.session_state.gap_agent = CareerGapAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    st.session_state.offer_agent = OfferProbabilityAgent(llm=llm, prompts_dir=cfg.prompts_dir)

    # V1.5 Agents & Stores
    from app.core.memory_store import MemoryStore
    from app.agents.memory_consolidation_agent import MemoryConsolidationAgent
    from app.agents.stock_pitch_agent import StockPitchAgent
    from app.agents.weakness_agent import WeaknessIntelligenceAgent
    
    st.session_state.memory_store = MemoryStore()
    st.session_state.research_memory = st.session_state.memory_store.load_memory()
    
    st.session_state.consolidation_agent = MemoryConsolidationAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    st.session_state.stock_pitch_agent = StockPitchAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    st.session_state.weakness_agent = WeaknessIntelligenceAgent(llm=llm, prompts_dir=cfg.prompts_dir)

    # Live Transcriber
    from app.core.live_transcriber import LiveTranscriber
    st.session_state.live_transcriber = LiveTranscriber(orchestrator=orchestrator)

    # Persist in session state
    st.session_state.orchestrator = orchestrator
    st.session_state.memory = memory
    st.session_state.config = cfg
    st.session_state.results_history = []
    st.session_state.initialised = True


# ═════════════════════════════════════════════════════════════════════════
# Dashboard Rendering
# ═════════════════════════════════════════════════════════════════════════

def render_dashboard() -> None:
    """Main entry point — renders the full Streamlit dashboard."""
    st.set_page_config(
        page_title="Finance Intelligence Copilot",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _inject_css()
    _init_session()

    # ── Header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="main-header">
            <h1>🏦 Finance Intelligence Copilot</h1>
            <p class="subtitle">Interview Intelligence · Powered by Gemini</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar ───────────────────────────────────────────────────────
    _render_sidebar()

    # ── Workspace Navigation ──────────────────────────────────────────
    if "active_workspace" not in st.session_state:
        st.session_state.active_workspace = "🎙️ Mock Interview"

    with st.sidebar:
        st.markdown("## 🖥️ OS Workspaces")
        st.session_state.active_workspace = st.radio(
            "Select Workspace:",
            [
                "🔴 Live Interview Copilot",
                "🎙️ Mock Interview",
                "📈 Stock Pitch",
                "🗺️ Career Intelligence",
                "🧠 Research Memory",
                "🎯 Weakness Dashboard",
                "📓 Research Notebook",
                "⚙️ Provider Intelligence"
            ],
            label_visibility="collapsed"
        )
        st.divider()

    workspace = st.session_state.active_workspace

    if workspace == "🔴 Live Interview Copilot":
        _render_live_copilot()

    elif workspace == "🎙️ Mock Interview":
        # ── Input Section ─────────────────────────────────────────────────
        col_audio, col_text = st.columns([1, 1])

        audio_bytes = None
        with col_audio:
            st.markdown("### 🎙️ Voice Input")
            try:
                from audio_recorder_streamlit import audio_recorder
                audio_bytes = audio_recorder(
                    text="Click to record your question",
                    recording_color="#e74c3c",
                    neutral_color="#6c757d",
                    icon_size="2x",
                    pause_threshold=2.5,
                    sample_rate=16000,
                )
            except ImportError:
                st.info(
                    "Audio recorder not available. Install `audio-recorder-streamlit` "
                    "or use the text input."
                )

            uploaded = st.file_uploader(
                "Or upload an audio file",
                type=["wav", "mp3", "m4a", "ogg", "flac"],
                key="audio_upload",
            )
            if uploaded is not None:
                audio_bytes = uploaded.getvalue()

        text_input = None
        with col_text:
            st.markdown("### ⌨️ Text Input")
            text_input = st.text_area(
                "Type your interview question",
                height=120,
                placeholder="e.g. Walk me through a DCF analysis…",
                key="text_question",
            )
            submit_text = st.button("Submit Question", type="primary", use_container_width=True)

        # ── Pipeline Execution ────────────────────────────────────────────
        orchestrator: Orchestrator = st.session_state.orchestrator

        if "processed_audio_hash" not in st.session_state:
            st.session_state.processed_audio_hash = None

        if audio_bytes:
            audio_hash = hash(audio_bytes)
            if audio_hash != st.session_state.processed_audio_hash:
                st.session_state.processed_audio_hash = audio_hash
                _run_audio_pipeline(orchestrator, audio_bytes)
        elif submit_text and text_input:
            clean_input = text_input.strip()
            if not clean_input:
                st.warning("Please enter a valid question.")
            elif len(clean_input) > 2000:
                st.warning("Question is too long (maximum 2000 characters).")
            else:
                clean_input = clean_input.replace("{", "").replace("}", "")
                _run_text_pipeline(orchestrator, clean_input)

        # ── Results History ───────────────────────────────────────────────
        _render_results_history()

    elif workspace == "📈 Stock Pitch":
        _render_stock_pitch_workspace()

    elif workspace == "🗺️ Career Intelligence":
        _render_career_intelligence()

    elif workspace == "🧠 Research Memory":
        _render_research_memory()

    elif workspace == "🎯 Weakness Dashboard":
        _render_weakness_dashboard()

    elif workspace == "📓 Research Notebook":
        _render_research_notebook()

    elif workspace == "⚙️ Provider Intelligence":
        _render_provider_intelligence()


# ═════════════════════════════════════════════════════════════════════════
# Pipeline Runners
# ═════════════════════════════════════════════════════════════════════════

def _run_audio_pipeline(orchestrator: Orchestrator, audio_bytes: bytes) -> None:
    status_placeholder = st.empty()

    def _update(msg: str) -> None:
        status_placeholder.markdown(f"**{msg}**")

    with st.spinner("Processing audio through the agent pipeline…"):
        result = orchestrator.run(audio_bytes, status_callback=_update)

    status_placeholder.empty()
    _display_result(result)
    st.session_state.results_history.append(result)


def _run_text_pipeline(orchestrator: Orchestrator, question: str) -> None:
    status_placeholder = st.empty()

    def _update(msg: str) -> None:
        status_placeholder.markdown(f"**{msg}**")

    with st.spinner("Processing question through the agent pipeline…"):
        result = orchestrator.run_text(question, status_callback=_update)

    status_placeholder.empty()
    _display_result(result)
    st.session_state.results_history.append(result)


# ═════════════════════════════════════════════════════════════════════════
# Result Display
# ═════════════════════════════════════════════════════════════════════════

def _display_result(result: PipelineResult) -> None:
    """Render a single pipeline result."""
    if not result.success:
        st.error(f"⚠️ Pipeline Error: {result.error}")
        return

    st.divider()

    # ── Transcript + Classification ───────────────────────────────────
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("#### 📝 Transcript")
        st.info(result.transcription.text if result.transcription else "—")
    with col2:
        st.markdown("#### 🏷️ Category")
        if result.classification:
            cat = result.classification.category.value.replace("_", " ").title()
            st.success(f"**{cat}**")
            if result.classification.subcategory:
                st.caption(result.classification.subcategory)
    with col3:
        st.markdown("#### 🎯 Classification Confidence")
        if result.classification:
            st.metric(
                label="Confidence",
                value=f"{result.classification.confidence:.0%}",
            )

    # ── Expert Answer ─────────────────────────────────────────────────
    if result.answer:
        st.markdown("#### 💡 Expert Answer")
        st.markdown(
            f'<div class="answer-card">{result.answer.answer}</div>',
            unsafe_allow_html=True,
        )

        if result.answer.key_points:
            st.markdown("**Key Points:**")
            for point in result.answer.key_points:
                st.markdown(f"- ✅ {point}")

        if result.answer.frameworks_used:
            st.markdown(
                "**Frameworks:** " + " · ".join(f"`{f}`" for f in result.answer.frameworks_used)
            )

    # ── Evaluation Scores ─────────────────────────────────────────────
    if result.evaluation:
        st.markdown("#### 📊 Evaluation")
        ev = result.evaluation
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overall", f"{ev.overall_score:.0f}/100")
        c2.metric("Confidence", f"{ev.confidence_score:.0f}/100")
        c3.metric("Completeness", f"{ev.completeness_score:.0f}/100")
        c4.metric("Accuracy", f"{ev.accuracy_score:.0f}/100")

        if ev.feedback:
            st.markdown(f"*{ev.feedback}*")

        col_s, col_i = st.columns(2)
        with col_s:
            if ev.strengths:
                st.markdown("**Strengths:**")
                for s in ev.strengths:
                    st.markdown(f"- 💪 {s}")
        with col_i:
            if ev.improvements:
                st.markdown("**Areas for Improvement:**")
                for imp in ev.improvements:
                    st.markdown(f"- 🔧 {imp}")

    # ── Follow-Up Questions ───────────────────────────────────────────
    if result.follow_ups and result.follow_ups.questions:
        st.markdown("#### 🔮 Predicted Follow-Up Questions")
        for i, q in enumerate(result.follow_ups.questions, 1):
            st.markdown(f"**{i}.** {q}")

    # ── Pipeline Timing ───────────────────────────────────────────────
    with st.expander("⏱️ Pipeline Performance", expanded=False):
        for t in result.timings:
            st.markdown(f"- **{t.agent_name}**: {t.duration_ms:.0f} ms")
        st.markdown(f"- **Total Pipeline**: {result.total_duration_ms:.0f} ms")


# ═════════════════════════════════════════════════════════════════════════
# Career Intelligence Tab
# ═════════════════════════════════════════════════════════════════════════

def _render_career_intelligence() -> None:
    st.markdown("## 🗺️ Career Intelligence")
    memory: SessionMemory = st.session_state.memory
    
    if not memory.candidate_profile or not memory.job_profile:
        st.info("👈 Upload your Resume and Target Job Description in the Sidebar to unlock Career Intelligence.")
        return

    # Trigger Generation if missing
    with st.spinner("Generating Career Intelligence..."):
        if not memory.career_stories:
            memory.career_stories = st.session_state.story_agent.run(memory.candidate_profile, memory.job_profile)
        if not memory.battlefield_map:
            memory.battlefield_map = st.session_state.battlefield_agent.run(memory.candidate_profile, memory.job_profile)
        if not memory.red_flag_analysis and memory.fit_analysis:
            memory.red_flag_analysis = st.session_state.red_flag_agent.run(memory.candidate_profile, memory.fit_analysis)
        if not memory.career_gap_analysis:
            memory.career_gap_analysis = st.session_state.gap_agent.run(memory.candidate_profile, memory.job_profile)
        if not memory.offer_probability and memory.fit_analysis and memory.battlefield_map:
            memory.offer_probability = st.session_state.offer_agent.run(
                memory.candidate_profile, memory.job_profile, memory.fit_analysis, memory.battlefield_map
            )

    # ── Offer Probability ──────────────────────────────────────────────
    if memory.offer_probability:
        st.markdown("### 🎯 Offer Probability")
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            st.metric("Estimated Probability", f"{memory.offer_probability.offer_probability:.0%}")
        with col2:
            st.markdown("**Top Risks:**")
            for r in memory.offer_probability.top_risks:
                st.markdown(f"- ⚠️ {r}")
        with col3:
            st.markdown("**Highest Leverage Improvements:**")
            for i in memory.offer_probability.highest_leverage_improvements:
                st.markdown(f"- 🚀 {i}")
        st.divider()

    # ── Red Flags & Gaps ───────────────────────────────────────────────
    col_rf, col_gap = st.columns(2)
    with col_rf:
        st.markdown("### 🚨 Red Flags")
        if memory.red_flag_analysis:
            for flag in memory.red_flag_analysis.flags:
                with st.expander(f"🚩 {flag.flag}"):
                    st.markdown(f"**Interviewer Worry:** {flag.interviewer_worry}")
                    st.markdown(f"**Suggested Response:** {flag.suggested_response}")
                    st.markdown(f"**Recovery Strategy:** {flag.recovery_strategy}")
    with col_gap:
        st.markdown("### 🧩 Career Gaps")
        if memory.career_gap_analysis:
            st.markdown("**Missing Experiences:**")
            for e in memory.career_gap_analysis.missing_experiences:
                st.markdown(f"- {e}")
            st.markdown("**Missing Skills:**")
            for s in memory.career_gap_analysis.missing_skills:
                st.markdown(f"- {s}")
            st.markdown("**Development Plan:**")
            for p in memory.career_gap_analysis.suggested_development_plan:
                st.markdown(f"- {p}")
    st.divider()

    # ── Story Engine ───────────────────────────────────────────────────
    st.markdown("### 📖 Story Intelligence")
    if memory.career_stories:
        tabs = st.tabs([s.title for s in memory.career_stories])
        for tab, story in zip(tabs, memory.career_stories):
            with tab:
                st.caption(f"**Target Duration:** {story.duration_target}")
                st.markdown(f"*{story.narrative}*")
                st.markdown("**Key Signals Transmitted:** " + " · ".join(story.key_signals))
    st.divider()

    # ── Battlefield Map ────────────────────────────────────────────────
    st.markdown("### ⚔️ Interview Battlefield Map")
    if memory.battlefield_map:
        for i, q in enumerate(memory.battlefield_map.top_questions):
            with st.expander(f"Q{i+1}: {q.question} (Prob: {q.probability:.0%} | Diff: {q.difficulty:.0%} | Pri: {q.preparation_priority})"):
                # On-Demand Intent Trigger
                if not q.intent or not q.verdict:
                    if st.button("Generate Intent & Verdict", key=f"intent_btn_{i}"):
                        with st.spinner("Analyzing intent..."):
                            q.intent, q.verdict = st.session_state.intent_agent.run(q.question)
                            st.rerun()
                else:
                    st.markdown("#### 🕵️ Interviewer Intent")
                    st.markdown(f"**Core Test:** {q.intent.core_test}")
                    st.markdown(f"**Technical Depth:** {q.intent.technical_depth}")
                    st.markdown("**Communication Signals:** " + " · ".join(q.intent.communication_signals))
                    st.markdown("**Common Mistakes:** " + " · ".join(q.intent.common_mistakes))
                    
                    st.markdown("#### ⚖️ Hiring Manager Verdict")
                    st.markdown(f"**Passing Criteria:** {q.verdict.passing_criteria}")
                    st.markdown("**Red Flag Triggers:** " + " · ".join(q.verdict.red_flag_triggers))
                    st.markdown("**Differentiation Factors:** " + " · ".join(q.verdict.differentiation_factors))


# ═════════════════════════════════════════════════════════════════════════
# Provider Intelligence Tab
# ═════════════════════════════════════════════════════════════════════════

def _render_provider_intelligence() -> None:
    st.markdown("## ⚙️ Provider Intelligence")
    st.caption("Real-time telemetry and health monitoring for the Multi-Provider LLM Router.")
    
    if "orchestrator" not in st.session_state:
        st.info("System initializing...")
        return
        
    orchestrator = st.session_state.orchestrator
    # Hack to get the LLM router from one of the agents
    router = orchestrator._expert._llm
    
    if not hasattr(router, "health"):
        st.warning("Multi-Provider architecture is not fully loaded yet.")
        return

    # ── Provider Health Status ─────────────────────────────────────────
    st.markdown("### 🏥 Provider Health")
    cols = st.columns(3)
    for i, provider in enumerate([ProviderName.GEMINI, ProviderName.GROQ, ProviderName.OPENROUTER]):
        health = router.health.get_health(provider)
        with cols[i]:
            if health.status.value == "online":
                st.success(f"**{provider.value.upper()}**: ONLINE 🟢")
            elif health.status.value == "degraded":
                st.warning(f"**{provider.value.upper()}**: DEGRADED 🟡 ({health.consecutive_failures} failures)")
            else:
                st.error(f"**{provider.value.upper()}**: OFFLINE 🔴")
            if health.last_error_message:
                st.caption(f"Last Error: {health.last_error_message[:50]}...")

    st.divider()

    # ── Benchmarking & Metrics ─────────────────────────────────────────
    st.markdown("### 📊 Live Benchmarks & Latency")
    metrics = router.benchmarker.get_all_metrics()
    
    m_cols = st.columns(3)
    for i, provider in enumerate([ProviderName.GEMINI, ProviderName.GROQ, ProviderName.OPENROUTER]):
        m = metrics[provider]
        with m_cols[i]:
            st.markdown(f"**{provider.value.upper()}**")
            st.metric("Total Requests", m.total_requests)
            st.metric("Failures / Fallbacks", m.failed_requests)
            st.metric("Avg Latency", f"{m.avg_latency_ms:.0f} ms")
            st.metric("Estimated Cost", f"${m.estimated_cost_usd:.6f}")


# ═════════════════════════════════════════════════════════════════════════
# Sidebar
# ═════════════════════════════════════════════════════════════════════════

def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 📋 Session")
        memory: SessionMemory = st.session_state.memory
        st.metric("Questions Asked", memory.question_count)

        if memory.session_topics:
            st.markdown("**Topics Covered:**")
            for topic in memory.session_topics:
                st.markdown(f"- {topic.replace('_', ' ').title()}")

        if memory.question_count > 0:
            if st.button("🗑️ Clear Session", use_container_width=True):
                memory.clear()
                st.session_state.results_history = []
                st.rerun()

        st.divider()
        st.markdown("## 🕵️ Candidate Setup")
        
        # Resume Upload
        resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"], key="resume_upload")
        if resume_file and not memory.candidate_profile:
            with st.spinner("Parsing Resume..."):
                from app.core.document_parser import extract_text_from_file
                text = extract_text_from_file(resume_file.getvalue(), resume_file.name)
                memory.candidate_profile = st.session_state.resume_agent.run(text)
                st.success("Resume parsed successfully!")
                
        # JD Upload
        jd_file = st.file_uploader("Upload Job Description (PDF/TXT)", type=["pdf", "txt"], key="jd_upload")
        if jd_file and not memory.job_profile:
            with st.spinner("Parsing Job Description..."):
                from app.core.document_parser import extract_text_from_file
                text = extract_text_from_file(jd_file.getvalue(), jd_file.name)
                memory.job_profile = st.session_state.jd_agent.run(text)
                st.success("JD parsed successfully!")
                
        # Fit Analysis Generation
        if memory.candidate_profile and memory.job_profile and not memory.fit_analysis:
            with st.spinner("Analyzing Fit..."):
                memory.fit_analysis = st.session_state.fit_agent.run(
                    memory.candidate_profile, memory.job_profile
                )
        
        # Display Fit
        if memory.fit_analysis:
            st.metric("Match Score", f"{memory.fit_analysis.match_score:.0f}/100")
            if memory.fit_analysis.strengths:
                st.caption(f"**Strengths:** {', '.join(memory.fit_analysis.strengths[:2])}")
            if memory.fit_analysis.skill_gaps:
                st.caption(f"**Gaps:** {', '.join(memory.fit_analysis.skill_gaps[:2])}")

        st.divider()
        st.markdown("## ⚙️ Configuration")
        
        stealth_mode = st.toggle("Stealth Mode", value=st.session_state.get("stealth_mode", False))
        if stealth_mode != st.session_state.get("stealth_mode", False):
            st.session_state.stealth_mode = stealth_mode
            st.rerun()
            
        cfg: AppConfig = st.session_state.config
        st.caption(f"**Model:** {cfg.gemini_model}")
        st.caption(f"**Whisper:** {cfg.whisper_model_size} ({cfg.whisper_device})")
        st.caption(f"**Mode:** {cfg.active_mode.value.replace('_', ' ').title()}")

        st.divider()
        st.markdown(
            """
            ## 🗺️ Future Modes
            - ✅ Interview Intelligence
            - ⬜ Equity Research Coach
            - ⬜ Stock Pitch Assistant
            - ⬜ Valuation Coach
            - ⬜ Accounting Coach
            - ⬜ Earnings Call Intelligence
            - ⬜ Market Intelligence
            """
        )


# ═════════════════════════════════════════════════════════════════════════
# Results History
# ═════════════════════════════════════════════════════════════════════════

def _render_results_history() -> None:
    history = st.session_state.get("results_history", [])
    if len(history) > 1:
        st.divider()
        st.markdown("### 📜 Previous Questions in This Session")
        # Show in reverse order, skip the most recent (already displayed)
        for i, res in enumerate(reversed(history[:-1]), 1):
            with st.expander(
                f"Q{len(history) - i}: {res.transcription.text[:80]}…"
                if res.transcription
                else f"Q{len(history) - i}"
            ):
                _display_result(res)


# ═════════════════════════════════════════════════════════════════════════
# CSS
# ═════════════════════════════════════════════════════════════════════════

def _inject_css() -> None:
    css = """
        <style>
        .main-header {
            text-align: center;
            padding: 1.5rem 0 0.5rem;
        }
        .main-header h1 {
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #FFD700 0%, #D4AF37 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
            letter-spacing: -0.5px;
        }
        .subtitle {
            font-size: 1.1rem;
            color: #94a3b8;
            margin-top: 0.2rem;
            font-weight: 500;
        }
        .answer-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 1.5rem 2rem;
            line-height: 1.8;
            font-size: 1rem;
            color: #f8fafc;
            margin: 0.5rem 0 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #e2e8f0 !important;
        }
        /* Hide Streamlit default branding */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
        
    if st.session_state.get("stealth_mode", False):
        css += """
        <style>
        /* Stealth Mode overrides */
        .main-header, [data-testid="stSidebar"], .subtitle, .stButton>button {
            opacity: 0.05 !important;
            transition: opacity 0.3s ease;
        }
        .main-header:hover, [data-testid="stSidebar"]:hover, .stButton>button:hover {
            opacity: 1 !important;
        }
        .answer-card {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            font-family: monospace;
            font-size: 0.8rem !important;
            color: #666 !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1rem !important;
            color: #666 !important;
        }
        </style>
        """

    st.markdown(css, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# OS Workspaces (V1.5)
# ═════════════════════════════════════════════════════════════════════════

def _render_stock_pitch_workspace() -> None:
    st.markdown("## 📈 Stock Pitch Intelligence")
    st.caption("Generate Institutional Equity Research Memos.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        company = st.text_input("Company Name", placeholder="e.g. Nvidia")
        ticker = st.text_input("Ticker", placeholder="e.g. NVDA")
        thesis = st.text_area("Investment Thesis & Notes", height=150, placeholder="Write your variant view here...")
        
        if st.button("Generate Pitch", type="primary", use_container_width=True):
            if company and ticker and thesis:
                with st.spinner("Generating Institutional Memo..."):
                    pitch = st.session_state.stock_pitch_agent.run(company, ticker, thesis)
                    # Save to memory
                    st.session_state.research_memory.stock_pitch.pitch_history.append(f"{ticker}: {thesis[:100]}")
                    st.session_state.memory_store.save_memory(st.session_state.research_memory)
                    st.session_state.current_pitch = pitch
            else:
                st.warning("Please fill all fields.")
                
    with col2:
        if "current_pitch" in st.session_state and st.session_state.current_pitch:
            p = st.session_state.current_pitch
            if p.memo:
                st.markdown(f"### {p.company_name} ({p.ticker}) Investment Memo")
                st.markdown(f"**Business Overview:** {p.memo.business_overview}")
                st.markdown(f"**Investment Thesis:** {p.memo.investment_thesis}")
                
                with st.expander("Detailed Analysis"):
                    st.markdown(f"**Industry Structure:** {p.memo.industry_structure}")
                    st.markdown(f"**Competitive Landscape:** {p.memo.competitive_landscape}")
                    st.markdown(f"**Management:** {p.memo.management_assessment}")
                    
                col_b, col_bear = st.columns(2)
                with col_b:
                    st.success(f"**Bull Case:** {p.memo.bull_case}")
                with col_bear:
                    st.error(f"**Bear Case:** {p.memo.bear_case}")
                    
                st.markdown("**Catalysts:**")
                for c in p.memo.catalysts: st.markdown(f"- {c}")
                
                st.markdown("**Valuation Framework:**")
                st.info(p.memo.valuation_framework)
                
                if p.memo.md_critique:
                    st.markdown("### 🧨 MD Critique")
                    st.warning(p.memo.md_critique.blunt_feedback)
                if p.memo.ic_verdict:
                    st.markdown(f"### ⚖️ IC Verdict: {p.memo.ic_verdict.decision}")


def _render_research_memory() -> None:
    st.markdown("## 🧠 Research Memory")
    st.caption("Persistent intelligence and timeline of your progression.")
    mem = st.session_state.research_memory
    
    st.markdown("### 📈 Candidate Evolution")
    st.info(mem.evolution.overall_trajectory if mem.evolution.overall_trajectory else "No trajectory established yet.")
    for event in mem.evolution.timeline_events:
        st.markdown(f"- {event}")
        
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💪 Top Strengths")
        for s in mem.candidate.strength_trends: st.markdown(f"- {s}")
    with col2:
        st.markdown("### 📉 Weakness Trends")
        for w in mem.candidate.weakness_trends: st.markdown(f"- {w}")

    st.markdown("### 📚 Interview History")
    st.metric("Recorded Readiness Data Points", len(mem.interview.readiness_history))
    if len(mem.interview.readiness_history) > 0:
        st.line_chart(mem.interview.readiness_history)
        
    if st.button("🔄 Force Consolidate Session Memory", use_container_width=True):
        with st.spinner("Consolidating session data..."):
            updated_memory = st.session_state.consolidation_agent.run(
                st.session_state.research_memory, 
                st.session_state.memory
            )
            st.session_state.research_memory = updated_memory
            st.session_state.memory_store.save_memory(updated_memory)
            st.success("Memory consolidated successfully!")


def _render_weakness_dashboard() -> None:
    st.markdown("## 🎯 Weakness Dashboard")
    st.caption("Skill gap analysis across finance verticals.")
    
    if st.button("Run Deep Skill Gap Analysis", type="primary"):
        with st.spinner("Analyzing cross-vertical gaps..."):
            analysis = st.session_state.weakness_agent.run(st.session_state.research_memory)
            st.session_state.current_weakness = analysis
            
    if "current_weakness" in st.session_state:
        w = st.session_state.current_weakness
        st.markdown("### 🗺️ Strength & Weakness Map")
        
        # Two column layout for strengths/weaknesses
        for category, strength in w.strength_map.items():
            st.success(f"**{category} Strength:** {strength}")
        for category, weakness in w.weakness_map.items():
            st.error(f"**{category} Weakness:** {weakness}")
            
        st.markdown("### ⚠️ Critical Skill Gaps")
        for gap in w.skill_gap_analysis:
            st.warning(gap)
            
        if w.roadmap:
            st.markdown("### 🗺️ Learning Roadmap")
            with st.expander("Immediate Actions (48 hrs)", expanded=True):
                for a in w.roadmap.immediate_actions: st.markdown(f"- {a}")
            with st.expander("Short Term Goals (2 weeks)"):
                for a in w.roadmap.short_term_goals: st.markdown(f"- {a}")


def _render_research_notebook() -> None:
    st.markdown("## 📓 Research Notebook")
    st.caption("A scratchpad for tracking companies, sectors, and personal insights.")
    st.info("Notebook feature relies on `data/notebook.json` (Coming in V1.6, local stub UI below).")
    
    note_type = st.selectbox("Category", ["Company", "Sector", "Interview", "Personal"])
    title = st.text_input("Title")
    content = st.text_area("Note Content", height=200)
    
    if st.button("Save Note"):
        st.success("Note saved to local storage.")


def _render_live_copilot() -> None:
    st.markdown("## 🔴 Live Interview Copilot")
    st.caption("Chiku AI Stealth Mode — Continuous listening and real-time insights.")
    
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
        else:
            st.markdown("**Status:** Idle")

    st.divider()

    st.markdown("<!-- Stealth CSS removed for debugging -->", unsafe_allow_html=True)


    @st.fragment(run_every="2s")
    def _poll_transcriber():
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

    _poll_transcriber()
