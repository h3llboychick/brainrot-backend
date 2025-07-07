from ..settings import settings

from openai import OpenAI

class AIClient:
    def __init__(self, api_key: str, base_url="https://api.sambanova.ai/v1"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def chat_completion(
        self,
        messages: list[dict],
        model: str = settings.AI_MODEL,
        temperature: float = settings.AI_TEMPERATURE,
        max_tokens: int = settings.AI_MAX_TOKENS,
    ) -> str:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                max_completion_tokens=max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content
    
    
def get_ai_client(api_key: str = settings.SAMBANOVA_API_KEY) -> AIClient:
    return AIClient(api_key=api_key)