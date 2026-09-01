from abc import ABC, abstractmethod
from typing import Optional
from app.agent.schemas import LLMRecommendation

class BaseLLMProvider(ABC):
    @abstractmethod
    def get_recommendation(self, prompt: str) -> Optional[LLMRecommendation]:
        """
        Request a structured recommendation from the LLM.
        Returns None if the LLM is unavailable, times out, or returns invalid data.
        """
        pass
