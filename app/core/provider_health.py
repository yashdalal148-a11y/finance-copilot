import time
import logging
from typing import Dict
from app.core.models import ProviderName, ProviderHealth, ProviderHealthStatus

logger = logging.getLogger(__name__)

class ProviderHealthTracker:
    def __init__(self):
        self._health: Dict[ProviderName, ProviderHealth] = {
            ProviderName.GEMINI: ProviderHealth(),
            ProviderName.GROQ: ProviderHealth(),
            ProviderName.OPENROUTER: ProviderHealth(),
        }
        self._max_failures = 3
        self._cooldown_s = 60.0

    def get_health(self, provider: ProviderName) -> ProviderHealth:
        return self._health[provider]

    def record_success(self, provider: ProviderName):
        h = self._health[provider]
        h.consecutive_failures = 0
        h.last_error_message = ""
        if h.status != ProviderHealthStatus.ONLINE:
            logger.info(f"Provider {provider.value} recovered and is back ONLINE.")
            h.status = ProviderHealthStatus.ONLINE

    def record_failure(self, provider: ProviderName, error_msg: str):
        h = self._health[provider]
        h.consecutive_failures += 1
        h.last_failure_time = time.time()
        h.last_error_message = error_msg
        
        if h.consecutive_failures >= self._max_failures:
            h.status = ProviderHealthStatus.OFFLINE
            logger.warning(f"Provider {provider.value} marked OFFLINE due to {h.consecutive_failures} consecutive failures.")
        else:
            h.status = ProviderHealthStatus.DEGRADED
            logger.warning(f"Provider {provider.value} marked DEGRADED (failure {h.consecutive_failures}/{self._max_failures}).")

    def is_available(self, provider: ProviderName) -> bool:
        h = self._health[provider]
        if h.status == ProviderHealthStatus.ONLINE:
            return True
        if h.status == ProviderHealthStatus.OFFLINE:
            # Check for cooldown
            if h.last_failure_time and (time.time() - h.last_failure_time > self._cooldown_s):
                logger.info(f"Provider {provider.value} cooldown elapsed. Attempting recovery.")
                h.status = ProviderHealthStatus.DEGRADED
                return True
            return False
        return True # Try if degraded
