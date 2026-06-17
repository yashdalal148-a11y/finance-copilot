import pytest
from unittest.mock import MagicMock
from pathlib import Path

from app.core.models import CandidateProfile, JobProfile, FitAnalysis
from app.core.candidate_context_builder import build_candidate_context
from app.core.document_parser import extract_text_from_file

from app.agents.resume_agent import ResumeIntelligenceAgent
from app.agents.jd_agent import JobDescriptionIntelligenceAgent
from app.agents.fit_agent import FitAnalysisAgent


# ── Parser Tests ──────────────────────────────────────────────────────────

def test_extract_text_fallback():
    # Should fallback to utf-8 decode for unknown extensions
    raw = b"hello world"
    res = extract_text_from_file(raw, "test.xyz")
    assert res == "hello world"


def test_extract_text_txt():
    raw = b"plaintext content"
    res = extract_text_from_file(raw, "test.txt")
    assert res == "plaintext content"


# ── Context Builder Tests ─────────────────────────────────────────────────

def test_build_candidate_context_empty():
    res = build_candidate_context(None, None, None)
    assert "No candidate resume" in res


def test_build_candidate_context_full():
    cand = CandidateProfile(
        experience=["Goldman Sachs - Analyst"],
        skills=["LBO Modeling"],
    )
    job = JobProfile(
        role="Private Equity Associate",
        required_skills=["LBO Modeling", "Excel"],
    )
    fit = FitAnalysis(
        match_score=95.0,
        strengths=["Strong modeling"],
        skill_gaps=[],
    )
    
    res = build_candidate_context(cand, job, fit)
    assert "CANDIDATE PROFILE" in res
    assert "Goldman Sachs" in res
    assert "TARGET JOB PROFILE" in res
    assert "Private Equity Associate" in res
    assert "FIT ANALYSIS" in res
    assert "95.0/100" in res


# ── Agent Tests ───────────────────────────────────────────────────────────

@pytest.fixture
def mock_llm():
    return MagicMock()

@pytest.fixture
def prompts_dir(tmp_path):
    (tmp_path / "resume_intelligence_prompt.txt").write_text("{raw_text}")
    (tmp_path / "job_intelligence_prompt.txt").write_text("{raw_text}")
    (tmp_path / "fit_analysis_prompt.txt").write_text("{candidate_profile} {job_profile}")
    return tmp_path

def test_resume_agent(mock_llm, prompts_dir):
    mock_llm.generate_json.return_value = {
        "experience": ["Company A"],
        "skills": ["Skill B"],
        "education": [],
        "certifications": [],
        "sector_expertise": [],
        "projects": [],
        "achievements": []
    }
    agent = ResumeIntelligenceAgent(llm=mock_llm, prompts_dir=prompts_dir)
    res = agent.run("some resume text")
    assert res.experience == ["Company A"]
    assert res.skills == ["Skill B"]

def test_jd_agent(mock_llm, prompts_dir):
    mock_llm.generate_json.return_value = {
        "role": "Analyst",
        "responsibilities": [],
        "required_skills": [],
        "preferred_skills": [],
        "seniority": "Junior",
        "domain": "Finance"
    }
    agent = JobDescriptionIntelligenceAgent(llm=mock_llm, prompts_dir=prompts_dir)
    res = agent.run("some jd text")
    assert res.role == "Analyst"

def test_fit_agent(mock_llm, prompts_dir):
    mock_llm.generate_json.return_value = {
        "match_score": 88.5,
        "strengths": ["a"],
        "skill_gaps": ["b"],
        "competitive_advantages": ["c"],
        "likely_interview_topics": ["d"]
    }
    agent = FitAnalysisAgent(llm=mock_llm, prompts_dir=prompts_dir)
    res = agent.run(CandidateProfile(), JobProfile())
    assert res.match_score == 88.5
    assert res.strengths == ["a"]
