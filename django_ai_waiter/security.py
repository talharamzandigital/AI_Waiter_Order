import time
import logging
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Rate limiting middleware.
    Limits requests per IP address.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 60      # requests
        self.time_window = 60     # seconds

    def __call__(self, request):
        # Only rate limit API endpoints
        if request.path.startswith("/api/"):
            ip = self.get_client_ip(request)
            key = f"rate_limit:{ip}"

            # Get current request count
            requests = cache.get(key, 0)

            if requests >= self.rate_limit:
                logger.warning(
                    f"Rate limit exceeded for IP: {ip}"
                )
                return JsonResponse(
                    {
                        "error": "Rate limit exceeded. Please wait before trying again.",
                        "retry_after": self.time_window,
                    },
                    status=429,
                )

            # Increment request count
            cache.set(key, requests + 1, self.time_window)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Get real IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class SecurityHeadersMiddleware:
    """Add security headers to all responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Cache-Control"] = "no-store"

        return response


def sanitize_input(text, max_length=1000):
    """
    Sanitize user input.
    - Remove dangerous characters
    - Limit length
    - Strip whitespace
    """
    if not text:
        return ""

    # Limit length
    text = str(text)[:max_length]

    # Strip whitespace
    text = text.strip()

    # Remove null bytes
    text = text.replace("\x00", "")

    return text


def validate_session_key(session_key):
    """Validate session key format."""
    if not session_key:
        return False
    if len(session_key) > 64:
        return False
    # Only allow alphanumeric and hyphens
    allowed = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789-_"
    )
    return all(c in allowed for c in session_key)