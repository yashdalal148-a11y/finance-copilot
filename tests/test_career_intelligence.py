import pytest
from unittest.mock import MagicMock
from pathlib import Path

from app.core.models import (
    CandidateProfile, JobProfile, FitAnalysis, CareerStory, BattlefieldMap,
    BattlefieldQuestion, RedFlagAnalysis, CareerGapAnalysis, OfferProbabilityAnalysis
)

from app.agents.story_agent import StoryIntelligenceAgent
from app.agents.battlefield_agent import BattlefieldMapAgent
from app.agents.red_flag_agent import RedFlagAgent
from app.agents.intent_agent import IntentVerdictAgent
from app.agents.gap_agent import CareerGapAgent
from app.agents.offer_agent import OfferProbabilityAgent

@pytest.fixture
def mock_llm():
    return MagicMock()

@pytest.fixture
def prompts_dir(tmp_path):
    for filename in [
        "story_intelligence_prompt.txt",
        "battlefield_map_prompt.txt",
        "red_flag_prompt.txt",
        "intent_verdict_prompt.txt",
        "career_gap_prompt.txt",
        "offer_probability_prompt.txt"
    ]:
        (tmp_path / filename).write_text("Dummy prompt")
    return tmp_path

def test_story_agent(mock_llm, prompts_dir):
    mock_llm.generate_json.return_value = [
        {"title": "Intro", "duration_target": "30s", "narrative": "Hello", "key_signals": ["A"]}
    ]
    agent = StoryIntelligenceAgent(mock_llm, prompts_dir)
    res = agent.run(CandidateProfile(), JobProfile())
    assert len(res) == 1
    assert res[0].title == "Intro"

def test_battlefield_agent(mock_llm, prompts_dir):
    mock_llm.generate_json.return_value = {
        "top_questions": [
            {"question": "Q1", "probability": 0.9, "difficulty": 0.5, "importance": 0.8, "preparation_priority": "High"}
        ]
    }
    agent = BattlefieldMapAgent(mock_llm, prompts_dir)
    res = agent.run(CandidateProfile(), JobProfile())
    assert len(res.top_questions) == 1
    assert res.top_questions[0].question == "Q1"

def test_red_flag_agent(mock_llm, prompts_dir):
    mock_llm.generate_json.return_value = {
        "flags": [
            {"flag": "F1", "interviewer_worry": "W1", "suggested_response": "R1", "recovery_strategy": "S1"}
        ]
    }
    agent = RedFlagAgent(mock_llm, prompts_dir)
    res = agent.run(CandidateProfile(), FitAnalysis())
    assert len(res.flags) == 1
    assert res.flags[0].flag == "F1"

def test_intent_verdict_agent(mock_llm, prompts_dir):
    mock_llm.generate_json.return_value = {
        "intent": {"core_test": "T1", "technical_depth": "D1", "communication_signals": [], "common_mistakes": []},
        "verdict": {"passing_criteria": "P1", "red_flag_triggers": [], "differentiation_factors": []}
    }
    agent = IntentVerdictAgent(mock_llm, prompts_dir)
    intent, verdict = agent.run("What is EBITDA?")
    assert intent.core_test == "T1"
    assert verdict.passing_criteria == "P1"

def test_gap_agent(mock_llm, prompts_dir):
    mock_llm.generate_json.return_value = {
        "missing_experiences": ["E1"],
        "missing_skills": ["S1"],
        "suggested_development_plan": ["D1"]
    }
    agent = CareerGapAgent(mock_llm, prompts_dir)
    res = agent.run(CandidateProfile(), JobProfile())
    assert res.missing_experiences == ["E1"]

def test_offer_agent(mock_llm, prompts_dir):
    mock_llm.generate_json.return_value = {
        "offer_probability": 0.85,
        "top_risks": ["R1"],
        "highest_leverage_improvements": ["I1"]
    }
    agent = OfferProbabilityAgent(mock_llm, prompts_dir)
    res = agent.run(CandidateProfile(), JobProfile(), FitAnalysis(), BattlefieldMap())
    assert res.offer_probability == 0.85
