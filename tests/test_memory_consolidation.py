import pytest
from unittest.mock import MagicMock
from app.core.models import ResearchMemory, TaskType
from app.core.session import SessionMemory, SessionEntry
from app.agents.memory_consolidation_agent import MemoryConsolidationAgent

def test_memory_consolidation_agent():
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = {
        "candidate": {"strength_trends": ["DCF Models"], "weakness_trends": ["LBO Math"], "career_goals": []},
        "evolution": {"timeline_events": ["Completed mock interview"], "overall_trajectory": "Improving"},
        "interview": {"best_answers": ["Good DCF explanation"], "common_mistakes": [], "readiness_history": [85.0]},
        "learning": {"learning_priorities": ["LBOs"], "improvement_history": []},
        "stock_pitch": {"pitch_history": []}
    }
    
    agent = MemoryConsolidationAgent(llm=mock_llm)
    
    current_mem = ResearchMemory()
    session = SessionMemory()
    session.entries.append(SessionEntry(question="Walk me through a DCF", answer="Here is my answer...", category="Valuation"))
    
    updated_mem = agent.run(current_mem, session)
    
    assert "DCF Models" in updated_mem.candidate.strength_trends
    assert "LBO Math" in updated_mem.candidate.weakness_trends
    assert updated_mem.evolution.overall_trajectory == "Improving"
    assert updated_mem.interview.readiness_history == [85.0]
    
    mock_llm.generate_json.assert_called_once()
    kwargs = mock_llm.generate_json.call_args.kwargs
    assert kwargs["task_type"] == TaskType.MEMORY_CONSOLIDATION
