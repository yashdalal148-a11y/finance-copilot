import pytest
from unittest.mock import MagicMock
from app.core.models import TaskType, ProviderName
from app.core.llm_router import LLMRouter
from app.core.provider_registry import ProviderRegistry

def test_llm_router_routing():
    # Setup mock registry with mock clients
    gemini_mock = MagicMock()
    gemini_mock.generate.return_value = "Gemini Answer"
    
    groq_mock = MagicMock()
    groq_mock.generate.return_value = "Groq Answer"
    
    openrouter_mock = MagicMock()
    openrouter_mock.generate.return_value = "OpenRouter Answer"

    registry_mock = MagicMock(spec=ProviderRegistry)
    
    def get_provider_side_effect(name):
        if name == ProviderName.GEMINI:
            return gemini_mock
        elif name == ProviderName.GROQ:
            return groq_mock
        elif name == ProviderName.OPENROUTER:
            return openrouter_mock
        return None
        
    registry_mock.get_provider.side_effect = get_provider_side_effect

    router = LLMRouter(registry=registry_mock)

    # Test classification routes to Groq
    res = router.generate("test prompt", task_type=TaskType.CLASSIFICATION)
    assert res == "Groq Answer"
    assert router.benchmarker.get_metrics(ProviderName.GROQ).successful_requests == 1
    assert router.benchmarker.get_metrics(ProviderName.GEMINI).successful_requests == 0
    
    # Test expert answer routes to Gemini
    res2 = router.generate("test prompt", task_type=TaskType.EXPERT_ANSWER)
    assert res2 == "Gemini Answer"
    assert router.benchmarker.get_metrics(ProviderName.GEMINI).successful_requests == 1

def test_llm_router_failover():
    # Setup mock registry where primary fails but fallback succeeds
    groq_mock = MagicMock()
    groq_mock.generate.side_effect = Exception("Rate Limited")
    
    openrouter_mock = MagicMock()
    openrouter_mock.generate.return_value = "OpenRouter Saved The Day"
    
    registry_mock = MagicMock(spec=ProviderRegistry)
    def get_provider_side_effect(name):
        if name == ProviderName.GROQ: return groq_mock
        if name == ProviderName.OPENROUTER: return openrouter_mock
        return None
    registry_mock.get_provider.side_effect = get_provider_side_effect

    router = LLMRouter(registry=registry_mock)

    # Classification routes to Groq -> Fails -> Falls back to OpenRouter
    res = router.generate("test prompt", task_type=TaskType.CLASSIFICATION)
    
    assert res == "OpenRouter Saved The Day"
    
    # Verify metrics
    assert router.benchmarker.get_metrics(ProviderName.GROQ).failed_requests == 1
    assert router.benchmarker.get_metrics(ProviderName.GROQ).successful_requests == 0
    assert router.benchmarker.get_metrics(ProviderName.OPENROUTER).successful_requests == 1
    
    # Verify health
    assert router.health.get_health(ProviderName.GROQ).consecutive_failures == 1
    assert router.health.get_health(ProviderName.GROQ).last_error_message == "Rate Limited"
