import os
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from config import AI_INTEGRATIONS_OPENAI_API_KEY, AI_INTEGRATIONS_OPENAI_BASE_URL

def is_rate_limit_error(exception: BaseException) -> bool:
    error_msg = str(exception)
    return (
        "429" in error_msg
        or "RATELIMIT_EXCEEDED" in error_msg
        or "quota" in error_msg.lower()
        or "rate limit" in error_msg.lower()
        or (hasattr(exception, "status_code") and exception.status_code == 429)
    )

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
client = OpenAI(
    api_key=AI_INTEGRATIONS_OPENAI_API_KEY,
    base_url=AI_INTEGRATIONS_OPENAI_BASE_URL
)

class AIAgent:
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.client = client
    
    @retry(
        stop=stop_after_attempt(7),
        wait=wait_exponential(multiplier=1, min=2, max=128),
        retry=retry_if_exception(is_rate_limit_error),
        reraise=True
    )
    def generate_response(self, system_prompt: str, user_message: str, context: str = "") -> str:
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Contexto adicional:\n{context}"})
        
        messages.append({"role": "user", "content": user_message})
        
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        response = self.client.chat.completions.create(
            model="gpt-5",
            messages=messages,
            max_completion_tokens=8192
        )
        
        return response.choices[0].message.content or ""
    
    @retry(
        stop=stop_after_attempt(7),
        wait=wait_exponential(multiplier=1, min=2, max=128),
        retry=retry_if_exception(is_rate_limit_error),
        reraise=True
    )
    def generate_structured_response(self, system_prompt: str, user_message: str, context: str = "") -> str:
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Contexto adicional:\n{context}"})
        
        messages.append({"role": "user", "content": user_message})
        
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        response = self.client.chat.completions.create(
            model="gpt-5",
            messages=messages,
            response_format={"type": "json_object"},
            max_completion_tokens=8192
        )
        
        return response.choices[0].message.content or ""
