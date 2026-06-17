import time
import logging
from typing import Any

from app.core.models import TaskType, ProviderName
from app.core.routing_policy import RoutingPolicy
from app.core.provider_health import ProviderHealthTracker
from app.core.provider_benchmarking import ProviderBenchmarker
from app.core.provider_registry import ProviderRegistry

logger = logging.getLogger(__name__)

class LLMRouter:
    """Intelligent router that dynamically dispatches LLM calls based on task type and provider health."""
    
    def __init__(self, registry: ProviderRegistry):
        self._registry = registry
        self._policy = RoutingPolicy()
        self._health = ProviderHealthTracker()
        self._benchmarker = ProviderBenchmarker()
        
    @property
    def health(self) -> ProviderHealthTracker:
        return self._health

    @property
    def benchmarker(self) -> ProviderBenchmarker:
        return self._benchmarker

    def _execute_with_failover(self, prompt: str, task_type: TaskType, is_json: bool, temperature: float) -> str | dict[str, Any]:
        """Tries providers in the route sequence until one succeeds."""
        route = self._policy.get_route(task_type)
        
        for provider_name in route:
            # 1. Check health
            if not self._health.is_available(provider_name):
                logger.warning(f"Skipping {provider_name.value} - marked unavailable.")
                continue
                
            # 2. Get client
            client = self._registry.get_provider(provider_name)
            if not client:
                logger.warning(f"Skipping {provider_name.value} - client not configured.")
                continue

            # 3. Execute
            logger.info(f"Routing {task_type.value} to {provider_name.value}")
            t0 = time.perf_counter()
            try:
                if is_json:
                    result = client.generate_json(prompt, temperature=temperature)
                    result_str = str(result)
                else:
                    result = client.generate(prompt, temperature=temperature)
                    result_str = result
                
                latency_ms = (time.perf_counter() - t0) * 1000
                
                # 4. Record Success
                self._health.record_success(provider_name)
                self._benchmarker.record_request(
                    provider=provider_name, 
                    latency_ms=latency_ms, 
                    success=True, 
                    input_chars=len(prompt), 
                    output_chars=len(result_str)
                )
                return result
                
            except Exception as exc:
                latency_ms = (time.perf_counter() - t0) * 1000
                logger.error(f"Provider {provider_name.value} failed: {exc}")
                
                # 4. Record Failure
                self._health.record_failure(provider_name, str(exc))
                self._benchmarker.record_request(
                    provider=provider_name, 
                    latency_ms=latency_ms, 
                    success=False, 
                    input_chars=len(prompt), 
                    output_chars=0
                )
                # Continue loop to next provider
                
        # If we exhausted all providers
        logger.error(f"All providers failed for task {task_type.value}")
        if is_json:
            return {}
        return "System is currently unavailable. Please try again later."

    def generate(self, prompt: str, temperature: float = 0.3, max_output_tokens: int = 4096, task_type: TaskType = TaskType.GENERAL, response_mime_type: str | None = None) -> str:
        res = self._execute_with_failover(prompt, task_type, is_json=False, temperature=temperature)
        if isinstance(res, str):
            return res
        return str(res)

    def generate_json(self, prompt: str, temperature: float = 0.2, task_type: TaskType = TaskType.GENERAL) -> dict[str, Any]:
        res = self._execute_with_failover(prompt, task_type, is_json=True, temperature=temperature)
        if isinstance(res, dict):
            return res
        return {}
