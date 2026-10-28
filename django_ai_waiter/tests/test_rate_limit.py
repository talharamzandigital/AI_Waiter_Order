from unittest.mock import patch
import pytest
from django.core.cache import cache
from django.test import Client, override_settings

from django_ai_waiter.llm_client import MockLLMClient


@pytest.fixture(autouse=True)
def mock_health_dependencies():
    with patch("django_ai_waiter.views.get_llm_client", return_value=MockLLMClient()), \
         patch("django_ai_waiter.views.get_mcp_client") as mock_mcp:
        mock_mcp.return_value.is_available.return_value = True
        yield


@pytest.mark.django_db
class TestRateLimitMiddleware:

    @override_settings(
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
        RATE_LIMIT_REQUESTS=60,
        RATE_LIMIT_WINDOW=60,
    )
    def test_61st_request_returns_http_429(self):
        cache.clear()
        client = Client()

        # Send 60 requests within window
        for i in range(60):
            response = client.get("/api/health/")
            assert response.status_code == 200, f"Request {i+1} failed with {response.status_code}"

        # 61st request must be rate-limited
        blocked_response = client.get("/api/health/")
        assert blocked_response.status_code == 429
        data = blocked_response.json()
        assert "Rate limit exceeded" in data["error"]
        assert data["retry_after"] == 60

    @override_settings(
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
        RATE_LIMIT_REQUESTS=5,
        RATE_LIMIT_WINDOW=30,
    )
    def test_configurable_rate_limit_and_window(self):
        cache.clear()
        client = Client()

        for _ in range(5):
            response = client.get("/api/health/")
            assert response.status_code == 200

        blocked_response = client.get("/api/health/")
        assert blocked_response.status_code == 429
        data = blocked_response.json()
        assert data["retry_after"] == 30

    @override_settings(
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
        RATE_LIMIT_REQUESTS=2,
        RATE_LIMIT_WINDOW=60,
    )
    def test_non_api_route_not_rate_limited(self):
        cache.clear()
        client = Client()

        # Non-API route should not be rate-limited even if exceeding RATE_LIMIT_REQUESTS
        for _ in range(5):
            response = client.get("/")
            assert response.status_code == 200
