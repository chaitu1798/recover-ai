import os
import json
import logging
from typing import Optional
from app.agent.schemas import LLMRecommendation
from app.agent.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning("openai package not installed. OpenAIProvider will be inactive.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    def get_recommendation(self, prompt: str) -> Optional[LLMRecommendation]:
        if not self.client:
            logger.warning("OpenAI client not initialized. Falling back.")
            return None
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a safe, recommendation-only recovery agent. Output valid JSON matching the schema."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                timeout=10.0
            )
            
            content = response.choices[0].message.content
            if not content:
                return None
                
            data = json.loads(content)
            recommendation = LLMRecommendation(**data)
            return recommendation
            
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            return None
