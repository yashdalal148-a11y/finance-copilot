import pytest
from unittest.mock import MagicMock
from app.core.models import TaskType, ResearchMemory
from app.agents.weakness_agent import WeaknessIntelligenceAgent

def test_weakness_agent():
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = {
        "strength_map": {"Accounting": "Good at 3 statements"},
        "weakness_map": {"Valuation": "Bad at LBOs"},
        "skill_gap_analysis": ["Needs LBO practice"],
        "roadmap": {
            "immediate_actions": ["Read Rosenbaum"],
            "short_term_goals": [],
            "long_term_goals": []
        }
    }
    
    agent = WeaknessIntelligenceAgent(llm=mock_llm)
    mem = ResearchMemory()
    analysis = agent.run(mem)
    
    assert analysis.strength_map["Accounting"] == "Good at 3 statements"
    assert analysis.skill_gap_analysis == ["Needs LBO practice"]
    assert analysis.roadmap is not None
    assert analysis.roadmap.immediate_actions == ["Read Rosenbaum"]
    
    mock_llm.generate_json.assert_called_once()
    kwargs = mock_llm.generate_json.call_args.kwargs
    assert kwargs["task_type"] == TaskType.WEAKNESS_ANALYSIS
