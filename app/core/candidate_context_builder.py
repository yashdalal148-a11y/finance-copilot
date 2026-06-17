"""
Candidate Context Builder.

Takes the structural output from the Intelligence Layer (CandidateProfile,
JobProfile, FitAnalysis) and condenses it into a dense narrative string
to be injected into the FinanceExpertAgent's prompt.
"""

from __future__ import annotations

from typing import Optional

from app.core.models import CandidateProfile, FitAnalysis, JobProfile


def build_candidate_context(
    candidate: Optional[CandidateProfile],
    job: Optional[JobProfile],
    fit: Optional[FitAnalysis],
) -> str:
    """Build a condensed narrative of the candidate's intelligence."""
    
    if not candidate and not job:
        return "No candidate resume or job description provided."

    lines = ["[CANDIDATE INTELLIGENCE CONTEXT]"]

    if candidate:
        lines.append("\n--- CANDIDATE PROFILE ---")
        if candidate.experience:
            lines.append(f"Experience: {', '.join(candidate.experience)}")
        if candidate.skills:
            lines.append(f"Skills: {', '.join(candidate.skills)}")
        if candidate.sector_expertise:
            lines.append(f"Sectors: {', '.join(candidate.sector_expertise)}")
        if candidate.achievements:
            lines.append(f"Key Achievements: {', '.join(candidate.achievements)}")

    if job:
        lines.append("\n--- TARGET JOB PROFILE ---")
        if job.role:
            lines.append(f"Role: {job.role}")
        if job.domain:
            lines.append(f"Domain: {job.domain}")
        if job.required_skills:
            lines.append(f"Required Skills: {', '.join(job.required_skills)}")

    if fit:
        lines.append("\n--- FIT ANALYSIS ---")
        lines.append(f"Match Score: {fit.match_score}/100")
        if fit.strengths:
            lines.append(f"Strengths to Highlight: {', '.join(fit.strengths)}")
        if fit.skill_gaps:
            lines.append(f"Skill Gaps to Defend: {', '.join(fit.skill_gaps)}")

    lines.append("\nINSTRUCTION FOR EXPERT: When answering the user's question, seamlessly weave in references to their actual experience and frame the answer for their target role. Do NOT mention that you are reading a profile. Speak naturally as if you already know their background.")

    return "\n".join(lines)
