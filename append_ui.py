import sys

CODE_TO_APPEND = """

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
"""

with open(r"e:\finance-intelligent-copilot\app\ui\dashboard.py", "a", encoding="utf-8") as f:
    f.write(CODE_TO_APPEND)

print("Workspaces successfully appended!")
