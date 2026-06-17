import logging
from typing import Dict
from app.core.models import ProviderName, ProviderMetrics

logger = logging.getLogger(__name__)

class ProviderBenchmarker:
    def __init__(self):
        self._metrics: Dict[ProviderName, ProviderMetrics] = {
            ProviderName.GEMINI: ProviderMetrics(),
            ProviderName.GROQ: ProviderMetrics(),
            ProviderName.OPENROUTER: ProviderMetrics(),
        }

    def get_metrics(self, provider: ProviderName) -> ProviderMetrics:
        return self._metrics[provider]

    def get_all_metrics(self) -> Dict[ProviderName, ProviderMetrics]:
        return self._metrics

    def record_request(self, provider: ProviderName, latency_ms: float, success: bool, input_chars: int, output_chars: int):
        m = self._metrics[provider]
        m.total_requests += 1
        m.total_latency_ms += latency_ms
        m.avg_latency_ms = m.total_latency_ms / m.total_requests
        
        if success:
            m.successful_requests += 1
        else:
            m.failed_requests += 1

        # Very rough cost estimation based on characters
        # Assuming ~4 chars per token
        input_tokens = input_chars / 4
        output_tokens = output_chars / 4
        
        if provider == ProviderName.GEMINI:
            m.estimated_cost_usd += (input_tokens * 0.000000075) + (output_tokens * 0.0000003)
        elif provider == ProviderName.GROQ:
            m.estimated_cost_usd += (input_tokens * 0.00000005) + (output_tokens * 0.00000005)
        elif provider == ProviderName.OPENROUTER:
            m.estimated_cost_usd += (input_tokens * 0.0000001) + (output_tokens * 0.0000002)

        logger.debug(f"Benchmarked {provider.value}: {latency_ms:.0f}ms. Total cost: ${m.estimated_cost_usd:.6f}")
