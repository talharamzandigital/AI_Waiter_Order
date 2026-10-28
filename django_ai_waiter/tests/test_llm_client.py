from unittest.mock import MagicMock
import pytest
from django_ai_waiter import app_settings
from django_ai_waiter.llm_client import (
    OllamaLLMClient,
    GroqLLMClient,
    MockLLMClient,
    get_llm_client,
)


class TestGetLLMClient:
    def test_ollama_path_when_available(self, monkeypatch, caplog):
        monkeypatch.setattr(OllamaLLMClient, "is_available", lambda self: True)
        with caplog.at_level("INFO"):
            client = get_llm_client(use_real=True)

        assert isinstance(client, OllamaLLMClient)
        assert "Selected LLM client: OllamaLLMClient" in caplog.text

    def test_groq_path_when_ollama_unavailable_and_key_present(self, monkeypatch, caplog):
        monkeypatch.setattr(OllamaLLMClient, "is_available", lambda self: False)
        monkeypatch.setattr(app_settings, "GROQ_API_KEY", "test-secret-key-12345")

        with caplog.at_level("INFO"):
            client = get_llm_client(use_real=True)

        assert isinstance(client, GroqLLMClient)
        assert "Selected LLM client: GroqLLMClient" in caplog.text
        # Ensure secret API key is NEVER logged
        assert "test-secret-key-12345" not in caplog.text

    def test_mock_path_when_no_key(self, monkeypatch, caplog):
        monkeypatch.setattr(OllamaLLMClient, "is_available", lambda self: False)
        monkeypatch.setattr(app_settings, "GROQ_API_KEY", "")

        with caplog.at_level("INFO"):
            client = get_llm_client(use_real=True)

        assert isinstance(client, MockLLMClient)
        assert "Selected LLM client: MockLLMClient" in caplog.text

    def test_mock_path_when_use_real_is_false(self, monkeypatch, caplog):
        monkeypatch.setattr(OllamaLLMClient, "is_available", lambda self: False)
        monkeypatch.setattr(app_settings, "GROQ_API_KEY", "test-secret-key-12345")

        with caplog.at_level("INFO"):
            client = get_llm_client(use_real=False)

        assert isinstance(client, MockLLMClient)
        assert "Selected LLM client: MockLLMClient" in caplog.text


class TestGroqClient:
    def test_sends_configured_model_name(self, monkeypatch):
        configured_model = "openai/gpt-oss-20b"
        client = GroqLLMClient(api_key="mock-key", model=configured_model)
        assert client.model == configured_model
        assert client.max_tokens >= 512

        mock_create = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Here is your pizza!"
        mock_choice.message.reasoning = None
        mock_create.return_value = MagicMock(choices=[mock_choice])
        monkeypatch.setattr(client.client.chat.completions, "create", mock_create)

        response = client.chat(
            system_prompt="You are a waiter",
            messages=[{"role": "user", "content": "I want pizza"}]
        )

        assert response["role"] == "assistant"
        assert response["content"] == "Here is your pizza!"
        assert response["model"] == configured_model
        assert not response["mock"]

        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["model"] == configured_model
        assert call_kwargs["max_tokens"] >= 512

    def test_handles_empty_message_content_fallback(self, monkeypatch):
        client = GroqLLMClient(api_key="mock-key", model="openai/gpt-oss-20b")
        mock_create = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = ""
        mock_choice.message.reasoning = None
        mock_create.return_value = MagicMock(choices=[mock_choice])
        monkeypatch.setattr(client.client.chat.completions, "create", mock_create)

        response = client.chat(
            system_prompt="You are a waiter",
            messages=[{"role": "user", "content": "hello"}]
        )

        assert response["content"] != ""
        assert "sorry" in response["content"].lower() or "could not generate" in response["content"].lower()

    def test_handles_reasoning_when_content_is_empty(self, monkeypatch):
        client = GroqLLMClient(api_key="mock-key", model="openai/gpt-oss-20b")
        mock_create = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = None
        mock_choice.message.reasoning = "I recommend our burger deal."
        mock_create.return_value = MagicMock(choices=[mock_choice])
        monkeypatch.setattr(client.client.chat.completions, "create", mock_create)

        response = client.chat(
            system_prompt="You are a waiter",
            messages=[{"role": "user", "content": "What do you recommend?"}]
        )

        assert response["content"] == "I recommend our burger deal."

    def test_groq_error_returns_clean_fallback(self, monkeypatch, caplog):
        client = GroqLLMClient(api_key="mock-key", model="openai/gpt-oss-20b")
        mock_create = MagicMock(side_effect=Exception("404 model_not_found: retired model llama-3.1-8b-instant"))
        monkeypatch.setattr(client.client.chat.completions, "create", mock_create)

        with caplog.at_level("ERROR"):
            response = client.chat(
                system_prompt="You are a waiter",
                messages=[{"role": "user", "content": "Show menu"}]
            )

        assert response["content"] == "Sorry, I am having trouble processing your request right now. Please try again."
        assert "404 model_not_found" not in response["content"]
        assert "Groq error:" not in response["content"]
        assert "Groq API error:" in caplog.text
