import requests
from abc import ABC, abstractmethod
from groq import Groq

from django_ai_waiter.app_settings import (
    AI_MODEL,
    AI_MAX_TOKENS,
    AI_TEMPERATURE,
    GROQ_API_KEY,
)

# ============================================================
# BASE CLIENT
# ============================================================

class BaseLLMClient(ABC):

    @abstractmethod
    def chat(self, system_prompt, messages, **kwargs):
        pass

    @abstractmethod
    def is_available(self):
        pass


# ============================================================
# MOCK CLIENT (for testing without AI)
# ============================================================

class MockLLMClient(BaseLLMClient):

    RESPONSES = [
        "Welcome! I am your AI waiter. How can I help you today?",
        "Great choice! I have added that to your order.",
        "Our menu is ready. What would you like to eat?",
        "Your item has been added to cart.",
        "Would you like anything else?",
        "Your order is confirmed!",
        "Let me suggest today's special items.",
    ]

    def __init__(self):
        self.model = AI_MODEL

    def chat(self, system_prompt, messages, **kwargs):

        import random

        last_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg.get("content", "").lower()
                break

        if "hello" in last_message or "hi" in last_message:
            response = "Hello! Welcome to AI Waiter 😊"
        elif "menu" in last_message:
            response = "We have Burger, Pizza, Pasta, Drinks."
        elif "order" in last_message or "want" in last_message:
            response = "Done! I added it to your order."
        elif "bill" in last_message or "total" in last_message:
            response = "Your bill will include tax (8%)."
        else:
            response = random.choice(self.RESPONSES)

        return {
            "role": "assistant",
            "content": response,
            "model": self.model,
            "mock": True,
        }

    def is_available(self):
        return True


# ============================================================
# GROQ CLIENT (REAL AI)
# ============================================================

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
                "content": "Groq API error occurred. Please try again.",
                "model": self.model,
                "mock": False,
                "error": str(e),
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


# ============================================================
# FACTORY FUNCTION
# ============================================================

def get_llm_client(use_real=True):
    """
    Returns Groq client if API key exists,
    otherwise fallback to Mock client.
    """

    if use_real and GROQ_API_KEY:
        return GroqLLMClient()

    return MockLLMClient()