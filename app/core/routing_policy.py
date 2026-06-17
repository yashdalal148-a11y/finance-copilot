from typing import Dict, List
from app.core.models import TaskType, ProviderName

class RoutingPolicy:
    """Defines which provider should handle which task, and the fallback order."""
    
    def __init__(self):
        # Maps TaskType -> List of ProviderNames (Primary, Fallback 1, Fallback 2...)
        self._routes: Dict[TaskType, List[ProviderName]] = {
            TaskType.CLASSIFICATION: [ProviderName.GROQ, ProviderName.OPENROUTER, ProviderName.GEMINI],
            TaskType.BATTLEFIELD_MAP: [ProviderName.GROQ, ProviderName.OPENROUTER, ProviderName.GEMINI],
            TaskType.FOLLOW_UP: [ProviderName.GROQ, ProviderName.OPENROUTER, ProviderName.GEMINI],
            TaskType.EVALUATION: [ProviderName.GROQ, ProviderName.OPENROUTER, ProviderName.GEMINI],
            
            TaskType.STORY_INTELLIGENCE: [ProviderName.GEMINI, ProviderName.OPENROUTER, ProviderName.GROQ],
            TaskType.RED_FLAG: [ProviderName.GEMINI, ProviderName.OPENROUTER, ProviderName.GROQ],
            TaskType.EXPERT_ANSWER: [ProviderName.GEMINI, ProviderName.OPENROUTER, ProviderName.GROQ],
            
            TaskType.RESUME_PARSING: [ProviderName.GEMINI, ProviderName.OPENROUTER],
            TaskType.JD_PARSING: [ProviderName.GEMINI, ProviderName.OPENROUTER],
            TaskType.FIT_ANALYSIS: [ProviderName.GEMINI, ProviderName.OPENROUTER],
            TaskType.INTENT_ANALYSIS: [ProviderName.GEMINI, ProviderName.OPENROUTER],
            TaskType.GAP_ANALYSIS: [ProviderName.GEMINI, ProviderName.OPENROUTER],
            TaskType.OFFER_PROBABILITY: [ProviderName.GEMINI, ProviderName.OPENROUTER],
            
            TaskType.GENERAL: [ProviderName.GEMINI, ProviderName.OPENROUTER, ProviderName.GROQ],
            
            # OS V1.5 Tasks
            TaskType.MEMORY_CONSOLIDATION: [ProviderName.GEMINI, ProviderName.OPENROUTER],
            TaskType.STOCK_PITCH: [ProviderName.GEMINI, ProviderName.OPENROUTER],
            TaskType.WEAKNESS_ANALYSIS: [ProviderName.GEMINI, ProviderName.OPENROUTER],
        }

    def get_route(self, task_type: TaskType) -> List[ProviderName]:
        """Return the prioritized list of providers for a given task."""
        return self._routes.get(task_type, [ProviderName.GEMINI, ProviderName.OPENROUTER])
