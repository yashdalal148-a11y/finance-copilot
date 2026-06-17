import pytest
from unittest.mock import MagicMock
from app.core.models import TaskType
from app.agents.stock_pitch_agent import StockPitchAgent

def test_stock_pitch_agent():
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = {
        "business_overview": "AI chips",
        "industry_structure": "Monopoly",
        "competitive_landscape": "No competition",
        "management_assessment": "Great CEO",
        "investment_thesis": "Long term growth",
        "bull_case": "Upside",
        "bear_case": "Downside",
        "catalysts": ["Earnings"],
        "risks": ["Supply chain"],
        "valuation_framework": "DCF",
        "md_critique": {"blunt_feedback": "Terrible", "fatal_flaws": []},
        "ic_verdict": {"decision": "PASS", "key_debate_points": []}
    }
    
    agent = StockPitchAgent(llm=mock_llm)
    pitch = agent.run("Nvidia", "NVDA", "AI boom")
    
    assert pitch.company_name == "Nvidia"
    assert pitch.ticker == "NVDA"
    assert pitch.memo is not None
    assert pitch.memo.business_overview == "AI chips"
    assert pitch.memo.md_critique.blunt_feedback == "Terrible"
    assert pitch.memo.ic_verdict.decision == "PASS"
    
    mock_llm.generate_json.assert_called_once()
    kwargs = mock_llm.generate_json.call_args.kwargs
    assert kwargs["task_type"] == TaskType.STOCK_PITCH
