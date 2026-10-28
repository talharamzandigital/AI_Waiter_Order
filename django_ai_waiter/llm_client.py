import logging
import requests
from abc import ABC, abstractmethod
from groq import Groq

from django_ai_waiter import app_settings

logger = logging.getLogger(__name__)

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
    def __init__(self, api_key=None, model=None, max_tokens=None, temperature=None):
        self.api_key = api_key if api_key is not None else getattr(app_settings, "GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model = model or getattr(app_settings, "AI_MODEL", "openai/gpt-oss-20b")
        self.max_tokens = max(512, max_tokens if max_tokens is not None else getattr(app_settings, "AI_MAX_TOKENS", 1024))
        self.temperature = temperature if temperature is not None else getattr(app_settings, "AI_TEMPERATURE", 0.3)

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

            choice = response.choices[0]
            content = choice.message.content
            if not content:
                content = getattr(choice.message, "reasoning", None) or "I'm sorry, I could not generate a response. Please try again."

            return {
                "role": "assistant",
                "content": content,
                "model": self.model,
                "mock": False,
            }

        except Exception as e:
            logger.error("Groq API error: %s", e)
            return {
                "role": "assistant",
                "content": "Sorry, I am having trouble processing your request right now. Please try again.",
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

                if role == last_role and role != "system":
                    # Merge with previous message instead of dropping it
                    cleaned_messages[-1]["content"] += "\n\n" + content
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
        logger.info("Selected LLM client: OllamaLLMClient")
        return ollama

    groq_api_key = getattr(app_settings, "GROQ_API_KEY", "")
    if use_real and groq_api_key:
        logger.info("Selected LLM client: GroqLLMClient")
        return GroqLLMClient(api_key=groq_api_key)

    logger.info("Selected LLM client: MockLLMClient")
    return MockLLMClient()