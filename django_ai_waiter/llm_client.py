import requests
from abc import ABC, abstractmethod
from groq import Groq

from django_ai_waiter.app_settings import (
    AI_MODEL,
    AI_MAX_TOKENS,
    AI_TEMPERATURE,
    GROQ_API_KEY,
)

# =========================
# BASE CLASS
# =========================
class BaseLLMClient(ABC):
    @abstractmethod
    def chat(self, system_prompt, messages, **kwargs):
        pass

    @abstractmethod
    def is_available(self):
        pass


# =========================
# MOCK CLIENT
# =========================
class MockLLMClient(BaseLLMClient):
    def chat(self, system_prompt, messages, **kwargs):
        return {
            "role": "assistant",
            "content": "Welcome! I am your AI waiter.",
            "model": "mock",
            "mock": True,
        }

    def is_available(self):
        return True


# =========================
# GROQ CLIENT
# =========================
class GroqLLMClient(BaseLLMClient):
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = AI_MODEL
        self.max_tokens = AI_MAX_TOKENS
        self.temperature = AI_TEMPERATURE

    def chat(self, system_prompt, messages, **kwargs):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            return {
                "role": "assistant",
                "content": response.choices[0].message.content,
                "model": self.model,
                "mock": False,
            }

        except Exception as e:
            return {
                "role": "assistant",
                "content": f"Groq error: {str(e)}",
                "model": self.model,
                "mock": False,
            }

    def is_available(self):
        try:
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
            )
            return True
        except Exception:
            return False


# =========================
# OLLAMA CLIENT (FIXED)
# =========================
class OllamaLLMClient(BaseLLMClient):
    def __init__(self):
        self.model = "ai-waiter:latest"
        self.base_url = "http://localhost:11434"

    def chat(self, system_prompt, messages, **kwargs):
        try:
            session = requests.Session()

            cleaned_messages = [
                {"role": "system", "content": system_prompt}
            ]

            last_role = "system"

            for msg in messages:
                role = msg.get("role")
                content = msg.get("content")

                if role == last_role:
                    continue

                cleaned_messages.append({
                    "role": role,
                    "content": content
                })

                last_role = role

            payload = {
                "model": self.model,
                "messages": cleaned_messages,
                "stream": False,
            }

            response = session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=600,
            )

            print("STATUS:", response.status_code)
            print("BODY:", response.text)

            response.raise_for_status()

            data = response.json()

            return {
                "role": "assistant",
                "content": data["message"]["content"],
                "model": self.model,
                "mock": False,
            }

        except Exception as e:
            return {
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "model": self.model,
                "mock": False,
                "error": str(e),
            }

    def is_available(self):
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False


# =========================
# FACTORY
# =========================
def get_llm_client(use_real=True):
    ollama = OllamaLLMClient()

    if ollama.is_available():
        return ollama

    if use_real and GROQ_API_KEY:
        return GroqLLMClient()

    return MockLLMClient()